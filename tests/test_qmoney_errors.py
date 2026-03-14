"""Tests for QMoney error handling and type safety."""

import pytest

from quantum_money import InvalidOperationError, QMoney


def test_qmoney_constructor_rejects_float():
    with pytest.raises(TypeError, match="got float"):
        QMoney(10.33)  # type: ignore[arg-type]


def test_qmoney_constructor_rejects_int():
    with pytest.raises(TypeError, match="got int"):
        QMoney(10)  # type: ignore[arg-type]


def test_qmoney_constructor_rejects_string():
    with pytest.raises(TypeError, match="got str"):
        QMoney("10")  # type: ignore[arg-type]


def test_qmoney_constructor_rejects_no_args():
    with pytest.raises(TypeError):
        QMoney()


def test_qmoney_mul_by_qmoney_raises(price, tax):
    with pytest.raises(InvalidOperationError, match="Cannot multiply"):
        price * tax


def test_qmoney_div_by_qmoney_raises(price, tax):
    with pytest.raises(InvalidOperationError, match="Cannot divide"):
        price / tax


def test_qmoney_pow_by_qmoney_raises(price, tax):
    with pytest.raises(InvalidOperationError, match="Cannot raise"):
        price**tax


def test_qmoney_add_non_qmoney_raises(price):
    with pytest.raises(TypeError):
        price + 5  # type: ignore[operator]


def test_qmoney_sub_non_qmoney_raises(price):
    with pytest.raises(TypeError):
        price - 5  # type: ignore[operator]


def test_qmoney_mul_by_float_raises(price):
    with pytest.raises(InvalidOperationError, match="got float"):
        price * 3.5


def test_float_conversion_raises(price):
    with pytest.raises(TypeError, match="Cannot convert QMoney to float"):
        float(price)


def test_int_conversion_raises(price):
    with pytest.raises(TypeError, match="Cannot convert QMoney to int"):
        int(price)


def test_bool_conversion_raises(price):
    with pytest.raises(TypeError, match="Cannot evaluate QMoney as bool"):
        bool(price)


@pytest.mark.parametrize(
    "op",
    ["__lt__", "__le__", "__gt__", "__ge__"],
    ids=["<", "<=", ">", ">="],
)
def test_ordering_comparison_raises(price, tax, op):
    with pytest.raises(TypeError, match="Cannot compare"):
        getattr(price, op)(tax)


def test_rtruediv_returns_not_implemented(price):
    with pytest.raises(TypeError):
        5 / price  # type: ignore[operator]
