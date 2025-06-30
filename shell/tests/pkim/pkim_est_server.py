#!/bin/env python3

import argparse
import base64
import datetime
import logging as log
import os
import random
import re
import ssl
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# Workaround for old openssl versions, such as the one found on FUT
# RPI servers
ANCIENT_OPENSSL = True


# ------------------------------------------------------------------------------
# Mock EST Server Implementation
#
# The EST server contains some features that are necessary to support FUTs, but
# the server can be run as a stand-alone service (see the main function below).
# ------------------------------------------------------------------------------
class ESTRequestHandler(BaseHTTPRequestHandler):
    BASE_URL = "/.well-known/est/"

    def __init__(self, request, client, server, est_server):
        self.est_server = est_server
        super().__init__(request, client, server)

    def do_GET(self):
        try:
            method = "GET_" + self.get_method()
            reply = getattr(self.est_server, method, self.GET_404_not_found)(self.path)
            self.http_reply(*reply)
        except Exception as e:
            log.error(f"GET method failed ({self.path})", exc_info=e)
            self.http_reply(418, "Error processing GET method: {0}\n".format(str(e)))

    def do_POST(self):
        try:
            method = "POST_" + self.get_method()
            # If there's data attached to the POST request (likely), read it to
            # memory
            data = None
            cl = self.headers.get("Content-length")
            if cl:
                sz = int(cl)
                data = self.rfile.read(sz)
            reply = getattr(self.est_server, method, self.POST_404_not_found)(self.path, data)
            self.http_reply(*reply)
        except Exception as e:
            log.error(f"POST method failed ({self.path})", exc_info=e)
            self.http_reply(418, "Error processing GET method: {0}\n".format(str(e)))

    def get_method(self):
        """Given URL in `self.path`, extract the method name."""
        if not self.path.startswith(self.BASE_URL):
            raise Exception(f"Not well known URL ({self.BASE_URL}): {self.path}")
        get_req = self.path[len(self.BASE_URL) :]

        method = re.sub(r"[^a-zA-Z0-9-_]", "_", get_req).lower().rstrip("_")
        if not method:
            raise ValueError(f"Error parsing method: {self.path}")
        return method

    def http_reply(self, code, body, headers=None):
        """Issue a HTTP reply."""
        if isinstance(body, str):
            body = body.encode()

        if headers is None:
            headers = {}

        if "Content-type" not in headers:
            headers["Content-type"] = "text/html"

        if "Content-length" not in headers:
            headers["Content-length"] = len(body)

        self.send_response(code)
        for header, data in headers.items():
            self.send_header(header, data)
        self.end_headers()
        self.wfile.write(body)

    def GET_404_not_found(self, url):
        return (404, "GET method not found.\n")

    def POST_404_not_found(self, url, data):
        return (404, "POST method not found.\n")


