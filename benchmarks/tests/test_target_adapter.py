"""Unit tests for the benchmark target adapter and registry."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from benchmarks.eval.target_adapter import BenchmarkTarget
from benchmarks.eval.target_registry import load_targets


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def targets_file(tmp_path: Path) -> Path:
    path = tmp_path / "targets.yaml"
    path.write_text(
        """
targets:
  - id: echo-cli
    type: cli
    command: ["python", "-c", "import sys; open(sys.argv[sys.argv.index('--output')+1], 'w').write(open(sys.argv[sys.argv.index('--prompt')+1]).read())"]
    timeout: 10

  - id: api-stub
    type: api
    provider: openai
    model: gpt-4o

  - id: http-stub
    type: http
    url: http://localhost:8080/v1/judge
""",
        encoding="utf-8",
    )
    return path


def test_load_targets_valid_registry(targets_file: Path) -> None:
    targets = load_targets(targets_file)
    assert set(targets.keys()) == {"echo-cli", "api-stub", "http-stub"}
    assert targets["echo-cli"].type == "cli"
    assert targets["api-stub"].type == "api"
    assert targets["http-stub"].type == "http"


def test_load_targets_duplicate_id_raises(temp_dir: Path) -> None:
    path = temp_dir / "targets.yaml"
    path.write_text(
        """
targets:
  - id: same
    type: cli
    command: ["echo"]
  - id: same
    type: cli
    command: ["echo"]
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate target id"):
        load_targets(path)


def test_api_stub_raises_not_implemented(targets_file: Path) -> None:
    targets = load_targets(targets_file)
    target = targets["api-stub"]
    with pytest.raises(NotImplementedError, match="API adapter not implemented"):
        target.invoke(Path("p"), Path("w"), Path("o"), 1)


def test_http_stub_raises_not_implemented(targets_file: Path) -> None:
    targets = load_targets(targets_file)
    target = targets["http-stub"]
    with pytest.raises(NotImplementedError, match="HTTP adapter not implemented"):
        target.invoke(Path("p"), Path("w"), Path("o"), 1)


def test_cli_invocation_reads_output_file(temp_dir: Path) -> None:
    prompt = temp_dir / "prompt.md"
    prompt.write_text("hello world", encoding="utf-8")
    output = temp_dir / "output.md"
    workspace = temp_dir / "workspace"
    workspace.mkdir()

    target = BenchmarkTarget(
        target_id="echo",
        target_type="cli",
        command=[
            "python",
            "-c",
            "import sys; "
            "out = sys.argv[sys.argv.index('--output')+1]; "
            "prompt = sys.argv[sys.argv.index('--prompt')+1]; "
            "open(out, 'w').write(open(prompt).read())",
        ],
    )
    result = target.invoke(prompt, workspace, output, 10)
    assert result.status == "PASS"
    assert result.output_content == "hello world"
    assert result.timed_out is False


def test_cli_falls_back_to_stdout(temp_dir: Path) -> None:
    prompt = temp_dir / "prompt.md"
    prompt.write_text("stdout content", encoding="utf-8")
    output = temp_dir / "output.md"
    workspace = temp_dir / "workspace"
    workspace.mkdir()

    target = BenchmarkTarget(
        target_id="stdout-only",
        target_type="cli",
        command=["python", "-c", "import sys; print(open(sys.argv[sys.argv.index('--prompt')+1]).read())"],
    )
    result = target.invoke(prompt, workspace, output, 10)
    assert result.status == "PASS"
    assert result.output_content.strip() == "stdout content"


def test_cli_no_output_status(temp_dir: Path) -> None:
    prompt = temp_dir / "prompt.md"
    prompt.write_text("irrelevant", encoding="utf-8")
    output = temp_dir / "output.md"
    workspace = temp_dir / "workspace"
    workspace.mkdir()

    target = BenchmarkTarget(
        target_id="silent",
        target_type="cli",
        command=["python", "-c", "pass"],
    )
    result = target.invoke(prompt, workspace, output, 10)
    assert result.status == "NO_OUTPUT"
    assert result.output_content == ""


def test_cli_timeout_kills_process(temp_dir: Path) -> None:
    prompt = temp_dir / "prompt.md"
    prompt.write_text("sleep", encoding="utf-8")
    output = temp_dir / "output.md"
    workspace = temp_dir / "workspace"
    workspace.mkdir()

    target = BenchmarkTarget(
        target_id="sleeper",
        target_type="cli",
        command=["python", "-c", "import time; time.sleep(30)"],
    )
    start = time.time()
    result = target.invoke(prompt, workspace, output, 1)
    elapsed = time.time() - start
    assert result.status == "TIMEOUT"
    assert result.timed_out is True
    assert elapsed < 5


