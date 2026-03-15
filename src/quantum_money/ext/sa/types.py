"""SQLAlchemy TypeDecorator for Money."""

from typing import Any

from sqlalchemy import Integer, Numeric
from sqlalchemy.types import TypeDecorator

from quantum_money.money import Money

_VALID_REPRESENTATIONS = ("raw", "real", "cents")


class MoneyType(TypeDecorator):
    """SQLAlchemy column type for :class:`~quantum_money.money.Money`.

    Args:
        precision: Total number of digits for the ``Numeric`` column
            (ignored when *representation* is ``"cents"``).
        scale: Number of fractional digits for the ``Numeric`` column
            (ignored when *representation* is ``"cents"``).
        representation: Controls storage format.
            ``"raw"`` (default) -- ``Numeric`` column storing ``raw_amount``.
            ``"real"`` -- ``Numeric`` column storing ``real_amount``.
            ``"cents"`` -- ``Integer`` column storing cents.
    """

    impl = Numeric
    cache_ok = True

    def __init__(
        self,
        precision: int = 20,
        scale: int = 10,
        representation: str = "raw",
    ) -> None:
        if representation not in _VALID_REPRESENTATIONS:
            raise ValueError(
                f"Invalid representation: '{representation}'. "
                f"Expected one of {_VALID_REPRESENTATIONS}"
            )
        self.representation = representation
        self.precision = precision
        self.scale = scale
        super().__init__()

    def load_dialect_impl(self, dialect: Any) -> Any:
        if self.representation == "cents":
            return dialect.type_descriptor(Integer())
        return dialect.type_descriptor(
            Numeric(precision=self.precision, scale=self.scale)
        )

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, Money):
            if self.representation == "raw":
                return value.raw_amount
            if self.representation == "real":
                return value.real_amount
            return value.cents
        return value

    def process_result_value(self, value: Any, dialect: Any) -> Money | None:
        if value is None:
            return None
        if self.representation == "cents":
            return Money.from_cents(int(value))
        return Money(value)
