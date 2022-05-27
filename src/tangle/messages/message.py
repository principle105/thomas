import math
import time

from objsize import get_deep_size

from constants import MAX_MSG_SIZE, MAX_PARENT_AGE, MAX_PARENTS
from p2p.requests import Request
from tangle import Signed
from utils.pow import get_hash_result, get_target, is_valid_hash, proof_of_work


class Message(Signed):
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
    def address(self):
        return self.node_id

    def update_state(self, tangle):
        """Updates the tangle with a message"""
        ...

    def is_valid(self, tangle, depth=1):
        # Check if the fields are the correct types and fall within the correct ranges
        data = self.to_dict()

        # Transaction does not exceed the maximum size
        if get_deep_size(data) > MAX_MSG_SIZE:
            return False

        # Field validation
        if (
            any(
                (
                    isinstance(self.node_id, str),
                    isinstance(self.payload, dict),
                    isinstance(self.parents, list),
                    isinstance(self.timestamp, float),
                )
            )
            is False
        ):
            return False

        from . import genesis_msg

        if data == genesis_msg.to_dict():
            return True

        # TODO: Add more timestamp validation

        current_time = time.time()

        if current_time < self.timestamp:
            return False

        raw_data = self.get_raw_data()

        # Checking if the hash matches the data
        if get_hash_result(raw_data, self.nonce) != self.hash:
            return False

        target = get_target(tangle.get_difficulty(self))

        # Checking if enough work has been done
        if is_valid_hash(self.hash, target) is False:
            return False

        # Checking if the signature is valid
        if self.is_signature_valid is False:
            return False

        # Checking if the payload is valid
        if self.is_payload_valid(tangle) is False:
            return False

        # Checking the amount, validity and age of the parents
        for _ in range(depth):
            if len(self.parents) > MAX_PARENTS:
                return False

            for p in self.parents:
                p_msg = tangle.get_msg(p)

                # The validity of the parents is known because they are valid if on the tangle

                if p_msg.hash != genesis_msg.hash:
                    if math.ceil(self.timestamp - p_msg.timestamp) not in range(
                        0, MAX_PARENT_AGE + 1
                    ):
                        return False

        return True

    def is_payload_valid(self, tangle) -> bool:
        ...

    def select_parents(self, tangle):
        self.parents = tangle.state.select_tips()

    def do_work(self, tangle):
        raw_data = self.get_raw_data()
        difficulty = tangle.get_difficulty(self)

        self.hash, self.nonce = proof_of_work(raw_data, difficulty)

    def get_raw_data(self) -> str:
        return "".join(str(s) for s in self.meta_data.values())

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
