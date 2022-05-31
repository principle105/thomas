from tangle.messages import generate_message_lookup

from .discover_peers import DiscoverPeers
from .get_msgs import GetMsgs

request_types = (DiscoverPeers, GetMsgs)
request_types_lookup = {c.value: c for c in request_types}

request_lookup = generate_message_lookup(request_types_lookup)
