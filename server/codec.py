"""Bowling King 1.50.19 HTTP compatibility encoding.

These constants are embedded client protocol values, not server credentials.
This reproduces a legacy wire format; it is not an authentication mechanism.
"""

import base64
import binascii
import json

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


PROFILES = {
    # VersionEncryptor .cctor 0x10BB99C; IV at metadata file offset 0x4012F9.
    "version": (b"1248674976451617", bytes.fromhex("01020408060704090706040501060107")),
    # BKPacketEncryptor .cctor 0xC4E334; IV at metadata file offset 0x401A65.
    "account": (b"7810775162280316", bytes.fromhex("07080100070705010602020800030106")),
}


def encrypt(plaintext: str, profile: str) -> str:
    key, iv = PROFILES[profile]
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode("utf-8")) + padder.finalize()
    context = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return base64.b64encode(context.update(padded) + context.finalize()).decode("ascii")


def decrypt(ciphertext: str, profile: str) -> str:
    key, iv = PROFILES[profile]
    # The client's Decrypt replaces spaces with '+', repairing form-decoded Base64.
    normalized = ciphertext.replace(" ", "+").translate(str.maketrans("", "", "\r\n\t"))
    try:
        encrypted = base64.b64decode(normalized, validate=True)
        if not encrypted or len(encrypted) % 16:
            raise ValueError("invalid block length")
        context = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
        padded = context.update(encrypted) + context.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return (unpadder.update(padded) + unpadder.finalize()).decode("utf-8")
    except (binascii.Error, ValueError, UnicodeError) as error:
        raise ValueError("invalid encrypted message") from error


def encode_message(payload: dict, profile: str) -> str:
    return encrypt(json.dumps(payload, separators=(",", ":"), ensure_ascii=False, allow_nan=False), profile)


def decode_message(ciphertext: str, profile: str) -> dict:
    payload = json.loads(decrypt(ciphertext, profile), parse_constant=_reject_constant)
    if not isinstance(payload, dict):
        raise ValueError("message must be a JSON object")
    return payload


def _reject_constant(value):
    raise ValueError(f"invalid JSON constant: {value}")
