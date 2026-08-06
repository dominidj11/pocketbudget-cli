import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_entry_point() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pocketbudget.cli"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Hello PocketBudget" in result.stdout
