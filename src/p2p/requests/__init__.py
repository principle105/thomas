from tangle.messages import generate_message_lookup

from .discover_peers import DiscoverPeers

request_types = (DiscoverPeers,)
request_types_lookup = {c.value: c for c in request_types}

request_lookup = generate_message_lookup(request_types_lookup)
