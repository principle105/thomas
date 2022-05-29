from constants import GENESIS_MSG_DATA

from .message import Message, MessageBase, generate_message_lookup
from .new_transaction import NewTransaction

message_types = (NewTransaction,)
message_types_lookup = {c.value: c for c in message_types}

message_lookup = generate_message_lookup(message_types_lookup)

genesis_msg = message_lookup(GENESIS_MSG_DATA)
