"""Target adapter contract and CLI adapter implementation."""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class InvocationResult:
    """Result of invoking a benchmark target against a single task."""

    exit_code: int
    stdout: str
    stderr: str
    output_content: str
    status: str  # PASS, TIMEOUT, NO_OUTPUT, ERROR
    timed_out: bool


class BenchmarkTarget:
    """A system under evaluation (raw model, agent flow, pipeline, etc.)."""

    def __init__(
        self,
        target_id: str,
        target_type: str,
        command: list[str],
        timeout: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.id = target_id
        self.type = target_type
        self.command = list(command)
        self.timeout = timeout
        self.metadata = metadata or {}

    def invoke(
        self,
        prompt_path: Path,
        workspace_dir: Path,
        output_path: Path,
        timeout: int,
    ) -> InvocationResult:
        """Invoke the target with the benchmark contract.

        Contract appended to the configured command:
            --prompt <prompt-file>
            --workspace <workspace-dir>
            --output <output-file>
            --no-interactive

        stdin is closed (DEVNULL) to enforce no-interaction. The process is
        killed if it exceeds ``timeout`` seconds.
        """
        if self.type == "cli":
            return self._invoke_cli(prompt_path, workspace_dir, output_path, timeout)
        if self.type == "api":
            raise NotImplementedError("API adapter not implemented in Phase 1")
        if self.type == "http":
            raise NotImplementedError("HTTP adapter not implemented in Phase 1")
        raise ValueError(f"Unknown target type: {self.type}")

    def _invoke_cli(
        self,
        prompt_path: Path,
        workspace_dir: Path,
        output_path: Path,
        timeout: int,
    ) -> InvocationResult:
        cmd = self.command + [
            "--prompt",
            str(prompt_path),
            "--workspace",
            str(workspace_dir),
            "--output",
            str(output_path),
            "--no-interactive",
        ]

        logger.info("Invoking target '%s': %s", self.id, " ".join(cmd))

        with subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        ) as proc:
            try:
                stdout, stderr = proc.communicate(timeout=timeout)
                output_content, status = self._read_output(output_path, stdout)
                return InvocationResult(
                    exit_code=proc.returncode,
                    stdout=stdout,
                    stderr=stderr,
                    output_content=output_content,
                    status=status,
                    timed_out=False,
                )
            except subprocess.TimeoutExpired:
                logger.warning("Target '%s' timed out after %ss", self.id, timeout)
                proc.kill()
                try:
                    stdout, stderr = proc.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    stdout, stderr = "", ""

                if stdout is None:
                    stdout = ""
                if stderr is None:
                    stderr = ""
                if isinstance(stdout, bytes):
                    stdout = stdout.decode("utf-8", errors="replace")
                if isinstance(stderr, bytes):
                    stderr = stderr.decode("utf-8", errors="replace")

                output_content, _ = self._read_output(output_path, stdout)
                return InvocationResult(
                    exit_code=-1,
                    stdout=stdout,
                    stderr=stderr,
                    output_content=output_content,
                    status="TIMEOUT",
                    timed_out=True,
                )

    def _read_output(self, output_path: Path, stdout: str) -> tuple[str, str]:
        """Read the target's output file, falling back to stdout."""
        if output_path.exists():
            content = output_path.read_text(encoding="utf-8")
            if content.strip():
                return content, "PASS"

        if stdout.strip():
            logger.warning(
                "Target '%s' did not write non-empty output file '%s'; falling back to stdout",
                self.id,
                output_path,
            )
            return stdout, "PASS"

        logger.warning("Target '%s' produced no output", self.id)
        return "", "NO_OUTPUT"
