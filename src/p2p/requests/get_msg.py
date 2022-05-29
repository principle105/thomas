from .request import Request


class GetMessage(Request):
    value = "request-tangle"

    def respond(self, client, node):
        ...

    def receive(self, client, node):
        ...
