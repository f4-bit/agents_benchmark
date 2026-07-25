"""Target registry: load and validate target definitions from targets.yaml."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from .target_adapter import BenchmarkTarget

logger = logging.getLogger(__name__)


# Valid adapter types for Phase 1; CLI is fully implemented, API/HTTP are stubs.
VALID_TYPES = {"cli", "api", "http"}


def load_targets(path: Path) -> dict[str, BenchmarkTarget]:
    """Load benchmark targets from a YAML registry.

    Args:
        path: Path to the ``targets.yaml`` file.

    Returns:
        A mapping from target id to :class:`BenchmarkTarget`.

    Raises:
        ValueError: If the file is invalid, a target id is duplicated, or a
            target type is unknown.
    """
    if not path.exists():
        raise FileNotFoundError(f"Targets registry not found: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    targets: dict[str, BenchmarkTarget] = {}

    for entry in data.get("targets", []):
        target_id = entry.get("id")
        if not target_id:
            raise ValueError(f"Target entry missing required field 'id': {entry}")

        if target_id in targets:
            raise ValueError(f"Duplicate target id in targets.yaml: {target_id}")

        target_type = entry.get("type", "cli")
        if target_type not in VALID_TYPES:
            raise ValueError(
                f"Unknown target type '{target_type}' for target '{target_id}'. "
                f"Valid types: {VALID_TYPES}"
            )

        command = entry.get("command")
        if target_type == "cli" and not command:
            raise ValueError(
                f"CLI target '{target_id}' requires a non-empty 'command' list"
            )

        targets[target_id] = BenchmarkTarget(
            target_id=target_id,
            target_type=target_type,
            command=command or [],
            timeout=entry.get("timeout"),
            metadata=entry.get("metadata", {}),
        )
        logger.info(
            "Registered target '%s' (type=%s, timeout_override=%s)",
            target_id,
            target_type,
            entry.get("timeout"),
        )

    if not targets:
        logger.warning("No targets found in %s", path)

    return targets
