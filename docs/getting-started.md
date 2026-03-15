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

## Two classes, two approaches

quantum-money provides **Money** for eager calculations and **QMoney** for lazy calculations with rounding control. They're connected: `QMoney.observe()` returns a `Money` object.

### Money — the simple path

```python
from quantum_money import Money

price = Money("10.33")
tax = Money("1.50")
total = price + tax

print(total.real_amount)  # Decimal('11.83')
print(total.cents)        # 1183
print(total)              # 11.83
```

Money accepts `Decimal`, `str`, `int`, or `float`. It maintains full internal precision and provides a rounded 2-decimal-place view for display and comparisons.

### QMoney — the lazy path

```python
from decimal import Decimal
from quantum_money import QMoney

price = QMoney(Decimal("10.33"))
tax = QMoney(Decimal("1.50"))

# Build an expression (nothing is calculated yet)
total = price + tax

# Evaluate when you're ready — returns a Money object
result = total.observe()
print(result.raw_amount)  # Decimal('11.83')
```

Three steps: **create**, **compose**, **observe**.

## Why Decimal for QMoney?

`QMoney` requires `Decimal` values, not `float` or `int`:

```python
# This works
QMoney(Decimal("10.33"))

# These raise TypeError
QMoney(10.33)   # float — loses precision
QMoney(10)      # int — use Decimal("10") instead
```

Floating-point arithmetic produces surprises like `0.1 + 0.2 = 0.30000000000000004`. QMoney enforces exact decimal arithmetic. Money is more lenient and converts inputs safely.

## Money arithmetic

```python
from quantum_money import Money

a = Money("100")
b = Money("5.50")

a + b         # Addition
a - b         # Subtraction
a * 3         # Multiply by scalar
a / 4         # Divide by scalar
-a            # Negation
abs(a)        # Absolute value
sum([a, b])   # Works with sum()
```

Money supports comparisons at `real_amount` (2 decimal place) precision:

```python
Money("10.334") < Money("10.335")  # True (10.33 < 10.34)
```

## QMoney arithmetic

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

## Rounding (QMoney)

Place `.round()` anywhere in the expression tree:

```python
from decimal import ROUND_HALF_UP, ROUND_DOWN

price = QMoney(Decimal("1.345"))

# Round at the end
(price * 10).round(ROUND_HALF_UP).observe().raw_amount
# Decimal('13.45')

# Round first
(price.round(ROUND_HALF_UP) * 10).observe().raw_amount
# Decimal('13.50')

# Different rounding strategy
(price * 10).round(ROUND_DOWN).observe().raw_amount
# Decimal('13.44')

# Custom decimal places
(price * 10).round(ROUND_HALF_UP, places=0).observe().raw_amount
# Decimal('13')
```

Default: `ROUND_HALF_UP` with 2 decimal places.

## The observe pattern

The key rule: **call `.observe()` to evaluate, then use Money properties**.

```python
expr = price * 3 + tax

# Evaluate the lazy tree → returns Money
result = expr.observe()

# Access the value through Money's properties
result.raw_amount    # Full precision Decimal
result.real_amount   # Rounded to 2 decimal places
result.cents         # Integer cents
```

## Inspecting expressions

Use `repr()` to see QMoney's expression tree:

```python
expr = (price * 3 + tax).round()
print(repr(expr))
# QMoney(round(((10.33 * 3) + 1.50), ROUND_HALF_UP, 2))
```

This is useful for debugging and understanding what will be computed.

## What's blocked on QMoney (and why)

Some operations are intentionally blocked because they don't make financial sense or could hide bugs:

| Operation | Why it's blocked |
|---|---|
| `QMoney * QMoney` | Dollars times dollars has no meaning |
| `QMoney / QMoney` | Use scalar division instead |
| `float(qmoney)` | Loses precision — use `.observe()` instead |
| `int(qmoney)` | Loses precision — use `.observe()` instead |
| `bool(qmoney)` | Ambiguous — observe and compare explicitly |
| `qmoney < other` | Meaningless on unevaluated trees — observe first |

## Next steps

- [Core concepts](concepts.md) — understand Money vs QMoney, expression trees, and lazy evaluation
- [API reference](api-reference.md) — complete method and class reference
- [Examples](examples.md) — practical recipes for financial calculations
