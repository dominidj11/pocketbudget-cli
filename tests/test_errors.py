from pathlib import Path

import pytest

from pocketbudget.account import Account
from pocketbudget.exceptions import (
    BudgetExceededError,
    InvalidCategoryError,
    InvalidTransactionError,
    StorageError,
)
from pocketbudget.storage import load_account


def test_negative_income_raises_invalid_transaction_error() -> None:
    account = Account()

    with pytest.raises(InvalidTransactionError):
        account.add_income(-50)

    assert account.balance == 0
    assert account.history == []


def test_negative_expense_raises_invalid_transaction_error() -> None:
    account = Account()
    account.add_income(100)

    with pytest.raises(InvalidTransactionError):
        account.add_expense(-20, "Food")

    assert account.balance == 100
    assert account.history == [("income", 100.0)]


def test_invalid_category_raises_invalid_category_error() -> None:
    account = Account()
    account.add_income(100)

    with pytest.raises(InvalidCategoryError):
        account.add_expense(10, "Clothing")

    assert account.balance == 100
    assert account.history == [("income", 100.0)]


def test_expense_over_strict_budget_raises_budget_exceeded_error() -> None:
    account = Account()
    account.add_income(100)
    account.set_budget("Food", 50, strict=True)

    with pytest.raises(BudgetExceededError):
        account.add_expense(60, "Food")

    assert account.balance == 100
    assert account.history == [("income", 100.0)]
    assert account.category_spending == {}


def test_soft_budget_still_records_with_warning() -> None:
    account = Account()
    account.add_income(100)
    account.set_budget("Food", 50)

    result = account.add_expense(60, "Food")

    assert result is not None
    assert account.balance == 40


def test_corrupted_data_file_raises_storage_error(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text("{ not valid json !!!")

    with pytest.raises(StorageError):
        load_account(path)