class ESTServer:
    def __init__(self, host, port, cafile=None, keyfile=None, cert_expire=180):
        self.host = host
        self.port = port
        self.keyfile = keyfile if keyfile else tempfile.NamedTemporaryFile().name
        self.cafile = cafile if cafile else tempfile.NamedTemporaryFile().name
        self.server = None
        self.test_flow = None
        self.retry_after = None
        self.serial = random.randint(0, 2**30)
        self.__generate_self_signed_cert()
        self.cert_expire = cert_expire

    def __enter__(self):
        """Start EST server within a `with` statement."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Stop EST server within a `with` statement."""
        self.stop()

    def __start_threaded(self):
        log.info(f"Serving EST/HTTPS on {self.host}:{self.port}")
        self.server.serve_forever()

    def start(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=self.cafile, keyfile=self.keyfile)

        def http_request_factory(request, client, server):
            return ESTRequestHandler(request, client, server, self)

        self.server = HTTPServer((self.host, self.port), http_request_factory)
        self.server.socket = context.wrap_socket(self.server.socket, server_side=True)
        self.server_thread = threading.Thread(target=self.__start_threaded)
        self.server_thread.start()

    def stop(self):
        log.info("Shutting down EST server...")
        # Shutdown http server instance
        self.server.shutdown()
        self.server.server_close()
        # Wait for the thread to exit
        self.server_thread.join(timeout=10)
        os.unlink(self.keyfile)
        os.unlink(self.cafile)
        log.info("EST server shutdown.")

    # Non-standard method for passing parameters to the FUT tests
    def GET_fut_params(self, url):
        # serial=<serial number of the next certificate>
        return (200, f"serial={self.serial:X}")

    def GET_cacerts(self, url):
        try:
            with open(self.cafile, "rb") as f:
                resp = f.read()
                if self.test_flow:
                    self.test_flow.event(step="HTTP_CaCerts")
        except Exception as e:
            log.error("Error during cacerts request", exc_info=e)
            if self.test_flow:
                self.test_flow.event(step="FAIL_CaCerts")
            raise e

        return (200, self.pem_to_pkcs7der_base64(resp), {"Content-type": "application/octet-stream"})

    def POST_simpleenroll(self, url, data):
        try:
            # Reply-After case
            if self.retry_after:
                # The test flow event below resets the retry_after value, so
                # construct the reply here
                retry_headers = {"Retry-After": self.retry_after}
                if self.test_flow:
                    self.test_flow.event(step="HTTP_RetryAfter")
                return (503, "Test Retry-After", retry_headers)

            (http_code, http_data) = self.__do_enroll(url, data)
            if self.test_flow:
                if http_code == 200:
                    self.test_flow.event(step="HTTP_SimpleEnroll")
                else:
                    self.test_flow.event(step="FAIL_SimpleEnroll")
        except Exception as e:
            log.error("SimpleEnroll exception", exc_info=e)
            if self.test_flow:
                self.test_flow.event(step="EXCEPTION_SimpleEnroll")
            raise e

        return (http_code, http_data, {"Content-type": "application/octet-stream"})

    def POST_simplereenroll(self, url, data):
        try:
            # Reply-After case
            if self.retry_after:
                # The test flow event below resets the retry_after value, so
                # construct the reply here
                retry_headers = {"Retry-After": self.retry_after}
                if self.test_flow:
                    self.test_flow.event(step="HTTP_RetryAfter")
                return (503, "Test Retry-After", retry_headers)

            (http_code, http_data) = self.__do_enroll(url, data)
            if self.test_flow:
                if http_code == 200:
                    self.test_flow.event(step="HTTP_SimpleReEnroll")
                else:
                    self.test_flow.event(step="FAIL_SimpleReEnroll")
        except Exception as e:
            log.error("SimpleReEnroll exception", exc_info=e)
            self.test_flow.event(step="EXCEPTION_SimpleReEnroll")
            return

        return (http_code, http_data, {"Content-type": "application/octet-stream"})

    def __do_enroll(self, url, data):
        if not data:
            return (400, "Bad request -- no data present.\n")

        if not ANCIENT_OPENSSL:
            # The client and server time may be out of sync by a
            # couple of seconds, give out a certificate that starts 10 minutes
            # earlier just to avoid these timing issues
            now = datetime.datetime.now(datetime.timezone.utc)
            now -= datetime.timedelta(minutes=10)
            asn1 = now.strftime("%y%m%d%H%M%SZ")
            crt_date = ["-not_before", asn1]

            # Get a DER certificate
            result = subprocess.run(
                [
                    "openssl",
                    "x509",
                    "-req",
                    "-inform",
                    "DER",
                    "-in",
                    "-",
                    "-CA",
                    self.cafile,
                    "-CAkey",
                    self.keyfile,
                    "-set_serial",
                    str(self.new_serial()),
                    "-days",
                    self.cert_expire,
                    *crt_date,
                ],
                stdout=subprocess.PIPE,
                input=base64.b64decode(data),
            )

            if result.returncode != 0:
                log.info(f"Error generating certificat: {result.stdout}")
                return (418, f"Error generating certificate: {result.stdout}")

            crt_pem = result.stdout
        else:
            # Older openssl versions seems to have problems reading a CSR in DER
            # format, so convert it to PEM before feeding it to x509
            result = subprocess.run(
                'openssl req -inform DER -in - | openssl x509 -req -inform DER -in - -CA "{0}" -CAkey "{1}" -set_serial "{2}" -days {3}'.format(
                    self.cafile,
                    self.keyfile,
                    self.new_serial(),
                    self.cert_expire,
                ),
                shell=True,
                stdout=subprocess.PIPE,
                input=base64.b64decode(data),
            )

            if result.returncode != 0:
                log.info(f"Error generating certificat: {result.stdout}")
                return (418, f"Error generating certificate: {result.stdout}")

            # Older versions of openssl do not support the -not_before flag, so
            # just sleep for a couple of seconds
            time.sleep(5.0)
            crt_pem = result.stdout

        # Convert PEM to PKCS7
        pkcs7 = self.pem_to_pkcs7der_base64(crt_pem)
        log.info(f"Handing out certificate with serial {self.serial}.")
        return (200, pkcs7)

    @staticmethod
    def pem_to_pkcs7der_base64(buf):
        # Convert PEM to PKCS7
        result = subprocess.run(
            ["openssl", "crl2pkcs7", "-certfile", "/dev/stdin", "-nocrl", "-outform", "DER"],
            stdout=subprocess.PIPE,
            input=buf,
            check=True,
        )

        return base64.b64encode(result.stdout)

    def set_test_flow(self, flow):
        self.test_flow = flow

    def __generate_self_signed_cert(self):
        if not os.path.exists(self.keyfile):
            subprocess.run(["openssl", "ecparam", "-genkey", "-name", "prime256v1", "-out", self.keyfile], check=True)
        log.info(f"Generated privte key: {self.keyfile}")

        if not os.path.exists(self.cafile):
            not_before = []
            if not ANCIENT_OPENSSL:
                # Due to time differences between the device and the server,
                # the certificate may not be yet valid when used by the
                # device. An alternative to this problem is to use
                # -not_before when generating the cert, but it is not
                # supported by openssl 3.0
                not_before = ["-not-before", time.strftime("%y%m%d%H%M%SZ", time.gmtime(time.time() - 60.0))]

            subprocess.run(
                [
                    "openssl",
                    "req",
                    "-x509",
                    "-new",
                    "-key",
                    self.keyfile,
                    "-out",
                    self.cafile,
                    "-days",
                    "365",
                    "-subj",
                    "/C=US/ST=Test/L=PKI/O=FUT/CN=fut.opensync.io",
                    *not_before,
                ],
                check=True,
            )

            if ANCIENT_OPENSSL:
                # If -not_before is not available, just wait a couple of seconds
                # before handing the certificate back to the device just to make
                # sure the certificate is valid also on the device (due to
                # inaccurate time synchronisation)
                time.sleep(5.0)
        log.info(f"Generated self-signed certificates: {self.keyfile}")

    def new_serial(self):
        """Return the next serial number that will be used for certificate signing."""
        rc = self.serial
        self.serial += 1
        return rc

    def get_serial(self):
        return hex(self.serial)


