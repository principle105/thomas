import math
import time

from objsize import get_deep_size

from constants import MAX_MSG_SIZE, MAX_PARENT_AGE, MAX_PARENTS
from tangle import Signed
from utils.pow import get_hash_result, get_target, is_valid_hash, proof_of_work


def generate_message_lookup(lookup: dict):
    def message_lookup(data: dict):
        data = data.copy()

        msg_type = data.pop("value", None)

        if msg_type is None:
            return False

        msg_cls = lookup.get(msg_type, None)

        if msg_cls is None:
            return False

        try:
            msg_obj = msg_cls(**data)

        except Exception as e:
            return False

        else:
            return msg_obj

    return message_lookup


class MessageBase(Signed):
    """
    value: str -- Identifier of type of message
    """

    def __init__(
        self,
        *,
        node_id: str,
        payload: dict,
        timestamp: float = None,
        hash: str = None,
        signature=None
    ):
        super().__init__(hash, signature)

        self.node_id = node_id

        if timestamp is None:
            timestamp = time.time()

        self.timestamp = timestamp

        self.payload = payload

    @property
    def address(self):
        return self.node_id

    def get_raw_data(self) -> str:
        return "".join(str(s) for s in self.meta_data.values())

    @property
    def meta_data(self) -> dict:
        return {
            "node_id": self.node_id,
            "value": self.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }

    def to_dict(self) -> dict:
        return {
            **self.meta_data,
            "hash": self.hash,
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(*data)


class Message(MessageBase):
    def __init__(self, *, parents: list = [], nonce: int = None, **kwargs):
        super().__init__(**kwargs)

        self.parents = parents

        self.nonce = nonce

    def update_state(self, tangle):
        """Updates the tangle with a message"""
        ...

    def is_valid(self, tangle, depth=2):
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

        parent_range = range(0, MAX_PARENT_AGE + 1)

        invalid_parents = {}

        # Checking the amount, validity and age of the parents
        for _ in range(depth):
            if len(self.parents) > MAX_PARENTS:
                return False

            for p in self.parents:
                # The validity of the parents is known because they are valid if on the tangle

                p_msg = tangle.get_msg(p)

                # Validating the parent's timestamp if it's not the genesis
                if p_msg is None or (
                    math.ceil(self.timestamp - p_msg.timestamp) not in parent_range
                    and p_msg.hash != genesis_msg.hash
                ):
                    invalid_parents[p_msg.hash] = p_msg

        if invalid_parents:
            return invalid_parents

        return True

    def is_payload_valid(self, tangle) -> bool:
        ...

    def select_parents(self, tangle):
        self.parents = tangle.state.select_tips()

    def do_work(self, tangle):
        raw_data = self.get_raw_data()
        difficulty = tangle.get_difficulty(self)

        self.hash, self.nonce = proof_of_work(raw_data, difficulty)

    @property
    def meta_data(self) -> dict:
        return {**super().meta_data, "parents": self.parents}

    def to_dict(self) -> dict:
        return {**super().to_dict(), "nonce": self.nonce}
