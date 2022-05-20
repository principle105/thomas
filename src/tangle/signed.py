from base64 import b64encode

from wallet import Wallet


class Signed:
    def __init__(self, signature: str = None):
        self.signature = signature

    @property
    def hash(self) -> str:
        ...

    @property
    def vk(self) -> str:
        ...

    @property
    def is_signed(self) -> bool:
        return self.signature is not None

    @property
    def is_signature_valid(self) -> bool:
        return self.is_signed and Wallet.is_signature_valid(
            self.vk, self.signature, self.hash
        )

    def sign(self, wallet: Wallet):
        if self.hash is None:
            raise ValueError("Hash must be defined to sign")

        self.signature = b64encode(wallet.sk.sign(self.hash.encode())).decode()
