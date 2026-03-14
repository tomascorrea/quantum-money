"""QMoney class — lazy monetary value built on an expression tree."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING, Self

from quantum_money.errors import InvalidOperationError, NotObservedError
from quantum_money.nodes import (
    Add,
    Div,
    Mul,
    Node,
    Pow,
    Root,
    Round,
    Sub,
    Value,
)

if TYPE_CHECKING:
    Scalar = int | Decimal


class QMoney:
    """A lazy monetary value that records operations as an expression tree.

    All arithmetic is deferred until .observe() is called, giving full control
    over when and how rounding is applied.
    """

    __slots__ = ("_node",)

    def __init__(
        self, value: Decimal | None = None, *, _node: Node | None = None
    ) -> None:
        if _node is not None:
            self._node = _node
        elif value is not None:
            if not isinstance(value, Decimal):
                raise TypeError(
                    f"QMoney requires a Decimal, got {type(value).__name__}. "
                    "Use Decimal('10.33') not 10.33"
                )
            self._node = Value(value)
        else:
            raise TypeError("QMoney requires a Decimal value")

    @classmethod
    def _from_node(cls, node: Node) -> Self:
        obj = object.__new__(cls)
        obj._node = node
        return obj

    @staticmethod
    def _to_decimal_scalar(other: object) -> Decimal:
        if isinstance(other, Decimal):
            return other
        if isinstance(other, int):
            return Decimal(other)
        raise InvalidOperationError(
            f"Operand must be int or Decimal, got {type(other).__name__}"
        )

    # --- Arithmetic: QMoney +/- QMoney ---

    def __add__(self, other: object) -> QMoney:
        if not isinstance(other, QMoney):
            return NotImplemented
        return QMoney._from_node(Add(self._node, other._node))

    def __radd__(self, other: object) -> QMoney:
        if other == 0:
            return self
        if not isinstance(other, QMoney):
            return NotImplemented
        return QMoney._from_node(Add(other._node, self._node))

    def __sub__(self, other: object) -> QMoney:
        if not isinstance(other, QMoney):
            return NotImplemented
        return QMoney._from_node(Sub(self._node, other._node))

    def __rsub__(self, other: object) -> QMoney:
        if not isinstance(other, QMoney):
            return NotImplemented
        return QMoney._from_node(Sub(other._node, self._node))

    # --- Arithmetic: QMoney */÷/^ scalar ---

    def __mul__(self, other: object) -> QMoney:
        if isinstance(other, QMoney):
            raise InvalidOperationError(
                "Cannot multiply QMoney by QMoney (no financial meaning). "
                "Multiply by int or Decimal instead."
            )
        factor = self._to_decimal_scalar(other)
        return QMoney._from_node(Mul(self._node, factor))

    def __rmul__(self, other: object) -> QMoney:
        if isinstance(other, QMoney):
            raise InvalidOperationError(
                "Cannot multiply QMoney by QMoney (no financial meaning)."
            )
        factor = self._to_decimal_scalar(other)
        return QMoney._from_node(Mul(self._node, factor))

    def __truediv__(self, other: object) -> QMoney:
        if isinstance(other, QMoney):
            raise InvalidOperationError(
                "Cannot divide QMoney by QMoney. Divide by int or Decimal instead."
            )
        divisor = self._to_decimal_scalar(other)
        return QMoney._from_node(Div(self._node, divisor))

    def __rtruediv__(self, other: object) -> QMoney:
        return NotImplemented

    def __pow__(self, other: object) -> QMoney:
        if isinstance(other, QMoney):
            raise InvalidOperationError("Cannot raise QMoney to a QMoney power.")
        exponent = self._to_decimal_scalar(other)
        return QMoney._from_node(Pow(self._node, exponent))

    # --- Unary operators ---

    def __neg__(self) -> QMoney:
        return QMoney._from_node(Mul(self._node, Decimal("-1")))

    def __pos__(self) -> QMoney:
        return self

    # --- Blocked conversions ---

    def __float__(self) -> float:
        raise TypeError(
            "Cannot convert QMoney to float. Use .observe().to_decimal() instead."
        )

    def __int__(self) -> int:
        raise TypeError(
            "Cannot convert QMoney to int. Use .observe().to_decimal() instead."
        )

    def __bool__(self) -> bool:
        raise TypeError(
            "Cannot evaluate QMoney as bool. Observe first, then compare the Decimal."
        )

    # --- Comparisons ---

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QMoney):
            return NotImplemented
        return self._node == other._node

    def __lt__(self, other: object) -> bool:
        raise TypeError(
            "Cannot compare QMoney. "
            "Use .observe().to_decimal() to get comparable values."
        )

    def __le__(self, other: object) -> bool:
        raise TypeError(
            "Cannot compare QMoney. "
            "Use .observe().to_decimal() to get comparable values."
        )

    def __gt__(self, other: object) -> bool:
        raise TypeError(
            "Cannot compare QMoney. "
            "Use .observe().to_decimal() to get comparable values."
        )

    def __ge__(self, other: object) -> bool:
        raise TypeError(
            "Cannot compare QMoney. "
            "Use .observe().to_decimal() to get comparable values."
        )

    def __hash__(self) -> int:
        return hash(self._node)

    # --- Core methods ---

    def round(self, rounding: str = ROUND_HALF_UP, places: int = 2) -> QMoney:
        """Record a rounding step in the expression tree (lazy)."""
        return QMoney._from_node(Round(self._node, rounding, places))

    def root(self, n: int | Decimal) -> QMoney:
        """Record an nth-root operation in the expression tree (lazy)."""
        index = self._to_decimal_scalar(n)
        return QMoney._from_node(Root(self._node, index))

    def observe(self) -> QMoney:
        """Evaluate the expression tree and return a new QMoney with the result."""
        result = _evaluate(self._node)
        return QMoney._from_node(Value(result))

    def to_decimal(self) -> Decimal:
        """Extract the Decimal value. Only works on observed (single-value) QMoney."""
        if not isinstance(self._node, Value):
            raise NotObservedError(
                "Cannot extract Decimal from an unevaluated expression tree. "
                "Call .observe() first."
            )
        return self._node.amount

    # --- Repr ---

    def __repr__(self) -> str:
        return f"QMoney({_repr_node(self._node)})"


def _eval_value(node: Value) -> Decimal:
    return node.amount


def _eval_add(node: Add) -> Decimal:
    return _evaluate(node.left) + _evaluate(node.right)


def _eval_sub(node: Sub) -> Decimal:
    return _evaluate(node.left) - _evaluate(node.right)


def _eval_mul(node: Mul) -> Decimal:
    return _evaluate(node.node) * node.factor


def _eval_div(node: Div) -> Decimal:
    return _evaluate(node.node) / node.divisor


def _eval_pow(node: Pow) -> Decimal:
    return _evaluate(node.node) ** node.exponent


def _eval_root(node: Root) -> Decimal:
    return _evaluate(node.node) ** (Decimal(1) / node.index)


def _eval_round(node: Round) -> Decimal:
    value = _evaluate(node.node)
    quantize_to = Decimal(10) ** -node.places
    return value.quantize(quantize_to, rounding=node.rounding)


_EVALUATORS = {
    Value: _eval_value,
    Add: _eval_add,
    Sub: _eval_sub,
    Mul: _eval_mul,
    Div: _eval_div,
    Pow: _eval_pow,
    Root: _eval_root,
    Round: _eval_round,
}


def _evaluate(node: Node) -> Decimal:
    """Recursively evaluate an expression tree to a Decimal."""
    evaluator = _EVALUATORS.get(type(node))
    if evaluator is not None:
        return evaluator(node)
    raise TypeError(f"Unknown node type: {type(node).__name__}")


def _repr_node(node: Node) -> str:
    """Human-readable representation of an expression tree."""
    match node:
        case Value(amount):
            return str(amount)
        case Add(left, right):
            return f"({_repr_node(left)} + {_repr_node(right)})"
        case Sub(left, right):
            return f"({_repr_node(left)} - {_repr_node(right)})"
        case Mul(inner, factor):
            return f"({_repr_node(inner)} * {factor})"
        case Div(inner, divisor):
            return f"({_repr_node(inner)} / {divisor})"
        case Pow(inner, exponent):
            return f"({_repr_node(inner)} ** {exponent})"
        case Root(inner, index):
            return f"root({_repr_node(inner)}, {index})"
        case Round(inner, rounding, places):
            return f"round({_repr_node(inner)}, {rounding}, {places})"
        case _:
            return f"<unknown: {node}>"
