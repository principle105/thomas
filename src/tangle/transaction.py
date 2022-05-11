import time
from hashlib import sha256

from .signed import Signed


class Transaction(Signed):
    def __init__(
        self,
        *,
        sender: str,
        receiver: str,
        amt: int,
        timestamp: float = None,
        nonce: str = None,
        signature: str = None,
    ):
        super().__init__(signature=signature)

        self.sender = sender
        self.receiver = receiver

        self.amt = amt

        if timestamp is None:
            timestamp = time.time()

        self.timestamp = timestamp

        self.nonce = nonce

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

    def do_work(self):
        ...

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amt": self.amt,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class Message(Transaction):
    def __init__(
        self,
        *,
        transaction: Transaction,
        trunk: str = None,
        branch: str = None,
    ):
        self.transaction = transaction

        self.trunk = trunk
        self.brank = branch
