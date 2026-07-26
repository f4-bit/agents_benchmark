#!/usr/bin/env python3
"""opencode CLI wrapper that translates the benchmark contract to ``opencode run``.

The distributed ``opencode`` binary is a compiled executable. Its ``run``
subcommand accepts a message and an ``--auto`` flag, but the benchmark runner
speaks a different contract: ``--prompt <file> --workspace <dir>
--output <file> --no-interactive``. This wrapper translates between the two.

When the non-interactive flag is present:

* Read the benchmark prompt, workspace, and output path.
* Locate the target file inside ``<workspace>/src/`` (heuristic).
* Invoke ``opencode run <task-message> --auto`` with a clear instruction to
  write the complete fixed source file to the target path.
* Copy the modified target file to the output path.
* Fall back to extracting a markdown code block from stdout if the target file
  was not changed.
* Return opencode's exit code (or 1 on timeout).

Without the flag, arguments are passed through unchanged.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Patterns that indicate an interactive prompt in opencode output.
# Anchored with word boundaries to avoid false positives on ordinary assistant
# prose (e.g., "I can confirm that...").
INTERACTIVE_PROMPT_PATTERNS = [
    re.compile(r"apply\s+changes?\s*\?\s*$", re.IGNORECASE),
    re.compile(r"apply\s+this\s+change\s*\?\s*$", re.IGNORECASE),
    re.compile(r"continue\s*\?\s*$", re.IGNORECASE),
    re.compile(r"\byes/no\b", re.IGNORECASE),
    re.compile(r"\?\s*\[y/n\]", re.IGNORECASE),
    re.compile(r"\?\s*\(y/n\)", re.IGNORECASE),
    re.compile(r"\[y/n\]", re.IGNORECASE),
]


def _find_opencode_binary() -> str:
    """Locate the real opencode executable.

    On Windows ``shutil.which('opencode')`` often returns the ``.cmd`` shim
    rather than the compiled binary. We resolve the binary directly from the
    npm global installation path so we can run it without ``shell=True``.
    """
    binary = shutil.which("opencode")
    if binary and binary.lower().endswith(".exe"):
        return binary

    # Standard npm global installation paths.
    candidates = [
        Path.home() / "AppData" / "Roaming" / "npm" / "node_modules" / "opencode-ai" / "bin" / "opencode.exe",
        Path.home() / ".npm" / "node_modules" / "opencode-ai" / "bin" / "opencode.exe",
        Path("/usr/local/lib/node_modules/opencode-ai/bin/opencode"),
        Path("/usr/lib/node_modules/opencode-ai/bin/opencode"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    if binary:
        # Return the .cmd shim as a last resort; caller will need shell=True.
        return binary

    raise RuntimeError("opencode binary not found on PATH")


def _parse_contract_args(args: list[str]) -> tuple[dict[str, str | None], list[str], bool]:
    """Parse the benchmark contract out of the argument list.

    Returns a mapping of ``prompt``/``workspace``/``output`` values (or
    ``None`` if missing), the remaining pass-through arguments, and the
    non-interactive flag state.
    """
    env_flag = os.environ.get("OPENCODE_NON_INTERACTIVE", "") == "1"
    result = []
    contract: dict[str, str | None] = {"prompt": None, "workspace": None, "output": None}
    flag = env_flag
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("--no-interactive", "-n"):
            flag = True
            i += 1
            continue
        if arg in ("--prompt", "--workspace", "--output") and i + 1 < len(args):
            key = arg.lstrip("-")
            contract[key] = args[i + 1]
            i += 2
            continue
        result.append(arg)
        i += 1
    return contract, result, flag


def _detect_interactive_prompt(text: str) -> bool:
    """Return True if the output contains an interactive prompt."""
    return any(pattern.search(text) for pattern in INTERACTIVE_PROMPT_PATTERNS)


def _resolve_target_file(workspace_dir: Path, rubric_path: Path | None) -> Path | None:
    """Resolve the target file from the rubric or a heuristic.

    The rubric's ``target_file`` is the authoritative source. When no rubric is
    available, fall back to selecting the newest ``.py`` file under ``src/``.
    """
    if rubric_path is not None and rubric_path.exists():
        try:
            rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
            target_file = rubric.get("target_file")
            if target_file:
                candidate = workspace_dir / target_file
                if candidate.exists():
                    return candidate
        except (json.JSONDecodeError, OSError):
            pass
    return _select_target_file_heuristic(workspace_dir)


def _select_target_file_heuristic(workspace_dir: Path) -> Path | None:
    """Pick a target file inside ``workspace_dir/src/`` using a heuristic.

    * If exactly one ``.py`` file exists anywhere under ``src/``, use it.
    * If multiple exist, prefer the most recently modified one. If several
      share the latest mtime, prefer a file directly under ``src/``.
    * If no ``.py`` files exist, return ``None``.
    """
    src_dir = workspace_dir / "src"
    if not src_dir.exists():
        return None

    py_files = sorted(src_dir.rglob("*.py"))
    if not py_files:
        return None

    if len(py_files) == 1:
        return py_files[0]

    # Multiple files: pick the most recently modified one, preferring top-level
    # files when mtimes are equal.
    def sort_key(path: Path) -> tuple[float, int]:
        try:
            mtime = path.stat().st_mtime
        except OSError:
            mtime = 0.0
        top_level = 1 if path.parent == src_dir else 0
        return (-mtime, top_level)

    py_files.sort(key=sort_key)
    return py_files[0]


def _extract_markdown_code_block(text: str) -> str | None:
    """Extract the contents of the first fenced markdown code block."""
    match = re.search(r"```(?:\w+)?\n(.*?)\n?```", text, re.DOTALL)
    if match:
        return match.group(1)
    return None


def _build_task_message(workspace_dir: Path, prompt: str, target_file: Path) -> str:
    """Build a concise instruction message for opencode."""
    return (
        "You are in the workspace "
        f"{workspace_dir.resolve()}.\n\n"
        "Task:\n"
        f"{prompt}\n\n"
        "Edit the file "
        f"{target_file.resolve()} "
        "to implement the required fix. "
        "Write the complete fixed source file to that exact path. "
        "Do not ask questions; do not output explanations."
    )


def _run_interactive(binary: str, args: list[str]) -> int:
    """Pass through to opencode without non-interactive enforcement."""
    return subprocess.call([binary, *args])


def _run_non_interactive(
    binary: str,
    contract: dict[str, str | None],
    pass_through_args: list[str],
) -> int:
    """Translate the benchmark contract and run opencode headlessly."""
    prompt_path = contract["prompt"]
    workspace_path = contract["workspace"]
    output_path = contract["output"]
    if not prompt_path or not workspace_path or not output_path:
        sys.stderr.write(
            "non-interactive mode requires --prompt, --workspace, and --output\n"
        )
        return 1

    prompt_file = Path(prompt_path)
    workspace_dir = Path(workspace_path)
    output_file = Path(output_path)

    if not prompt_file.exists():
        sys.stderr.write(f"prompt file not found: {prompt_path}\n")
        return 1

    if not workspace_dir.exists():
        sys.stderr.write(f"workspace directory not found: {workspace_path}\n")
        return 1

    prompt = prompt_file.read_text(encoding="utf-8-sig")
    rubric_path = prompt_file.parent / "rubric.json"
    target_file = _resolve_target_file(workspace_dir, rubric_path)

    if target_file is None:
        # No Python source to edit; the best we can do is ask opencode to
        # produce the answer and write it directly to the output file.
        message = (
            "Task:\n"
            f"{prompt}\n\n"
            "Write the complete solution. "
            "Do not ask questions; do not output explanations."
        )
        snapshot = None
    else:
        message = _build_task_message(workspace_dir, prompt, target_file)
        try:
            snapshot = target_file.read_text(encoding="utf-8")
        except OSError:
            snapshot = None

    cmd = [
        binary,
        "run",
        message,
        "--auto",
        "--dir",
        str(workspace_dir),
        *pass_through_args,
    ]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    timed_out = False
    detected_prompt = False
    try:
        stdout, _ = process.communicate(timeout=None)
        return_code = process.returncode
    except subprocess.TimeoutExpired:
        # This should normally not fire because the runner kills the wrapper
        # process, but keep it as a safety net.
        process.kill()
        try:
            stdout, _ = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            stdout = ""
        timed_out = True
        return_code = 1

    sys.stdout.write(stdout)
    sys.stdout.flush()

    if _detect_interactive_prompt(stdout):
        detected_prompt = True
        sys.stderr.write("user input requested in non-interactive mode\n")
        return_code = 1

    # Always write the output before returning, even if we detected an
    # interactive prompt or a non-zero exit code. The runner may still inspect the
    # edited file for partial progress.
    output_file.parent.mkdir(parents=True, exist_ok=True)
    written = False
    try:
        if target_file is not None:
            try:
                after_content = target_file.read_text(encoding="utf-8")
            except OSError:
                after_content = ""
            if after_content and (snapshot is None or after_content != snapshot):
                output_file.write_text(after_content, encoding="utf-8")
                written = True

        if not written:
            # Target file was not modified or no Python source was found. Try to
            # extract a code block from stdout.
            code_block = _extract_markdown_code_block(stdout)
            if code_block:
                output_file.write_text(code_block, encoding="utf-8")
            elif stdout.strip():
                output_file.write_text(stdout, encoding="utf-8")
            else:
                output_file.write_text("", encoding="utf-8")
    except OSError as exc:
        sys.stderr.write(f"failed to write output file {output_path}: {exc}\n")
        return_code = 1

    if timed_out or detected_prompt:
        return_code = 1
    return return_code


def main() -> int:
    # Ensure UTF-8-safe output on Windows consoles so progress characters from
    # the opencode binary do not crash the wrapper.
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr is not None and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    args = sys.argv[1:]
    contract, pass_through, non_interactive = _parse_contract_args(args)
    binary = _find_opencode_binary()

    if non_interactive:
        return _run_non_interactive(binary, contract, pass_through)
    return _run_interactive(binary, args)


if __name__ == "__main__":
    sys.exit(main())
