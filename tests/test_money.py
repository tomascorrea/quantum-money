"""Tests for Money class — ported from money-warp and adapted for quantum-money."""

from decimal import Decimal

import pytest

from quantum_money import Money

# ===========================================================================
# Creation
# ===========================================================================


@pytest.mark.parametrize(
    "amount,expected",
    [
        ("100.50", Decimal("100.50")),
        (100, Decimal("100.00")),
        (Decimal("100.50"), Decimal("100.50")),
        (100.50, Decimal("100.50")),
    ],
    ids=["str", "int", "decimal", "float"],
)
def test_money_creation_from_various_types(amount, expected):
    """Money can be created from str, int, Decimal, or float."""
    money = Money(amount)
    assert money.real_amount == expected


def test_money_creation_zero_class_method():
    """Money.zero() produces a zero-valued Money."""
    money = Money.zero()
    assert money.real_amount == Decimal("0.00")


def test_money_creation_zero_is_zero():
    """Money.zero() reports is_zero() as True."""
    money = Money.zero()
    assert money.is_zero()


def test_money_creation_from_cents():
    """Money.from_cents builds from an integer cent count."""
    money = Money.from_cents(12345)
    assert money.real_amount == Decimal("123.45")


# ===========================================================================
# Precision
# ===========================================================================


def test_money_high_precision_internal_storage():
    """raw_amount preserves full input precision."""
    money = Money("100.123456789")
    assert money.raw_amount == Decimal("100.123456789")


def test_money_real_amount_rounds_to_two_decimals():
    """real_amount rounds to 2dp."""
    money = Money("100.123456789")
    assert money.real_amount == Decimal("100.12")


@pytest.mark.parametrize(
    "amount,expected",
    [
        ("100.125", Decimal("100.13")),
        ("100.124", Decimal("100.12")),
        ("100.115", Decimal("100.12")),
    ],
    ids=["round-up", "round-down", "round-up-half"],
)
def test_money_precision_rounding(amount, expected):
    """ROUND_HALF_UP rounding for real_amount."""
    money = Money(amount)
    assert money.real_amount == expected


def test_money_debug_precision_shows_internal():
    """debug_precision() includes the full-precision amount."""
    money = Money("100.123456")
    assert "Internal: 100.123456" in money.debug_precision()


def test_money_debug_precision_shows_real():
    """debug_precision() includes the rounded amount."""
    money = Money("100.123456")
    assert "Real: 100.12" in money.debug_precision()


# ===========================================================================
# Arithmetic
# ===========================================================================


def test_money_addition_basic(m_price, m_tax):
    """Adding two Money objects sums their raw amounts."""
    result = m_price + m_tax
    assert result.raw_amount == Decimal("11.83")


def test_money_subtraction_basic(m_price, m_tax):
    """Subtracting two Money objects subtracts their raw amounts."""
    result = m_price - m_tax
    assert result.raw_amount == Decimal("8.83")


def test_money_multiplication_by_integer():
    """Money * int multiplies the raw amount."""
    result = Money("100.00") * 2
    assert result.real_amount == Decimal("200.00")


def test_money_multiplication_by_decimal():
    """Money * Decimal multiplies the raw amount."""
    result = Money("100.00") * Decimal("1.5")
    assert result.real_amount == Decimal("150.00")


def test_money_division_by_integer():
    """Money / int divides the raw amount."""
    result = Money("100.00") / 2
    assert result.real_amount == Decimal("50.00")


def test_money_division_maintains_high_precision():
    """Division keeps full internal precision in raw_amount."""
    result = Money("100.00") / 3
    assert result.raw_amount == Decimal("100.00") / 3


def test_money_division_rounds_real_amount():
    """Division result rounds to 2dp in real_amount."""
    result = Money("100.00") / 3
    assert result.real_amount == Decimal("33.33")


def test_money_negation():
    """Unary minus flips the sign."""
    result = -Money("100.50")
    assert result.real_amount == Decimal("-100.50")


def test_money_absolute_value():
    """abs() on negative Money returns positive."""
    result = abs(Money("-100.50"))
    assert result.real_amount == Decimal("100.50")


def test_money_sum():
    """Built-in sum() works via __radd__(0)."""
    values = [Money("1"), Money("2"), Money("3")]
    result = sum(values)
    assert result.raw_amount == Decimal("6")


# ===========================================================================
# Comparisons (at real_amount precision)
# ===========================================================================


