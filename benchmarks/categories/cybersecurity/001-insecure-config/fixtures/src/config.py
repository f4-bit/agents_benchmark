import json


def load_config(config_json, production=True):
    """Load a JSON configuration string."""
    config = json.loads(config_json)

    # Insecure defaults that should never be used in production.
    config.setdefault("debug", True)
    config.setdefault("secret_key", "changeme")
    config.setdefault("allowed_hosts", ["*"])

    return config
