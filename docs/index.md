# quantum-money

**Lazy evaluation library for monetary calculations in Python.**

Like a quantum object that can be in many states before observation, quantum-money builds an expression tree of your calculations and only evaluates them when you call `.observe()`.

## The problem

In financial software, **rounding order changes results**. Consider a unit price of $1.345 multiplied by 10:

- Round first, then multiply: `round(1.345) × 10 = 1.35 × 10 = 13.50`
- Multiply first, then round: `round(1.345 × 10) = round(13.45) = 13.45`

A 5-cent difference from the same inputs. At scale, these discrepancies compound.

## The solution

quantum-money defers all computation until you explicitly call `.observe()`. You build an expression tree using normal Python operators, place `.round()` exactly where you want it, and evaluate everything at once.

```python
from decimal import Decimal, ROUND_HALF_UP
from quantum_money import QMoney

price = QMoney(Decimal("29.99"))
qty = 3
shipping = QMoney(Decimal("5.00"))
discount = QMoney(Decimal("2.50"))

total = (price * qty + shipping - discount).round(ROUND_HALF_UP)
result = total.observe().to_decimal()
# Decimal('92.47')
```

Nothing is calculated until `.observe()`. You have full control.

## Features

- **Lazy evaluation** — operations build an expression tree, computed only on `.observe()`
- **Rounding control** — place `.round()` anywhere in the expression with any strategy
- **Type safety** — requires `Decimal` inputs, blocks `float` and `int` conversion
- **Immutable** — all operations return new `QMoney` instances
- **Inspectable** — `repr()` shows the full expression tree
- **Hashable** — can be used in sets and as dict keys

## Next steps

<div class="grid cards" markdown>

-   **Getting started**

    ---

    Install quantum-money and write your first expression.

    [:octicons-arrow-right-24: Getting started](getting-started.md)

-   **Core concepts**

    ---

    Understand expression trees, lazy evaluation, and the observe pattern.

    [:octicons-arrow-right-24: Concepts](concepts.md)

-   **API reference**

    ---

    Complete reference for `QMoney`, exceptions, and node types.

    [:octicons-arrow-right-24: API reference](api-reference.md)

-   **Examples**

    ---

    Practical recipes for common financial calculations.

    [:octicons-arrow-right-24: Examples](examples.md)

</div>
