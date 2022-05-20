from tangle import Transaction

from .message import Message


class NewTransaction(Message):
    value = "new-transaction"

    def __init__(self, transaction: Transaction):
        self.transaction = transaction

    def process(self, tangle, _):
        tangle.add_transaction(self.transaction)

    def to_dict(self):
        return {"transaction": self.transaction}
