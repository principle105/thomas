from constants import MAX_TIPS_REQUESTED
from tangle.messages import NewTransaction

from .request import Request


# TODO: send in chunks
class GetMsgs(Request):
    value = "get-msgs"

    def respond(self, client, node):
        # TODO: do some payload validation, make sure history is only True when needed

        tips = self.payload.get("tips", None)
        history = self.payload.get("history", None)

        if tips is None or history is None:
            return

        if any((isinstance(tips, list), isinstance(history, bool))) is False:
            return

        # Validating tip amount
        if len(tips) not in range(1, MAX_TIPS_REQUESTED + 1):
            return

        if history:
            msg_hashes = set()

            for t in tips:
                children = client.tangle.get_children(t)

                if children is not None:
                    msg_hashes.update(set(children))

            # Fetching the message data from the hashes
            msgs = [t.to_dict() for t in client.tangle.get_msgs(msg_hashes).values()]

        else:
            msgs = []

            for t in tips:
                msg = client.tangle.get_msg(t)

                msgs.append(None if msg is None else msg.to_dict())

        # TODO: respond in multiple messages if data is large enough

        self.response = {"msgs": msgs}

    def receive(self, client, node):
        # TODO: do some validation
        msgs = self.response.get("msgs", None)

        if msgs is None:
            return

        for m in msgs:
            if m is not None:
                client.handle_new_message(node, m, propagate=False)
