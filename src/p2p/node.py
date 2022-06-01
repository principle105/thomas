import json
import logging
import os
import random
import socket
import time
from threading import Event, Thread

from config import STORAGE_DIRECTORY
from constants import REQUEST_CHILDREN_AFTER
from tangle import Tangle
from tangle.messages import message_lookup
from wallet import Wallet

from .node_connection import NodeConnection
from .requests import DiscoverPeers, GetMsgs, request_lookup

KNOWN_PEERS_PATH = f"{STORAGE_DIRECTORY}/known_peers.json"


class Node(Thread):
    def __init__(
        self,
        *,
        host: str,
        port: int,
        tangle: Tangle,
        wallet: Wallet,
        full_node: bool = False,
        max_connections: int,
    ):
        super().__init__()

        self.terminate_flag = Event()

        self.host = host
        self.port = port

        self.tangle = tangle

        self.wallet = wallet

        # Connections
        self.nodes_inbound = []
        self.nodes_outbound = []

        # Other nodes that are known about
        self.other_nodes = {}

        self.max_connections = max_connections
        self.full_node = full_node

        # Initializing the TCP/IP server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_server()

    @property
    def all_nodes(self):
        return self.nodes_inbound + self.nodes_outbound

    @property
    def id(self):
        return self.wallet.address

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

    def get_known_nodes(self):
        if not os.path.exists(KNOWN_PEERS_PATH):
            return {}

        with open(KNOWN_PEERS_PATH, "r") as f:
            return json.load(f)

    def connect_to_known_nodes(self):
        saved_nodes = self.get_known_nodes()

        # Trying to connect with up to 30 saved nodes
        if saved_nodes:
            amt = min(max(len(saved_nodes), 1), 30)

            for host, port in random.sample(list(saved_nodes.values()), amt):
                self.connect_to_node(host, port)

    def create_message(self, msg_cls, payload: dict):
        return msg_cls(node_id=self.id, payload=payload)

    def create_request(self, request_cls, payload: dict = {}):
        request = request_cls(node_id=self.id, payload=payload)

        request.add_hash()
        request.sign(self.wallet)

        return request

    def save_all_nodes(self):
        data = self.get_known_nodes()

        for n in self.nodes_outbound:
            data[n.id] = [n.host, n.port]

        for i, (host, port) in self.other_nodes.items():
            data[i] = [host, port]

        with open(KNOWN_PEERS_PATH, "w+") as f:
            json.dump(data, f)

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

            self.nodes_outbound.append(thread_client)

        except Exception:
            logging.exception("Could not connect with node")

        else:
            # Peer discovery
            request = self.create_request(DiscoverPeers)

            self.send_to_node(thread_client, request.to_dict())

    def create_new_connection(self, sock: socket.socket, id: str, host: str, port: int):
        return NodeConnection(main_node=self, sock=sock, id=id, host=host, port=port)

    def node_disconnected(self, node):
        if node in self.nodes_inbound:
            self.nodes_inbound.remove(node)

        if node in self.nodes_outbound:
            self.nodes_outbound.remove(node)

    def message_from_node(self, node: NodeConnection, data: dict):
        if self.handle_new_request(node, data):
            return

        self.handle_new_message(node, data)

    def handle_new_request(self, node: NodeConnection, data: dict):
        request = request_lookup(data)

        if request is False:
            return

        if request.is_valid() is False:
            return

        if request.response is None:
            request.respond(self, node)

            if request.response:
                self.send_to_node(node, request.to_dict())
            return True

        if self.id == request.node_id:
            request.receive(self, node)
            return True

    def request_msgs(self, msgs: list, history=False):
        request = self.create_request(GetMsgs, {"tips": list(msgs), "history": history})

        self.send_to_nodes(request.to_dict())

    def handle_new_message(self, node: NodeConnection, data: dict, propagate=True):
        msg = message_lookup(data)

        if msg is False:
            return

        result = msg.is_valid(self.tangle)

        if result is False:
            return

        if result is not True:
            age = time.time() - msg.timestamp

            if age >= REQUEST_CHILDREN_AFTER:
                payload = list(self.tangle.state.tips.keys())
                self.request_msgs(payload, True)

            else:
                self.request_msgs(result)

            return True

        if self.tangle.get_msg(msg.hash) is None:
            # Adding the message to the tangle if it doesn't exist yet
            self.tangle.add_msg(msg)

            # Propagating message to other nodes
            if propagate:
                self.send_to_nodes(data, exclude=[node])

        return True

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

        for node in self.all_nodes:
            node.stop()

        time.sleep(1)

        for node in self.all_nodes:
            node.join()

        self.sock.settimeout(None)
        self.sock.close()

        logging.info("Node stopped")
