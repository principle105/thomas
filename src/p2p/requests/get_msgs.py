from .request import Request


class GetMsgs(Request):
    value = "get-msgs"

    def respond(self, client, node):
        # TODO: do some payload validation, eg: maximum amount

        tips = self.payload.get("tips", None)

        if tips is None:
            return

        msgs = []

        for t in tips:
            msg = client.tangle.get_msg(t)

            msgs.append(None if msg is None else msg.to_dict())

        self.response = {"msgs": msgs}

    def receive(self, client, node):
        # TODO: do some validation
        for msg in self.response["msgs"]:
            if msg is not None:
                client.handle_new_message(node, msg, propagate=False)
