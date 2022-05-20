from ecdsa.curves import SECP256k1

# Wallets
CURVE = SECP256k1
PREFIX = "T"

# Transactions
MAX_NONCE = 2**32

# Currency details
MINIMUM_SEND_AMT = 1

# Genesis Transactions
TRUNK_GENESIS_DATA = {
    "sender": "0",
    "receiver": "ThomaodF2haqH2fdADTr7vPmfnEX8sRnJgAC36jbs1fMe",
    "amt": 250000,
    "timestamp": 1653011572.168865,
    "hash": "0000e5d6bbcc6638bdf3ceaef6b6030b092d409da29e004ad3584ff9e2d58b16",
    "nonce": 41583,
    "signature": "gz8gHhMT8WD1khhyBLyvA9QjVLZx/PyYkCZodZZ1UwpRB7gQvtv7l+G6O+Rws7hsYk2srXqL3hn383oByVr8uQ==",
    "trunk": "0",
    "branch": "0",
}
BRANCH_GENESIS_DATA = {
    "sender": "0",
    "receiver": "TeGEeVrxHQXMmkNuySg4T9sjAWRRUxC6EVEPj4Yw4r5qV",
    "amt": 1000,
    "timestamp": 1653011684.297066,
    "hash": "00005adbff7be2da2d859caba9c8ca66832a46e699151a24d41d1316e262826b",
    "nonce": 63729,
    "signature": "cRdcUBnJH8s6TWebQ6GL1qLKww7t/WMDM4YH+YPvaXsAY7KA4kcS0IDkAXbCYcdMDKDiB5Z9216roZwSqis8AQ==",
    "trunk": "0",
    "branch": "0",
}
