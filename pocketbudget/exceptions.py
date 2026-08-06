"""Custom domain exceptions."""


class PocketBudgetError(Exception):
    """Base class for all PocketBudget domain errors."""


class InsufficientFundsError(PocketBudgetError):
    """Raised when an expense exceeds the available balance."""


class StorageError(PocketBudgetError):
    """Raised when a save file cannot be read or validated."""
