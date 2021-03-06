import json
import logging
import sys

import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.utils import color_print
from InquirerPy.validator import EmptyInputValidator
from pyfiglet import figlet_format
from yaspin import yaspin
from yaspin.spinners import Spinners

from config import MAX_CONNECTIONS
from constants import MINIMUM_SEND_AMT
from p2p import Node
from tangle import Tangle, Transaction
from tangle.messages import NewTransaction
from wallet import Wallet

# Setting up logging

log = logging.getLogger()
log.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)

log.addHandler(handler)

fmt = logging.Formatter(
    "[{asctime}] [{levelname}]: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)

# Initializing cli
app = typer.Typer()


class Send:
    @staticmethod
    def success(text: str):
        color_print([("green", text)])

    @staticmethod
    def fail(text: str):
        color_print([("red", text)])

    @staticmethod
    def important(text: str):
        color_print([("#f6ca44", text)])

    @staticmethod
    def regular(text: str):
        color_print([("", text)])

    @staticmethod
    def spinner(text: str):
        return yaspin(Spinners.moon, text=text)


def handle_wallet_input(secret):
    try:
        wallet = Wallet(secret=secret)
    except ValueError:
        Send.fail("That is not a valid private key")
        return

    return wallet


@app.command()
def info():
    Send.important(
        figlet_format("Thomas Coin")
        + '"The final currency"\n\nThomas coin is a fast and lightweight crypto currency designed for every-day applications.'
    )


@app.command()
def wallet():
    secret = inquirer.secret(
        message="Wallet Secret:",
        instruction="(blank to create new)",
    ).execute()

    if not secret:
        secret = None

    wallet = handle_wallet_input(secret)

    if wallet is None:
        return

    Send.important(f"ADDRESS: {wallet.address}\nPRIVATE KEY: {wallet.pk}")


def node_stats(_, node):
    Send.important(
        f"Inbound Connections: {len(node.nodes_inbound)}\n"
        f"Outbound Connections: {len(node.nodes_outbound)}"
    )


def tangle_stats(tangle, _):
    msg_amt = tangle.graph.number_of_nodes()

    t_amt = 0
    sent = 0

    for _, m in tangle.graph.nodes(data="data"):
        if m.value == NewTransaction.value:
            t = m.get_transaction()
            sent += t.amt

            t_amt += 1

    Send.important(
        f"Total Messages: {msg_amt}\n"
        f"Total Transactions: {t_amt}\n"
        f"Total Sent: {sent}"
    )


def view_msg(tangle, _):
    msg_hash = inquirer.text(
        message="Message Hash:",
        validate=EmptyInputValidator(),
    ).execute()

    msg = tangle.get_msg(msg_hash)

    if msg is None:
        return Send.fail("A message with that hash does not exist")

    formatted_data = json.dumps(msg.to_dict(), indent=4)

    Send.regular(formatted_data)


def connect(_, node):
    host = inquirer.text(
        message="Host:",
        validate=EmptyInputValidator(),
    ).execute()

    port = inquirer.number(
        message="Port:",
        validate=EmptyInputValidator(),
    ).execute()

    node.connect_to_node(host, int(port))


def send(tangle, node):
    receiver = inquirer.text(
        message="Recipient's Address:",
        validate=EmptyInputValidator(),
    ).execute()

    amt = inquirer.number(
        message="Amount:",
        min_allowed=MINIMUM_SEND_AMT,
        validate=EmptyInputValidator(),
    ).execute()

    index = tangle.get_address_transaction_index(node.wallet.address)

    # Create the transaction object
    t = Transaction(receiver=receiver, amt=int(amt), index=index)

    # Creating the message object
    msg = node.create_message(NewTransaction, t.to_dict())

    proceed = inquirer.confirm(
        message="Are you sure you want to send this transaction?", default=False
    ).execute()

    if proceed is False:
        return Send.fail("Transaction cancelled!")

    msg.select_parents(tangle)

    with Send.spinner("Solving Proof of Work"):
        msg.do_work(tangle)

    Send.success("Completed Proof of Work!")

    msg.sign(node.wallet)

    if msg.is_valid(tangle) is not True:
        return Send.fail("Invalid transaction")

    tangle.add_msg(msg)

    with Send.spinner("Broadcasting the transaction to network"):
        node.send_to_nodes(msg.to_dict())

    Send.success("Transaction sent!")
    Send.important(f"Message Hash: {msg.hash}")


def view_balance(tangle, _):
    address = inquirer.text(
        message="Address:",
        validate=EmptyInputValidator(),
    ).execute()

    balance = tangle.get_balance(address)

    sender = Send.success if balance else Send.fail

    sender(f"Balance: {balance}")


@app.command()
def start():
    host = inquirer.text(
        message="Host:",
        validate=EmptyInputValidator(),
    ).execute()

    port = inquirer.number(
        message="Port:",
        validate=EmptyInputValidator(),
    ).execute()

    private_key = inquirer.secret(
        message="Your Private Key:",
        validate=EmptyInputValidator(),
    ).execute()

    wallet = handle_wallet_input(private_key)

    if wallet is None:
        return

    full_node = inquirer.confirm(
        message="Would you like it to be a full node?", default=False
    ).execute()

    tangle = Tangle.from_save()

    node = Node(
        host=host,
        port=int(port),
        tangle=tangle,
        wallet=wallet,
        full_node=full_node,
        max_connections=MAX_CONNECTIONS,
    )

    node.start()

    node.connect_to_known_nodes()

    Send.success("Node started!")

    choices = {
        "Send": send,
        "View Balance": view_balance,
        "View Message": view_msg,
        "Node Stats": node_stats,
        "Tangle Stats": tangle_stats,
        "Connect": connect,
    }

    is_done = False

    while is_done is False:
        result = inquirer.select(
            message="What do you want to do?",
            choices=list(choices.keys()) + [Choice(value=None, name="Stop Node")],
        ).execute()

        if result is None:
            is_done = inquirer.confirm(
                message="Are you sure you want to stop this node?", default=False
            ).execute()

        else:
            callback = choices[result]

            callback(tangle, node)

    Send.fail("Stopping Node...")

    node.stop()

    node.save_all_nodes()

    tangle.save()


if __name__ == "__main__":
    app()
