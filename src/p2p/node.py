import logging
import socket
import time
import uuid
from threading import Event, Thread

from .node_connection import NodeConnection


class Node(Thread):
    def __init__(
        self,
        *,
        host: str,
        port: int,
        full_node: bool = False,
        max_connections: int = 30,
    ):
        super().__init__()

        self.terminate_flag = Event()

        self.host = host
        self.port = port

        self.id = self.generate_uuid()

        # Connections
        self.nodes_inbound = []
        self.nodes_outbound = []

        self.max_connections = max_connections
        self.full_node = full_node

        # Initializing the TCP/IP server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_server()

    @property
    def all_nodes(self):
        return self.nodes_inbound + self.nodes_outbound

    def generate_uuid(self):
        return uuid.uuid4().hex

    def init_server(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(10.0)
        self.sock.listen(1)

    def stop(self):
        self.terminate_flag.set()

    def send_to_nodes(self, data, exclude=[]):
        for n in self.all_nodes:
            if n not in exclude:
                self.send_to_node(n, data)

    def send_to_node(self, node, data):
        if node in self.all_nodes:
            node.send(data)

    def connect_to_node(self, host: str, port: int):
        if host == self.host and port == self.port:
            logging.info("You cannot connect with yourself")
            return False

        if any(n.host == host and n.port == port for n in self.nodes_outbound):
            logging.info("You are already connected with that node")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logging.debug(f"Connecting to {host} port {port}")
            sock.connect((host, port))

            # Sending our id to other node
            sock.send(self.id.encode("utf-8"))

            # Receiving the node id once complete
            connected_node_id = sock.recv(4096).decode("utf-8")

            thread_client = self.create_new_connection(
                sock, connected_node_id, host, port
            )
            thread_client.start()

        except Exception:
            logging.exception("Could not connect with node")

    def disconnect_from_node(self, node):
        if node in self.nodes_outbound:
            node.stop()
            node.join()
            del self.nodes_outbound[self.nodes_outbound.index(node)]

    def create_new_connection(self, sock: socket.socket, id: str, host: str, port: int):
        return NodeConnection(main_node=self, sock=sock, id=id, host=host, port=port)

    def node_disconnected(self, node):
        if node in self.nodes_outbound:
            node.stop()

    def message_from_node(self, node: NodeConnection, data):
        ...

    def run(self):
        while not self.terminate_flag.is_set():
            try:
                logging.debug("Waiting for incoming connections...")
                connection, client_address = self.sock.accept()

                if (
                    self.max_connections == 0
                    or len(self.nodes_inbound) < self.max_connections
                ):

                    connected_node_id = connection.recv(4096).decode("utf-8")

                    connection.send(self.id.encode("utf-8"))

                    thread_client = self.create_new_connection(
                        connection,
                        connected_node_id,
                        client_address[0],
                        client_address[1],
                    )
                    thread_client.start()

                    self.nodes_inbound.append(thread_client)

                else:
                    logging.debug("Reached maximum connection limit")
                    connection.close()

            except socket.timeout:
                logging.debug("Connection timed out")

            except Exception as e:
                raise e

            time.sleep(0.01)

        logging.info("Nodes stopping...")

        for node in self.all_nodes:
            node.stop()

        time.sleep(1)

        for node in self.all_nodes:
            node.join()

        self.sock.settimeout(None)
        self.sock.close()

        logging.info("Node stopped")
