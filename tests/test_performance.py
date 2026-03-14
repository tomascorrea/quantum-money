"""Performance tests — QMoney should not add too much overhead vs plain Decimal."""

import time
from decimal import Decimal

import pytest

from quantum_money import QMoney

ITERATIONS = 5_000
MAX_SLOWDOWN = 8  # QMoney may be at most Nx slower than raw Decimal


def _bench(fn, iterations: int = ITERATIONS) -> float:
    """Run *fn* `iterations` times and return elapsed seconds."""
    start = time.perf_counter()
    for _ in range(iterations):
        fn()
    return time.perf_counter() - start


# --- helpers that define the operations under test ---


def _decimal_add() -> Decimal:
    a = Decimal("10.33")
    b = Decimal("1.50")
    return a + b


def _qmoney_add() -> Decimal:
    a = QMoney(Decimal("10.33"))
    b = QMoney(Decimal("1.50"))
    return (a + b).observe().raw_amount


def _decimal_chain() -> Decimal:
    a = Decimal("100")
    b = Decimal("5.50")
    c = Decimal("0.25")
    return a * 3 - b + c


def _qmoney_chain() -> Decimal:
    a = QMoney(Decimal("100"))
    b = QMoney(Decimal("5.50"))
    c = QMoney(Decimal("0.25"))
    return (a * 3 - b + c).observe().raw_amount


def _decimal_sum() -> Decimal:
    values = [Decimal("1"), Decimal("2"), Decimal("3"), Decimal("4"), Decimal("5")]
    return sum(values)


def _qmoney_sum() -> Decimal:
    values = [
        QMoney(Decimal("1")),
        QMoney(Decimal("2")),
        QMoney(Decimal("3")),
        QMoney(Decimal("4")),
        QMoney(Decimal("5")),
    ]
    return sum(values).observe().raw_amount


def _decimal_mul_chain() -> Decimal:
    v = Decimal("100")
    for i in range(1, 6):
        v = v * i
    return v


def _qmoney_mul_chain() -> Decimal:
    v = QMoney(Decimal("100"))
    for i in range(1, 6):
        v = v * i
    return v.observe().raw_amount


# --- tests ---


class TestPerformance:
    """Assert QMoney overhead stays within acceptable bounds."""

    @pytest.mark.parametrize(
        "label, decimal_fn, qmoney_fn",
        [
            ("add", _decimal_add, _qmoney_add),
            ("chain (a*3 - b + c)", _decimal_chain, _qmoney_chain),
            ("sum of 5 values", _decimal_sum, _qmoney_sum),
            ("multiply chain (5 steps)", _decimal_mul_chain, _qmoney_mul_chain),
        ],
        ids=["add", "chain", "sum", "mul_chain"],
    )
    def test_overhead_within_bounds(
        self, label: str, decimal_fn, qmoney_fn
    ) -> None:
        # warm-up
        for _ in range(100):
            decimal_fn()
            qmoney_fn()

        decimal_time = _bench(decimal_fn)
        qmoney_time = _bench(qmoney_fn)

        ratio = qmoney_time / decimal_time
        # Print for visibility in pytest -v output
        print(
            f"\n  {label}: Decimal={decimal_time:.4f}s  "
            f"QMoney={qmoney_time:.4f}s  ratio={ratio:.1f}x"
        )
        assert ratio < MAX_SLOWDOWN, (
            f"{label}: QMoney is {ratio:.1f}x slower than Decimal "
            f"(threshold: {MAX_SLOWDOWN}x)"
        )
