"""Regression tests for the LOLDLE_HISTORY_DIR override in config.py."""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEGACY_DIR = Path.home() / ".loldle-resolver"


def _run_python(snippet: str, env_value: str | None) -> str:
    """Run a snippet in a fresh subprocess with an explicitly built child env."""
    env = {k: v for k, v in os.environ.items() if k != "LOLDLE_HISTORY_DIR"}
    if env_value is not None:
        env["LOLDLE_HISTORY_DIR"] = env_value
    result = subprocess.run(
        [sys.executable, "-c", snippet],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
    )
    return result.stdout.strip()


def test_history_dir_defaults_to_legacy_path_when_env_absent() -> None:
    out = _run_python("import loldle.config; print(loldle.config.HISTORY_DIR)", None)
    assert out == str(LEGACY_DIR)


def test_history_file_follows_env_override(tmp_path: Path) -> None:
    out = _run_python("import loldle.history; print(loldle.history.HISTORY_FILE)", str(tmp_path))
    assert out == str(tmp_path / "history.json")


def test_history_dir_falls_back_to_legacy_when_env_empty() -> None:
    out = _run_python("import loldle.config; print(loldle.config.HISTORY_DIR)", "")
    assert out == str(LEGACY_DIR)
