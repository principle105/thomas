import json
import zlib
from base64 import b64decode, b64encode
from socket import socket
from threading import Event, Thread

EOT_CHAR = 0x04.to_bytes(1, "big")


class NodeConnection(Thread):
    def __init__(self, *, main_node, sock: socket, id: str, host: str, port: int):
        super().__init__()

        self.terminate_flag = Event()

        self.main_node = main_node
        self.sock = sock

        self.host = host
        self.port = port

        self.id = id

    def compress(self, data):
        return b64encode(zlib.compress(data, 6))

    def decompress(self, compressed):
        return zlib.decompress(b64decode(compressed))

    def send(self, data: bytes):
        if not isinstance(data, bytes):
            raise ValueError("Input argument must be bytes")

        send_data = data + EOT_CHAR

        self.sock.sendal(send_data)

    def stop(self):
        self.terminate_flag.set()

    def parse_packet(self, packet):
        packet = self.decompress(packet)

        try:
            data = packet.decode("utf-8")

            try:
                return json.loads(data)

            except json.decoder.JSONDecodeError:
                return data

        except UnicodeDecodeError:
            return packet

    def run(self):
        ...
