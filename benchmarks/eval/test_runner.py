"""Deterministic pytest execution layer for the benchmark eval engine."""

from __future__ import annotations

import logging
import os
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


# Regex matching pytest's final summary line, e.g.:
# "1 passed in 0.03s"
# "3 failed, 2 passed in 1.23s"
# "no tests ran in 0.00s"
_SUMMARY_RE = re.compile(
    r"^(?P<no_tests>no tests ran|\d+\s+\w+(?:,\s+\d+\s+\w+)*)\s+in\s+[\d.]+s",
    re.IGNORECASE,
)


def _discover_tests(workspace_dir: Path) -> list[Path]:
    """Return a list of pytest-discoverable test files in the workspace."""
    tests_dir = workspace_dir / "tests"
    if not tests_dir.is_dir():
        return []
    return [
        p
        for p in tests_dir.rglob("*.py")
        if p.name.startswith("test_") or p.name == "tests.py"
    ]


def _parse_summary(stdout: str) -> tuple[int, int]:
    """Parse pytest stdout and return (passed, total) counts."""
    passed = 0
    total = 0

    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if not line:
            continue

        # Strip pytest border characters so "============================== 1 passed in 0.02s =============================="
        # becomes "1 passed in 0.02s".
        clean = line.strip("=").strip()

        if "no tests ran" in clean.lower():
            return 0, 0

        # Match fragments like "3 passed, 2 failed"
        if re.search(r"\b\d+\s+(passed|failed|error|skipped|deselected)\b", clean):
            parts = re.findall(r"(\d+)\s+(passed|failed|error|skipped)", clean)
            for count, status in parts:
                count_int = int(count)
                if status == "passed":
                    passed = count_int
                if status in {"passed", "failed", "error"}:
                    total += count_int
            if total > 0:
                return passed, total

    return 0, 0


def run_pytest(workspace_dir: Path, test_selector: str | None = None) -> dict[str, object]:
    """Run pytest in ``workspace_dir`` and return pass statistics.

    Args:
        workspace_dir: Directory containing ``src/`` and ``tests/``.
        test_selector: Optional pytest node id (e.g.
            ``tests/test_foo.py::test_bar``). If omitted, the whole suite is run.

    Returns:
        Dictionary with ``passed``, ``total``, ``tests_pct`` (0-100), and
        ``has_tests``.
    """
    env = os.environ.copy()
    src_dir = (workspace_dir / "src").resolve()
    env["PYTHONPATH"] = str(src_dir) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    cmd = [
        "python",
        "-m",
        "pytest",
        "--tb=no",
    ]
    if test_selector:
        cmd.append(test_selector)

    logger.debug("Running pytest in %s: %s", workspace_dir, " ".join(cmd))

    result = subprocess.run(
        cmd,
        cwd=str(workspace_dir),
        env=env,
        capture_output=True,
        text=True,
    )

    passed, total = _parse_summary(result.stdout)

    has_tests = total > 0
    tests_pct = (passed / total * 100.0) if total > 0 else 0.0

    logger.debug(
        "Pytest result: %s/%s passed (%.1f%%)", passed, total, tests_pct
    )

    return {
        "passed": passed,
        "total": total,
        "tests_pct": tests_pct,
        "has_tests": has_tests,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode,
    }


def has_pytest_suite(workspace_dir: Path) -> bool:
    """Return True if ``workspace_dir`` contains at least one pytest test file."""
    return len(_discover_tests(workspace_dir)) > 0
