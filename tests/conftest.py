"""Shared fixtures for quantum-money tests."""

from decimal import Decimal

import pytest

from quantum_money import Money, QMoney

# --- QMoney fixtures ---


@pytest.fixture
def price() -> QMoney:
    return QMoney(Decimal("10.33"))


@pytest.fixture
def tax() -> QMoney:
    return QMoney(Decimal("1.50"))


# --- Money fixtures ---


@pytest.fixture
def m_price() -> Money:
    return Money("10.33")


@pytest.fixture
def m_tax() -> Money:
    return Money("1.50")
