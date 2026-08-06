"""Domain: budgeting rules and protected account state."""

from pocketbudget.exceptions import InsufficientFundsError


class Account:
    """Protected account balance with validated transactions."""

    def __init__(self) -> None:
        self._balance = 0.0

    @property
    def balance(self) -> float:
        """Current account balance."""
        return self._balance

    def add_income(self, amount: float) -> None:
        """Add income to the balance after validating the amount."""
        self._validate_amount(amount)
        self._balance += amount

    def add_expense(self, amount: float) -> None:
        """Record an expense after validating the amount and balance."""
        self._validate_amount(amount)
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Expense of {amount:.2f} exceeds available balance of "
                f"{self._balance:.2f}"
            )
        self._balance -= amount

    @staticmethod
    def _validate_amount(amount: float) -> None:
        if amount <= 0:
            raise ValueError(f"Transaction amount must be positive, got {amount}")
