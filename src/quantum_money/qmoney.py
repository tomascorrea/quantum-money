"""QMoney class — lazy monetary value built on an expression tree."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING, Self

from quantum_money.errors import InvalidOperationError
from quantum_money.money import Money
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

# Pre-cached constants used in evaluation hot paths.
_DECIMAL_1 = Decimal(1)
_DECIMAL_10 = Decimal(10)
_DECIMAL_NEG1 = Decimal("-1")

# Module-level QMoney wrapper — avoids classmethod descriptor overhead.
_new_qmoney = object.__new__


def _wrap(node: Node) -> QMoney:
    """Create a QMoney directly from a node, bypassing __init__."""
    obj = _new_qmoney(QMoney)
    obj._node = node
    return obj


class QMoney:
    """A lazy monetary value that records operations as an expression tree.

    All arithmetic is deferred until .observe() is called, giving full control
    over when and how rounding is applied.
    """

    __slots__ = ("_node",)

    def __init__(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError(
                f"QMoney requires a Decimal, got {type(value).__name__}. "
                "Use Decimal('10.33') not 10.33"
            )
        self._node = Value(value)

    # --- Arithmetic: QMoney +/- QMoney ---

    def __add__(self, other: object) -> QMoney:
        if not isinstance(other, QMoney):
            return NotImplemented
        return _wrap(Add(self._node, other._node))

    def __radd__(self, other: object) -> QMoney:
        if other == 0:
            return self
        if not isinstance(other, QMoney):
            return NotImplemented
        return _wrap(Add(other._node, self._node))

    def __sub__(self, other: object) -> QMoney:
        if not isinstance(other, QMoney):
            return NotImplemented
        return _wrap(Sub(self._node, other._node))

    def __rsub__(self, other: object) -> QMoney:
        if not isinstance(other, QMoney):
            return NotImplemented
        return _wrap(Sub(other._node, self._node))

    # --- Arithmetic: QMoney */÷/^ scalar ---

    def __mul__(self, other: object) -> QMoney:
        if isinstance(other, QMoney):
            raise InvalidOperationError(
                "Cannot multiply QMoney by QMoney (no financial meaning). "
                "Multiply by int or Decimal instead."
            )
        if isinstance(other, Decimal):
            return _wrap(Mul(self._node, other))
        if isinstance(other, int):
            return _wrap(Mul(self._node, Decimal(other)))
        raise InvalidOperationError(
            f"Operand must be int or Decimal, got {type(other).__name__}"
        )

    def __rmul__(self, other: object) -> QMoney:
        if isinstance(other, QMoney):
            raise InvalidOperationError(
                "Cannot multiply QMoney by QMoney (no financial meaning)."
            )
        if isinstance(other, Decimal):
            return _wrap(Mul(self._node, other))
        if isinstance(other, int):
            return _wrap(Mul(self._node, Decimal(other)))
        raise InvalidOperationError(
            f"Operand must be int or Decimal, got {type(other).__name__}"
        )

    def __truediv__(self, other: object) -> QMoney:
        if isinstance(other, QMoney):
            raise InvalidOperationError(
                "Cannot divide QMoney by QMoney. Divide by int or Decimal instead."
            )
        if isinstance(other, Decimal):
            return _wrap(Div(self._node, other))
        if isinstance(other, int):
            return _wrap(Div(self._node, Decimal(other)))
        raise InvalidOperationError(
            f"Operand must be int or Decimal, got {type(other).__name__}"
        )

    def __rtruediv__(self, other: object) -> QMoney:
        return NotImplemented

    def __pow__(self, other: object) -> QMoney:
        if isinstance(other, QMoney):
            raise InvalidOperationError("Cannot raise QMoney to a QMoney power.")
        if isinstance(other, Decimal):
            return _wrap(Pow(self._node, other))
        if isinstance(other, int):
            return _wrap(Pow(self._node, Decimal(other)))
        raise InvalidOperationError(
            f"Operand must be int or Decimal, got {type(other).__name__}"
        )

    # --- Unary operators ---

    def __neg__(self) -> QMoney:
        return _wrap(Mul(self._node, _DECIMAL_NEG1))

    def __pos__(self) -> QMoney:
        return self

    # --- Blocked conversions ---

    def __float__(self) -> float:
        raise TypeError(
            "Cannot convert QMoney to float. Use .observe() instead."
        )

    def __int__(self) -> int:
        raise TypeError(
            "Cannot convert QMoney to int. Use .observe() instead."
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
            "Use .observe() to get comparable Money values."
        )

    def __le__(self, other: object) -> bool:
        raise TypeError(
            "Cannot compare QMoney. "
            "Use .observe() to get comparable Money values."
        )

    def __gt__(self, other: object) -> bool:
        raise TypeError(
            "Cannot compare QMoney. "
            "Use .observe() to get comparable Money values."
        )

    def __ge__(self, other: object) -> bool:
        raise TypeError(
            "Cannot compare QMoney. "
            "Use .observe() to get comparable Money values."
        )

    def __hash__(self) -> int:
        return hash(self._node)

    # --- Core methods ---

    def round(self, rounding: str = ROUND_HALF_UP, places: int = 2) -> QMoney:
        """Record a rounding step in the expression tree (lazy)."""
        return _wrap(Round(self._node, rounding, places))

    def root(self, n: int | Decimal) -> QMoney:
        """Record an nth-root operation in the expression tree (lazy)."""
        if isinstance(n, Decimal):
            return _wrap(Root(self._node, n))
        if isinstance(n, int):
            return _wrap(Root(self._node, Decimal(n)))
        raise InvalidOperationError(
            f"Operand must be int or Decimal, got {type(n).__name__}"
        )

    def observe(self) -> Money:
        """Evaluate the expression tree and return a Money with the result."""
        return Money(_evaluate(self._node))

    # --- Repr ---

    def __repr__(self) -> str:
        return f"QMoney({_repr_node(self._node)})"


# --- Evaluation engine ---


def _evaluate(node: Node) -> Decimal:
    """Recursively evaluate an expression tree to a Decimal."""
    return _EVALUATORS[type(node)](node)


def _eval_value(node: Value) -> Decimal:
    return node.amount


def _eval_add(node: Add) -> Decimal:
    return _EVALUATORS[type(node.left)](node.left) + _EVALUATORS[type(node.right)](node.right)


def _eval_sub(node: Sub) -> Decimal:
    return _EVALUATORS[type(node.left)](node.left) - _EVALUATORS[type(node.right)](node.right)


def _eval_mul(node: Mul) -> Decimal:
    return _EVALUATORS[type(node.node)](node.node) * node.factor


def _eval_div(node: Div) -> Decimal:
    return _EVALUATORS[type(node.node)](node.node) / node.divisor


def _eval_pow(node: Pow) -> Decimal:
    return _EVALUATORS[type(node.node)](node.node) ** node.exponent


def _eval_root(node: Root) -> Decimal:
    return _EVALUATORS[type(node.node)](node.node) ** (_DECIMAL_1 / node.index)


def _eval_round(node: Round) -> Decimal:
    value = _EVALUATORS[type(node.node)](node.node)
    quantize_to = _DECIMAL_10 ** -node.places
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
