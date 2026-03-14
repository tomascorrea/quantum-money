"""Smoke tests for quantum-money package imports."""

import quantum_money
from quantum_money import InvalidOperationError, NotObservedError, QMoney


def test_import():
    assert quantum_money is not None


def test_qmoney_importable_from_package():
    assert QMoney is not None


def test_errors_importable_from_package():
    assert NotObservedError is not None
    assert InvalidOperationError is not None
