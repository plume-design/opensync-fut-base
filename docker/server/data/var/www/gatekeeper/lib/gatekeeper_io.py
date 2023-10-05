import base64
import ipaddress
import json
import logging
import socket
from enum import Enum

from flask import jsonify, make_response
from google.protobuf import json_format
from google.protobuf import message as pb_message

from . import gatekeeper_pb2

logger = logging.getLogger(__file__)


class ReqType(Enum):
    UNKNOWN = 0
    FQDN = 1
    IPv4 = 2
    IPv6 = 3
    IPV4_TUPLE = 4
    IPV6_TUPLE = 5
    APP = 6
    SNI = 7
    HOST = 8
    URL = 9


# The protobuf json_format method translates bytes arrays in base64 encoded string.
# This method translates such strings in their expected form (mac address, IP address)
def present_data(d):
    ipv4_fields = ["addr_ipv4", "source_ipv4", "destination_ipv4", "redirect_ipv4"]
    ipv6_fields = ["addr_ipv6", "source_ipv6", "destination_ipv6", "redirect_ipv6"]
    transport_ports = ["source_port", "destination_port"]
    for k, v in d.items():
        if isinstance(v, dict):
            present_data(v)
        else:
            if k == "device_id":  # decode mac address
                binstr = base64.b64decode(v)
                ba = bytearray(binstr)
                mac_bytes = [hex(a)[2:] for a in list(ba)]
                mac = ":".join(mac_bytes)
                d[k] = mac

            elif k in ipv4_fields:
                ipv4 = socket.inet_ntop(socket.AF_INET, v.to_bytes(4, byteorder="big"))
                d[k] = ipv4

            elif k in transport_ports:
                port = socket.ntohs(v)
                d[k] = port

            elif k in ipv6_fields:
                binstr = base64.b64decode(v)
                ba = bytearray(binstr)
                ipv6 = socket.inet_ntop(socket.AF_INET6, ba)
                d[k] = ipv6


class GatekeeperError(Exception):
    pass


# Request handler
# Deserialize a request
# Presents the request in human readabler form:
#  represent byte arrays to their meaning (mac address, ip addresses
class Req:
    def __init__(self, client_req, logger=logger):
        self.logger = logger
        self.req = client_req
        self.response = None
        self.raw_response = None

    # deserialize the received request
    def deserialize(self):
        message = gatekeeper_pb2.GatekeeperReq()
        self.logger.debug(f"Headers:\n{self.req.headers}")

        try:
            message.ParseFromString(self.req.get_data())
        except pb_message.DecodeError:
            self.logger.error("Error decoding message")
            bar = {"bar": "error"}
            response = make_response(jsonify(bar))
            response.headers["Content-Type"] = "application/json"
            self.raw_response = jsonify(bar)
            return response

        the_data = json_format.MessageToDict(message, preserving_proto_field_name=True)
        present_data(the_data)
        json_data = json.dumps(the_data, indent=4, sort_keys=True)
        self.raw_response = json_data
        self.logger.debug(f"deserialized data:\n{json_data}")
        self.response = Response(message, self.logger)
        self.logger.debug(f"Request type: {self.response.rtype}")
        response = make_response(self.response.serialize())
        response.headers["Content-Type"] = "application/octet-stream"
        return response


