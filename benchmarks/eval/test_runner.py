"""Deterministic pytest execution layer for the benchmark eval engine."""

from __future__ import annotations

import logging
import os
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def _parse_summary(stdout: str) -> tuple[int, int]:
    """Parse pytest stdout and return (passed, total) counts."""
    passed = 0
    total = 0

    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if not line:
            continue

        # Strip pytest border characters so "============================== 1 passed in 0.02s ==============================="
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


def run_pytest(
    workspace_dir: Path,
    test_selector: str | None = None,
    timeout: int | None = None,
) -> dict[str, object]:
    """Run pytest in ``workspace_dir`` and return pass statistics.

    Args:
        workspace_dir: Directory containing ``src/`` and ``tests/``.
        test_selector: Optional pytest node id (e.g.
            ``tests/test_foo.py::test_bar``). If omitted, the whole suite is run.
        timeout: Optional timeout in seconds for the pytest subprocess.

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
    if timeout:
        cmd.extend(["--timeout", str(timeout)])
    if test_selector:
        cmd.append(test_selector)

    logger.debug("Running pytest in %s: %s", workspace_dir, " ".join(cmd))

    try:
        result = subprocess.run(
            cmd,
            cwd=str(workspace_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        logger.warning("Pytest timed out after %ss in %s", timeout, workspace_dir)
        stdout = exc.stdout if exc.stdout else ""
        stderr = exc.stderr if exc.stderr else ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return {
            "passed": 0,
            "total": 0,
            "tests_pct": 0.0,
            "has_tests": False,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": -1,
            "pytest_timeout": True,
        }
    except (FileNotFoundError, OSError) as exc:
        logger.warning("Pytest subprocess failed to start in %s: %s", workspace_dir, exc)
        return {
            "passed": 0,
            "total": 0,
            "tests_pct": 0.0,
            "has_tests": False,
            "stdout": "",
            "stderr": str(exc),
            "exit_code": -1,
            "pytest_unavailable": True,
        }

    passed, total = _parse_summary(result.stdout)

    has_tests = total > 0
    tests_pct = round((passed / total * 100.0) if total > 0 else 0.0, 6)

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
