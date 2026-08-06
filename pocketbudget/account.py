"""Domain: budgeting rules and protected account state."""

from pocketbudget.exceptions import InsufficientFundsError


class Account:
    """Protected account balance with validated transactions."""

    def __init__(self) -> None:
        self._balance = 0.0
        self._history: list[tuple[str, float]] = []

    @property
    def balance(self) -> float:
        """Current account balance."""
        return self._balance

    @property
    def history(self) -> list[tuple[str, float]]:
        """Read-only view of the transaction history."""
        return list(self._history)

    def add_income(self, amount: float) -> None:
        """Add income to the balance after validating the amount."""
        self._validate_amount(amount)
        self._balance += amount
        self._history.append(("income", amount))

    def add_expense(self, amount: float) -> None:
        """Record an expense after validating the amount and balance."""
        self._validate_amount(amount)
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Expense of {amount:.2f} exceeds available balance of "
                f"{self._balance:.2f}"
            )
        self._balance -= amount
        self._history.append(("expense", amount))

    @staticmethod
    def _validate_amount(amount: float) -> None:
        if amount <= 0:
            raise ValueError(f"Transaction amount must be positive, got {amount}")