# ------------------------------------------------------------------------------
# TestFlow -- ensure that a sequence of asynchronous events happen in a certain
# order. The flow of events is defined using a python iterator
# ------------------------------------------------------------------------------
class TestFlowError(Exception):
    pass


class TestFlow:
    result = False
    event_args = {}
    flow = None

    def __init__(self, flow):
        self.waitobj = threading.Event()
        self.flow = flow(self.event_args)
        self.exception = None

    def event(self, **kwargs):
        if self.waitobj.is_set():
            return False

        # Update the arguments array held by the iterator
        self.event_args.clear()
        self.event_args.update(kwargs)

        try:
            for flow in self.flow:
                return flow
        except TestFlowError as e:
            log.error("TestFlow failed", exc_info=e)
            self.done(False)
            raise e

        self.done(True)

    def done(self, result):
        self.result = result
        self.waitobj.set()

    def wait(self, timeout=10.0):
        if not self.waitobj.wait(timeout=timeout):
            self.event(step="TIMEOUT")

        # Broadcast the TestFlow exception to the waiter thread
        if self.exception:
            raise self.exception

        return self.result


# ------------------------------------------------------------------------------
# Test Simple Enroll
# ------------------------------------------------------------------------------
def test_enroll(server):
    class EnrollFlow:
        def flow(self, params):
            if params["step"] != "START":
                raise TestFlowError(f"Expected step START, but got: {params}")
            log.info("START OK")
            yield

            if params["step"] != "HTTP_CaCerts":
                raise TestFlowError(f"Expected step HTTP_CaCerts, but got: {params}")
            log.info("HTTP_CaCerts OK")
            yield

            if params["step"] != "HTTP_SimpleEnroll":
                raise TestFlowError(f"Expected step HTTP_SimpleEnroll, but got: {params}")
            log.info("HTTP_SimpleEnroll OK")
            return

    flow = TestFlow(EnrollFlow().flow)
    server.set_test_flow(flow)
    flow.event(step="START")
    flow.wait(30.0)


