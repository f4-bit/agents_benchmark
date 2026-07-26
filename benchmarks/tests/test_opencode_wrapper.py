"""Unit tests for the opencode CLI wrapper."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

from benchmarks import opencode_cli_wrapper as wrapper


def test_interactive_patterns_do_not_match_confirm_prose() -> None:
    text = "I can confirm that the fix is applied."
    assert not wrapper._detect_interactive_prompt(text)


def test_interactive_patterns_match_yes_no_prompt() -> None:
    assert wrapper._detect_interactive_prompt("Apply changes? yes/no")
    assert wrapper._detect_interactive_prompt("Apply changes? [y/n]")
    assert wrapper._detect_interactive_prompt("Apply changes? (y/n)")


def test_resolve_target_file_from_rubric(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "src").mkdir()
    (workspace / "src" / "handler.py").write_text("original", encoding="utf-8")
    (workspace / "src" / "solution.py").write_text("newer", encoding="utf-8")

    rubric = tmp_path / "rubric.json"
    rubric.write_text(
        '{"target_file": "src/handler.py"}', encoding="utf-8"
    )

    selected = wrapper._resolve_target_file(workspace, rubric)
    assert selected == workspace / "src" / "handler.py"


def test_extract_markdown_code_block_no_trailing_newline() -> None:
    text = "```python\ncode\n```"
    assert wrapper._extract_markdown_code_block(text) == "code"


def test_run_non_interactive_writes_output_on_detected_prompt(tmp_path: Path) -> None:
    """Even when a prompt is detected in stdout, the edited file is written."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "src").mkdir()
    src_file = workspace / "src" / "handler.py"
    src_file.write_text("before", encoding="utf-8")
    rubric = tmp_path / "rubric.json"
    rubric.write_text('{"target_file": "src/handler.py"}', encoding="utf-8")
    prompt = tmp_path / "prompt.md"
    prompt.write_text("fix it", encoding="utf-8")
    output = tmp_path / "output.txt"

    class FakeProcess:
        def __init__(self):
            self.returncode = 0

        def communicate(self, timeout=None):
            src_file.write_text("after", encoding="utf-8")
            return "Apply changes? yes/no\n", ""

        def kill(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    with mock.patch("subprocess.Popen", return_value=FakeProcess()):
        code = wrapper._run_non_interactive(
            "opencode",
            {
                "prompt": str(prompt),
                "workspace": str(workspace),
                "output": str(output),
            },
            [],
        )

    assert code == 1
    assert output.read_text(encoding="utf-8") == "after"


def test_run_non_interactive_includes_dir_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "src").mkdir()
    src_file = workspace / "src" / "handler.py"
    src_file.write_text("before", encoding="utf-8")
    rubric = tmp_path / "rubric.json"
    rubric.write_text('{"target_file": "src/handler.py"}', encoding="utf-8")
    prompt = tmp_path / "prompt.md"
    prompt.write_text("fix it", encoding="utf-8")
    output = tmp_path / "output.txt"

    with mock.patch.object(
        wrapper,
        "_find_opencode_binary",
        return_value=sys.executable,
    ):
        # Capture the command passed to subprocess.Popen.
        popen_calls = []
        original_popen = subprocess.Popen

        def tracking_popen(cmd, **kwargs):
            popen_calls.append((cmd, kwargs))
            # Create a real subprocess that just writes the file.
            script = (
                f"from pathlib import Path; "
                f"Path('{src_file.as_posix()}').write_text('after', encoding='utf-8')"
            )
            return original_popen([sys.executable, "-c", script], **kwargs)

        with mock.patch("subprocess.Popen", side_effect=tracking_popen):
            wrapper._run_non_interactive(
                sys.executable,
                {
                    "prompt": str(prompt),
                    "workspace": str(workspace),
                    "output": str(output),
                },
                [],
            )

    assert popen_calls
    cmd, _ = popen_calls[0]
    assert "--dir" in cmd
    assert str(workspace) in cmd


def test_prompt_bom_stripped(tmp_path: Path) -> None:
    prompt = tmp_path / "prompt.md"
    prompt.write_bytes(b"\xef\xbb\xbffix it")
    text = prompt.read_text(encoding="utf-8-sig")
    assert text == "fix it"
    assert not text.startswith("\ufeff")
