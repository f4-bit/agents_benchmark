import hashlib
from passwords import hash_password, verify_password


def test_hash_is_not_md5():
    hashed = hash_password('password')
    assert hashed != hashlib.md5(b'password').hexdigest()


def test_hash_uses_random_salt():
    h1 = hash_password('password')
    h2 = hash_password('password')
    assert h1 != h2


def test_verify_valid_password():
    password = 'password'
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_invalid_password():
    hashed = hash_password('password')
    assert verify_password('wrong', hashed) is False
