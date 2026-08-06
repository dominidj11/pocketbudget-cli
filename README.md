# PocketBudget

A command-line budget tracker that records income and expenses by category, enforces per-category spending limits, and persists all state to a local JSON file. It keeps the account balance safe from direct outside mutation and validates every transaction before it touches any state.

## Installation & Setup

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install the quality gates as a git hook:

```bash
pre-commit install
```

Pre-commit runs `ruff` (lint, format, cyclomatic complexity ≤ 7), `mypy --strict`, and `pytest` on every commit.

## Usage

Run the CLI from the project root. State is stored in `data/budget.json`.

```bash
# Record a deposit
python -m pocketbudget.cli add-income 200 Other

# Set a spending ceiling for a category
python -m pocketbudget.cli set-budget Food 100

# Record an expense (checked against funds and the category budget)
python -m pocketbudget.cli add-expense 30 Food

# Show the current balance
python -m pocketbudget.cli show-balance

# List every executed transaction
python -m pocketbudget.cli show-history

# Show spending per category against its budget
python -m pocketbudget.cli show-summary
```

Commands and their arguments:

| Command                     | Arguments             | Purpose                                        |
| --------------------------- | --------------------- | ---------------------------------------------- |
| `add-income <amount> <category>`  | amount, category | Record a deposit                                |
| `add-expense <amount> <category>` | amount, category | Record an expense, validated against budget     |
| `show-balance`              | —                     | Print the current balance                       |
| `show-history`              | —                     | List all executed transactions                  |
| `set-budget <category> <limit>`   | category, limit | Set a ceiling for a spending category           |
| `show-summary`              | —                     | Visualize spending against established budgets  |

Allowed categories: `Food`, `Transport`, `Utilities`, `Entertainment`, `Other`. An invalid category is rejected and nothing is recorded.

Every command follows the same lifecycle: load the saved state → run the domain operation → save the result.

## Running the Tests

```bash
pytest
```

All tests are written first as the spec for each feature (TDD) and live in `tests/`. A passing run looks like:

```
46 passed in 0.26s
```

## Design Decisions

The balance is the single source of truth for how much money the account holds, and it is protected:

- `Account.balance` is a read-only property with no setter, backed by a private `_balance`. `account.balance = 500` raises `AttributeError`; the only way money moves is through `add_income()` and `add_expense()`.
- `Account.history` returns a fresh list copy each time, and each entry is an immutable tuple. Mutating the returned list can never alter the account's internal transaction log.
- Every transaction is validated **before** any state changes. Non-positive amounts raise `InvalidTransactionError`, unknown categories raise `InvalidCategoryError`, overdrawing raises `InsufficientFundsError`, and an expense past a *strict* budget raises `BudgetExceededError` — in all cases the balance, history, and category spending are left untouched.
- Budgets are soft by default (an over-budget expense is recorded with a warning, per the domain rules), but can be set strict via `set_budget(category, limit, strict=True)` to block over-budget spending outright.
- Persistence is defensive: the app saves the balance, history, budgets, strict flags, and per-category spending to `data/budget.json`. On load, history is replayed through the same validated entry points the live app uses, and the saved balance must match the replayed history sum; a missing file yields a fresh empty account, while malformed or inconsistent files raise `StorageError` rather than crashing or silently producing a wrong balance.

The authoritative domain rules live in `rules.md`; each rule maps to at least one test.
