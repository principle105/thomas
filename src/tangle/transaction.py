import time
from hashlib import sha256

from utils.pow import proof_of_work

from .signed import Signed

# TODO: make this adaptive
DIFFICULTY = 10


class Transaction(Signed):
    def __init__(
        self,
        *,
        sender: str,
        receiver: str,
        amt: int,
        timestamp: float = None,
        hash: str = None,
        nonce: int = None,
        signature: str = None,
        trunk: str = None,
        branch: str = None,
    ):
        super().__init__(signature=signature)

        self.sender = sender
        self.receiver = receiver

        self.amt = amt

        if timestamp is None:
            timestamp = time.time()

        self.timestamp = timestamp

        self.hash = hash
        self.nonce = nonce

        # Hashes of tips
        self.trunk = trunk
        self.branch = branch

    @property
    def hash(self) -> str:
        return sha256(self.raw_transaction_data.encode()).hexdigest()

    @property
    def vk(self) -> str:
        return self.sender

    @property
    def raw_transaction_data(self):
        return f"{self.sender}{self.receiver}{self.amt}{self.timestamp}{self.nonce}"

    @property
    def is_valid(self):
        ...

    def add_tips(self):
        ...

    def do_work(self):
        self.hash, self.nonce = proof_of_work(self.raw_transaction_data, DIFFICULTY)

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amt": self.amt,
            "timestamp": self.timestamp,
            "hash": self.hash,
            "nonce": self.nonce,
            "signature": self.signature,
            "trunk": self.trunk,
            "branch": self.branch,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
