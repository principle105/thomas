import logging
import sys

import typer
from InquirerPy import inquirer
from InquirerPy.utils import color_print
from InquirerPy.validator import EmptyInputValidator
from pyfiglet import figlet_format

from constants import MINIMUM_SEND_AMT
from node import Node
from wallet import Wallet

# Setting up logging

log = logging.getLogger()
log.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)

log.addHandler(handler)

fmt = logging.Formatter(
    "[{asctime}] [{levelname}]: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)


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
        Send.regular("Generating wallet...")

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

    node = Node(host=host, port=port)
    node.start()


@app.command()
def send():
    address = inquirer.text(
        message="Your Address:",
        validate=EmptyInputValidator(),
    ).execute()

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
    ...

    proceed = inquirer.confirm(
        message="Are you sure you want to send this transaction?", default=False
    ).execute()

    if proceed:
        Send.success("Sending transaction...")

        # Send the transaction
        ...

    else:
        Send.fail("Aborted!")


if __name__ == "__main__":
    app()
