import pytest

from pocketbudget.account import Account
from pocketbudget.exceptions import InsufficientFundsError


def test_balance_is_readable_from_outside() -> None:
    account = Account()
    assert account.balance == 0


def test_balance_cannot_be_assigned_from_outside() -> None:
    account = Account()
    with pytest.raises(AttributeError):
        setattr(account, "balance", 500)
    assert account.balance == 0


def test_add_income_increases_balance() -> None:
    account = Account()
    account.add_income(100)
    assert account.balance == 100


def test_add_expense_decreases_balance() -> None:
    account = Account()
    account.add_income(100)
    account.add_expense(30)
    assert account.balance == 70


def test_transactions_accumulate() -> None:
    account = Account()
    account.add_income(100)
    account.add_income(50)
    account.add_expense(20)
    account.add_expense(10)
    assert account.balance == 120


def test_negative_income_is_rejected() -> None:
    account = Account()
    with pytest.raises(ValueError):
        account.add_income(-50)
    assert account.balance == 0


def test_negative_expense_is_rejected() -> None:
    account = Account()
    account.add_income(100)
    with pytest.raises(ValueError):
        account.add_expense(-20)
    assert account.balance == 100


def test_zero_amount_is_rejected() -> None:
    account = Account()
    with pytest.raises(ValueError):
        account.add_income(0)
    with pytest.raises(ValueError):
        account.add_expense(0)
    assert account.balance == 0


def test_expense_larger_than_balance_is_blocked() -> None:
    account = Account()
    account.add_income(50)
    with pytest.raises(InsufficientFundsError):
        account.add_expense(100)
    assert account.balance == 50


def test_expense_equal_to_balance_is_allowed() -> None:
    account = Account()
    account.add_income(50)
    account.add_expense(50)
    assert account.balance == 0
