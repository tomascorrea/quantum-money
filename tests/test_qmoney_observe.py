"""Tests for QMoney observe() returning Money."""

from decimal import Decimal

from quantum_money import Money, QMoney


def test_observe_returns_money(price):
    result = price.observe()
    assert isinstance(result, Money)


def test_observe_returns_new_object(price):
    result = price.observe()
    assert result is not price


def test_observe_is_idempotent(price):
    expr = price * 3 + QMoney(Decimal("1"))
    first = expr.observe().raw_amount
    second = expr.observe().raw_amount
    assert first == second


def test_observe_raw_amount():
    expr = QMoney(Decimal("10")) * 3
    result = expr.observe()
    assert result.raw_amount == Decimal("30")


def test_observe_deep_tree():
    value = QMoney(Decimal("1"))
    expr = value
    for i in range(1, 6):
        expr = expr + QMoney(Decimal(str(i)))
    result = expr.observe().raw_amount
    assert result == Decimal("16")


def test_observe_preserves_decimal_precision():
    value = QMoney(Decimal("1.000"))
    result = value.observe().raw_amount
    assert result == Decimal("1.000")
