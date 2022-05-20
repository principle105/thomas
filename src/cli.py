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

from constants import MINIMUM_SEND_AMT
from p2p import Node
from tangle import Tangle, Transaction
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
        return None

    return wallet


@app.command()
def info():
    Send.important(figlet_format("Thomas Coin") + "The final currency")


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


def send(tangle, node):
    private_key = inquirer.secret(
        message="Your Private Key:",
        validate=EmptyInputValidator(),
    ).execute()

    wallet = handle_wallet_input(private_key)

    if wallet is None:
        return

    receiver = inquirer.text(
        message="Recipient's Address:",
        validate=EmptyInputValidator(),
    ).execute()

    amt = inquirer.number(
        message="Amount:",
        min_allowed=MINIMUM_SEND_AMT,
        validate=EmptyInputValidator(),
    ).execute()

    # Create the transaction object
    t = Transaction(sender=wallet.address, receiver=receiver, amt=int(amt))

    with Send.spinner("Solving Proof of Work"):
        t.do_work()

    Send.success("Completed Proof of Work!")

    proceed = inquirer.confirm(
        message="Are you sure you want to send this transaction?", default=False
    ).execute()

    t.add_tips(tangle)

    tangle.add_transaction(t)

    if proceed:
        with Send.spinner("Broadcasting the transaction to network"):
            ...

        Send.success("Transaction broadcasted!")

    else:
        Send.fail("Transaction cancelled!")


def view_wallet_balance(tangle, _):
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

    full_node = inquirer.confirm(
        message="Would you like it to be a full node?", default=False
    ).execute()

    tangle = Tangle.from_save()

    node = Node(
        host=host,
        port=int(port),
        tangle=tangle,
        full_node=full_node,
    )

    node.start()

    Send.success("Node started!")

    choices = {"Send": send, "View Wallet Balance": view_wallet_balance}

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

    tangle.save()


if __name__ == "__main__":
    app()
