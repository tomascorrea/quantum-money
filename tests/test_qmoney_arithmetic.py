"""Tests for QMoney arithmetic operations."""

from decimal import Decimal

from quantum_money import QMoney


def test_qmoney_add_two_values(price, tax):
    result = (price + tax).observe().raw_amount
    assert result == Decimal("11.83")


def test_qmoney_sub_two_values(price, tax):
    result = (price - tax).observe().raw_amount
    assert result == Decimal("8.83")


def test_qmoney_mul_by_int(price):
    result = (price * 3).observe().raw_amount
    assert result == Decimal("30.99")


def test_qmoney_mul_by_decimal(price):
    result = (price * Decimal("1.1")).observe().raw_amount
    assert result == Decimal("11.363")


def test_qmoney_rmul_int(price):
    result = (3 * price).observe().raw_amount
    assert result == Decimal("30.99")


def test_qmoney_div_by_int():
    value = QMoney(Decimal("10"))
    result = (value / 3).observe().raw_amount
    assert result == Decimal("10") / Decimal("3")


def test_qmoney_div_by_decimal():
    value = QMoney(Decimal("10"))
    result = (value / Decimal("2.5")).observe().raw_amount
    assert result == Decimal("4")


def test_qmoney_pow():
    value = QMoney(Decimal("4"))
    result = (value**2).observe().raw_amount
    assert result == Decimal("16")


def test_qmoney_root():
    value = QMoney(Decimal("9"))
    result = value.root(2).observe().raw_amount
    assert result == Decimal("3")


def test_qmoney_neg(price):
    result = (-price).observe().raw_amount
    assert result == Decimal("-10.33")


def test_qmoney_pos(price):
    result = (+price).observe().raw_amount
    assert result == Decimal("10.33")


def test_qmoney_chained_operations(price, tax):
    result = (price * 3 + tax).observe().raw_amount
    assert result == Decimal("32.49")


def test_qmoney_radd_supports_sum():
    values = [QMoney(Decimal("1")), QMoney(Decimal("2")), QMoney(Decimal("3"))]
    result = sum(values).observe().raw_amount
    assert result == Decimal("6")


def test_qmoney_complex_expression():
    a = QMoney(Decimal("100"))
    b = QMoney(Decimal("5.50"))
    result = (a * 3 - b + QMoney(Decimal("0.25"))).observe().raw_amount
    assert result == Decimal("294.75")
