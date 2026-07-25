"""AST-based structural diff for the benchmark eval engine."""

from __future__ import annotations

import ast
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _node_types(source: str) -> list[str]:
    """Return the pre-order sequence of AST node type names for ``source``."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        logger.warning("Cannot parse source for AST diff: %s", exc)
        return []
    return [type(node).__name__ for node in ast.walk(tree)]


def _levenshtein(a: list[str], b: list[str]) -> int:
    """Compute the Levenshtein edit distance between two sequences."""
    n, m = len(a), len(b)
    if n == 0:
        return m
    if m == 0:
        return n

    # Use two rows for O(min(n,m)) space.
    previous = list(range(m + 1))
    current = [0] * (m + 1)

    for i in range(1, n + 1):
        current[0] = i
        ai = a[i - 1]
        for j in range(1, m + 1):
            cost = 0 if ai == b[j - 1] else 1
            current[j] = min(
                current[j - 1] + 1,      # insertion
                previous[j] + 1,         # deletion
                previous[j - 1] + cost,  # substitution
            )
        previous, current = current, previous

    return previous[m]


def compute_ast_diff(target_source: str, reference_source: str) -> float:
    """Return a structural similarity percentage (0-100) between two sources.

    The comparison is based on the sequence of AST node types, so two
    functionally equivalent implementations with different variable names or
    formatting can still score highly.
    """
    target_nodes = _node_types(target_source)
    reference_nodes = _node_types(reference_source)

    max_len = max(len(target_nodes), len(reference_nodes))
    if max_len == 0:
        return 100.0

    distance = _levenshtein(target_nodes, reference_nodes)
    similarity = 1.0 - (distance / max_len)
    return max(0.0, similarity * 100.0)


def evaluate_diff(workspace_dir: Path, target_file: str, expected_dir: Path) -> dict[str, object]:
    """Compare the target file in the workspace with the reference solution.

    Returns:
        Dictionary with ``diff_pct`` (0-100), ``has_reference``, and the
        resolved reference path.
    """
    reference_file = expected_dir / target_file
    target_path = workspace_dir / target_file

    if not reference_file.exists():
        logger.warning("No reference solution found at %s", reference_file)
        return {"diff_pct": 0.0, "has_reference": False, "reference_file": None}

    target_source = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
    reference_source = reference_file.read_text(encoding="utf-8")

    diff_pct = compute_ast_diff(target_source, reference_source)

    return {
        "diff_pct": diff_pct,
        "has_reference": True,
        "reference_file": str(reference_file),
    }
