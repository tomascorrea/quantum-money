"""Expression tree node types for lazy monetary calculations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Value:
    amount: Decimal


@dataclass(frozen=True, slots=True)
class Add:
    left: Node
    right: Node


@dataclass(frozen=True, slots=True)
class Sub:
    left: Node
    right: Node


@dataclass(frozen=True, slots=True)
class Mul:
    node: Node
    factor: Decimal


@dataclass(frozen=True, slots=True)
class Div:
    node: Node
    divisor: Decimal


@dataclass(frozen=True, slots=True)
class Pow:
    node: Node
    exponent: Decimal


@dataclass(frozen=True, slots=True)
class Root:
    node: Node
    index: Decimal


@dataclass(frozen=True, slots=True)
class Round:
    node: Node
    rounding: str
    places: int


Node = Value | Add | Sub | Mul | Div | Pow | Root | Round
