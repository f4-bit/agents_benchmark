import hashlib
import secrets


def hash_password(password):
    salt = secrets.token_hex(16)
    pwd = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    hash_bytes = hashlib.scrypt(
        pwd,
        salt=salt_bytes,
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    )
    return f'{salt}:{hash_bytes.hex()}'


def verify_password(password, hashed):
    salt, stored_hash = hashed.split(':')
    pwd = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    hash_bytes = hashlib.scrypt(
        pwd,
        salt=salt_bytes,
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    )
    return hash_bytes.hex() == stored_hash
