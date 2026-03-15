"""Tests for Marshmallow MoneyField."""

from decimal import Decimal

import pytest
from marshmallow import Schema, ValidationError

from quantum_money.ext.marshmallow import MoneyField
from quantum_money.money import Money


# ---------------------------------------------------------------------------
# Helper schemas
# ---------------------------------------------------------------------------


class RawMoneySchema(Schema):
    amount = MoneyField(representation="raw")


class RealMoneySchema(Schema):
    amount = MoneyField(representation="real")


class CentsMoneySchema(Schema):
    amount = MoneyField(representation="cents")


class FloatMoneySchema(Schema):
    amount = MoneyField(representation="float")


# ===========================================================================
# Construction
# ===========================================================================


def test_money_field_invalid_representation_raises():
    """Invalid representation raises ValueError."""
    with pytest.raises(ValueError, match="Invalid representation"):
        MoneyField(representation="unknown")


@pytest.mark.parametrize("representation", ["raw", "real", "cents", "float"])
def test_money_field_valid_representation_accepted(representation):
    """All valid representations are accepted."""
    field = MoneyField(representation=representation)
    assert field.representation == representation


# ===========================================================================
# Serialization
# ===========================================================================


@pytest.mark.parametrize(
    "amount_str,expected",
    [
        ("100.50", "100.50"),
        ("0", "0"),
        ("999999999.123456789", "999999999.123456789"),
        ("-50.25", "-50.25"),
    ],
    ids=["positive", "zero", "high-precision", "negative"],
)
def test_money_field_serialize_raw(amount_str, expected):
    """Raw serialization outputs raw_amount as string."""
    result = RawMoneySchema().dump({"amount": Money(amount_str)})
    assert result["amount"] == expected


@pytest.mark.parametrize(
    "amount_str,expected",
    [
        ("100.50", "100.50"),
        ("100.125", "100.13"),
        ("0.001", "0.00"),
        ("-50.255", "-50.26"),
    ],
    ids=["exact", "rounded-up", "sub-cent", "negative-round"],
)
def test_money_field_serialize_real(amount_str, expected):
    """Real serialization outputs rounded real_amount as string."""
    result = RealMoneySchema().dump({"amount": Money(amount_str)})
    assert result["amount"] == expected


@pytest.mark.parametrize(
    "amount_str,expected_cents",
    [
        ("100.50", 10050),
        ("0", 0),
        ("0.01", 1),
        ("-25.99", -2599),
    ],
    ids=["dollars", "zero", "one-cent", "negative"],
)
def test_money_field_serialize_cents(amount_str, expected_cents):
    """Cents serialization outputs integer cents."""
    result = CentsMoneySchema().dump({"amount": Money(amount_str)})
    assert result["amount"] == expected_cents


def test_money_field_serialize_none_returns_none():
    """Serializing None yields None."""
    result = RawMoneySchema().dump({"amount": None})
    assert result["amount"] is None


# ===========================================================================
# Deserialization
# ===========================================================================


@pytest.mark.parametrize(
    "input_val,expected_raw",
    [
        ("100.50", Decimal("100.50")),
        ("0", Decimal("0")),
        ("999999999.123456789", Decimal("999999999.123456789")),
    ],
    ids=["positive", "zero", "high-precision"],
)
def test_money_field_deserialize_raw(input_val, expected_raw):
    """Raw deserialization builds Money from string."""
    result = RawMoneySchema().load({"amount": input_val})
    assert result["amount"].raw_amount == expected_raw


def test_money_field_deserialize_real():
    """Real deserialization builds Money from string."""
    result = RealMoneySchema().load({"amount": "100.50"})
    assert result["amount"].raw_amount == Decimal("100.50")


@pytest.mark.parametrize(
    "cents_input,expected_real",
    [
        (10050, Decimal("100.50")),
        (0, Decimal("0.00")),
        (1, Decimal("0.01")),
    ],
    ids=["dollars", "zero", "one-cent"],
)
def test_money_field_deserialize_cents(cents_input, expected_real):
    """Cents deserialization builds Money from integer cents."""
    result = CentsMoneySchema().load({"amount": cents_input})
    assert result["amount"].real_amount == expected_real


def test_money_field_deserialize_invalid_raises():
    """Invalid input raises ValidationError."""
    with pytest.raises(ValidationError):
        RawMoneySchema().load({"amount": "not-a-number"})


# ===========================================================================
# Round-trips
# ===========================================================================


