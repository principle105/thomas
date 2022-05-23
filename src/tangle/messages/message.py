import time

from tangle import Signed
from utils.pow import proof_of_work


class Message(Signed):
    """
    value: str -- Identifier of type of message
    """

    def __init__(
        self,
        *,
        node_id: str,
        payload: dict,
        parents: list = [],
        timestamp: float = None,
        nonce: int = None,
        hash: str = None,
        signature: str = None
    ):
        super().__init__(hash, signature)

        self.node_id = node_id

        self.parents = parents

        self.nonce = nonce

        if timestamp is None:
            timestamp = time.time()

        self.timestamp = timestamp

        self.payload = payload

    @property
    def vk(self):
        return self.node_id

    def update_state(self, tangle):
        """Updates the tangle with a message"""
        ...

    def is_valid(self, tangle, node) -> bool:
        ...

    def select_parents(self, tangle):
        tips = tangle.state.select_tips()

        self.parents = tips

    def do_work(self, tangle):
        difficulty = tangle.get_difficulty(self)

        self.hash, self.nonce = proof_of_work(self.raw_data, difficulty)

    def raw_data(self) -> str:
        # TODO: sort values for consistency
        return "".join(self.meta_data.values())

    @property
    def meta_data(self):
        return {
            "node_id": self.node_id,
            "value": self.value,
            "payload": self.payload,
            "parents": self.parents,
            "timestamp": self.timestamp,
        }

    def to_dict(self) -> dict:
        return {
            **self.meta_data,
            "nonce": self.nonce,
            "hash": self.hash,
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(*data)

    def __eq__(self, other) -> bool:
        return other == self.node_id
