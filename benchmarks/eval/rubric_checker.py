"""Pattern-based rubric evaluation for the benchmark eval engine."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from .test_runner import run_pytest

logger = logging.getLogger(__name__)


def evaluate_rubric(
    rubric_path: Path,
    output_content: str,
    workspace_dir: Path,
) -> dict[str, object]:
    """Evaluate the rubric criteria against the target output and tests.

    Args:
        rubric_path: Path to the task's ``rubric.json``.
        output_content: The text produced by the target.
        workspace_dir: The isolated workspace directory where tests can be run.

    Returns:
        Dictionary with ``rubric_pct`` (0-100), ``has_rubric``, and a
        ``criteria`` breakdown.
    """
    if not rubric_path.exists():
        logger.warning("No rubric found at %s", rubric_path)
        return {"rubric_pct": 0.0, "has_rubric": False, "criteria": []}

    try:
        with rubric_path.open("r", encoding="utf-8") as fh:
            rubric = json.load(fh)
        if not isinstance(rubric, dict):
            raise TypeError("rubric.json top-level must be an object")
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("Malformed rubric at %s: %s", rubric_path, exc)
        return {"rubric_pct": 0.0, "has_rubric": False, "criteria": []}

    criteria = rubric.get("criteria", [])
    total_weight = sum(criterion.get("weight", 0) for criterion in criteria)
    if total_weight == 0:
        logger.warning("Rubric at %s has no weighted criteria", rubric_path)
        return {"rubric_pct": 0.0, "has_rubric": True, "criteria": []}

    earned = 0.0
    breakdown = []

    for criterion in criteria:
        criterion_id = criterion.get("id", "unknown")
        criterion_type = criterion.get("type")
        check = criterion.get("check")
        weight = criterion.get("weight", 0)
        matched = False
        reason = ""

        if criterion_type == "pattern":
            pattern = criterion.get("pattern", "")
            if check == "output_contains":
                try:
                    compiled = re.compile(pattern)
                    matched = bool(compiled.search(output_content))
                    reason = f"pattern '{pattern}' {'matched' if matched else 'not matched'}"
                except re.error:
                    matched = False
                    reason = f"invalid regex '{pattern}'"
            else:
                logger.warning("Unknown pattern check '%s' for criterion %s", check, criterion_id)
                reason = f"unknown pattern check '{check}'"
        elif criterion_type == "test":
            test_result = run_pytest(workspace_dir, check)
            test_passed = test_result.get("has_tests", False) and round(test_result.get("tests_pct", 0.0), 6) == 100.0
            matched = test_passed
            reason = f"test '{check}' {'passed' if matched else 'failed'}"
        else:
            logger.warning("Unknown criterion type '%s' for criterion %s", criterion_type, criterion_id)
            reason = f"unknown criterion type '{criterion_type}'"

        score = weight if matched else 0.0
        earned += score
        breakdown.append(
            {
                "id": criterion_id,
                "type": criterion_type,
                "check": check,
                "weight": weight,
                "matched": matched,
                "score": score,
                "reason": reason,
            }
        )

    rubric_pct = round((earned / total_weight) * 100.0, 6)

    return {
        "rubric_pct": rubric_pct,
        "has_rubric": True,
        "criteria": breakdown,
    }
