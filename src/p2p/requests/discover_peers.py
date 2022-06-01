from .request import Request


class DiscoverPeers(Request):
    value = "discover-peers"

    def respond(self, client, node):
        nodes = {n.id: [n.host, n.port] for n in client.nodes_outbound}

        nodes.update(client.other_nodes)

        if node.id in nodes:
            del nodes[node.id]

        self.response = nodes

    def receive(self, client, node):
        # TODO: add some validation here
        for i, (host, port) in self.response.items():
            client.other_nodes[i] = [host, port]