@pytest.mark.parametrize(
    "amount_str",
    ["100.50", "0", "999999999.123456789", "-50.25"],
    ids=["positive", "zero", "high-precision", "negative"],
)
def test_money_field_roundtrip_raw(amount_str):
    """Raw representation round-trips losslessly."""
    original = Money(amount_str)
    serialized = RawMoneySchema().dump({"amount": original})
    loaded = RawMoneySchema().load(serialized)
    assert loaded["amount"].raw_amount == original.raw_amount


@pytest.mark.parametrize(
    "amount_str",
    ["100.50", "100.125", "0.001"],
    ids=["exact", "rounded", "sub-cent"],
)
def test_money_field_roundtrip_real(amount_str):
    """Real representation round-trips at 2dp precision."""
    original = Money(amount_str)
    serialized = RealMoneySchema().dump({"amount": original})
    loaded = RealMoneySchema().load(serialized)
    assert loaded["amount"].real_amount == original.real_amount


@pytest.mark.parametrize(
    "amount_str",
    ["100.50", "0.01", "0"],
    ids=["dollars", "one-cent", "zero"],
)
def test_money_field_roundtrip_cents(amount_str):
    """Cents representation round-trips at 2dp precision."""
    original = Money(amount_str)
    serialized = CentsMoneySchema().dump({"amount": original})
    loaded = CentsMoneySchema().load(serialized)
    assert loaded["amount"].real_amount == original.real_amount


# ===========================================================================
# Edge cases
# ===========================================================================


def test_money_field_zero_money():
    """Zero money serializes to '0'."""
    result = RawMoneySchema().dump({"amount": Money.zero()})
    assert result["amount"] == "0"


def test_money_field_very_large_amount():
    """Very large amounts round-trip correctly."""
    big = Money("99999999999.99")
    loaded = RawMoneySchema().load(RawMoneySchema().dump({"amount": big}))
    assert loaded["amount"].raw_amount == big.raw_amount


# ===========================================================================
# Float representation
# ===========================================================================


@pytest.mark.parametrize(
    "amount_str,expected",
    [
        ("100.50", 100.50),
        ("0", 0.0),
        ("999.99", 999.99),
        ("-50.25", -50.25),
    ],
    ids=["positive", "zero", "large", "negative"],
)
def test_money_field_serialize_float(amount_str, expected):
    """Float serialization outputs real_amount as float."""
    result = FloatMoneySchema().dump({"amount": Money(amount_str)})
    assert result["amount"] == expected
    assert isinstance(result["amount"], float)


@pytest.mark.parametrize(
    "amount_str,expected",
    [
        ("100.125", 100.13),
        ("0.001", 0.0),
        ("-50.255", -50.26),
    ],
    ids=["round-up", "sub-cent", "negative-round"],
)
def test_money_field_serialize_float_rounds(amount_str, expected):
    """Float serialization rounds to 2dp."""
    result = FloatMoneySchema().dump({"amount": Money(amount_str)})
    assert result["amount"] == expected


def test_money_field_serialize_float_none_returns_none():
    """Float serialization of None returns None."""
    result = FloatMoneySchema().dump({"amount": None})
    assert result["amount"] is None


@pytest.mark.parametrize(
    "input_val,expected_real",
    [
        (100.50, Decimal("100.50")),
        (0.0, Decimal("0.00")),
        (999.99, Decimal("999.99")),
        (-25.99, Decimal("-25.99")),
    ],
    ids=["positive", "zero", "large", "negative"],
)
def test_money_field_deserialize_float(input_val, expected_real):
    """Float deserialization builds Money from float."""
    result = FloatMoneySchema().load({"amount": input_val})
    assert result["amount"].real_amount == expected_real


@pytest.mark.parametrize(
    "input_val,expected_real",
    [
        (100, Decimal("100.00")),
        (0, Decimal("0.00")),
    ],
    ids=["hundred", "zero"],
)
def test_money_field_deserialize_float_from_int(input_val, expected_real):
    """Float deserialization accepts integer input."""
    result = FloatMoneySchema().load({"amount": input_val})
    assert result["amount"].real_amount == expected_real


def test_money_field_deserialize_float_invalid_raises():
    """Invalid float input raises ValidationError."""
    with pytest.raises(ValidationError):
        FloatMoneySchema().load({"amount": "not-a-number"})


@pytest.mark.parametrize(
    "amount_str",
    ["100.50", "0.01", "0", "-25.99"],
    ids=["positive", "one-cent", "zero", "negative"],
)
def test_money_field_roundtrip_float(amount_str):
    """Float representation round-trips at 2dp precision."""
    original = Money(amount_str)
    serialized = FloatMoneySchema().dump({"amount": original})
    loaded = FloatMoneySchema().load(serialized)
    assert loaded["amount"].real_amount == original.real_amount
