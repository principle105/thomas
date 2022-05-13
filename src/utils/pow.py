from hashlib import sha256

from constants import MAX_NONCE


def get_target(difficulty: int) -> int:
    return 2 ** (256 - difficulty)


def is_valid_hash(hash_str: str, target: int) -> bool:
    return int(hash_str, 16) < target


def get_hash_result(msg: str, nonce: int) -> str:
    return sha256(f"{msg}{nonce}".encode()).hexdigest()


def is_valid_pow(*, hash_str: str, nonce: int, msg: str, difficulty: int) -> bool:
    target = get_target(difficulty)

    hash_result = get_hash_result(msg, nonce)

    return hash_str == hash_result and is_valid_hash(hash_result, target)


def proof_of_work(msg: str, difficulty: int):
    target = get_target(difficulty)

    for nonce in range(MAX_NONCE):
        hash_result = get_hash_result(msg, nonce)

    if is_valid_hash(hash_result, target):
        return hash_result, nonce
