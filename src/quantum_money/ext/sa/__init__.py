"""SQLAlchemy extension for quantum-money.

Requires the ``sa`` extra::

    pip install quantum-money[sa]
"""

from quantum_money.ext.sa.types import MoneyType

__all__ = ["MoneyType"]
