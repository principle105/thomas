import math
import os
import pickle

import networkx as nx

from config import TANGLE_PATH
from constants import BASE_DIFFICULTY, GAMMA, TIME_WINDOW

from .messages import Message, genesis_msg
from .transaction import Transaction


class TangleState:
    def __init__(self):
        self.tips = []
        self.wallets = {}

    def add_transaction(self, t: Transaction):
        sender_bal = self.get_balance(t.sender)
        receiver_bal = self.get_balance(t.receiver)

        if t.sender != "0":
            self.wallets[t.sender] = sender_bal - t.amt

        self.wallets[t.receiver] = receiver_bal + t.amt

    def add_tip(self, tip: str):
        self.tips.append(tip)

    def remove_tip(self, tip: str):
        self.tips.remove(tip)

    def remove_tips(self, tips: list[str]):
        for t in tips:
            self.remove_tip(t)

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
        return (
            len(self.graph.nodes) > 0
            and self.graph.nodes[0] == Message.genesis_msg.hash
        )

    @property
    def get_balance(self):
        return self.state.get_balance

    def add_genesis(self):
        self.raw_add_msg(genesis_msg)

    def get_difficulty(self, msg: Message):
        # Amount of messages in the last time window
        # TODO: cache messages
        msg_count = sum(
            1
            for mt in self.graph.nodes(data=True)
            if (b := mt[1]["data"]) == msg.node_id
            and b.timestamp > msg.timestamp - TIME_WINDOW
            and b.timestamp < msg.timestamp
        )

        return BASE_DIFFICULTY + math.floor(GAMMA * msg_count)

    def get_msg(self, hash_str: str) -> Message:
        return self.graph.nodes(data=True)[hash_str]["data"]

    def raw_add_msg(self, msg: Message):
        self.graph.add_node(msg.hash, data=msg)

        msg.update_state(self)

    def add_msg(self, msg: Message):
        # Removing the tips from the pool
        self.state.remove_tips(msg.parents)

        self.state.add_tip(msg.hash)

        self.raw_add_msg(msg)

        for p in msg.parents:
            self.graph.add_edge(p, msg.hash)

    def save(self):
        with open(TANGLE_PATH, "wb") as f:
            pickle.dump(self, f, protocol=2)

    @classmethod
    def from_save(cls):
        if not os.path.exists(TANGLE_PATH):
            return cls()

        with open(TANGLE_PATH, "rb") as f:
            return pickle.load(f)
