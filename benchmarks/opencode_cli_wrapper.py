#!/usr/bin/env python3
"""opencode CLI wrapper that adds ``--no-interactive`` / ``-n`` support.

The distributed ``opencode`` binary is a compiled executable, so its argument
parser cannot be modified directly. This wrapper provides the same flag surface:

* ``--no-interactive`` / ``-n`` suppresses all interactive prompts.
* When the flag is present, stdin is closed, stdout/stderr are monitored for
  interactive prompts, and the process is killed if one is detected.
* Without the flag, arguments are passed through unchanged.

The wrapper also honours the ``OPENCODE_NON_INTERACTIVE=1`` environment
variable as an alias for the flag.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# Patterns that indicate an interactive prompt in opencode output.
INTERACTIVE_PROMPT_PATTERNS = [
    re.compile(r"apply\s+this\s+change\?", re.IGNORECASE),
    re.compile(r"continue\?", re.IGNORECASE),
    re.compile(r"confirm", re.IGNORECASE),
    re.compile(r"\?\s*\[Y/n\]", re.IGNORECASE),
    re.compile(r"\?\s*\(y/N\)", re.IGNORECASE),
    re.compile(r"\(yes/no\)", re.IGNORECASE),
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


def _strip_no_interactive(args: list[str]) -> tuple[list[str], bool]:
    """Remove --no-interactive / -n from args and return the flag state."""
    env_flag = os.environ.get("OPENCODE_NON_INTERACTIVE", "") == "1"
    result = []
    flag = env_flag
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("--no-interactive", "-n"):
            flag = True
            i += 1
            continue
        result.append(arg)
        i += 1
    return result, flag


def _detect_interactive_prompt(text: str) -> bool:
    """Return True if the output contains an interactive prompt."""
    return any(pattern.search(text) for pattern in INTERACTIVE_PROMPT_PATTERNS)


def _run_interactive(binary: str, args: list[str]) -> int:
    """Pass through to opencode without non-interactive enforcement."""
    return subprocess.call([binary, *args])


def _run_non_interactive(binary: str, args: list[str]) -> int:
    """Run opencode with closed stdin and prompt detection."""
    process = subprocess.Popen(
        [binary, *args],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    captured = []
    if process.stdout is not None:
        for line in process.stdout:
            captured.append(line)
            sys.stdout.write(line)
            sys.stdout.flush()
            if _detect_interactive_prompt(line):
                process.kill()
                process.wait()
                sys.stderr.write(
                    "user input requested in non-interactive mode\n"
                )
                return 1

    return_code = process.wait()
    return return_code


def main() -> int:
    args, non_interactive = _strip_no_interactive(sys.argv[1:])
    binary = _find_opencode_binary()

    if non_interactive:
        return _run_non_interactive(binary, args)
    return _run_interactive(binary, args)


if __name__ == "__main__":
    sys.exit(main())
