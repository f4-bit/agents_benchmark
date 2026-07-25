import pytest

from config import load_config


GOOD_SECRET = "a_very_long_secret_key_for_tests"


def test_rejects_default_secret_key():
    config_json = '{"allowed_hosts": ["example.com"], "debug": false}'
    with pytest.raises(ValueError):
        load_config(config_json, production=True)


def test_rejects_changeme_secret():
    config_json = '{"secret_key": "changeme", "allowed_hosts": ["example.com"], "debug": false}'
    with pytest.raises(ValueError):
        load_config(config_json, production=True)


def test_rejects_empty_secret():
    config_json = '{"secret_key": "", "allowed_hosts": ["example.com"], "debug": false}'
    with pytest.raises(ValueError):
        load_config(config_json, production=True)


def test_rejects_short_secret():
    config_json = '{"secret_key": "short", "allowed_hosts": ["example.com"], "debug": false}'
    with pytest.raises(ValueError):
        load_config(config_json, production=True)


def test_rejects_wildcard_allowed_hosts():
    config_json = (
        f'{{"secret_key": "{GOOD_SECRET}", "allowed_hosts": ["*"], "debug": false}}'
    )
    with pytest.raises(ValueError):
        load_config(config_json, production=True)


def test_rejects_empty_allowed_hosts():
    config_json = f'{{"secret_key": "{GOOD_SECRET}", "allowed_hosts": [], "debug": false}}'
    with pytest.raises(ValueError):
        load_config(config_json, production=True)


def test_rejects_debug_in_production():
    config_json = (
        f'{{"secret_key": "{GOOD_SECRET}", "allowed_hosts": ["example.com"], "debug": true}}'
    )
    with pytest.raises(ValueError):
        load_config(config_json, production=True)


def test_returns_secure_defaults():
    config_json = f'{{"secret_key": "{GOOD_SECRET}"}}'
    result = load_config(config_json, production=True)
    assert result["debug"] is False
    assert result["allowed_hosts"] == ["localhost"]
    assert result["secret_key"] == GOOD_SECRET


def test_accepts_valid_config():
    config_json = (
        f'{{"secret_key": "{GOOD_SECRET}", "debug": false, '
        f'"allowed_hosts": ["example.com", "api.example.com"]}}'
    )
    result = load_config(config_json, production=True)
    assert result["debug"] is False
    assert result["allowed_hosts"] == ["example.com", "api.example.com"]
    assert result["secret_key"] == GOOD_SECRET
