"""Property-based tests for QMoney using Hypothesis."""

from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from quantum_money import QMoney

# Strategy: Decimals suitable for monetary calculations.
# Avoids extremes that would cause Decimal overflow or slow computation.
money_decimals = st.decimals(
    min_value=Decimal("-1_000_000"),
    max_value=Decimal("1_000_000"),
    places=4,
    allow_nan=False,
    allow_infinity=False,
)

positive_decimals = st.decimals(
    min_value=Decimal("0.01"),
    max_value=Decimal("1_000_000"),
    places=4,
    allow_nan=False,
    allow_infinity=False,
)

scalar_ints = st.integers(min_value=-1_000, max_value=1_000).filter(lambda x: x != 0)


# --- Commutativity & identity ---


@given(a=money_decimals, b=money_decimals)
def test_addition_is_commutative(a: Decimal, b: Decimal) -> None:
    qa, qb = QMoney(a), QMoney(b)
    left = (qa + qb).observe().raw_amount
    right = (qb + qa).observe().raw_amount
    assert left == right


@given(a=money_decimals)
def test_add_zero_is_identity(a: Decimal) -> None:
    qa = QMoney(a)
    result = (qa + QMoney(Decimal("0"))).observe().raw_amount
    assert result == a


@given(a=money_decimals)
def test_sub_self_is_zero(a: Decimal) -> None:
    qa = QMoney(a)
    result = (qa - qa).observe().raw_amount
    assert result == Decimal("0")


@given(a=money_decimals)
def test_mul_one_is_identity(a: Decimal) -> None:
    qa = QMoney(a)
    result = (qa * 1).observe().raw_amount
    assert result == a


@given(a=money_decimals)
def test_negation_inverts(a: Decimal) -> None:
    qa = QMoney(a)
    result = (qa + (-qa)).observe().raw_amount
    assert result == Decimal("0")


# --- QMoney matches plain Decimal arithmetic ---


@given(a=money_decimals, b=money_decimals)
def test_add_matches_decimal(a: Decimal, b: Decimal) -> None:
    result = (QMoney(a) + QMoney(b)).observe().raw_amount
    assert result == a + b


@given(a=money_decimals, b=money_decimals)
def test_sub_matches_decimal(a: Decimal, b: Decimal) -> None:
    result = (QMoney(a) - QMoney(b)).observe().raw_amount
    assert result == a - b


@given(a=money_decimals, n=scalar_ints)
def test_mul_int_matches_decimal(a: Decimal, n: int) -> None:
    result = (QMoney(a) * n).observe().raw_amount
    assert result == a * n


@given(a=money_decimals, b=positive_decimals)
def test_div_matches_decimal(a: Decimal, b: Decimal) -> None:
    result = (QMoney(a) / b).observe().raw_amount
    assert result == a / b


# --- Chained operations ---


@given(a=money_decimals, b=money_decimals, n=scalar_ints)
def test_chained_mul_add_matches_decimal(
    a: Decimal, b: Decimal, n: int
) -> None:
    result = (QMoney(a) * n + QMoney(b)).observe().raw_amount
    assert result == a * n + b


@given(
    a=money_decimals,
    b=money_decimals,
    c=money_decimals,
)
def test_sum_matches_decimal(a: Decimal, b: Decimal, c: Decimal) -> None:
    values = [QMoney(a), QMoney(b), QMoney(c)]
    result = sum(values).observe().raw_amount
    assert result == a + b + c
