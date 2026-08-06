from pathlib import Path

import pytest

from pocketbudget.cli import main
from pocketbudget.storage import load_account


def _run(
    argv: list[str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> tuple[int, str, str]:
    monkeypatch.chdir(tmp_path)
    code = main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_add_income_records_deposit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    code, out, _ = _run(["add-income", "100", "Food"], tmp_path, monkeypatch, capsys)

    assert code == 0
    assert "100.00" in out
    assert load_account().balance == 100


def test_add_expense_records_expense_and_persists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(["add-income", "200", "Other"], tmp_path, monkeypatch, capsys)
    code, out, _ = _run(["add-expense", "30", "Food"], tmp_path, monkeypatch, capsys)

    assert code == 0
    assert "30.00" in out
    assert load_account().balance == 170


def test_show_balance_prints_saved_balance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(["add-income", "100", "Other"], tmp_path, monkeypatch, capsys)

    code, out, _ = _run(["show-balance"], tmp_path, monkeypatch, capsys)

    assert code == 0
    assert "100.00" in out


def test_show_history_lists_all_transactions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(["add-income", "100", "Food"], tmp_path, monkeypatch, capsys)
    _run(["add-expense", "30", "Food"], tmp_path, monkeypatch, capsys)

    code, out, _ = _run(["show-history"], tmp_path, monkeypatch, capsys)

    assert code == 0
    assert "100.00" in out
    assert "30.00" in out


def test_set_budget_persists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    code, out, _ = _run(["set-budget", "Food", "100"], tmp_path, monkeypatch, capsys)

    assert code == 0
    assert "100.00" in out
    assert load_account().budgets["Food"] == 100


def test_show_summary_visualizes_spending_against_budgets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(["add-income", "200", "Other"], tmp_path, monkeypatch, capsys)
    _run(["set-budget", "Food", "100"], tmp_path, monkeypatch, capsys)
    _run(["add-expense", "30", "Food"], tmp_path, monkeypatch, capsys)

    code, out, _ = _run(["show-summary"], tmp_path, monkeypatch, capsys)

    assert code == 0
    assert "Food" in out
    assert "30.00" in out
    assert "100.00" in out


def test_expense_overdraw_prints_error_and_keeps_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(["add-income", "50", "Other"], tmp_path, monkeypatch, capsys)

    code, _, err = _run(["add-expense", "100", "Food"], tmp_path, monkeypatch, capsys)

    assert code != 0
    assert err
    assert load_account().balance == 50


def test_invalid_category_prints_error_and_keeps_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(["add-income", "50", "Other"], tmp_path, monkeypatch, capsys)

    code, _, err = _run(
        ["add-expense", "10", "Clothing"], tmp_path, monkeypatch, capsys
    )

    assert code != 0
    assert err
    assert load_account().balance == 50


def test_unknown_command_prints_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    code, _, err = _run(["frobnicate"], tmp_path, monkeypatch, capsys)

    assert code != 0
    assert err


def test_corrupted_save_file_prints_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "budget.json").write_text("{ not valid json !!!")

    code, _, err = _run(["show-balance"], tmp_path, monkeypatch, capsys)

    assert code != 0
    assert err
