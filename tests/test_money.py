"""Tests for Money class — eager financial calculations."""

from decimal import Decimal

import pytest

from quantum_money import Money


# --- Construction ---


def test_money_from_decimal():
    m = Money(Decimal("10.33"))
    assert m.raw_amount == Decimal("10.33")


def test_money_from_string():
    m = Money("10.33")
    assert m.raw_amount == Decimal("10.33")


def test_money_from_int():
    m = Money(100)
    assert m.raw_amount == Decimal("100")


def test_money_from_float():
    m = Money(10.33)
    assert m.raw_amount == Decimal("10.33")


def test_money_zero():
    m = Money.zero()
    assert m.raw_amount == Decimal("0")


def test_money_from_cents():
    m = Money.from_cents(1050)
    assert m.real_amount == Decimal("10.50")


# --- Properties ---


def test_raw_amount(m_price):
    assert m_price.raw_amount == Decimal("10.33")


def test_real_amount_rounds():
    m = Money("10.335")
    assert m.real_amount == Decimal("10.34")


def test_cents(m_price):
    assert m_price.cents == 1033


# --- Arithmetic ---


def test_add(m_price, m_tax):
    result = m_price + m_tax
    assert result.raw_amount == Decimal("11.83")


def test_sub(m_price, m_tax):
    result = m_price - m_tax
    assert result.raw_amount == Decimal("8.83")


def test_mul_by_int(m_price):
    result = m_price * 3
    assert result.raw_amount == Decimal("30.99")


def test_mul_by_decimal(m_price):
    result = m_price * Decimal("1.1")
    assert result.raw_amount == Decimal("11.363")


def test_rmul_int(m_price):
    result = 3 * m_price
    assert result.raw_amount == Decimal("30.99")


def test_div_by_int():
    m = Money("10")
    result = m / 4
    assert result.raw_amount == Decimal("2.5")


def test_neg(m_price):
    result = -m_price
    assert result.raw_amount == Decimal("-10.33")


def test_abs_negative():
    m = Money("-5.00")
    assert abs(m).raw_amount == Decimal("5.00")


def test_pos(m_price):
    result = +m_price
    assert result is m_price


def test_sum():
    values = [Money("1"), Money("2"), Money("3")]
    result = sum(values)
    assert result.raw_amount == Decimal("6")


# --- Comparisons (at real_amount precision) ---


def test_eq(m_price):
    assert m_price == Money("10.33")


def test_eq_with_rounding():
    # 10.335 rounds to 10.34 (HALF_UP), 10.334 rounds to 10.33
    assert Money("10.335") == Money("10.336")


def test_lt():
    assert Money("1") < Money("2")


def test_le():
    assert Money("1") <= Money("1")


def test_gt():
    assert Money("2") > Money("1")


def test_ge():
    assert Money("2") >= Money("2")


# --- Helpers ---


def test_is_positive(m_price):
    assert m_price.is_positive()


def test_is_negative():
    assert Money("-1").is_negative()


def test_is_zero():
    assert Money.zero().is_zero()


def test_to_real_money():
    m = Money("10.335")
    real = m.to_real_money()
    assert real.raw_amount == Decimal("10.34")


def test_float_conversion(m_price):
    assert float(m_price) == 10.33


def test_str(m_price):
    assert str(m_price) == "10.33"


def test_repr(m_price):
    assert repr(m_price) == "Money(10.33)"
