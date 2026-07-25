"""Weighted scoring aggregator for the benchmark eval engine."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


DEFAULT_WEIGHTS = {
    "tests": 0.5,
    "diff": 0.3,
    "rubric": 0.2,
}


def _redistribute_weights(
    weights: dict[str, float],
    has_tests: bool,
    has_reference: bool,
    has_rubric: bool,
) -> dict[str, float]:
    """Redistribute weights from missing layers to present layers.

    Args:
        weights: Raw weights for tests, diff, and rubric.
        has_tests: Whether the task has a pytest suite.
        has_reference: Whether the task has a reference solution.
        has_rubric: Whether the task has a rubric.

    Returns:
        Normalized weights that sum to 1.0 across only the available layers.
    """
    available = {}
    if has_tests:
        available["tests"] = weights["tests"]
    if has_reference:
        available["diff"] = weights["diff"]
    if has_rubric:
        available["rubric"] = weights["rubric"]

    total = sum(available.values())
    if total == 0:
        return {}

    return {key: value / total for key, value in available.items()}


def score_task(
    tests_pct: float,
    has_tests: bool,
    diff_pct: float,
    has_reference: bool,
    rubric_pct: float,
    has_rubric: bool,
    weights: dict[str, float] | None = None,
) -> tuple[float, str, dict[str, float]]:
    """Compute the final weighted score and status for a task.

    Returns:
        A tuple ``(score, eval_status, adjusted_weights)``. ``score`` is in the
        range [0, 100]. ``eval_status`` is ``NO_EVAL_DATA`` when no eval data is
        available, otherwise ``PASS`` for a perfect score and ``FAIL``
        otherwise.
    """
    weights = dict(weights or DEFAULT_WEIGHTS)
    adjusted = _redistribute_weights(
        weights, has_tests, has_reference, has_rubric
    )

    if not adjusted:
        logger.warning("No eval data available for task; returning NO_EVAL_DATA")
        return 0.0, "NO_EVAL_DATA", adjusted

    score = 0.0
    if "tests" in adjusted:
        score += adjusted["tests"] * tests_pct
    if "diff" in adjusted:
        score += adjusted["diff"] * diff_pct
    if "rubric" in adjusted:
        score += adjusted["rubric"] * rubric_pct

    eval_status = "PASS" if round(score, 6) == 100.0 else "FAIL"
    return score, eval_status, adjusted


def build_eval_json(
    task_id: str,
    target_id: str,
    final_status: str,
    score: float,
    tests_pct: float,
    has_tests: bool,
    diff_pct: float,
    has_reference: bool,
    rubric_pct: float,
    has_rubric: bool,
    criteria: list[dict[str, Any]],
    weights: dict[str, float],
) -> dict[str, Any]:
    """Return the canonical eval.json payload for a task execution.

    ``final_status`` is the combined status chosen by the runner (e.g.
    ``TIMEOUT``, ``NO_OUTPUT``, ``PASS``, ``FAIL``, ``NO_EVAL_DATA``).
    """
    return {
        "task_id": task_id,
        "target_id": target_id,
        "status": final_status,
        "score": score,
        "max_score": 100.0,
        "tests_pct": tests_pct,
        "has_tests": has_tests,
        "diff_pct": diff_pct,
        "has_reference": has_reference,
        "rubric_pct": rubric_pct,
        "has_rubric": has_rubric,
        "criteria": criteria,
        "weights": weights,
    }
