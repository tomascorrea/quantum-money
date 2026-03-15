"""Money class for high-precision eager financial calculations."""

from __future__ import annotations

import numbers
from decimal import ROUND_HALF_UP, Decimal
from typing import Union

_QUANTIZE_2DP = Decimal("0.01")


class Money:
    """Represents a monetary amount with high internal precision.

    Maintains full precision internally for calculations but provides
    'real money' representation rounded to 2 decimal places for display
    and comparisons.
    """

    __slots__ = ("_amount",)

    def __init__(self, amount: Union[Decimal, str, int, float]) -> None:
        if isinstance(amount, float):
            self._amount = Decimal(str(amount))
        elif isinstance(amount, Decimal):
            self._amount = amount
        else:
            self._amount = Decimal(amount)

    # --- Factory methods ---

    @classmethod
    def zero(cls) -> Money:
        return cls(Decimal(0))

    @classmethod
    def from_cents(cls, cents: int) -> Money:
        return cls(Decimal(cents) / 100)

    # --- Arithmetic: Money +/- Money ---

    def __add__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self._amount + other._amount)

    def __radd__(self, other: object) -> Money:
        if other == 0:
            return self
        if isinstance(other, Money):
            return Money(other._amount + self._amount)
        if isinstance(other, (Decimal, int, float)):
            return Money(Decimal(str(other)) + self._amount)
        return NotImplemented

    def __sub__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self._amount - other._amount)

    def __rsub__(self, other: object) -> Money:
        if isinstance(other, Money):
            return Money(other._amount - self._amount)
        if isinstance(other, (Decimal, int, float)):
            return Money(Decimal(str(other)) - self._amount)
        return NotImplemented

    # --- Arithmetic: Money */÷ scalar ---

    def __mul__(self, factor: object) -> Money:
        if isinstance(factor, Money):
            return NotImplemented
        if isinstance(factor, Decimal):
            return Money(self._amount * factor)
        if isinstance(factor, (int, float)):
            return Money(self._amount * Decimal(str(factor)))
        return NotImplemented

    def __rmul__(self, factor: object) -> Money:
        if isinstance(factor, Money):
            return NotImplemented
        if isinstance(factor, Decimal):
            return Money(self._amount * factor)
        if isinstance(factor, (int, float)):
            return Money(self._amount * Decimal(str(factor)))
        return NotImplemented

    def __truediv__(self, divisor: object) -> Money:
        if isinstance(divisor, Money):
            return NotImplemented
        if isinstance(divisor, Decimal):
            return Money(self._amount / divisor)
        if isinstance(divisor, (int, float)):
            return Money(self._amount / Decimal(str(divisor)))
        return NotImplemented

    # --- Unary operators ---

    def __neg__(self) -> Money:
        return Money(-self._amount)

    def __abs__(self) -> Money:
        return Money(abs(self._amount))

    def __pos__(self) -> Money:
        return self

    # --- Comparisons (at real_amount precision) ---

    def _compare_value(self, other: object) -> Decimal | type(NotImplemented):
        if isinstance(other, Money):
            return other.real_amount
        if isinstance(other, (Decimal, int, float)):
            return Decimal(str(other))
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        value = self._compare_value(other)
        if value is NotImplemented:
            return NotImplemented
        return self.real_amount == value

    def __lt__(self, other: object) -> bool:
        value = self._compare_value(other)
        if value is NotImplemented:
            return NotImplemented
        return self.real_amount < value

    def __le__(self, other: object) -> bool:
        value = self._compare_value(other)
        if value is NotImplemented:
            return NotImplemented
        return self.real_amount <= value

    def __gt__(self, other: object) -> bool:
        value = self._compare_value(other)
        if value is NotImplemented:
            return NotImplemented
        return self.real_amount > value

    def __ge__(self, other: object) -> bool:
        value = self._compare_value(other)
        if value is NotImplemented:
            return NotImplemented
        return self.real_amount >= value

    def __hash__(self) -> int:
        return hash(self.real_amount)

    # --- Properties ---

    @property
    def raw_amount(self) -> Decimal:
        """High-precision internal amount."""
        return self._amount

    @property
    def real_amount(self) -> Decimal:
        """Amount rounded to 2 decimal places (ROUND_HALF_UP)."""
        return self._amount.quantize(_QUANTIZE_2DP, rounding=ROUND_HALF_UP)

    @property
    def cents(self) -> int:
        """Real amount expressed in cents."""
        return int(self.real_amount * 100)

    # --- Conversions ---

    def to_real_money(self) -> Money:
        """Return a new Money rounded to 2 decimal places."""
        return Money(self.real_amount)

    def is_positive(self) -> bool:
        return self._amount > 0

    def is_negative(self) -> bool:
        return self._amount < 0

    def is_zero(self) -> bool:
        return self._amount == 0

    def __float__(self) -> float:
        return float(self._amount)

    def __str__(self) -> str:
        return f"{self.real_amount:,.2f}"

    def __repr__(self) -> str:
        return f"Money({self._amount})"

    def debug_precision(self) -> str:
        """Show both internal and real amounts for debugging."""
        return f"Internal: {self._amount}, Real: {self.real_amount}"


numbers.Real.register(Money)
