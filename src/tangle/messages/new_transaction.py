from constants import MINIMUM_SEND_AMT

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
        # TODO: not working with sync check

        # Transaction form is valid
        try:
            t = self.get_transaction()
        except Exception:
            return False

        # Field validation
        if (
            any(
                (
                    isinstance(t.amt, int),
                    isinstance(t.receiver, str),
                    isinstance(t.index, int),
                )
            )
            is False
        ):
            return False

        # Making sure you aren't sending to yourself
        if self.node_id == t.receiver:
            return False

        index = tangle.get_address_transaction_index(self.node_id)

        if index != t.index:
            return False

        # Checking if the sender has/had enough to send the transaction

        if t.amt < MINIMUM_SEND_AMT:
            return False

        balance = tangle.get_balance(self.node_id)

        if balance < t.amt:
            return False

        return True
