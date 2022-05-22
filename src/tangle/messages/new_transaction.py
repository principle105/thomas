from ..transaction import Transaction
from .message import Message


class NewTransaction(Message):
    value = "new-transaction"

    @property
    def transaction(self) -> Transaction:
        return Transaction.from_dict(self.payload)

    def process(self, node, _):
        ...

    def update_state(self, tangle):
        # Checking if the transaction is valid
        tangle.state.add_transaction(self.transaction)

    def is_valid(self, tangle) -> bool:
        return self.transaction.is_valid(tangle)
