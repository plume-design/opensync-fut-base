#!/usr/bin/env python3

# Open unprivileged port and echo incoming traffic back to sender
import argparse
import os
import socket
from time import sleep, strftime

# Backlog specifies number of unaccepted connections that the system will allow before refusing new connections.
BACKLOG = 1
SOCKET_BUF = 1024
CLOUD_RESPONSES = {
    "echo": '{"params":[],"id":"echo","method":"echo"}',
}
SOCKET_LISTEN_SLEEP = 1


parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument(
    "--host",
    required=False,
    default="0.0.0.0",
    type=str,
    help="Hostname/IP to bind\n",
)
parser.add_argument(
    "--port",
    required=False,
    default="65001",
    type=int,
    help="Port to bind\n",
)
parser.add_argument(
    "--verbose",
    "-v",
    action="store_true",
    help="Enable logging\n",
)
args = parser.parse_args()
verbose = args.verbose


def log(msg=""):
    if verbose:
        time = strftime("%d/%m/%Y %H:%M:%S")
        line = f"{time} - {msg}"
        os.system(f'echo "{line}" >> /tmp/cloud_listener.log')


class DeviceSocket:
    def __init__(self, sock=None):
        if sock is None:
            # If no socket specified, create new INET domain, STREAM type socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = sock

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((args.host, args.port))
        self.sock.listen(BACKLOG)
        self.connection = None

    def close(self):
        self.sock.close()
        return True

    def connect(self, host, port):
        self.sock.connect((host, port))

    def open(self):
        connection, address = self.sock.accept()
        log(f"Connected by {address}")
        self.__setattr__("connection", connection)

    def receive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd == 0:
            chunk = self.connection.recv(min(SOCKET_BUF - bytes_recd, 2048))
            if chunk == b"":
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        receive_msg = b"".join(chunks)
        log(f"Received:\n{receive_msg}")
        return receive_msg

    def send(self, msg):
        log(f"Sending:\n{msg}")
        sent = self.connection.send(msg.encode("ascii"))
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        return True

    def send_type(self, msg_type=None):
        return self.send(CLOUD_RESPONSES[msg_type])


device_socket = DeviceSocket()
device_socket.open()

while 1:
    try:
        try:
            data = device_socket.receive()
            if data:
                device_socket.send_type("echo")
                device_socket.receive()
                log(f"Sleep {SOCKET_LISTEN_SLEEP} seconds")
                sleep(SOCKET_LISTEN_SLEEP)
        except RuntimeError as e:
            log(f"RuntimeError - {e}")
            device_socket.open()
    except Exception as e:
        log(f"EXCEPTION: {e}")
        device_socket.open()
