import socket
from threading import Thread


class Node(Thread):
    def __init__(self, *, host: str, port: int, max_connections: int):
        self.host = host
        self.port = port

        # Connections
        self.nodes_inbound = []
        self.nodes_outbound = []

        self.max_connections = max_connections

        # Initializing the TCP/IP server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_server()

    @property
    def all_nodes(self):
        return self.nodes_inbound + self.nodes_outbound

    def init_server(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(10.0)
        self.sock.listen(1)

    def run(self):
        ...
