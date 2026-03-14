"""Custom exceptions for quantum-money."""


class QuantumMoneyError(Exception):
    """Base exception for quantum-money."""


class NotObservedError(QuantumMoneyError):
    """Raised when .to_decimal() is called on an unevaluated expression tree."""


class InvalidOperationError(QuantumMoneyError):
    """Raised when an unsupported operation is attempted (e.g., QMoney * QMoney)."""
