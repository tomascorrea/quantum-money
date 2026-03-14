"""Expression tree node types for lazy monetary calculations."""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from decimal import Decimal


class Value(NamedTuple):
    amount: Decimal


class Add(NamedTuple):
    left: Node
    right: Node


class Sub(NamedTuple):
    left: Node
    right: Node


class Mul(NamedTuple):
    node: Node
    factor: Decimal


class Div(NamedTuple):
    node: Node
    divisor: Decimal


class Pow(NamedTuple):
    node: Node
    exponent: Decimal


class Root(NamedTuple):
    node: Node
    index: Decimal


class Round(NamedTuple):
    node: Node
    rounding: str
    places: int


Node = Value | Add | Sub | Mul | Div | Pow | Root | Round
