"""Tests for QMoney observe() and to_decimal()."""

from decimal import Decimal

from quantum_money import QMoney
from quantum_money.nodes import Value


def test_observe_returns_new_qmoney(price):
    result = price.observe()
    assert result is not price


def test_observe_result_has_value_node(price):
    result = (price * 3).observe()
    assert isinstance(result._node, Value)


def test_observe_is_idempotent(price):
    expr = price * 3 + QMoney(Decimal("1"))
    first = expr.observe().to_decimal()
    second = expr.observe().observe().to_decimal()
    assert first == second


def test_to_decimal_on_value_constructor():
    value = QMoney(Decimal("5.00"))
    assert value.to_decimal() == Decimal("5.00")


def test_to_decimal_on_observed():
    expr = QMoney(Decimal("10")) * 3
    result = expr.observe()
    assert result.to_decimal() == Decimal("30")


def test_observe_deep_tree():
    value = QMoney(Decimal("1"))
    expr = value
    for i in range(1, 6):
        expr = expr + QMoney(Decimal(str(i)))
    result = expr.observe().to_decimal()
    assert result == Decimal("16")


def test_observe_preserves_decimal_precision():
    value = QMoney(Decimal("1.000"))
    result = value.observe().to_decimal()
    assert result == Decimal("1.000")
