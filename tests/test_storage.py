import json
from pathlib import Path

import pytest

from pocketbudget.account import Account
from pocketbudget.exceptions import StorageError
from pocketbudget.storage import load_account, save_account


def test_save_writes_balance_and_history_to_file(tmp_path: Path) -> None:
    account = Account()
    account.add_income(100)
    account.add_expense(30)

    path = tmp_path / "budget.json"
    save_account(account, path)

    assert path.exists()
    data = json.loads(path.read_text())
    assert data["balance"] == 70
    assert data["history"] == [["income", 100.0], ["expense", 30.0]]


def test_save_creates_data_directory(tmp_path: Path) -> None:
    account = Account()
    account.add_income(50)

    path = tmp_path / "data" / "budget.json"
    save_account(account, path)

    assert path.exists()


def test_load_rebuilds_account_from_file(tmp_path: Path) -> None:
    account = Account()
    account.add_income(100)
    account.add_expense(30)
    path = tmp_path / "budget.json"
    save_account(account, path)

    loaded = load_account(path)

    assert loaded.balance == 70
    assert loaded.history == [("income", 100.0), ("expense", 30.0)]


def test_load_missing_file_returns_empty_account(tmp_path: Path) -> None:
    loaded = load_account(tmp_path / "does-not-exist.json")

    assert loaded.balance == 0
    assert loaded.history == []


def test_load_corrupted_file_raises_storage_error(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text("{ not valid json !!!")

    with pytest.raises(StorageError):
        load_account(path)


def test_load_invalid_structure_raises_storage_error(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text(json.dumps([1, 2, 3]))

    with pytest.raises(StorageError):
        load_account(path)


def test_load_invalid_transaction_raises_storage_error(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text(json.dumps({"balance": 70.0, "history": [["expense", -30.0]]}))

    with pytest.raises(StorageError):
        load_account(path)


def test_load_balance_mismatch_raises_storage_error(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text(json.dumps({"balance": 999.0, "history": [["income", 100.0]]}))

    with pytest.raises(StorageError):
        load_account(path)
