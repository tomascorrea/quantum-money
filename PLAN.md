# Plan: Port Tests, SQLAlchemy Extension, and Marshmallow Extension from money-warp

## Overview

Port three things from [money-warp](https://github.com/tomascorrea/money-warp):
1. Money-specific tests (adapted to quantum-money's API)
2. SQLAlchemy `MoneyType` extension (only Money, skip Rate/InterestRate/DueDates)
3. Marshmallow `MoneyField` extension (only Money, skip Rate/InterestRate)

---

## Step 1: Enhance `Money` class to support money-warp features

Before porting tests, quantum-money's `Money` needs a few features that money-warp has:

### 1a. Cross-type comparisons
money-warp compares `Money` against `Decimal`, `int`, `float`. quantum-money only compares `Money` vs `Money`.

**Change**: Update `_compare_value()` in `money.py` to accept `Decimal`, `int`, `float`.

### 1b. Reflected arithmetic with scalars
money-warp supports `Decimal("50") + Money("30")` and `100 - Money("30")`. quantum-money's `__radd__` only accepts `Money` (plus `0` for `sum()`).

**Change**: Update `__radd__` and `__rsub__` to handle `Decimal`, `int`, `float` by converting to `Money`.

### 1c. `debug_precision()` method
money-warp has `debug_precision()` → `"Internal: X | Real: Y"`.

**Change**: Add `debug_precision()` to `Money`.

### 1d. `pytest.approx` compatibility
money-warp's `Money` works with `pytest.approx`. This likely requires `__sub__` and `__abs__` to work with non-Money types, or registering with `numbers.Number`.

**Change**: Investigate and add `__float__` based approx support (already has `__float__`), may need `__sub__` to return a numeric for approx comparison.

---

## Step 2: Port and adapt money-warp tests

Replace `tests/test_money.py` with the money-warp test suite, adapted for quantum-money imports.

**Tests to port** (from money-warp's `test_money.py`):
- Creation: parametrized creation from `str`, `int`, `float`, `Decimal` ✓
- Precision: high-precision storage, rounding, `debug_precision()` ✓
- Arithmetic: add, sub, mul, div, negation, abs ✓
- Comparisons: Money vs Money, Money vs Decimal/int/float ✓
- Properties: cents, is_positive, is_negative, is_zero, to_real_money ✓
- Float conversion: parametrized ✓
- Display: str (comma-formatted), repr ✓
- Edge cases: very large, very small, negative zero, compound ops ✓
- Reflected arithmetic: radd, rsub, rmul with Decimal/int/float ✓
- pytest.approx compatibility ✓

**Adaptation needed**:
- Change `from money_warp.money import Money` → `from quantum_money import Money`
- Remove any tests for Rate/InterestRate (not in quantum-money)

---

## Step 3: Create SQLAlchemy `MoneyType` extension

**New files**:
- `src/quantum_money/ext/__init__.py`
- `src/quantum_money/ext/sa/__init__.py`
- `src/quantum_money/ext/sa/types.py`

**MoneyType** (from money-warp's `types.py`, only the Money part):
- `TypeDecorator` subclass wrapping `Numeric` or `Integer`
- Three representations: `"raw"`, `"real"`, `"cents"`
- Configurable `precision` and `scale` (default: 20, 10)
- `process_bind_param()`: Money → DB value
- `process_result_value()`: DB value → Money
- None passthrough

**pyproject.toml**: Add optional `[sa]` dependency group for `sqlalchemy`.

---

## Step 4: Create Marshmallow `MoneyField` extension

**New files**:
- `src/quantum_money/ext/marshmallow.py`

**MoneyField** (from money-warp's `marshmallow.py`, only the Money part):
- `marshmallow.fields.Field` subclass
- Four representations: `"raw"`, `"real"`, `"cents"`, `"float"`
- `_serialize()`: Money → serialized value
- `_deserialize()`: serialized value → Money
- None passthrough, validation

**pyproject.toml**: Add optional `[marshmallow]` dependency group for `marshmallow`.

---

## Step 5: Port SQLAlchemy MoneyType tests

**New file**: `tests/ext/__init__.py`, `tests/ext/sa/__init__.py`, `tests/ext/sa/conftest.py`, `tests/ext/sa/test_sa_money_type.py`

Adapted from money-warp's test suite:
- Constructor validation (valid/invalid representations)
- Round-trip persistence for raw, real, cents
- Precision/scale configuration
- None handling

Uses SQLite in-memory for simplicity.

---

## Step 6: Port Marshmallow MoneyField tests

**New file**: `tests/ext/test_marshmallow.py`

Adapted from money-warp's test suite (only MoneyField tests):
- Construction: valid/invalid representations
- Serialization: raw, real, cents, float modes
- Deserialization: all modes
- Round-trips: all modes
- Edge cases: None, zero, very large

---

## Step 7: Update pyproject.toml

- Add optional dependencies: `sqlalchemy` and `marshmallow`
- Add `marshmallow` and `sqlalchemy` to dev dependencies for testing

---

## Step 8: Run quality checks

- `uv run ruff check .`
- `uv run black .`
- `uv run pytest`

---

## File Summary

| Action | File |
|--------|------|
| Edit | `src/quantum_money/money.py` (cross-type comparisons, reflected arithmetic, debug_precision) |
| Edit | `tests/test_money.py` (replace with money-warp adapted tests) |
| Create | `src/quantum_money/ext/__init__.py` |
| Create | `src/quantum_money/ext/sa/__init__.py` |
| Create | `src/quantum_money/ext/sa/types.py` |
| Create | `src/quantum_money/ext/marshmallow.py` |
| Create | `tests/ext/__init__.py` |
| Create | `tests/ext/sa/__init__.py` |
| Create | `tests/ext/sa/conftest.py` |
| Create | `tests/ext/sa/test_sa_money_type.py` |
| Create | `tests/ext/test_marshmallow.py` |
| Edit | `pyproject.toml` (optional deps) |
