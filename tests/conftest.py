"""Shared fixtures for quantum-money tests."""

from decimal import Decimal

import pytest

from quantum_money import QMoney


@pytest.fixture
def price() -> QMoney:
    return QMoney(Decimal("10.33"))


@pytest.fixture
def tax() -> QMoney:
    return QMoney(Decimal("1.50"))
