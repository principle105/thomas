import time

from tangle import Signed


class Request(Signed):
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
        self.node_id = node_id

        if timestamp is None:
            timestamp = time.time()

        self.timestamp = timestamp

        self.payload = payload
