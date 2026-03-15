"""Tests proving the core value proposition: controlled rounding."""

from decimal import ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

from quantum_money import QMoney


def test_round_after_multiply():
    price = QMoney(Decimal("10.33"))
    result = (price * 3).round(ROUND_HALF_UP).observe().raw_amount
    assert result == Decimal("30.99")


def test_round_before_add():
    a = QMoney(Decimal("10.335"))
    b = QMoney(Decimal("10.335"))
    result = (a.round(ROUND_HALF_UP) + b.round(ROUND_HALF_UP)).observe().raw_amount
    assert result == Decimal("20.68")


def test_round_half_up():
    value = QMoney(Decimal("2.555"))
    result = value.round(ROUND_HALF_UP).observe().raw_amount
    assert result == Decimal("2.56")


def test_round_half_down():
    value = QMoney(Decimal("2.555"))
    result = value.round(ROUND_HALF_DOWN).observe().raw_amount
    assert result == Decimal("2.55")


def test_round_half_even():
    value = QMoney(Decimal("2.545"))
    result = value.round(ROUND_HALF_EVEN).observe().raw_amount
    assert result == Decimal("2.54")


def test_round_zero_places():
    value = QMoney(Decimal("10.6"))
    result = value.round(ROUND_HALF_UP, places=0).observe().raw_amount
    assert result == Decimal("11")


def test_round_three_places():
    value = QMoney(Decimal("1.23456"))
    result = value.round(ROUND_HALF_UP, places=3).observe().raw_amount
    assert result == Decimal("1.235")


def test_rounding_order_matters():
    """The core value proposition: WHERE you round changes the result.

    Given unit price 1.345 and quantity 10:
    - Round first, then multiply: round(1.345) * 10 = 1.35 * 10 = 13.50
    - Multiply first, then round: round(1.345 * 10) = round(13.45) = 13.45

    These produce different results, proving lazy evaluation with controlled
    rounding solves a real financial problem.
    """
    unit_price = QMoney(Decimal("1.345"))

    round_first = (unit_price.round(ROUND_HALF_UP) * 10).observe().raw_amount
    round_last = (unit_price * 10).round(ROUND_HALF_UP).observe().raw_amount

    assert round_first == Decimal("13.50")
    assert round_last == Decimal("13.45")
    assert round_first != round_last


def test_round_is_lazy():
    """Calling .round() does not evaluate — the tree still contains a Round node."""
    price = QMoney(Decimal("10.335"))
    rounded = price.round(ROUND_HALF_UP)
    assert repr(rounded) == "QMoney(round(10.335, ROUND_HALF_UP, 2))"


def test_readme_example():
    """The exact example from the brainstorm session."""
    price = QMoney(Decimal("10.33"))
    total = price * 3
    rounded_total = total.round(ROUND_HALF_UP)
    final = rounded_total + QMoney(Decimal("0.01"))

    result = final.observe()
    assert result.raw_amount == Decimal("31.00")
