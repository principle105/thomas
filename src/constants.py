from ecdsa.curves import SECP256k1

# Wallets
CURVE = SECP256k1
PREFIX = "T"

# Messages
MAX_NONCE = 2**32
BASE_DIFFICULTY = 10
GAMMA = 0.1
TIME_WINDOW = 1000 * 1000  # ms

# Currency details
MINIMUM_SEND_AMT = 1

# Genesis message
GENESIS_MSG_DATA = {
    "nonce": 0,
    "hash": "0",
    "signature": "0",
    "node_id": "0",
    "value": "new-transaction",
    "payload": {
        "sender": "0",
        "receiver": "ThomaodF2haqH2fdADTr7vPmfnEX8sRnJgAC36jbs1fMe",
        "amt": 25000,
        "index": 0,
    },
    "parents": [],
    "timestamp": 1653098327.3540611,
}
