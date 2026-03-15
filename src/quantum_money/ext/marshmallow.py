"""Marshmallow custom field for Money.

Requires the ``marshmallow`` extra::

    pip install quantum-money[marshmallow]
"""

from marshmallow import fields

from quantum_money.money import Money

__all__ = ["MoneyField"]

_VALID_REPRESENTATIONS = ("raw", "real", "cents", "float")


class MoneyField(fields.Field):
    """Marshmallow field for :class:`~quantum_money.money.Money`.

    Args:
        representation: Controls serialization format.
            ``"raw"`` (default) -- full-precision ``raw_amount`` as string.
            ``"real"`` -- rounded ``real_amount`` as string.
            ``"cents"`` -- integer cents.
            ``"float"`` -- rounded ``real_amount`` as a Python float.
    """

    default_error_messages = {
        "invalid": "Not a valid monetary amount.",
    }

    def __init__(self, representation: str = "raw", **kwargs: object) -> None:
        super().__init__(**kwargs)
        if representation not in _VALID_REPRESENTATIONS:
            raise ValueError(
                f"Invalid representation: '{representation}'. "
                f"Expected one of {_VALID_REPRESENTATIONS}"
            )
        self.representation = representation

    def _serialize(self, value: object, attr: str | None, obj: object, **kwargs: object) -> str | int | float | None:
        if value is None:
            return None
        if not isinstance(value, Money):
            raise self.make_error("invalid")

        if self.representation == "raw":
            return str(value.raw_amount)
        if self.representation == "real":
            return str(value.real_amount)
        if self.representation == "float":
            return float(value.real_amount)
        return value.cents

    def _deserialize(self, value: object, attr: str | None, data: object, **kwargs: object) -> Money | None:
        if value is None:
            return None
        try:
            if self.representation == "cents":
                return Money.from_cents(int(value))
            if self.representation == "float":
                return Money(str(value))
            return Money(value)
        except Exception as exc:
            raise self.make_error("invalid") from exc
