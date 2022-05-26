from constants import GENESIS_MSG_DATA

from .message import Message
from .new_transaction import NewTransaction

message_types = (NewTransaction,)

message_types_lookup = {c.value: c for c in message_types}


def get_message_from_data(data: dict):
    msg_type = data.pop("value", None)

    if msg_type is None:
        return False

    msg_cls = message_types_lookup.get(msg_type, None)

    if msg_cls is None:
        return False

    try:
        msg_obj = msg_cls(**data)

    except Exception:
        return False

    else:
        return msg_obj


genesis_msg = get_message_from_data(GENESIS_MSG_DATA)
