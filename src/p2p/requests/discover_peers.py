from .request import Request


class DiscoverPeers(Request):
    value = "discover-peer"

    def respond(self, client, node):
        self.response = {
            n.id: [n.host, n.port] for n in client.nodes_outbound if n.id != node.id
        }

    def receive(self, client, node):
        # TODO: add some validation here
        for i, (host, port) in self.response.items():
            client.other_nodes[i] = [host, port]
