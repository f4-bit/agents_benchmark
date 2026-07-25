#!/usr/bin/env python3
"""Benchmark runner: execute targets against tasks and produce reports."""

from __future__ import annotations

# When executed as a script (python benchmarks/run.py), ensure the repo root is
# on sys.path so the ``benchmarks`` package can be imported.
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import argparse
import hashlib
import json
import logging
import shutil
import time
from collections import defaultdict
from pathlib import Path

from benchmarks.eval.diff_engine import evaluate_diff
from benchmarks.eval.rubric_checker import evaluate_rubric
from benchmarks.eval.scorer import build_eval_json, score_task
from benchmarks.eval.target_adapter import InvocationResult
from benchmarks.eval.target_registry import load_targets
from benchmarks.eval.test_runner import run_pytest

logger = logging.getLogger(__name__)


BENCHMARKS_DIR = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARKS_DIR.parent
CATEGORIES_DIR = BENCHMARKS_DIR / "categories"
MANIFEST_PATH = BENCHMARKS_DIR / "manifest.json"
TARGETS_PATH = BENCHMARKS_DIR / "targets.yaml"
RESULTS_DIR = BENCHMARKS_DIR / "results"


def load_manifest(path: Path) -> dict:
    """Load the benchmark manifest JSON."""
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _hash_files(*paths: Path) -> str:
    """Return a short hex hash of the concatenated file contents."""
    hasher = hashlib.sha256()
    for p in paths:
        if p.exists():
            hasher.update(p.read_bytes())
    return hasher.hexdigest()[:8]


def generate_run_id() -> str:
    """Generate a run id from timestamp and config hashes."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    config_hash = _hash_files(MANIFEST_PATH, TARGETS_PATH)
    return f"{timestamp}-{config_hash}"


def _task_dir(category: str, task_id: str) -> Path:
    return CATEGORIES_DIR / category / task_id


def _task_timeout(task: dict, manifest: dict) -> int:
    """Resolve task timeout from task entry, category, or default by difficulty."""
    if task.get("timeout"):
        return task["timeout"]
    difficulty = task.get("difficulty", "medium")
    return manifest["defaults"]["timeouts"][difficulty]


def _task_weights(task: dict, category: dict, manifest: dict) -> dict[str, float]:
    """Resolve scoring weights for a task: task > category > defaults."""
    if task.get("weights"):
        return task["weights"]
    if category.get("weights"):
        return category["weights"]
    return manifest["defaults"]["weights"]


def _apply_target_output(
    workspace_dir: Path,
    target_file: str,
    result: InvocationResult,
) -> None:
    """Write the target's output into the workspace if it is non-empty."""
    if not result.output_content.strip():
        logger.info("No output content for target file %s; leaving fixtures intact", target_file)
        return

    target_path = workspace_dir / target_file
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(result.output_content, encoding="utf-8")
    logger.info("Applied target output to %s", target_path)


def _evaluate_task(
    workspace_dir: Path,
    task_dir: Path,
    target_file: str,
    weights: dict[str, float],
    result: InvocationResult,
) -> dict:
    """Run the deterministic eval engine on a workspace."""
    test_info = run_pytest(workspace_dir)
    diff_info = evaluate_diff(workspace_dir, target_file, task_dir / "expected")
    rubric_info = evaluate_rubric(
        task_dir / "rubric.json", result.output_content, workspace_dir
    )

    score, eval_status, adjusted = score_task(
        tests_pct=test_info["tests_pct"],
        has_tests=test_info["has_tests"],
        diff_pct=diff_info["diff_pct"],
        has_reference=diff_info["has_reference"],
        rubric_pct=rubric_info["rubric_pct"],
        has_rubric=rubric_info["has_rubric"],
        weights=weights,
    )

    if result.status in {"TIMEOUT", "NO_OUTPUT", "ERROR"}:
        final_status = result.status
        score = 0.0
    elif eval_status == "NO_EVAL_DATA":
        final_status = "NO_EVAL_DATA"
    else:
        final_status = eval_status

    return build_eval_json(
        task_id=task_dir.name,
        target_id=result.target_id if hasattr(result, "target_id") else "unknown",
        final_status=final_status,
        score=score,
        tests_pct=test_info["tests_pct"],
        has_tests=test_info["has_tests"],
        diff_pct=diff_info["diff_pct"],
        has_reference=diff_info["has_reference"],
        rubric_pct=rubric_info["rubric_pct"],
        has_rubric=rubric_info["has_rubric"],
        criteria=rubric_info["criteria"],
        weights=adjusted,
    )