def test_cli_stdin_is_closed(temp_dir: Path) -> None:
    prompt = temp_dir / "prompt.md"
    prompt.write_text("input", encoding="utf-8")
    output = temp_dir / "output.md"
    workspace = temp_dir / "workspace"
    workspace.mkdir()

    target = BenchmarkTarget(
        target_id="stdin-reader",
        target_type="cli",
        command=[
            "python",
            "-c",
            "import sys; data = sys.stdin.read(); open(sys.argv[sys.argv.index('--output')+1], 'w').write(repr(data))",
        ],
    )
    result = target.invoke(prompt, workspace, output, 5)
    assert result.status == "PASS"
    # stdin is DEVNULL, so read() returns empty string.
    assert result.output_content == "''"


def test_cli_non_zero_exit_with_stdout_is_error(temp_dir: Path) -> None:
    prompt = temp_dir / "prompt.md"
    prompt.write_text("input", encoding="utf-8")
    output = temp_dir / "output.md"
    workspace = temp_dir / "workspace"
    workspace.mkdir()

    target = BenchmarkTarget(
        target_id="error-with-stdout",
        target_type="cli",
        command=["python", "-c", "import sys; print('I crashed'); sys.exit(1)"],
    )
    result = target.invoke(prompt, workspace, output, 5)
    assert result.status == "ERROR"
    assert result.exit_code == 1
    assert result.output_content == "I crashed\n"


def test_cli_zero_exit_no_output_is_no_output(temp_dir: Path) -> None:
    prompt = temp_dir / "prompt.md"
    prompt.write_text("input", encoding="utf-8")
    output = temp_dir / "output.md"
    workspace = temp_dir / "workspace"
    workspace.mkdir()

    target = BenchmarkTarget(
        target_id="silent",
        target_type="cli",
        command=["python", "-c", "pass"],
    )
    result = target.invoke(prompt, workspace, output, 5)
    assert result.status == "NO_OUTPUT"
    assert result.output_content == ""


def test_cli_invalid_utf8_output_file_decoded_with_replace(temp_dir: Path) -> None:
    prompt = temp_dir / "prompt.md"
    prompt.write_text("input", encoding="utf-8")
    output = temp_dir / "output.md"
    workspace = temp_dir / "workspace"
    workspace.mkdir()

    # Write invalid UTF-8 bytes directly to the output file.
    output.write_bytes(b"\xff\xfe\x00hello")

    target = BenchmarkTarget(
        target_id="invalid-utf8",
        target_type="cli",
        command=["python", "-c", "pass"],
    )
    result = target.invoke(prompt, workspace, output, 5)
    assert result.status == "PASS"
    assert "hello" in result.output_content
    assert "\ufffd" in result.output_content


def test_cli_output_path_is_directory_falls_back_to_stdout(temp_dir: Path) -> None:
    prompt = temp_dir / "prompt.md"
    prompt.write_text("input", encoding="utf-8")
    output = temp_dir / "output_dir"
    output.mkdir()
    workspace = temp_dir / "workspace"
    workspace.mkdir()

    target = BenchmarkTarget(
        target_id="dir-output",
        target_type="cli",
        command=["python", "-c", "print('fallback stdout')"],
    )
    result = target.invoke(prompt, workspace, output, 5)
    assert result.status == "PASS"
    assert result.output_content.strip() == "fallback stdout"


def test_load_targets_scalar_string_command_raises(tmp_path: Path) -> None:
    path = tmp_path / "targets.yaml"
    path.write_text(
        """
targets:
  - id: bad
    type: cli
    command: echo hi
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="list of strings"):
        load_targets(path)


def test_load_targets_command_with_non_string_element_raises(tmp_path: Path) -> None:
    path = tmp_path / "targets.yaml"
    path.write_text(
        """
targets:
  - id: bad
    type: cli
    command: ["echo", 123]
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="list of strings"):
        load_targets(path)


def test_load_targets_non_numeric_timeout_raises(tmp_path: Path) -> None:
    path = tmp_path / "targets.yaml"
    path.write_text(
        """
targets:
  - id: bad
    type: cli
    command: ["echo", "hi"]
    timeout: "60s"
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="positive integer"):
        load_targets(path)


def test_load_targets_yaml_root_list_raises(tmp_path: Path) -> None:
    path = tmp_path / "targets.yaml"
    path.write_text(
        """
- targets:
    - id: bad
      type: cli
      command: ["echo", "hi"]
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="mapping at the top level"):
        load_targets(path)
