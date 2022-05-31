from .request import Request


class GetMsgs(Request):
    value = "get-msgs"

    def respond(self, client, node):
        ...

    def receive(self, client, node):
        ...
