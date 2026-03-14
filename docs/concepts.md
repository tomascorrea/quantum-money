# Core concepts

## Money vs QMoney

quantum-money provides two classes for different needs:

| | Money | QMoney |
|---|---|---|
| **Evaluation** | Eager — computes immediately | Lazy — defers until `.observe()` |
| **Input types** | `Decimal`, `str`, `int`, `float` | `Decimal` only |
| **Rounding** | Automatic via `real_amount` | Explicit via `.round()` in the tree |
| **Comparisons** | Full (`<`, `>`, `==`, etc.) | Only `==` (tree structure) |
| **Use case** | General monetary arithmetic | Rounding-sensitive calculations |

The bridge between them: `QMoney.observe()` returns a `Money` object.

```python
from decimal import Decimal
from quantum_money import Money, QMoney

# Money: immediate
total = Money("29.99") * 3
print(total.real_amount)  # Decimal('89.97')

# QMoney: deferred, then becomes Money
result = (QMoney(Decimal("29.99")) * 3).observe()
print(result.real_amount)  # Decimal('89.97')
assert isinstance(result, Money)
```

## Money: high-precision eager values

Money maintains **full internal precision** (`raw_amount`) while providing a **rounded display** (`real_amount`) at 2 decimal places using ROUND_HALF_UP.

```python
from quantum_money import Money

m = Money("10.335")
m.raw_amount    # Decimal('10.335')  — full precision
m.real_amount   # Decimal('10.34')   — rounded for display
m.cents         # 1034
```

Comparisons use `real_amount`, so values that round to the same 2-decimal-place amount are considered equal:

```python
Money("10.335") == Money("10.336")  # True — both round to 10.34
```

## Expression trees

When you write `price + tax` with QMoney, no sum is computed. Instead, a tree node records "add these two things." Each operation adds a new node.

```python
from decimal import Decimal
from quantum_money import QMoney

price = QMoney(Decimal("29.99"))
tax = QMoney(Decimal("2.40"))
total = (price * 3 + tax).round()
```

This builds the following tree:

```
Round(ROUND_HALF_UP, 2)
└── Add
    ├── Mul(factor=3)
    │   └── Value(29.99)
    └── Value(2.40)
```

You can see it with `repr()`:

```python
print(repr(total))
# QMoney(round(((29.99 * 3) + 2.40), ROUND_HALF_UP, 2))
```

## Node types

Each operation creates a specific node type:

| Node | Created by | Fields |
|---|---|---|
| `Value` | `QMoney(Decimal(...))` | `amount` |
| `Add` | `a + b` | `left`, `right` |
| `Sub` | `a - b` | `left`, `right` |
| `Mul` | `a * scalar` | `node`, `factor` |
| `Div` | `a / scalar` | `node`, `divisor` |
| `Pow` | `a ** scalar` | `node`, `exponent` |
| `Root` | `a.root(n)` | `node`, `index` |
| `Round` | `a.round(...)` | `node`, `rounding`, `places` |

All nodes are **NamedTuples** — immutable and hashable. Expression trees can be compared for equality and used as dictionary keys.

## Lazy evaluation

"Lazy" means computation is deferred. No arithmetic happens until you call `.observe()`.

This is the opposite of how Python normally works:

```python
# Standard Python: computed immediately
result = 29.99 * 3 + 2.40  # result is 92.37 right now

# quantum-money: deferred
result = price * 3 + tax    # result is an expression tree
value = result.observe()     # NOW it computes → returns Money
```

### Why defer computation?

**Rounding control.** In financial calculations, when you round matters as much as how you round. By deferring computation, you can place `.round()` at any point in the tree and know exactly when it will be applied.

**Auditability.** The expression tree is a complete record of the calculation. You can inspect it with `repr()` before evaluating.

**Correctness.** Intermediate rounding can silently change results. By making rounding explicit and visible in the tree, quantum-money prevents accidental rounding.

## The observe pattern

`.observe()` evaluates the tree recursively and returns a `Money` object:

```python
expr = price * 3 + tax
# expr._node is Add(Mul(Value(29.99), 3), Value(2.40))

result = expr.observe()
# result is Money(92.37)

result.raw_amount    # Decimal('92.37')
result.real_amount   # Decimal('92.37')
result.cents         # 9237
```

After observation, the QMoney collapses from a complex tree into a concrete Money value — much like a quantum measurement collapsing a superposition into a definite state.

### Idempotent observation

Calling `.observe()` multiple times on the same expression is safe:

```python
a = expr.observe()
b = expr.observe()
assert a.raw_amount == b.raw_amount  # True
```

## Immutability

Every operation returns a **new** object. Nothing is ever modified in place:

```python
price = QMoney(Decimal("10"))
doubled = price * 2
# price is unchanged — still QMoney(10)
# doubled is a new QMoney(10 * 2)

m = Money("10")
total = m + Money("5")
# m is unchanged — still Money(10)
```

This makes quantum-money safe to use in concurrent code.

## QMoney equality and hashing

Two `QMoney` values are equal if their expression trees are structurally identical:

```python
a = QMoney(Decimal("10")) + QMoney(Decimal("5"))
b = QMoney(Decimal("10")) + QMoney(Decimal("5"))
a == b  # True — same tree structure

c = QMoney(Decimal("5")) + QMoney(Decimal("10"))
a == c  # False — different tree structure (addition is not reordered)
```

Equality compares **trees**, not **results**. To compare results, observe both and compare the Money objects.

## Type safety

quantum-money is deliberately strict about types on QMoney:

- **Requires `Decimal`** — prevents float precision bugs from entering the system
- **Blocks `QMoney * QMoney`** — dollars times dollars has no financial meaning
- **Blocks `float()` / `int()` / `bool()`** — forces evaluation through `.observe()`
- **Blocks comparisons** (`<`, `>`, etc.) — meaningless on unevaluated trees

Money is more permissive, accepting multiple input types and supporting full comparisons.
