import os
import pickle
import random

import networkx as nx

from config import TANGLE_PATH

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

        self.tips.append(t.hash)

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

        if self.has_genesis_transactions is False:
            self.add_genesis_transactions()

    @property
    def get_balance(self):
        return self.state.get_balance

    @property
    def has_genesis_transactions(self):
        return list(self.graph.nodes)[:2] == [
            Transaction.trunk_genesis.hash,
            Transaction.branch_genesis.hash,
        ]

    def add_genesis_transactions(self):
        self.raw_add_transaction(Transaction.trunk_genesis)
        self.raw_add_transaction(Transaction.branch_genesis)

    def is_transaction_verified(self, hash_str: str):
        return len(self.graph.neighbors(hash_str)) != 0

    def select_tips(self):
        # TODO: implement better tip selection
        return random.sample(self.state.tips, 2)

    def raw_add_transaction(self, t: Transaction):
        self.graph.add_node(t.hash, data=t)

        self.state.add_transaction(t)

    def add_transaction(self, t: Transaction):
        # Removing the tips from the pool
        self.state.remove_tips([t.trunk, t.branch])

        # Adding the transaction as a node
        self.raw_add_transaction(t)

        # Connecting it to the tip and branch
        self.graph.add_edge(t.trunk, t.hash)
        self.graph.add_edge(t.branch, t.hash)

    def save(self):
        with open(TANGLE_PATH, "wb") as f:
            pickle.dump(self, f, protocol=2)

    @classmethod
    def from_save(cls):
        if not os.path.exists(TANGLE_PATH):
            return cls()

        with open(TANGLE_PATH, "rb") as f:
            return pickle.load(f)
