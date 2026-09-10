import base64
import hashlib

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def _evp_bytes_to_key(
    password: bytes,
    salt: bytes,
    key_len: int = 32,
    iv_len: int = 16,
) -> tuple[bytes, bytes]:
    """OpenSSL EVP_BytesToKey — same derivation used by CryptoJS."""
    dtotallen = key_len + iv_len
    d = b""
    d_i = b""
    while len(d) < dtotallen:
        d_i = hashlib.md5(d_i + password + salt).digest()
        d += d_i
    return d[:key_len], d[key_len : key_len + iv_len]


def decrypt(ciphertext_b64: str, password: str) -> str:
    """Decrypt CryptoJS AES string (Base64 with Salted__ prefix).

    Compatible with: CryptoJS.AES.encrypt(data, password).toString()
    """
    raw = base64.b64decode(ciphertext_b64)

    if raw[:8] != b"Salted__":
        raise ValueError("Invalid format: missing 'Salted__' prefix")

    salt = raw[8:16]
    ciphertext = raw[16:]

    key, iv = _evp_bytes_to_key(password.encode("utf-8"), salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

    return plaintext.decode("utf-8")
