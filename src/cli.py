import logging
import sys

import typer
from InquirerPy import inquirer
from InquirerPy.utils import color_print
from InquirerPy.validator import EmptyInputValidator
from pyfiglet import figlet_format
from yaspin import yaspin
from yaspin.spinners import Spinners

from constants import MINIMUM_SEND_AMT
from p2p import Node
from tangle import Transaction
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

    wallet = Wallet(secret=secret)

    Send.important(f"ADDRESS: {wallet.address}\nPRIVATE KEY: {wallet.pk}")


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

    node = Node(host=host, port=int(port), full_node=full_node)

    Send.success("Node started!")

    node.start()

    node.connect_to_node(input("host: "), int(input("port: ")))


@app.command()
def send():
    private_key = inquirer.secret(
        message="Your Private Key:",
        validate=EmptyInputValidator(),
    ).execute()

    wallet = Wallet(secret=private_key)

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
    t = Transaction(sender=wallet.address, receiver=receiver, amt=amt)

    # Signing the transaction
    t.sign(wallet)

    with Send.spinner("Solving Proof of Work"):
        t.do_work()

    Send.success("Completed Proof of Work!")

    proceed = inquirer.confirm(
        message="Are you sure you want to send this transaction?", default=False
    ).execute()

    if proceed:
        with Send.spinner("Sending transaction"):
            # Sending the transaction
            ...

        Send.success("Transaction successfully sent!")

    else:
        Send.fail("Transaction cancelled!")


if __name__ == "__main__":
    app()
