import pytest

from pocketbudget.account import Account
from pocketbudget.exceptions import InsufficientFundsError


def test_set_budget_for_category() -> None:
    account = Account()
    account.set_budget("Food", 100)

    assert account.budgets["Food"] == 100


def test_remaining_budget_is_limit_minus_spent() -> None:
    account = Account()
    account.add_income(200)
    account.set_budget("Food", 100)
    account.add_expense(30, "Food")

    assert account.remaining_budget("Food") == 70


def test_remaining_budget_is_none_without_a_budget() -> None:
    account = Account()
    account.add_income(200)
    account.add_expense(30, "Food")

    assert account.remaining_budget("Food") is None


def test_expense_within_budget_returns_no_warning() -> None:
    account = Account()
    account.add_income(200)
    account.set_budget("Food", 100)

    result = account.add_expense(30, "Food")

    assert result is None
    assert account.balance == 170


def test_expense_over_budget_is_recorded_with_warning() -> None:
    account = Account()
    account.add_income(200)
    account.set_budget("Food", 100)

    result = account.add_expense(150, "Food")

    assert result is not None
    assert account.balance == 50
    assert account.history == [("income", 200.0), ("expense", 150.0)]


def test_insufficient_funds_blocks_even_with_budget() -> None:
    account = Account()
    account.add_income(50)
    account.set_budget("Food", 1000)

    with pytest.raises(InsufficientFundsError):
        account.add_expense(100, "Food")

    assert account.balance == 50


def test_invalid_category_is_rejected() -> None:
    account = Account()
    account.add_income(200)

    with pytest.raises(ValueError):
        account.add_expense(10, "Clothing")

    assert account.balance == 200
    assert account.history == [("income", 200.0)]


def test_set_budget_invalid_category_is_rejected() -> None:
    account = Account()

    with pytest.raises(ValueError):
        account.set_budget("Clothing", 100)
