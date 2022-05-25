import math
import os
import pickle
import random
import time

import networkx as nx

from config import STORAGE_DIRECTORY
from constants import BASE_DIFFICULTY, GAMMA, MAX_PARENT_AGE, MAX_PARENTS, TIME_WINDOW

from .messages import Message, NewTransaction, genesis_msg

TANGLE_PATH = f"{STORAGE_DIRECTORY}/tangle.thomas"


class TangleState:
    """Keeps track of the tangle's state"""

    def __init__(self):
        self._tips = {}  # hash: timestamp
        self.wallets = {}  # address: balance

    def add_transaction(self, msg: NewTransaction):
        t = msg.get_transaction()

        sender_bal = self.get_balance(msg.node_id)
        receiver_bal = self.get_balance(t.receiver)

        if msg.node_id != "0":
            self.wallets[msg.node_id] = sender_bal - t.amt

        self.wallets[t.receiver] = receiver_bal + t.amt

    def get_tips(self):
        current_time = time.time()

        # Purging tips that are too old
        self._tips = {
            h: t for h, t in self._tips.items() if t + MAX_PARENT_AGE >= current_time
        }

        return list(self._tips.keys())

    def select_tips(self):
        tips = self.get_tips()

        if tips == []:
            return genesis_msg.hash

        amt = min(len(tips), MAX_PARENTS)

        return random.sample(tips, amt)

    def get_balance(self, address: str):
        return self.wallets.get(address, 0)


class Tangle:
    def __init__(self, graph: nx.Graph = None, state: TangleState = None):
        if state is None:
            state = TangleState()

        self.state = state

        if graph is None:
            graph = nx.Graph()

        self.graph = graph

        if self.has_genesis is False:
            self.add_genesis()

    @property
    def has_genesis(self):
        return self.graph.has_node(genesis_msg.hash)

    @property
    def get_balance(self):
        return self.state.get_balance

    def add_genesis(self):
        self.add_msg(genesis_msg)

    def get_address_transaction_index(self, address: str):
        return sum(
            1 for n in self.graph.nodes(data=True) if n[1]["data"].node_id == address
        )

    def get_difficulty(self, msg: Message):
        # Amount of messages in the last time window
        # TODO: cache messages

        def _in_window(v):
            m = v[1]["data"]

            return (
                m.node_id == msg.node_id
                and m.timestamp > msg.timestamp - TIME_WINDOW
                and m.timestamp < msg.timestamp
            )

        msg_count = len(list(filter(_in_window, self.graph.nodes(data=True))))

        return BASE_DIFFICULTY + math.floor(GAMMA * msg_count)

    def get_msg(self, hash_str: str) -> Message:
        if hash_str in self.graph:
            return self.graph.nodes(data=True)[hash_str]["data"]

        return

    def add_msg(self, msg: Message):
        self.graph.add_node(msg.hash, data=msg)

        msg.update_state(self)

        for p in msg.parents:
            self.graph.add_edge(p, msg.hash)

            self.state._tips[msg.hash] = msg.timestamp

    def save(self):
        with open(TANGLE_PATH, "wb") as f:
            pickle.dump(self, f, protocol=2)

    @classmethod
    def from_save(cls):
        if not os.path.exists(TANGLE_PATH):
            return cls()

        with open(TANGLE_PATH, "rb") as f:
            return pickle.load(f)