def test_money_equality_same_amounts():
    """Same amounts are equal."""
    assert Money("100.50") == Money("100.50")


def test_money_equality_with_precision_difference():
    """Amounts that round to the same 2dp are equal."""
    assert Money("100.501") == Money("100.504")


def test_money_less_than():
    """Less-than comparison at real_amount precision."""
    assert Money("100.00") < Money("100.50")


def test_money_less_than_or_equal_smaller():
    """Less-than-or-equal with smaller value."""
    assert Money("100.00") <= Money("100.50")


def test_money_less_than_or_equal_equal():
    """Less-than-or-equal with equal values."""
    assert Money("100.00") <= Money("100.00")


def test_money_greater_than():
    """Greater-than comparison at real_amount precision."""
    assert Money("100.50") > Money("100.00")


def test_money_greater_than_or_equal_larger():
    """Greater-than-or-equal with larger value."""
    assert Money("100.50") >= Money("100.00")


def test_money_greater_than_or_equal_equal():
    """Greater-than-or-equal with equal values."""
    assert Money("100.50") >= Money("100.50")


# ===========================================================================
# Cross-type comparisons (Money vs Decimal/int/float)
# ===========================================================================


def test_money_equality_with_decimal():
    """Money equals a Decimal with the same 2dp value."""
    assert Money("100.50") == Decimal("100.50")


def test_money_equality_with_decimal_rounds():
    """Money rounds before comparing against Decimal."""
    assert Money("100.504") == Decimal("100.50")


def test_money_inequality_with_decimal():
    """Money != Decimal when values differ."""
    assert Money("100.50") != Decimal("100.51")


def test_money_less_than_decimal():
    """Money < Decimal comparison."""
    assert Money("100.00") < Decimal("100.50")


def test_money_less_than_or_equal_decimal_smaller():
    """Money <= Decimal when Money is smaller."""
    assert Money("100.00") <= Decimal("100.50")


def test_money_less_than_or_equal_decimal_equal():
    """Money <= Decimal when equal."""
    assert Money("100.50") <= Decimal("100.50")


def test_money_greater_than_decimal():
    """Money > Decimal comparison."""
    assert Money("100.50") > Decimal("100.00")


def test_money_greater_than_or_equal_decimal_larger():
    """Money >= Decimal when Money is larger."""
    assert Money("100.50") >= Decimal("100.00")


def test_money_greater_than_or_equal_decimal_equal():
    """Money >= Decimal when equal."""
    assert Money("100.50") >= Decimal("100.50")


def test_money_equality_with_unsupported_type_returns_not_implemented():
    """__eq__ returns NotImplemented for unsupported types."""
    assert Money("100.50").__eq__("100.50") is NotImplemented


def test_money_equality_with_int():
    """Money equals an int with matching value."""
    assert Money("100") == 100


def test_money_equality_with_float():
    """Money equals a float with matching value."""
    assert Money("100.50") == 100.5


# ===========================================================================
# Properties
# ===========================================================================


def test_money_cents_property():
    """cents converts real_amount to integer cents."""
    assert Money("123.45").cents == 12345


def test_money_is_positive(m_price):
    """is_positive() for a positive amount."""
    assert m_price.is_positive()


def test_money_is_negative():
    """is_negative() for a negative amount."""
    assert Money("-100.50").is_negative()


def test_money_is_zero():
    """is_zero() for zero amount."""
    assert Money("0.00").is_zero()


def test_money_to_real_money_raw_amount():
    """to_real_money() raw_amount is the rounded value."""
    real = Money("100.123456").to_real_money()
    assert real.raw_amount == Decimal("100.12")


def test_money_to_real_money_real_amount():
    """to_real_money() real_amount matches."""
    real = Money("100.123456").to_real_money()
    assert real.real_amount == Decimal("100.12")


# ===========================================================================
# Float conversion
# ===========================================================================


@pytest.mark.parametrize(
    "amount,expected",
    [
        ("100.50", 100.50),
        ("0.00", 0.0),
        ("-50.25", -50.25),
        ("100.123456789", 100.123456789),
    ],
    ids=["positive", "zero", "negative", "high-precision"],
)
def test_money_float_conversion(amount, expected):
    """float(Money) returns full internal precision as float."""
    assert float(Money(amount)) == expected


