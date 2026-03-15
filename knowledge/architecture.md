# Architecture

Like a quantum object that can be in many states before observation, quantum-money only performs its calculations when someone tries to observe the value.

## Package Structure

```
src/
└── quantum_money/
    ├── __init__.py          # Public API: Money, QMoney, errors
    ├── money.py             # Eager Money class (high-precision Decimal)
    ├── qmoney.py            # Lazy QMoney class (expression tree, observe to evaluate)
    ├── nodes.py             # Expression tree node types for QMoney
    ├── errors.py            # Custom exceptions
    └── ext/
        ├── __init__.py
        ├── sa/
        │   ├── __init__.py  # Exports MoneyType
        │   └── types.py     # SQLAlchemy TypeDecorator for Money
        └── marshmallow.py   # Marshmallow MoneyField
```

## Core Design Decisions

### Two Money Types
`Money` is eager — all arithmetic happens immediately on `Decimal`. `QMoney` is lazy — it builds an expression tree and only evaluates when `.observe()` is called. This allows testing rounding-order effects.

### High-Precision Internals, 2dp Display
`Money` stores the full `Decimal` precision internally (`raw_amount`) but rounds to 2 decimal places (`real_amount`) for display, comparison, and cents. `ROUND_HALF_UP` is used.

### Cross-Type Interoperability
`Money` supports comparison and reflected arithmetic (`__radd__`, `__rsub__`, `__rmul__`) with `Decimal`, `int`, and `float`. It is registered as `numbers.Real` for `pytest.approx` compatibility.

### Optional Extensions
SQLAlchemy and Marshmallow integrations live under `ext/` with optional dependency groups (`quantum-money[sa]`, `quantum-money[marshmallow]`). Both support multiple storage representations: `raw`, `real`, `cents` (and `float` for Marshmallow).

## Component Relationships

```
User code
    │
    ├── Money  ← eager, Decimal-based
    │     ├── ext.sa.MoneyType       ← SQLAlchemy TypeDecorator
    │     └── ext.marshmallow.MoneyField  ← Marshmallow Field
    │
    └── QMoney ← lazy, expression-tree
          ├── nodes.*  ← Value, Add, Sub, Mul, Div, Pow, Root, Round
          └── .observe() → Money
```
