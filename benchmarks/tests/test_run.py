"""Unit tests for the benchmark runner orchestration and CLI behavior."""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest import mock

import pytest

from benchmarks import run as run_module
from benchmarks.eval.target_adapter import InvocationResult
from benchmarks.run import (
    _is_active_category,
    _task_timeout,
    generate_run_id,
    main,
    run_benchmark,
)


@pytest.fixture
def tmp_results(tmp_path: Path) -> Path:
    """Provide a temporary results directory for isolated runs."""
    return tmp_path / "results"


def test_is_active_category_only_accepts_status_active() -> None:
    assert _is_active_category({"status": "active"}) is True
    assert _is_active_category({"status": "deferred"}) is False
    assert _is_active_category({"status": "experimental"}) is False
    assert _is_active_category({}) is False


def test_task_timeout_uses_task_timeout_when_present() -> None:
    manifest = {"defaults": {"timeouts": {"easy": 300, "medium": 1200, "hard": 2400}}}
    task = {"timeout": 99, "difficulty": "easy"}
    assert _task_timeout(task, manifest) == 99


def test_task_timeout_uses_difficulty_default() -> None:
    manifest = {"defaults": {"timeouts": {"easy": 300, "medium": 1200, "hard": 2400}}}
    task = {"difficulty": "hard"}
    assert _task_timeout(task, manifest) == 2400


def test_task_timeout_unknown_difficulty_falls_back_to_medium() -> None:
    manifest = {"defaults": {"timeouts": {"easy": 300, "medium": 1200, "hard": 2400}}}
    task = {"difficulty": "expert"}
    assert _task_timeout(task, manifest) == 1200


def test_generate_run_id_is_deterministic_for_same_inputs() -> None:
    rid1 = generate_run_id(["mock-reference", "opencode-glm-default"], ["bug-hunt"])
    rid2 = generate_run_id(["opencode-glm-default", "mock-reference"], ["bug-hunt"])
    rid3 = generate_run_id(["mock-reference", "opencode-glm-default"], ["bug-hunt"])
    assert rid1 == rid2
    assert rid1 == rid3


def test_generate_run_id_differs_for_different_inputs() -> None:
    rid1 = generate_run_id(["mock-reference"], ["bug-hunt"])
    rid2 = generate_run_id(["mock-reference"], ["backend"])
    rid3 = generate_run_id(["mock-reference"], ["bug-hunt", "backend"])
    assert rid1 != rid2
    assert rid1 != rid3


def test_generate_run_id_no_time_component() -> None:
    """The run id should not change based on wall-clock time."""
    with mock.patch.object(time, "strftime", return_value="20210101-000000"):
        rid1 = generate_run_id(["mock-reference"], ["bug-hunt"])
    rid2 = generate_run_id(["mock-reference"], ["bug-hunt"])
    assert rid1 == rid2


def test_run_benchmark_deterministic_summary(tmp_path: Path) -> None:
    """Two identical runs produce byte-identical summary.json files."""
    results_dir = tmp_path / "results"
    manifest = run_module.load_manifest(run_module.MANIFEST_PATH)
    targets = run_module.load_targets(run_module.TARGETS_PATH)
    requested = {tid: targets[tid] for tid in ["mock-reference"]}

    run_dir1 = run_benchmark(
        requested,
        manifest,
        selected_categories=["bug-hunt"],
        output_dir=results_dir,
    )
    run_module.generate_report(run_dir1, manifest)
    run_dir2 = run_benchmark(
        requested,
        manifest,
        selected_categories=["bug-hunt"],
        output_dir=results_dir,
    )
    run_module.generate_report(run_dir2, manifest)

    summary1 = (run_dir1 / "summary.json").read_bytes()
    summary2 = (run_dir2 / "summary.json").read_bytes()
    assert summary1 == summary2