def test_money_float_returns_float_type():
    """float(Money) returns an actual float."""
    assert type(float(Money("100.50"))) is float


# ===========================================================================
# Display
# ===========================================================================


@pytest.mark.parametrize(
    "amount,expected",
    [
        ("1234.56", "1,234.56"),
        ("0.00", "0.00"),
        ("999999.99", "999,999.99"),
    ],
    ids=["thousands", "zero", "large"],
)
def test_money_string_representation(amount, expected):
    """str(Money) shows comma-formatted 2dp."""
    assert str(Money(amount)) == expected


def test_money_repr_representation():
    """repr(Money) shows the internal precision."""
    assert repr(Money("100.123")) == "Money(100.123)"


# ===========================================================================
# Edge cases
# ===========================================================================


def test_money_very_large_amount():
    """Very large amounts are preserved."""
    assert Money("999999999.99").real_amount == Decimal("999999999.99")


def test_money_very_small_amount_rounds_to_zero():
    """Sub-cent amounts round to zero."""
    assert Money("0.001").real_amount == Decimal("0.00")


def test_money_negative_zero_is_zero():
    """Negative zero is treated as zero."""
    assert Money("-0.00").is_zero()


def test_money_compound_operations_precision():
    """Divide-then-multiply stays close to original due to precision."""
    result = Money("100.00") / 3 * 3
    assert abs(result.real_amount - Decimal("100.00")) <= Decimal("0.01")


# ===========================================================================
# Reflected arithmetic (__radd__, __rsub__, __rmul__)
# ===========================================================================


def test_money_radd_decimal_plus_money():
    """Decimal + Money returns Money."""
    result = Decimal("50.00") + Money("30.25")
    assert result.real_amount == Decimal("80.25")


def test_money_radd_int_plus_money():
    """int + Money returns Money."""
    result = 50 + Money("30.25")
    assert result.real_amount == Decimal("80.25")


def test_money_radd_float_plus_money():
    """float + Money returns Money."""
    result = 50.0 + Money("30.25")
    assert result.real_amount == Decimal("80.25")


def test_money_radd_unsupported_type_returns_not_implemented():
    """__radd__ returns NotImplemented for unsupported types."""
    assert Money("100").__radd__("bad") is NotImplemented


def test_money_rsub_decimal_minus_money():
    """Decimal - Money returns Money."""
    result = Decimal("100.00") - Money("30.25")
    assert result.real_amount == Decimal("69.75")


def test_money_rsub_int_minus_money():
    """int - Money returns Money."""
    result = 100 - Money("30.25")
    assert result.real_amount == Decimal("69.75")


def test_money_rsub_float_minus_money():
    """float - Money returns Money."""
    result = 100.0 - Money("30.25")
    assert result.real_amount == Decimal("69.75")


def test_money_rsub_unsupported_type_returns_not_implemented():
    """__rsub__ returns NotImplemented for unsupported types."""
    assert Money("100").__rsub__("bad") is NotImplemented


def test_money_rmul_int_times_money():
    """int * Money returns Money."""
    result = 3 * Money("50.00")
    assert result.real_amount == Decimal("150.00")


def test_money_rmul_float_times_money():
    """float * Money returns Money."""
    result = 1.5 * Money("100.00")
    assert result.real_amount == Decimal("150.00")


def test_money_rmul_decimal_times_money():
    """Decimal * Money returns Money."""
    result = Decimal("2.5") * Money("100.00")
    assert result.real_amount == Decimal("250.00")


def test_money_rmul_unsupported_type_returns_not_implemented():
    """__rmul__ returns NotImplemented for unsupported types."""
    assert Money("100").__rmul__("bad") is NotImplemented


# ===========================================================================
# pytest.approx compatibility
# ===========================================================================


def test_money_approx_exact_match():
    """Money works with pytest.approx for exact matches."""
    assert Money("200.00") == pytest.approx(Money("200.00"))


def test_money_approx_within_tolerance():
    """Money works with pytest.approx within specified tolerance."""
    assert Money("200.01") == pytest.approx(Money("200"), abs=Decimal("0.02"))


def test_money_approx_outside_tolerance():
    """Money outside tolerance is not approx-equal."""
    assert Money("200.05") != pytest.approx(Money("200"), abs=Decimal("0.02"))


def test_money_approx_default_tolerance():
    """Money works with pytest.approx using default tolerance."""
    assert Money("200.00") == pytest.approx(Money("200"))
