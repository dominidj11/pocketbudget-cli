"""Domain: budgeting rules and protected account state."""

from pocketbudget.exceptions import (
    BudgetExceededError,
    InsufficientFundsError,
    InvalidCategoryError,
    InvalidTransactionError,
)

VALID_CATEGORIES = frozenset(
    {"Food", "Transport", "Utilities", "Entertainment", "Other"}
)


class Account:
    """Protected account balance with validated transactions."""

    def __init__(self) -> None:
        self._balance = 0.0
        self._history: list[tuple[str, float]] = []
        self._budgets: dict[str, float] = {}
        self._strict_budgets: dict[str, bool] = {}
        self._category_spending: dict[str, float] = {}

    @property
    def balance(self) -> float:
        """Current account balance."""
        return self._balance

    @property
    def history(self) -> list[tuple[str, float]]:
        """Read-only view of the transaction history."""
        return list(self._history)

    @property
    def budgets(self) -> dict[str, float]:
        """Read-only view of the category budgets."""
        return dict(self._budgets)

    @property
    def strict_budgets(self) -> dict[str, bool]:
        """Read-only view of which categories have strict budgets."""
        return dict(self._strict_budgets)

    @property
    def category_spending(self) -> dict[str, float]:
        """Read-only view of spending per category."""
        return dict(self._category_spending)

    def add_income(self, amount: float) -> None:
        """Add income to the balance after validating the amount."""
        self._validate_amount(amount)
        self._balance += amount
        self._history.append(("income", amount))

    def add_expense(self, amount: float, category: str = "Other") -> str | None:
        """Record an expense after validating the amount, category and balance.

        Returns a budget warning when the expense exceeds the category's
        remaining budget, otherwise None.
        """
        self._validate_amount(amount)
        self._validate_category(category)
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Expense of {amount:.2f} exceeds available balance of "
                f"{self._balance:.2f}"
            )
        if self._strict_budget_exceeded(category, amount):
            raise BudgetExceededError(
                f"Expense of {amount:.2f} exceeds the strict budget for {category}"
            )
        self._balance -= amount
        self._history.append(("expense", amount))
        self._category_spending[category] = (
            self._category_spending.get(category, 0.0) + amount
        )
        return self._budget_warning(category, amount)

    def set_budget(self, category: str, limit: float, strict: bool = False) -> None:
        """Set the spending limit for a category."""
        self._validate_category(category)
        self._validate_amount(limit)
        self._budgets[category] = limit
        self._strict_budgets[category] = strict

    def remaining_budget(self, category: str) -> float | None:
        """Remaining budget for a category, or None if no budget is set."""
        self._validate_category(category)
        limit = self._budgets.get(category)
        if limit is None:
            return None
        spent = self._category_spending.get(category, 0.0)
        return limit - spent

    def restore_spending(self, spending: dict[str, float]) -> None:
        """Restore persisted per-category spending after validation."""
        self._category_spending.clear()
        for category, amount in spending.items():
            self._validate_category(category)
            if amount < 0:
                raise ValueError(f"Spending must be non-negative, got {amount}")
            self._category_spending[category] = amount

    @staticmethod
    def _validate_amount(amount: float) -> None:
        if amount <= 0:
            raise InvalidTransactionError(
                f"Transaction amount must be positive, got {amount}"
            )

    @staticmethod
    def _validate_category(category: str) -> None:
        if category not in VALID_CATEGORIES:
            raise InvalidCategoryError(
                f"Invalid category {category!r}; "
                f"valid categories: {sorted(VALID_CATEGORIES)}"
            )

    def _strict_budget_exceeded(self, category: str, amount: float) -> bool:
        if not self._strict_budgets.get(category, False):
            return False
        remaining = self.remaining_budget(category)
        return remaining is not None and amount > remaining

    def _budget_warning(self, category: str, amount: float) -> str | None:
        remaining = self.remaining_budget(category)
        if remaining is not None and amount > remaining:
            return (
                f"Budget exceeded for {category}: spent {amount:.2f}, "
                f"only {remaining:.2f} left"
            )
        return None
