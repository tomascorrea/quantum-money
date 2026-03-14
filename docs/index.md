# quantum-money

**Eager and lazy evaluation library for monetary calculations in Python.**

quantum-money provides two complementary classes:

- **Money** — eager evaluation with high internal precision, rounded display, and full comparison support.
- **QMoney** — lazy evaluation via expression trees, giving full control over when and how rounding is applied.

`QMoney.observe()` returns a `Money` object, creating a natural bridge from lazy to eager.

## The problem

In financial software, **rounding order changes results**. Consider a unit price of $1.345 multiplied by 10:

- Round first, then multiply: `round(1.345) × 10 = 1.35 × 10 = 13.50`
- Multiply first, then round: `round(1.345 × 10) = round(13.45) = 13.45`

A 5-cent difference from the same inputs. At scale, these discrepancies compound.

## The solution

**Money** handles straightforward calculations where you don't need rounding control:

```python
from quantum_money import Money

price = Money("29.99")
total = price * 3 + Money("5.00")
print(total.real_amount)  # Decimal('94.97')
```

**QMoney** defers all computation until you explicitly call `.observe()`. You build an expression tree, place `.round()` exactly where you want it, and evaluate everything at once:

```python
from decimal import Decimal, ROUND_HALF_UP
from quantum_money import QMoney

price = QMoney(Decimal("29.99"))
qty = 3
shipping = QMoney(Decimal("5.00"))
discount = QMoney(Decimal("2.50"))

total = (price * qty + shipping - discount).round(ROUND_HALF_UP)
result = total.observe()
print(result.raw_amount)  # Decimal('92.47')
```

Nothing is calculated until `.observe()`. You have full control.

## Features

- **Two classes** — Money (eager) and QMoney (lazy) for different use cases
- **Natural bridge** — `QMoney.observe()` returns a `Money` object
- **High precision** — Money keeps full internal precision, rounds only for display
- **Rounding control** — QMoney lets you place `.round()` anywhere in the expression
- **Type safety** — QMoney requires `Decimal` inputs; Money accepts `Decimal`, `str`, `int`, `float`
- **Immutable** — all operations return new instances
- **Inspectable** — `repr()` shows QMoney's full expression tree

## Next steps

<div class="grid cards" markdown>

-   **Getting started**

    ---

    Install quantum-money and write your first expression.

    [:octicons-arrow-right-24: Getting started](getting-started.md)

-   **Core concepts**

    ---

    Understand Money vs QMoney, expression trees, and the observe pattern.

    [:octicons-arrow-right-24: Concepts](concepts.md)

-   **API reference**

    ---

    Complete reference for `Money`, `QMoney`, exceptions, and node types.

    [:octicons-arrow-right-24: API reference](api-reference.md)

-   **Examples**

    ---

    Practical recipes for common financial calculations.

    [:octicons-arrow-right-24: Examples](examples.md)

</div>
