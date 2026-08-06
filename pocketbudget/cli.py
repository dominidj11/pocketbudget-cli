"""CLI: user input and command routing."""

import sys
from collections.abc import Callable

from pocketbudget.account import VALID_CATEGORIES, Account
from pocketbudget.exceptions import PocketBudgetError
from pocketbudget.storage import load_account, save_account

EXPECTED_ARGS: dict[str, int] = {
    "add-income": 2,
    "add-expense": 2,
    "show-balance": 0,
    "show-history": 0,
    "set-budget": 2,
    "show-summary": 0,
}


def main(argv: list[str]) -> int:
    """Run the PocketBudget CLI."""
    if not argv:
        print("Hello PocketBudget")
        return 0

    command = argv[0]
    handler = HANDLERS.get(command)
    if handler is None:
        print(f"Unknown command: {command}", file=sys.stderr)
        return 1

    try:
        _check_arity(command, argv[1:])
        account = load_account()
        handler(account, argv[1:])
        save_account(account)
    except (PocketBudgetError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


def _check_arity(command: str, args: list[str]) -> None:
    expected = EXPECTED_ARGS[command]
    if len(args) != expected:
        raise ValueError(f"{command} expects {expected} argument(s), got {len(args)}")


def _parse_amount(raw: str) -> float:
    try:
        return float(raw)
    except ValueError:
        raise ValueError(f"Invalid amount: {raw!r}") from None


def _parse_category(raw: str) -> str:
    if raw not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category {raw!r}; valid: {sorted(VALID_CATEGORIES)}")
    return raw


def _add_income(account: Account, args: list[str]) -> None:
    amount = _parse_amount(args[0])
    category = _parse_category(args[1])
    account.add_income(amount)
    print(f"Added ${amount:.2f} income ({category}).")


def _add_expense(account: Account, args: list[str]) -> None:
    amount = _parse_amount(args[0])
    category = _parse_category(args[1])
    warning = account.add_expense(amount, category)
    print(f"Recorded ${amount:.2f} expense ({category}).")
    if warning:
        print(f"Warning: {warning}")


def _show_balance(account: Account, args: list[str]) -> None:
    print(f"Balance: ${account.balance:.2f}")


def _show_history(account: Account, args: list[str]) -> None:
    for kind, amount in account.history:
        print(f"{kind}: ${amount:.2f}")


def _set_budget(account: Account, args: list[str]) -> None:
    category = _parse_category(args[0])
    limit = _parse_amount(args[1])
    account.set_budget(category, limit)
    print(f"Budget set for {category}: ${limit:.2f}")


def _show_summary(account: Account, args: list[str]) -> None:
    for category in sorted(account.budgets):
        limit = account.budgets[category]
        spent = account.category_spending.get(category, 0.0)
        print(f"{category}: spent ${spent:.2f} of ${limit:.2f}")


HANDLERS: dict[str, Callable[[Account, list[str]], None]] = {
    "add-income": _add_income,
    "add-expense": _add_expense,
    "show-balance": _show_balance,
    "show-history": _show_history,
    "set-budget": _set_budget,
    "show-summary": _show_summary,
}


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
