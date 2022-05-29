from tangle.messages import MessageBase
from utils.pow import get_raw_hash_result


class Request(MessageBase):
    def __init__(self, *, response: dict = None, **kwargs):
        super().__init__(**kwargs)

        self.response = response

    def get_hash(self):
        raw_data = self.get_raw_data()

        return get_raw_hash_result(raw_data)

    def add_hash(self):
        self.hash = self.get_hash()

    def respond(self, client, node):
        ...

    def receive(self, client, node):
        ...

    def is_valid(self):
        # Checking if the hash matches the data
        if self.hash != self.get_hash():
            return False

        # Checking if the signature is valid
        if self.is_signature_valid is False:
            return False

        return True

    def to_dict(self) -> dict:
        return {**super().to_dict(), "response": self.response}
