"""Storage: saving and loading application state."""

import json
from pathlib import Path
from typing import Any

from pocketbudget.account import Account
from pocketbudget.exceptions import StorageError

DATA_DIR = Path("data")
BUDGET_FILE = DATA_DIR / "budget.json"


def save_account(account: Account, path: Path | str = BUDGET_FILE) -> None:
    """Write the account's state to the given file."""
    data = {
        "balance": account.balance,
        "history": [list(entry) for entry in account.history],
        "budgets": account.budgets,
        "category_spending": account.category_spending,
    }
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(data, indent=2))


def load_account(path: Path | str = BUDGET_FILE) -> Account:
    """Rebuild an Account from the given file, validating everything.

    Returns a fresh, empty Account if the file does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        return Account()

    data = _read_json(file_path)
    balance, history, budgets, spending = _extract_data(data)
    account = _replay_history(history)

    if account.balance != balance:
        raise StorageError(
            f"Saved balance {balance} does not match history sum {account.balance}"
        )

    _restore_state(account, budgets, spending)
    return account


def _read_json(file_path: Path) -> object:
    try:
        return json.loads(file_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise StorageError(f"Cannot read save file {file_path}") from exc


def _extract_data(
    data: object,
) -> tuple[float, list[object], dict[Any, Any], dict[Any, Any]]:
    if not isinstance(data, dict):
        raise StorageError("Save file must contain a JSON object")

    balance = data.get("balance")
    history = data.get("history")
    budgets = data.get("budgets", {})
    spending = data.get("category_spending", {})

    if not isinstance(history, list):
        raise StorageError("Save file history must be a list")
    if not isinstance(balance, (int, float)):
        raise StorageError("Save file balance must be a number")
    if not isinstance(budgets, dict):
        raise StorageError("Save file budgets must be an object")
    if not isinstance(spending, dict):
        raise StorageError("Save file category_spending must be an object")

    return balance, history, budgets, spending


def _replay_history(history: list[object]) -> Account:
    account = Account()
    try:
        for entry in history:
            if not isinstance(entry, list) or len(entry) != 2:
                raise ValueError("malformed transaction entry")
            kind, amount = entry
            if kind == "income":
                account.add_income(amount)
            elif kind == "expense":
                account.add_expense(amount)
            else:
                raise ValueError(f"unknown transaction kind {kind!r}")
    except ValueError as exc:
        raise StorageError(f"Invalid transaction in save file: {exc}") from exc
    return account


def _restore_state(
    account: Account, budgets: dict[Any, Any], spending: dict[Any, Any]
) -> None:
    try:
        for category, limit in budgets.items():
            account.set_budget(category, limit)
        account.restore_spending(spending)
    except (ValueError, TypeError) as exc:
        raise StorageError(f"Invalid budget state in save file: {exc}") from exc