def test_run_benchmark_uses_run_id_override(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    manifest = run_module.load_manifest(run_module.MANIFEST_PATH)
    targets = run_module.load_targets(run_module.TARGETS_PATH)
    requested = {tid: targets[tid] for tid in ["mock-reference"]}

    run_dir = run_benchmark(
        requested,
        manifest,
        selected_categories=["bug-hunt"],
        output_dir=results_dir,
        run_id="my-experiment-1",
    )
    assert run_dir.name == "my-experiment-1"


def test_run_benchmark_overwrites_results_jsonl_on_re_run(tmp_path: Path) -> None:
    """Re-running the same inputs truncates results.jsonl instead of appending."""
    results_dir = tmp_path / "results"
    manifest = run_module.load_manifest(run_module.MANIFEST_PATH)
    targets = run_module.load_targets(run_module.TARGETS_PATH)
    requested = {tid: targets[tid] for tid in ["mock-reference"]}

    run_dir1 = run_benchmark(
        requested,
        manifest,
        selected_categories=["bug-hunt"],
        output_dir=results_dir,
    )
    run_dir2 = run_benchmark(
        requested,
        manifest,
        selected_categories=["bug-hunt"],
        output_dir=results_dir,
    )

    assert run_dir1 == run_dir2
    lines = (run_dir2 / "results.jsonl").read_text(encoding="utf-8").strip().splitlines()
    # 3 bug-hunt tasks × 1 target = 3 lines.
    assert len(lines) == 3


def test_run_benchmark_continues_on_task_error(tmp_path: Path) -> None:
    """A single task that raises an exception does not abort the whole run."""
    results_dir = tmp_path / "results"
    manifest = run_module.load_manifest(run_module.MANIFEST_PATH)
    targets = run_module.load_targets(run_module.TARGETS_PATH)
    requested = {tid: targets[tid] for tid in ["mock-reference"]}

    # Patch the target's invoke so it raises once for the first task.
    call_count = 0
    original_invoke = targets["mock-reference"].invoke

    def flaky_invoke(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("simulated failure")
        return original_invoke(*args, **kwargs)

    with mock.patch.object(targets["mock-reference"], "invoke", flaky_invoke):
        run_dir = run_benchmark(
            requested,
            manifest,
            selected_categories=["bug-hunt"],
            output_dir=results_dir,
        )

    eval_paths = sorted(run_dir.rglob("eval.json"))
    statuses = [json.loads(p.read_text(encoding="utf-8"))["status"] for p in eval_paths]
    assert "ERROR" in statuses
    # All three tasks still produced eval.json files.
    assert len(statuses) == 3


def test_run_benchmark_fail_fast_aborts_after_first_error(tmp_path: Path) -> None:
    """--fail-fast re-raises after writing the ERROR eval.json."""
    results_dir = tmp_path / "results"
    manifest = run_module.load_manifest(run_module.MANIFEST_PATH)
    targets = run_module.load_targets(run_module.TARGETS_PATH)
    requested = {tid: targets[tid] for tid in ["mock-reference"]}

    with mock.patch.object(targets["mock-reference"], "invoke", side_effect=RuntimeError("boom")):
        with pytest.raises(RuntimeError, match="boom"):
            run_benchmark(
                requested,
                manifest,
                selected_categories=["bug-hunt"],
                output_dir=results_dir,
                fail_fast=True,
            )

    eval_paths = sorted(results_dir.rglob("eval.json"))
    assert len(eval_paths) == 1


def test_main_unknown_category_returns_one() -> None:
    exit_code = main(["--targets", "mock-reference", "--categories", "bug-huntt"])
    assert exit_code == 1


def test_main_whitespace_in_targets() -> None:
    """Whitespace around comma-separated targets is stripped."""
    exit_code = main(["--targets", " mock-reference , unknown-target ", "--categories", "bug-hunt"])
    assert exit_code == 1


def test_main_all_tasks_pass_returns_zero(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    exit_code = main(
        [
            "--targets",
            "mock-reference",
            "--categories",
            "bug-hunt",
            "--output",
            str(results_dir),
        ]
    )
    assert exit_code == 0


def test_main_any_failure_returns_two(tmp_path: Path) -> None:
    """A non-perfect score yields exit code 2."""
    results_dir = tmp_path / "results"

    # Patch mock-reference to write the buggy fixture, producing a failing score.
    original_targets = run_module.load_targets(run_module.TARGETS_PATH)
    patched_targets = dict(original_targets)

    def failing_invoke(*args, **kwargs):
        prompt_path = kwargs.get("prompt_path") or args[0]
        output_path = kwargs.get("output_path") or args[2]
        task_dir = Path(prompt_path).parent
        rubric = json.loads((task_dir / "rubric.json").read_text(encoding="utf-8"))
        fixture_src = (task_dir / "fixtures" / rubric["target_file"]).read_text(encoding="utf-8")
        Path(output_path).write_text(fixture_src, encoding="utf-8")
        return InvocationResult(
            exit_code=0,
            stdout="",
            stderr="",
            output_content=fixture_src,
            status="PASS",
            timed_out=False,
        )

    patched_targets["mock-reference"] = original_targets["mock-reference"]
    with mock.patch.object(patched_targets["mock-reference"], "invoke", failing_invoke):
        with mock.patch.object(
            run_module, "load_targets", return_value=patched_targets
        ):
            exit_code = run_module.main(
                [
                    "--targets",
                    "mock-reference",
                    "--categories",
                    "bug-hunt",
                    "--output",
                    str(results_dir),
                ]
            )
    assert exit_code == 2


def test_report_only_regenerates_summary_byte_identically(tmp_path: Path) -> None:
    """--report-only on the same run dir produces byte-identical summary.json."""
    results_dir = tmp_path / "results"
    main(
        [
            "--targets",
            "mock-reference",
            "--categories",
            "bug-hunt",
            "--output",
            str(results_dir),
        ]
    )
    run_dirs = [d for d in results_dir.iterdir() if d.is_dir()]
    assert len(run_dirs) == 1
    run_dir = run_dirs[0]

    summary1 = (run_dir / "summary.json").read_bytes()
    main(
        [
            "--report-only",
            run_dir.name,
            "--output",
            str(results_dir),
        ]
    )
    summary2 = (run_dir / "summary.json").read_bytes()
    assert summary1 == summary2


def test_run_benchmark_run_id_override_cli(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    exit_code = main(
        [
            "--targets",
            "mock-reference",
            "--categories",
            "bug-hunt",
            "--output",
            str(results_dir),
            "--run-id",
            "my-experiment-1",
        ]
    )
    assert exit_code == 0
    assert (results_dir / "my-experiment-1").exists()
