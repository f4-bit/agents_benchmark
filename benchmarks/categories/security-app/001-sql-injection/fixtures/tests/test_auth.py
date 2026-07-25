import pytest
from auth import authenticate


def test_valid_credentials_authenticate():
    assert authenticate('admin', 'secret') is True


def test_invalid_password_rejected():
    assert authenticate('admin', 'wrong') is False


def test_sql_injection_payload_rejected():
    # A classic injection payload must not bypass authentication.
    assert authenticate('admin', "' OR '1'='1") is False
