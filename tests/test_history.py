from pocketbudget.account import Account


def test_history_records_transactions() -> None:
    account = Account()
    account.add_income(100)
    account.add_expense(30)
    assert account.history == [("income", 100.0), ("expense", 30.0)]


def test_mutating_returned_history_does_not_change_account() -> None:
    account = Account()
    account.add_income(100)
    account.add_expense(30)

    history = account.history
    history.append(("expense", 999.0))
    history[0] = ("income", 9999.0)

    assert account.history == [("income", 100.0), ("expense", 30.0)]
