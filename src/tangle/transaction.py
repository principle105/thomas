import time
from hashlib import sha256

from .signed import Signed


class Transaction(Signed):
    def __init__(
        self,
        *,
        sender: str,
        receiver: str,
        amount: int,
        timestamp: float = None,
        nonce: str = None,
        signature: str = Signed,
    ):
        super().__init__(signature=signature)

        self.sender = sender
        self.receiver = receiver

        self.amount = amount

        if timestamp is None:
            timestamp = time.time()

        self.timestamp = timestamp

        self.nonce = nonce

    @property
    def hash(self) -> str:
        return sha256(self.get_raw_transaction_data().encode()).hexdigest()

    @property
    def vk(self) -> str:
        return self.sender

    def get_raw_transaction_data(self):
        return f"{self.sender}{self.receiver}{self.amount}{self.timestamp}{self.nonce}"


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