def _write_result_line(
    results_jsonl: Path,
    target_id: str,
    category: str,
    task: dict,
    eval_json: dict,
) -> None:
    line = {
        "target_id": target_id,
        "task_id": task["id"],
        "category": category,
        "difficulty": task["difficulty"],
        "status": eval_json["status"],
        "score": eval_json["score"],
        "max_score": eval_json["max_score"],
    }
    with results_jsonl.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")


def _iter_tasks(manifest: dict, selected_categories: list[str] | None):
    """Yield (category_name, category_data, task) for active tasks."""
    for category_name, category_data in manifest["categories"].items():
        if category_data.get("status") == "deferred":
            logger.warning("Skipping deferred category: %s", category_name)
            continue
        if selected_categories and category_name not in selected_categories:
            continue
        for task in category_data.get("tasks", []):
            if task.get("status") != "active":
                continue
            yield category_name, category_data, task


def run_benchmark(
    targets: dict,
    manifest: dict,
    selected_categories: list[str] | None,
    output_dir: Path,
) -> Path:
    """Run the benchmark and return the run directory."""
    run_id = generate_run_id()
    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    results_jsonl = run_dir / "results.jsonl"

    logger.info("Starting benchmark run: %s", run_id)

    for target_id, target in targets.items():
        for category_name, category_data, task in _iter_tasks(manifest, selected_categories):
            task_id = task["id"]
            task_dir = _task_dir(category_name, task_id)
            task_workspace = run_dir / target_id / task_id / "workspace"
            task_workspace.mkdir(parents=True, exist_ok=True)

            logger.info(
                "Executing target '%s' against %s/%s", target_id, category_name, task_id
            )

            # Prepare workspace.
            shutil.copytree(
                task_dir / "fixtures",
                task_workspace,
                dirs_exist_ok=True,
            )

            prompt_path = task_dir / "prompt.md"
            output_path = task_workspace / "target_output.md"
            timeout = target.timeout or _task_timeout(task, manifest)

            result = target.invoke(
                prompt_path=prompt_path,
                workspace_dir=task_workspace,
                output_path=output_path,
                timeout=timeout,
            )
            # Stash target_id on result for reporting.
            result.target_id = target_id  # type: ignore[attr-defined]

            # Write stdout/stderr logs.
            (task_workspace.parent / "stdout.log").write_text(
                result.stdout, encoding="utf-8"
            )
            (task_workspace.parent / "stderr.log").write_text(
                result.stderr, encoding="utf-8"
            )

            # Apply target output to the target file.
            rubric_path = task_dir / "rubric.json"
            target_file = "src/module.py"
            if rubric_path.exists():
                rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
                target_file = rubric.get("target_file", target_file)

            _apply_target_output(task_workspace, target_file, result)

            # Evaluate.
            weights = _task_weights(task, category_data, manifest)
            eval_json = _evaluate_task(task_workspace, task_dir, target_file, weights, result)
            eval_path = task_workspace.parent / "eval.json"
            eval_path.write_text(json.dumps(eval_json, indent=2, ensure_ascii=False), encoding="utf-8")

            _write_result_line(results_jsonl, target_id, category_name, task, eval_json)

    return run_dir


def _load_eval_results(run_dir: Path) -> list[dict]:
    """Read all eval.json files from a run directory."""
    results = []
    for eval_path in run_dir.rglob("eval.json"):
        with eval_path.open("r", encoding="utf-8") as fh:
            results.append(json.load(fh))
    return results


def _task_to_category_map(manifest: dict) -> dict[str, str]:
    """Return a mapping from task id to category name."""
    mapping = {}
    for category_name, category_data in manifest["categories"].items():
        for task in category_data.get("tasks", []):
            mapping[task["id"]] = category_name
    return mapping


