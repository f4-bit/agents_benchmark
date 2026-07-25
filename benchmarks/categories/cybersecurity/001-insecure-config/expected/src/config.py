import json


DEFAULT_SECRET_KEY = "changeme"
DEFAULT_ALLOWED_HOSTS = ["*"]
SECURE_ALLOWED_HOSTS = ["localhost"]
MIN_SECRET_LENGTH = 16


def load_config(config_json, production=True):
    """Load and validate a JSON configuration string."""
    config = json.loads(config_json)

    # Apply defaults, then validate or replace insecure values.
    config.setdefault("debug", False)
    config.setdefault("secret_key", DEFAULT_SECRET_KEY)
    config.setdefault("allowed_hosts", SECURE_ALLOWED_HOSTS)

    if production:
        if config.get("debug", True) is not False:
            raise ValueError("debug must be False in production")

        allowed_hosts = config.get("allowed_hosts", [])
        if not allowed_hosts or "*" in allowed_hosts:
            raise ValueError("allowed_hosts must be restricted and cannot contain '*'")

        secret_key = config.get("secret_key", "")
        if (
            not secret_key
            or secret_key == DEFAULT_SECRET_KEY
            or len(secret_key) < MIN_SECRET_LENGTH
        ):
            raise ValueError("secret_key must be a non-default secret of at least 16 characters")

    return config
