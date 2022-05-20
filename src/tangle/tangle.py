import random

import networkx as nx

from constants import BRANCH_GENESIS, TRUNK_GENESIS

from .transaction import Transaction


class TangleState:
    def __init__(self):
        self.tips = []
        self.wallets = {}

    def add_transaction(self, t: Transaction):
        balance = self.get_balance(t.sender)

        self.wallets[t.sender] = balance
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
        if graph is None:
            graph = nx.Graph()

            self.add_genesis_transactions()

        self.graph = graph

        if state is None:
            state = TangleState()

        self.state = state

    @property
    def get_balance(self):
        return self.state.get_balance

    def add_genesis_transactions(self):
        ...

    def is_transaction_verified(self, hash_str: str):
        return len(self.graph.neighbors(hash_str)) != 0

    def select_tips(self):
        # TODO: implement better tip selection
        return random.sample(self.state.tips, 2)

    def add_transaction(self, t: Transaction):
        # Removing the tips from the pool
        self.state.remove_tips([t.trunk, t.branch])

        # Adding the transaction as a node
        self.graph.add_node(t.hash, data=t)

        # Connecting it to the tip and branch
        self.graph.add_edge(t.trunk, t.hash)
        self.graph.add_edge(t.branch, t.hash)
