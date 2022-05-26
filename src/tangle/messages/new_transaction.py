from ..transaction import Transaction
from .message import Message


class NewTransaction(Message):
    value = "new-transaction"

    def get_transaction(self) -> Transaction:
        return Transaction.from_dict(self.payload)

    def update_state(self, tangle):
        # Checking if the transaction is valid
        tangle.state.add_transaction(self)

    def is_payload_valid(self, tangle) -> bool:
        # Transaction form is valid
        try:
            t = self.get_transaction()
        except Exception:
            return False

        # Field validation
        if (
            any(
                isinstance(t.amt, int),
                isinstance(t.reciever, str),
                isinstance(t.index, int),
            )
            is False
        ):
            return False

        # Check if the transaction index is valid
        ...

        # Checking if the sender has/had enough to send the transaction
        ...

        return True
