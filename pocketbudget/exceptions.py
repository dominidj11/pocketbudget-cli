"""Custom domain exceptions."""


class PocketBudgetError(Exception):
    """Base class for all PocketBudget domain errors."""


class InsufficientFundsError(PocketBudgetError):
    """Raised when an expense exceeds the available balance."""


class StorageError(PocketBudgetError):
    """Raised when a save file cannot be read or validated."""


class InvalidTransactionError(PocketBudgetError, ValueError):
    """Raised when a transaction amount is not positive."""


class InvalidCategoryError(PocketBudgetError, ValueError):
    """Raised when a category is not on the allowed list."""


class BudgetExceededError(PocketBudgetError):
    """Raised when an expense exceeds a strict category budget."""