def _build_summary(results: list[dict], manifest: dict) -> dict:
    """Aggregate per-target, per-category, and global scores."""
    active_categories = {
        name
        for name, data in manifest["categories"].items()
        if data.get("status") == "active"
    }

    task_category = _task_to_category_map(manifest)
    target_category_scores: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for result in results:
        category_name = task_category.get(result["task_id"], "unknown")
        target_category_scores[result["target_id"]][category_name].append(
            result["score"]
        )

    summary: dict[str, Any] = {}
    for target_id, category_scores in target_category_scores.items():
        target_summary: dict[str, Any] = {}
        category_avgs: dict[str, float] = {}
        for category_name, scores in category_scores.items():
            if scores:
                category_avgs[category_name] = sum(scores) / len(scores)

        for category_name in sorted(active_categories):
            target_summary[category_name] = {
                "score": category_avgs.get(category_name, 0.0),
                "tasks": len(category_scores.get(category_name, [])),
            }

        if category_avgs:
            target_summary["global"] = sum(category_avgs.values()) / len(category_avgs)
        else:
            target_summary["global"] = 0.0

        summary[target_id] = target_summary

    return summary


def _generate_report(summary: dict) -> str:
    """Render a human-readable markdown report from a summary."""
    lines = ["# Benchmark Report\n", ""]
    if not summary:
        lines.append("No targets executed.\n")
        return "\n".join(lines)

    categories = sorted(
        {
            key
            for target_summary in summary.values()
            for key in target_summary.keys()
            if key != "global"
        }
    )

    # Sort targets by global score descending.
    sorted_targets = sorted(
        summary.items(), key=lambda item: item[1].get("global", 0.0), reverse=True
    )

    header = ["Target", *categories, "Global"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    for target_id, target_summary in sorted_targets:
        row = [target_id]
        for category in categories:
            score = target_summary.get(category, {}).get("score", 0.0)
            row.append(f"{score:.1f}")
        row.append(f"{target_summary.get('global', 0.0):.1f}")
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines) + "\n"


def generate_report(run_dir: Path, manifest: dict) -> None:
    """Generate summary.json and report.md for a run directory."""
    results = _load_eval_results(run_dir)
    summary = _build_summary(results, manifest)

    summary_path = run_dir / "summary.json"
    summary_path.write_text(
        json.dumps({"run_id": run_dir.name, "targets": summary}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    report_path = run_dir / "report.md"
    report_path.write_text(_generate_report(summary), encoding="utf-8")

    logger.info("Generated summary.json and report.md in %s", run_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Execute benchmark targets against benchmark tasks."
    )
    parser.add_argument(
        "--targets",
        default="all",
        help="Comma-separated target IDs, or 'all'.",
    )
    parser.add_argument(
        "--categories",
        default="all",
        help="Comma-separated category names, or 'all'.",
    )
    parser.add_argument(
        "--report-only",
        metavar="RUN_ID",
        help="Regenerate summary.json and report.md from an existing run.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS_DIR,
        help="Directory for results (default: benchmarks/results).",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    manifest = load_manifest(MANIFEST_PATH)

    if args.report_only:
        run_dir = args.output / args.report_only
        if not run_dir.exists():
            logger.error("Run directory not found: %s", run_dir)
            return 1
        generate_report(run_dir, manifest)
        return 0

    targets = load_targets(TARGETS_PATH)
    selected_targets = (
        list(targets.keys()) if args.targets == "all" else args.targets.split(",")
    )
    selected_categories = (
        None if args.categories == "all" else args.categories.split(",")
    )

    requested_targets = {tid: targets[tid] for tid in selected_targets if tid in targets}
    unknown = [tid for tid in selected_targets if tid not in targets]
    if unknown:
        logger.error("Unknown targets: %s", unknown)
        return 1

    run_dir = run_benchmark(
        requested_targets,
        manifest,
        selected_categories,
        args.output,
    )
    generate_report(run_dir, manifest)

    logger.info("Benchmark complete: %s", run_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
