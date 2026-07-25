"""Unit tests for the deterministic benchmark eval engine."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmarks.eval.diff_engine import compute_ast_diff, evaluate_diff
from benchmarks.eval.rubric_checker import evaluate_rubric
from benchmarks.eval.scorer import score_task


def test_score_task_all_layers_perfect() -> None:
    score, status, adjusted = score_task(
        tests_pct=100.0,
        has_tests=True,
        diff_pct=100.0,
        has_reference=True,
        rubric_pct=100.0,
        has_rubric=True,
    )
    assert score == 100.0
    assert status == "PASS"
    assert adjusted == {"tests": 0.5, "diff": 0.3, "rubric": 0.2}


def test_score_task_all_layers_partial() -> None:
    score, status, adjusted = score_task(
        tests_pct=80.0,
        has_tests=True,
        diff_pct=60.0,
        has_reference=True,
        rubric_pct=50.0,
        has_rubric=True,
    )
    expected = 0.5 * 80.0 + 0.3 * 60.0 + 0.2 * 50.0
    assert score == expected
    assert status == "FAIL"


def test_score_task_missing_tests_redistributes() -> None:
    score, status, adjusted = score_task(
        tests_pct=0.0,
        has_tests=False,
        diff_pct=100.0,
        has_reference=True,
        rubric_pct=100.0,
        has_rubric=True,
    )
    # Original weights: diff=0.3, rubric=0.2 -> normalized to 0.6 and 0.4.
    assert adjusted == pytest.approx({"diff": 0.6, "rubric": 0.4})
    assert score == 100.0
    assert status == "PASS"


def test_score_task_only_tests() -> None:
    score, status, adjusted = score_task(
        tests_pct=70.0,
        has_tests=True,
        diff_pct=0.0,
        has_reference=False,
        rubric_pct=0.0,
        has_rubric=False,
    )
    assert adjusted == {"tests": 1.0}
    assert score == 70.0
    assert status == "FAIL"


def test_score_task_no_eval_data() -> None:
    score, status, adjusted = score_task(
        tests_pct=0.0,
        has_tests=False,
        diff_pct=0.0,
        has_reference=False,
        rubric_pct=0.0,
        has_rubric=False,
    )
    assert score == 0.0
    assert status == "NO_EVAL_DATA"
    assert adjusted == {}


def test_score_task_custom_weights() -> None:
    score, status, adjusted = score_task(
        tests_pct=100.0,
        has_tests=True,
        diff_pct=0.0,
        has_reference=False,
        rubric_pct=100.0,
        has_rubric=True,
        weights={"tests": 0.3, "diff": 0.2, "rubric": 0.5},
    )
    # tests=0.3, rubric=0.5 -> normalized to 0.375 and 0.625.
    assert adjusted == pytest.approx({"tests": 0.375, "rubric": 0.625})
    assert score == 100.0
    assert status == "PASS"


def test_ast_diff_identical_sources() -> None:
    source = "def add(a, b):\n    return a + b\n"
    assert compute_ast_diff(source, source) == 100.0


def test_ast_diff_different_but_similar_sources() -> None:
    a = "def add(a, b):\n    return a + b\n"
    b = "def sum(x, y):\n    return x + y\n"
    pct = compute_ast_diff(a, b)
    assert pct > 50.0


def test_ast_diff_completely_different_sources() -> None:
    a = "def add(a, b):\n    return a + b\n"
    b = "class Foo:\n    pass\n"
    pct = compute_ast_diff(a, b)
    assert pct < 50.0


def test_ast_diff_invalid_syntax_returns_zero() -> None:
    pct = compute_ast_diff("def foo(", "def foo(): pass")
    assert pct == 0.0


def test_evaluate_diff_with_reference(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    expected = tmp_path / "expected"
    expected.mkdir()

    (workspace / "src").mkdir()
    (workspace / "src" / "counter.py").write_text("x = 1\n", encoding="utf-8")
    (expected / "src").mkdir()
    (expected / "src" / "counter.py").write_text("x = 1\n", encoding="utf-8")

    result = evaluate_diff(workspace, "src/counter.py", expected)
    assert result["has_reference"] is True
    assert result["diff_pct"] == 100.0


def test_evaluate_diff_without_reference(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    expected = tmp_path / "expected"
    expected.mkdir()

    result = evaluate_diff(workspace, "src/missing.py", expected)
    assert result["has_reference"] is False
    assert result["diff_pct"] == 0.0


def test_evaluate_rubric_pattern(tmp_path: Path) -> None:
    rubric_path = tmp_path / "rubric.json"
    rubric_path.write_text(
        json.dumps(
            {
                "criteria": [
                    {
                        "id": "uses_lock",
                        "type": "pattern",
                        "check": "output_contains",
                        "pattern": r"threading\.Lock\(",
                        "weight": 100,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    result = evaluate_rubric(rubric_path, "import threading\nlock = threading.Lock()", tmp_path)
    assert result["rubric_pct"] == 100.0
    assert result["has_rubric"] is True
    assert result["criteria"][0]["matched"] is True


def test_evaluate_rubric_missing_file(tmp_path: Path) -> None:
    result = evaluate_rubric(tmp_path / "missing.json", "", tmp_path)
    assert result["has_rubric"] is False
    assert result["rubric_pct"] == 0.0


def test_determinism(tmp_path: Path) -> None:
    """Same inputs produce identical scores and adjusted weights."""
    result1 = score_task(
        tests_pct=75.0,
        has_tests=True,
        diff_pct=50.0,
        has_reference=True,
        rubric_pct=25.0,
        has_rubric=True,
    )
    result2 = score_task(
        tests_pct=75.0,
        has_tests=True,
        diff_pct=50.0,
        has_reference=True,
        rubric_pct=25.0,
        has_rubric=True,
    )
    assert result1 == result2

    source = "def add(a, b):\n    return a + b\n"
    assert compute_ast_diff(source, source) == compute_ast_diff(source, source)
