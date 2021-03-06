from ecdsa.curves import SECP256k1

# Wallets
CURVE = SECP256k1
PREFIX = "T"

# Messages
MAX_NONCE = 2**32
BASE_DIFFICULTY = 20
GAMMA = 0.2
TIME_WINDOW = 1000 * 1000  # ms
MAX_PARENTS = 6
MAX_PARENT_AGE = 60 * 60
MAX_MSG_SIZE = 4096  # bytes

# Requests
MAX_TIPS_REQUESTED = 10
REQUEST_CHILDREN_AFTER = 60 * 60 * 24  # s

# Currency details
MINIMUM_SEND_AMT = 1

# Genesis message
GENESIS_MSG_DATA = {
    "node_id": "0",
    "value": "new-transaction",
    "payload": {
        "receiver": "ThomaodF2haqH2fdADTr7vPmfnEX8sRnJgAC36jbs1fMe",
        "amt": 25000,
        "index": 0,
    },
    "parents": [],
    "timestamp": 1653266909.9701052,
    "nonce": 0,
    "hash": "0",
    "signature": "0",
}
