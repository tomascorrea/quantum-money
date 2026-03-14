# quantum-money

Lazy evaluation library for monetary calculations in Python.

Like a quantum object that can be in many states before observation, quantum-money builds an expression tree of your calculations and only evaluates them when you call `.observe()`. This gives you full control over when and how rounding is applied — which matters, because **rounding order changes results**.

## Why?

```python
from decimal import Decimal, ROUND_HALF_UP
from quantum_money import QMoney

unit_price = QMoney(Decimal("1.345"))

# Round first, then multiply → 13.50
round_first = (unit_price.round(ROUND_HALF_UP) * 10).observe().to_decimal()

# Multiply first, then round → 13.45
round_last = (unit_price * 10).round(ROUND_HALF_UP).observe().to_decimal()

assert round_first != round_last  # Rounding order matters!
```

With quantum-money, you decide exactly where rounding happens in your calculations.

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

```python
from decimal import Decimal
from quantum_money import QMoney

# Create monetary values (must use Decimal)
price = QMoney(Decimal("29.99"))
tax = QMoney(Decimal("2.40"))

# Build an expression tree — nothing is calculated yet
total = price + tax
print(repr(total))  # QMoney((29.99 + 2.40))

# Evaluate when you're ready
result = total.observe().to_decimal()
print(result)  # 32.39
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

### The observe/to_decimal pattern

```python
# Build expression (lazy)
expr = price * 3 + tax

# Evaluate the tree
observed = expr.observe()

# Extract the Decimal
value = observed.to_decimal()
```

Calling `.to_decimal()` on an unevaluated expression raises `NotObservedError` — this prevents accidental use of intermediate values.

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