# ------------------------------------------------------------------------------
# Test Simple Enroll
# ------------------------------------------------------------------------------
def test_reenroll(server):
    class ReEnrollFlow:
        def flow(self, params):
            if params["step"] != "START":
                raise TestFlowError(f"Expected step START, but got: {params}")
            log.info("START OK")
            yield

            if params["step"] != "HTTP_CaCerts":
                raise TestFlowError(f"Expected step HTTP_CaCerts, but got: {params}")
            log.info("HTTP_CaCerts OK")
            yield

            if params["step"] != "HTTP_SimpleReEnroll":
                raise TestFlowError(f"Expected step HTTP_SimpleReEnroll, but got: {params}")
            log.info("HTTP_SimpleReEnroll OK")
            return

    flow = TestFlow(ReEnrollFlow().flow)
    server.set_test_flow(flow)
    flow.event(step="START")
    flow.wait(30.0)


# ------------------------------------------------------------------------------
# Test Simple Enroll with Retry-After
# ------------------------------------------------------------------------------
def test_enroll_retry_after(server, retry_after):
    class EnrollFlowRetryAfter:
        def __init__(self, est_server, retry_after):
            self.est_server = est_server
            self.est_server.retry_after = retry_after

        def flow(self, params):
            if params["step"] != "START":
                raise TestFlowError(f"Expected step START, but got: {params}")
            log.info("START OK")
            yield

            if params["step"] != "HTTP_CaCerts":
                raise TestFlowError(f"Expected step HTTP_CaCerts, but got: {params}")
            log.info("HTTP_CaCerts OK")
            yield

            if params["step"] != "HTTP_RetryAfter":
                raise TestFlowError(f"Expected step HTTP_RetryAfter, but got: {params}")
            # Do not use the Retry-After header for the next request
            self.est_server.retry_after = None
            log.info("RetryAfter OK")
            yield

            if params["step"] != "HTTP_CaCerts":
                raise TestFlowError(f"Expected step HTTP_CaCerts, but got: {params}")
            log.info("HTTP_CaCerts OK")
            yield

            if params["step"] != "HTTP_SimpleEnroll":
                raise TestFlowError(f"Expected step HTTP_SimpleEnroll, but got: {params}")
            log.info("SimpleEnroll OK")
            yield

            return

    flow = TestFlow(EnrollFlowRetryAfter(server, retry_after).flow)
    server.set_test_flow(flow)
    flow.event(step="START")
    flow.wait(30.0)


