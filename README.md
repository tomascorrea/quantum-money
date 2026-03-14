# quantum-money

Eager and lazy evaluation library for monetary calculations in Python.

quantum-money provides two classes: **Money** for straightforward calculations with high internal precision, and **QMoney** for lazy evaluation where you need full control over rounding order. QMoney builds an expression tree and only evaluates when you call `.observe()`, which returns a `Money` object.

## Why?

In financial software, **rounding order changes results**:

```python
from decimal import Decimal, ROUND_HALF_UP
from quantum_money import QMoney

unit_price = QMoney(Decimal("1.345"))

# Round first, then multiply → 13.50
round_first = (unit_price.round(ROUND_HALF_UP) * 10).observe().raw_amount

# Multiply first, then round → 13.45
round_last = (unit_price * 10).round(ROUND_HALF_UP).observe().raw_amount

assert round_first != round_last  # Rounding order matters!
```

With quantum-money, you decide exactly where rounding happens.

## Installation

```bash
pip install quantum-money
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add quantum-money
```

Requires Python 3.12+.

## Quick start

### Money — eager calculations

```python
from quantum_money import Money

price = Money("29.99")
tax = Money("2.40")

total = price + tax
print(total.real_amount)  # 32.39
print(total.cents)        # 3239
```

Money accepts `Decimal`, `str`, `int`, or `float`. It maintains full internal precision (`raw_amount`) and provides a rounded 2-decimal-place view (`real_amount`).

### QMoney — lazy calculations with rounding control

```python
from decimal import Decimal
from quantum_money import QMoney

# Create monetary values (must use Decimal)
price = QMoney(Decimal("29.99"))
tax = QMoney(Decimal("2.40"))

# Build an expression tree — nothing is calculated yet
total = price + tax
print(repr(total))  # QMoney((29.99 + 2.40))

# Evaluate when you're ready — returns a Money object
result = total.observe()
print(result.raw_amount)  # 32.39
```

### The bridge: QMoney → Money

`.observe()` evaluates the expression tree and returns a `Money` object:

```python
from decimal import Decimal, ROUND_HALF_UP
from quantum_money import Money, QMoney

# Build a lazy expression
expr = (QMoney(Decimal("10.33")) * 3).round(ROUND_HALF_UP)

# Observe collapses QMoney → Money
result = expr.observe()
assert isinstance(result, Money)

print(result.raw_amount)   # Decimal('30.99')
print(result.real_amount)  # Decimal('30.99')
print(result.cents)        # 3099
```

### Supported operations

```python
a = QMoney(Decimal("100"))
b = QMoney(Decimal("5.50"))

a + b           # Addition
a - b           # Subtraction
a * 3           # Multiply by scalar (int or Decimal)
a / 4           # Divide by scalar
a ** 2          # Power
a.root(2)       # Nth root
-a              # Negation
a.round()       # Round (default: ROUND_HALF_UP, 2 places)
sum([a, b])     # Works with sum()
```

## Documentation

Full documentation: [quantum-money docs](https://your-username.github.io/quantum-money/)

## Development

```bash
git clone https://github.com/your-username/quantum-money.git
cd quantum-money
uv sync --dev
```

```bash
uv run pytest              # Run tests
uv run ruff check .        # Lint
uv run black .             # Format
uv run mkdocs serve        # Serve docs locally
```

## License

MIT
