"""Integration tests for the benchmark runner."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from benchmarks.eval.target_adapter import BenchmarkTarget
from benchmarks.eval.target_registry import load_targets
from benchmarks.run import run_benchmark, generate_run_id


@pytest.fixture
def mini_manifest(tmp_path: Path) -> Path:
    """Create a minimal manifest with one category and one task."""
    categories_dir = tmp_path / "categories"
    task_dir = categories_dir / "demo" / "001-sleep"
    (task_dir / "fixtures" / "src").mkdir(parents=True)
    (task_dir / "fixtures" / "tests").mkdir(parents=True)
    (task_dir / "expected" / "src").mkdir(parents=True)

    (task_dir / "fixtures" / "src" / "module.py").write_text(
        "def work(): pass\n", encoding="utf-8"
    )
    (task_dir / "fixtures" / "tests" / "test_module.py").write_text(
        "from module import work\ndef test_work(): work()\n", encoding="utf-8"
    )
    (task_dir / "expected" / "src" / "module.py").write_text(
        "def work(): pass\n", encoding="utf-8"
    )
    (task_dir / "prompt.md").write_text("fix it", encoding="utf-8")
    (task_dir / "rubric.json").write_text(
        json.dumps(
            {
                "target_file": "src/module.py",
                "criteria": [
                    {
                        "id": "tests-pass",
                        "type": "test",
                        "check": "tests/test_module.py",
                        "weight": 100,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    manifest = {
        "version": "1.0.0",
        "defaults": {
            "timeouts": {"easy": 1, "medium": 1, "hard": 1},
            "weights": {"tests": 1.0, "diff": 0.0, "rubric": 0.0},
        },
        "categories": {
            "demo": {
                "status": "active",
                "eval_mode": "deterministic",
                "tasks": [
                    {
                        "id": "001-sleep",
                        "name": "sleep",
                        "difficulty": "easy",
                        "timeout": 1,
                        "status": "active",
                    }
                ],
            }
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path


def test_run_benchmark_with_mock_target(mini_manifest: Path, tmp_path: Path) -> None:
    """A target that writes the reference solution scores 100."""
    import benchmarks.run as run_module

    # Monkey-patch the global constants to point at our mini repository.
    original_categories_dir = run_module.CATEGORIES_DIR
    original_manifest_path = run_module.MANIFEST_PATH
    original_results_dir = run_module.RESULTS_DIR
    original_targets_path = run_module.TARGETS_PATH

    try:
        run_module.CATEGORIES_DIR = mini_manifest / "categories"
        run_module.MANIFEST_PATH = mini_manifest / "manifest.json"
        run_module.RESULTS_DIR = tmp_path / "results"
        # Use a minimal targets.yaml that references the mock target.
        targets_path = mini_manifest / "targets.yaml"
        mock_target_script = Path(__file__).resolve().parents[1] / "tests" / "mock_target.py"
        targets_path.write_text(
            f"""
targets:
  - id: mock
    type: cli
    command:
      - python
      - {mock_target_script}
    timeout: 10
""",
            encoding="utf-8",
        )
        run_module.TARGETS_PATH = targets_path

        targets = run_module.load_targets(targets_path)
        manifest = run_module.load_manifest(mini_manifest / "manifest.json")
        run_dir = run_module.run_benchmark(
            targets={"mock": targets["mock"]},
            manifest=manifest,
            selected_categories=None,
            output_dir=tmp_path / "results",
        )
        run_module.generate_report(run_dir, manifest)

        eval_path = run_dir / "mock" / "001-sleep" / "eval.json"
        assert eval_path.exists()
        eval_result = json.loads(eval_path.read_text(encoding="utf-8"))
        assert eval_result["status"] == "PASS"
        assert eval_result["score"] == 100.0

        summary_path = run_dir / "summary.json"
        assert summary_path.exists()
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        assert summary["targets"]["mock"]["global"] == 100.0
    finally:
        run_module.CATEGORIES_DIR = original_categories_dir
        run_module.MANIFEST_PATH = original_manifest_path
        run_module.RESULTS_DIR = original_results_dir
        run_module.TARGETS_PATH = original_targets_path


def test_timeout_enforcement(tmp_path: Path) -> None:
    """A target that sleeps longer than the timeout is killed and marked TIMEOUT."""
    target = BenchmarkTarget(
        target_id="sleeper",
        target_type="cli",
        command=["python", "-c", "import time; time.sleep(30)"],
    )
    result = target.invoke(tmp_path / "prompt.md", tmp_path / "workspace", tmp_path / "output.md", timeout=1)
    assert result.status == "TIMEOUT"
    assert result.timed_out is True