# ------------------------------------------------------------------------------
# Test Simple ReEnroll with Retry-After
# ------------------------------------------------------------------------------
def test_reenroll_retry_after(server, retry_after):
    class ReEnrollFlowRetryAfter:
        def __init__(self, est_server, retry_after):
            self.est_server = est_server
            self.est_server.retry_after = retry_after

        def flow(self, params):
            if params["step"] != "START":
                raise TestFlowError(f"Expected step START, but got: {params}")
            log.info("START OK")
            yield

            if params["step"] != "HTTP_CaCerts":
                raise TestFlowError(f"Expected step HTTP_CaCerts, but got: {params}")
            log.info("HTTP_CaCerts OK")
            yield

            if params["step"] != "HTTP_RetryAfter":
                raise TestFlowError(f"Expected step HTTP_RetryAfter, but got: {params}")
            # Do not use the Retry-After header for the next request
            self.est_server.retry_after = None
            log.info("RetryAfter OK")
            yield

            if params["step"] != "HTTP_CaCerts":
                raise TestFlowError(f"Expected step HTTP_CaCerts, but got: {params}")
            log.info("HTTP_CaCerts OK")
            yield

            if params["step"] != "HTTP_SimpleReEnroll":
                raise TestFlowError(f"Expected step HTTP_SimpleReEnroll, but got: {params}")
            log.info("SimpleReEnroll OK")
            yield

            return

    flow = TestFlow(ReEnrollFlowRetryAfter(server, retry_after).flow)
    server.set_test_flow(flow)
    flow.event(step="START")
    flow.wait(30.0)


# ------------------------------------------------------------------------------
# Main function -- porse command line arguments
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="FUT -- EST Test Server")
    parser.add_argument("--expire", type=int, default=180, help="Certificate validity in days")
    parser.add_argument(
        "test",
        choices=[
            "test_enroll",
            "test_reenroll",
            "test_enroll_ra_int",
            "test_reenroll_ra_int",
            "test_enroll_ra_str",
            "test_reenroll_ra_str",
            "server",
        ],
        help="Test to execute or use 'server' for a standalone EST server.",
    )
    args = parser.parse_args()

    try:
        with ESTServer("0.0.0.0", 1100, cert_expire=args.expire) as server:

            if args.test == "test_enroll":
                test_enroll(server)
            elif args.test == "test_reenroll":
                test_reenroll(server)
            elif args.test == "test_enroll_ra_int":
                test_enroll_retry_after(server, str(3))
            elif args.test == "test_reenroll_ra_int":
                test_reenroll_retry_after(server, str(3))
            elif args.test == "test_enroll_ra_str":
                future_date = time.strftime("%A, %d-%b-%y %H:%M:%S GMT", time.gmtime(time.time() + 5.0))
                test_enroll_retry_after(server, future_date)
            elif args.test == "test_reenroll_ra_str":
                future_date = time.strftime("%A, %d-%b-%y %H:%M:%S GMT", time.gmtime(time.time() + 5.0))
                test_reenroll_retry_after(server, future_date)
            elif args.test == "server":
                # Stand-alone EST server for testing purposes, just sleep forever
                while True:
                    time.sleep(100000)
            else:
                # initiate the testflow
                log.error(f"Unknown test: '{args.test}'")
                sys.exit(1)
    except Exception as e:
        log.error("Caught exception", exc_info=e)
        sys.exit(1)
    except TestFlowError as e:
        log.error(f"Test {args.tst} FAILED", exc_info=e)
        sys.exit(1)
    except KeyboardInterrupt:
        log.error("Interrupted.")


if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG, stream=sys.stdout)
    log.getLogger().handlers[0].setFormatter(
        log.Formatter("PKIM_EST_SERVER: %(asctime)s,%(msecs)d %(name)s: [%(levelname)s] %(message)s"),
    )
    main()