class Response:
    def __init__(self, client_req, logger=logger):
        self.logger = logger
        self.req = client_req
        self.rtype = None
        self.key = None
        self.attribute = None
        self.req_type()
        self.response = None
        self.db = None
        self.category_db = None
        self.lib_path = "/var/www/gatekeeper/lib"
        with open(f"{self.lib_path}/gatekeeper_content.json", "r") as f:
            content = f.read()
            self.db = json.loads(content)

        with open(f"{self.lib_path}/gatekeeper_category.json", "r") as f:
            content = f.read()
            self.category_db = json.loads(content)

    def req_type(self):
        if self.req.HasField("req_fqdn"):
            self.rtype = ReqType.FQDN
            self.key = "fqdn"

        elif self.req.HasField("req_http_url"):
            self.rtype = ReqType.URL
            self.key = "http_url"

        elif self.req.HasField("req_http_host"):
            self.rtype = ReqType.HOST
            self.key = "http_host"

        elif self.req.HasField("req_https_sni"):
            self.rtype = ReqType.SNI
            self.key = "https_sni"

        elif self.req.HasField("req_ipv4"):
            self.rtype = ReqType.IPv4
            self.key = "ipv4"

        elif self.req.HasField("req_ipv6"):
            self.rtype = ReqType.IPv6
            self.key = "ipv6"

        elif self.req.HasField("req_app"):
            self.rtype = ReqType.APP
            self.key = "app"

        return ReqType.UNKNOWN

    def fill_fqdn_reply_body(self, request_header, reply_redirect, action):
        # if the action is set to redirect populate redirect IP address
        if action != gatekeeper_pb2.GatekeeperAction.GATEKEEPER_ACTION_REDIRECT:
            return

        try:
            ipv4_addr = self.db[self.key][self.attribute]["redirect_v4"]
            reply_redirect.redirect_ipv4 = socket.htonl(
                int(ipaddress.ip_address(ipv4_addr)),
            )
        except KeyError:
            reply_redirect.redirect_ipv4 = 0

        try:
            ipv6_addr = self.db[self.key][self.attribute]["redirect_v6"]
            reply_redirect.redirect_ipv6 = ipaddress.IPv6Address(ipv6_addr).packed
        except KeyError:
            reply_redirect.redirect_ipv6 = bytes()

        try:
            cname = self.db[self.key][self.attribute]["redirect_cname"]
            reply_redirect.redirect_cname = cname
        except KeyError:
            reply_redirect.redirect_cname = ""

    @property
    def formatted_attribute(self):
        if self.rtype == ReqType.IPv4:
            ipstr = socket.inet_ntop(
                socket.AF_INET,
                self.attribute.to_bytes(4, byteorder="big"),
            )
            return ipstr

        return self.attribute

    def update_category(self, reply_header):
        self.logger.debug(f"attribute: {self.formatted_attribute}")
        if self.formatted_attribute not in self.category_db:
            return

        if "category_id" in self.category_db[self.formatted_attribute]:
            reply_header.category_id = self.category_db[self.formatted_attribute]["category_id"]

        if "confidence_level" in self.category_db[self.formatted_attribute]:
            reply_header.confidence_level = self.category_db[self.formatted_attribute]["confidence_level"]

        if "policy" in self.category_db[self.formatted_attribute]:
            reply_header.policy = self.category_db[self.formatted_attribute]["policy"]

    def access_db(self, request_header, reply_header):
        action_map = {
            "allow": gatekeeper_pb2.GatekeeperAction.GATEKEEPER_ACTION_ACCEPT,
            "block": gatekeeper_pb2.GatekeeperAction.GATEKEEPER_ACTION_BLOCK,
            "redirect": gatekeeper_pb2.GatekeeperAction.GATEKEEPER_ACTION_REDIRECT,
        }

        reply_header.request_id = request_header.request_id
        reply_header.ttl = 10
        reply_header.policy = f"{request_header.policy_rule}_from_gk"
        reply_header.category_id = 100
        reply_header.confidence_level = 5

        self.update_category(reply_header)

        attr = self.formatted_attribute
        try:
            db_action = self.db[self.key][attr]["action"]
        except KeyError:
            self.logger.debug(f"No db action found for {self.key} attribute {attr} type {self.rtype}, accepting")
            db_action = "allow"

        self.logger.debug(f"db action for {self.key} attribute {attr} type {self.rtype}: {db_action}")
        # Raise our own error if the action is unkown
        try:
            reply_header.action = action_map[db_action]
        except KeyError:
            self.logger.error("Raising an error for testing purposes")
            raise GatekeeperError

        try:
            db_flow_marker = self.db[self.key][attr]["flow_marker"]
        except KeyError:
            self.logger.debug(f"No db flow marker found for {self.key} attribute {attr} type {self.rtype}, accepting")
            db_flow_marker = 0

        self.logger.debug(f"db flow marker for {self.key} attribute {attr} type {self.rtype}: {db_flow_marker}")
        reply_header.flow_marker = db_flow_marker

    def fill_header(self):
        if self.rtype == ReqType.FQDN:
            reply_fqdn = self.response.reply_fqdn
            reply_header = reply_fqdn.header
            reply_redirect = reply_fqdn.redirect
            request_header = self.req.req_fqdn.header
            self.attribute = self.req.req_fqdn.fqdn
            self.logger.debug(f"fqdn: {self.attribute}")
            self.access_db(request_header, reply_header)
            self.fill_fqdn_reply_body(
                request_header,
                reply_redirect,
                reply_header.action,
            )

        elif self.rtype == ReqType.URL:
            reply_url = self.response.reply_http_url
            reply_header = reply_url.header
            request_header = self.req.req_http_url.header
            self.attribute = self.req.req_http_url.http_url
            self.access_db(request_header, reply_header)

        elif self.rtype == ReqType.HOST:
            reply_host = self.response.reply_http_host
            reply_header = reply_host.header
            request_header = self.req.req_http_host.header
            self.attribute = self.req.req_http_host.http_host
            self.access_db(request_header, reply_header)

        elif self.rtype == ReqType.SNI:
            reply_sni = self.response.reply_https_sni
            reply_header = reply_sni.header
            request_header = self.req.req_https_sni.header
            self.attribute = self.req.req_https_sni.https_sni
            self.access_db(request_header, reply_header)

        elif self.rtype == ReqType.APP:
            reply_app = self.response.reply_app
            reply_header = reply_app.header
            request_header = self.req.req_app.header
            self.attribute = self.req.req_app.app_name
            self.access_db(request_header, reply_header)

        elif self.rtype == ReqType.IPv4:
            reply_ipv4 = self.response.reply_ipv4
            reply_header = reply_ipv4.header
            request_header = self.req.req_ipv4.header
            self.attribute = self.req.req_ipv4.addr_ipv4
            self.access_db(request_header, reply_header)

        elif self.rtype == ReqType.IPv6:
            reply_ipv6 = self.response.reply_ipv6
            reply_header = reply_ipv6.header
            request_header = self.req.req_ipv6.header
            self.attribute = self.req.req_ipv6.addr_ipv6
            self.access_db(request_header, reply_header)

    def serialize(self):
        self.response = gatekeeper_pb2.GatekeeperReply()
        self.fill_header()
        the_data = json_format.MessageToDict(
            self.response,
            preserving_proto_field_name=True,
        )
        present_data(the_data)
        self.logger.debug(f"Reply data:\n{json.dumps(the_data, indent=4, sort_keys=True)}")
        return self.response.SerializeToString()
