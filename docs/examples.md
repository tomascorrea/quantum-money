# Examples

Practical recipes for common financial calculations with quantum-money.

## Invoice total with tax

```python
from decimal import Decimal, ROUND_HALF_UP
from quantum_money import QMoney

line_items = [
    QMoney(Decimal("29.99")),
    QMoney(Decimal("14.50")),
    QMoney(Decimal("7.25")),
]

subtotal = sum(line_items)
tax_rate = Decimal("0.0825")  # 8.25%
tax = subtotal * tax_rate
total = (subtotal + tax).round(ROUND_HALF_UP)

result = total.observe().to_decimal()
# Decimal('55.91')
```

## Discount then tax vs. tax then discount

The order of operations produces different totals. quantum-money lets you choose explicitly.

```python
from decimal import Decimal, ROUND_HALF_UP
from quantum_money import QMoney

price = QMoney(Decimal("99.99"))
discount = Decimal("0.90")   # 10% off
tax = Decimal("1.08")        # 8% tax

# Discount first, then tax
option_a = (price * discount * tax).round(ROUND_HALF_UP).observe().to_decimal()

# Tax first, then discount
option_b = (price * tax * discount).round(ROUND_HALF_UP).observe().to_decimal()

# Same result here because multiplication is associative,
# but rounding at different points would change results:
option_c = ((price * discount).round(ROUND_HALF_UP) * tax).round(ROUND_HALF_UP).observe().to_decimal()
option_d = ((price * tax).round(ROUND_HALF_UP) * discount).round(ROUND_HALF_UP).observe().to_decimal()
```

## Splitting a bill

```python
from decimal import Decimal, ROUND_HALF_UP
from quantum_money import QMoney

total = QMoney(Decimal("100.00"))
people = 3

per_person = (total / people).round(ROUND_HALF_UP).observe().to_decimal()
# Decimal('33.33')

# Note: 33.33 * 3 = 99.99, not 100.00
# Handle the remainder explicitly:
remainder = (total - QMoney(per_person) * people).observe().to_decimal()
# Decimal('0.01')
```

## Compound interest

```python
from decimal import Decimal, ROUND_HALF_UP
from quantum_money import QMoney

principal = QMoney(Decimal("1000.00"))
rate = Decimal("1.05")  # 5% annual rate
years = 3

# Compound: principal * (1 + rate)^years
future_value = (principal * rate ** years).round(ROUND_HALF_UP)
result = future_value.observe().to_decimal()
# Decimal('1157.63')
```

## Rounding strategies compared

Python's `decimal` module supports several rounding modes. Here's how they differ:

```python
from decimal import (
    Decimal,
    ROUND_HALF_UP,
    ROUND_HALF_DOWN,
    ROUND_HALF_EVEN,
    ROUND_DOWN,
    ROUND_UP,
)
from quantum_money import QMoney

price = QMoney(Decimal("2.345"))

strategies = {
    "ROUND_HALF_UP":   ROUND_HALF_UP,    # 2.35 (round 5 up)
    "ROUND_HALF_DOWN": ROUND_HALF_DOWN,   # 2.34 (round 5 down)
    "ROUND_HALF_EVEN": ROUND_HALF_EVEN,   # 2.34 (banker's rounding)
    "ROUND_DOWN":      ROUND_DOWN,        # 2.34 (truncate)
    "ROUND_UP":        ROUND_UP,          # 2.35 (always round away from zero)
}

for name, strategy in strategies.items():
    result = price.round(strategy).observe().to_decimal()
    print(f"{name}: {result}")
```

## Chained operations with intermediate rounding

```python
from decimal import Decimal, ROUND_HALF_UP
from quantum_money import QMoney

# Simulate a multi-step pricing calculation
base_price = QMoney(Decimal("49.99"))
markup = Decimal("1.30")           # 30% markup
bulk_discount = Decimal("0.85")    # 15% discount
tax = Decimal("1.0725")            # 7.25% tax

# Round after each step (common in invoicing)
after_markup = (base_price * markup).round(ROUND_HALF_UP)
after_discount = (after_markup * bulk_discount).round(ROUND_HALF_UP)
final = (after_discount * tax).round(ROUND_HALF_UP)

result = final.observe().to_decimal()

# Compare: no intermediate rounding
no_rounding = (base_price * markup * bulk_discount * tax).round(ROUND_HALF_UP)
result_no_rounding = no_rounding.observe().to_decimal()

# These will typically differ due to intermediate rounding
```

## Inspecting the expression tree

```python
from decimal import Decimal, ROUND_HALF_UP
from quantum_money import QMoney

price = QMoney(Decimal("29.99"))
qty = 3
shipping = QMoney(Decimal("5.00"))

expr = (price * qty + shipping).round(ROUND_HALF_UP)

# See the full expression tree
print(repr(expr))
# QMoney(round(((29.99 * 3) + 5.00), ROUND_HALF_UP, 2))
```

## Using QMoney in collections

Since `QMoney` is hashable, it works with sets and dicts:

```python
from decimal import Decimal
from quantum_money import QMoney

prices = {
    QMoney(Decimal("9.99")): "Basic",
    QMoney(Decimal("19.99")): "Pro",
    QMoney(Decimal("49.99")): "Enterprise",
}

unique_totals = {
    (QMoney(Decimal("9.99")) + QMoney(Decimal("1.00"))),
    (QMoney(Decimal("9.99")) + QMoney(Decimal("1.00"))),  # Duplicate — deduped
}
assert len(unique_totals) == 1
```

## Error handling

```python
from decimal import Decimal
from quantum_money import QMoney, NotObservedError, InvalidOperationError

price = QMoney(Decimal("10.00"))
tax = QMoney(Decimal("1.50"))

# Catch unevaluated access
try:
    value = (price + tax).to_decimal()
except NotObservedError:
    value = (price + tax).observe().to_decimal()

# Catch invalid operations
try:
    result = price * tax  # QMoney * QMoney
except InvalidOperationError as e:
    print(f"Invalid: {e}")
```
