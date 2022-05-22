from .messages.payload import Payload


class Transaction(Payload):
    def __init__(self, *, sender: str, receiver: str, amt: int, index: int):

        self.sender = sender
        self.receiver = receiver

        self.amt = amt

        self.index = index

    @property
    def vk(self) -> str:
        return self.sender

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amt": self.amt,
            "index": self.index,
        }
