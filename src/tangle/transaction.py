from .messages.payload import Payload


class Transaction(Payload):
    def __init__(self, *, receiver: str, amt: int, index: int):

        self.receiver = receiver

        self.amt = amt

        self.index = index

    def to_dict(self):
        return {
            "receiver": self.receiver,
            "amt": self.amt,
            "index": self.index,
        }
