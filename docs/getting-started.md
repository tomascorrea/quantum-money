# Getting started

## Installation

Install with pip:

```bash
pip install quantum-money
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add quantum-money
```

Requires **Python 3.12** or later. No runtime dependencies beyond the standard library.

## Your first expression

```python
from decimal import Decimal
from quantum_money import QMoney

# Create monetary values — always use Decimal
price = QMoney(Decimal("10.33"))
tax = QMoney(Decimal("1.50"))

# Build an expression (nothing is calculated yet)
total = price + tax

# Evaluate when you're ready
result = total.observe().to_decimal()
print(result)  # 11.83
```

Three steps: **create**, **compose**, **observe**.

## Why Decimal?

`QMoney` requires `Decimal` values, not `float` or `int`:

```python
# This works
QMoney(Decimal("10.33"))

# These raise TypeError
QMoney(10.33)   # float — loses precision
QMoney(10)      # int — use Decimal("10") instead
```

Floating-point arithmetic produces surprises like `0.1 + 0.2 = 0.30000000000000004`. Financial calculations need exact decimal arithmetic, which Python's `decimal` module provides.

## Arithmetic operations

### QMoney with QMoney

```python
a = QMoney(Decimal("100"))
b = QMoney(Decimal("5.50"))

a + b    # Addition
a - b    # Subtraction
```

### QMoney with scalars

Multiply, divide, and exponentiate with `int` or `Decimal`:

```python
a * 3                     # Multiply by int
a * Decimal("1.08")       # Multiply by Decimal
a / 4                     # Divide by int
a ** 2                    # Power
a.root(2)                 # Nth root
```

### Other operations

```python
-a                        # Negation
+a                        # Identity (returns self)
sum([a, b, a])            # Works with sum()
```

## Rounding

Place `.round()` anywhere in the expression tree:

```python
from decimal import ROUND_HALF_UP, ROUND_DOWN

price = QMoney(Decimal("1.345"))

# Round at the end
(price * 10).round(ROUND_HALF_UP).observe().to_decimal()
# Decimal('13.45')

# Round first
(price.round(ROUND_HALF_UP) * 10).observe().to_decimal()
# Decimal('13.50')

# Different rounding strategy
(price * 10).round(ROUND_DOWN).observe().to_decimal()
# Decimal('13.44')

# Custom decimal places
(price * 10).round(ROUND_HALF_UP, places=0).observe().to_decimal()
# Decimal('13')
```

Default: `ROUND_HALF_UP` with 2 decimal places.

## The observe pattern

The key rule: **call `.observe()` before `.to_decimal()`**.

```python
expr = price * 3 + tax

# This works
value = expr.observe().to_decimal()

# This raises NotObservedError
value = expr.to_decimal()  # Error! Expression not evaluated yet.
```

This is intentional. It prevents you from accidentally extracting a value from an unevaluated expression, which would be a bug in financial code.

## Inspecting expressions

Use `repr()` to see the expression tree:

```python
expr = (price * 3 + tax).round()
print(repr(expr))
# QMoney(round(((10.33 * 3) + 1.50), ROUND_HALF_UP, 2))
```

This is useful for debugging and understanding what will be computed.

## What's blocked (and why)

Some operations are intentionally blocked because they don't make financial sense or could hide bugs:

| Operation | Why it's blocked |
|---|---|
| `QMoney * QMoney` | Dollars times dollars has no meaning |
| `QMoney / QMoney` | Use scalar division instead |
| `float(qmoney)` | Loses precision — use `.observe().to_decimal()` |
| `int(qmoney)` | Loses precision — use `.observe().to_decimal()` |
| `bool(qmoney)` | Ambiguous — observe and compare explicitly |
| `qmoney < other` | Meaningless on unevaluated trees — observe first |

## Next steps

- [Core concepts](concepts.md) — understand expression trees and lazy evaluation
- [API reference](api-reference.md) — complete method and class reference
- [Examples](examples.md) — practical recipes for financial calculations
