#!/usr/bin/env python3
"""Mock benchmark target that outputs the reference solution for a task.

This target is used only for end-to-end verification. It derives the task
directory from the --prompt argument, reads the expected solution, and writes
it to the --output file.
"""

import json
import sys
from pathlib import Path


def _arg_value(flag: str) -> str:
    idx = sys.argv.index(flag)
    if idx + 1 >= len(sys.argv):
        raise ValueError(f"Missing value for {flag}")
    return sys.argv[idx + 1]


def main() -> int:
    prompt_path = Path(_arg_value("--prompt"))
    output_path = Path(_arg_value("--output"))
    task_dir = prompt_path.parent

    rubric_path = task_dir / "rubric.json"
    target_file = "src/module.py"
    if rubric_path.exists():
        rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
        target_file = rubric.get("target_file", target_file)

    expected_path = task_dir / "expected" / target_file
    if not expected_path.exists():
        print(f"Reference solution not found: {expected_path}", file=sys.stderr)
        return 1

    solution = expected_path.read_text(encoding="utf-8")
    output_path.write_text(solution, encoding="utf-8")
    print(f"Wrote reference solution for {task_dir.name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
