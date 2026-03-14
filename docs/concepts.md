# Core concepts

## Expression trees

When you write `price + tax`, quantum-money does not compute the sum. Instead, it creates a tree node that records "add these two things." Each operation adds a new node to the tree.

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

All nodes are **frozen dataclasses** — immutable and hashable. This means expression trees can be compared for equality and used as dictionary keys.

## Lazy evaluation

"Lazy" means computation is deferred. No arithmetic happens until you call `.observe()`.

This is the opposite of how Python normally works:

```python
# Standard Python: computed immediately
result = 29.99 * 3 + 2.40  # result is 92.37 right now

# quantum-money: deferred
result = price * 3 + tax    # result is an expression tree
value = result.observe()     # NOW it computes 92.37
```

### Why defer computation?

**Rounding control.** In financial calculations, when you round matters as much as how you round. By deferring computation, you can place `.round()` at any point in the tree and know exactly when it will be applied.

**Auditability.** The expression tree is a complete record of the calculation. You can inspect it with `repr()` before evaluating.

**Correctness.** Intermediate rounding can silently change results. By making rounding explicit and visible in the tree, quantum-money prevents accidental rounding.

## The observe pattern

`.observe()` evaluates the tree recursively and returns a new `QMoney` containing just the result:

```python
expr = price * 3 + tax
# expr._node is Add(Mul(Value(29.99), 3), Value(2.40))

observed = expr.observe()
# observed._node is Value(92.37)
```

After observation, the `QMoney` collapses from a complex tree to a single `Value` node — much like a quantum measurement collapsing a superposition into a definite state.

### observe then to_decimal

To get a Python `Decimal` out, call `.to_decimal()` on an observed value:

```python
result = expr.observe().to_decimal()
# Decimal('92.37')
```

Calling `.to_decimal()` on an unobserved expression raises `NotObservedError`. This is a safety mechanism — it forces you to be explicit about when evaluation happens.

### Idempotent observation

Calling `.observe()` on an already-observed `QMoney` is safe and returns the same value:

```python
a = expr.observe()
b = a.observe()
a.to_decimal() == b.to_decimal()  # True
```

## Immutability

Every operation returns a **new** `QMoney`. Nothing is ever modified in place:

```python
price = QMoney(Decimal("10"))
doubled = price * 2
# price is unchanged — still QMoney(10)
# doubled is a new QMoney(10 * 2)
```

This makes quantum-money safe to use in concurrent code and eliminates an entire class of bugs related to shared mutable state.

## Equality and hashing

Two `QMoney` values are equal if their expression trees are structurally identical:

```python
a = QMoney(Decimal("10")) + QMoney(Decimal("5"))
b = QMoney(Decimal("10")) + QMoney(Decimal("5"))
a == b  # True — same tree structure

c = QMoney(Decimal("5")) + QMoney(Decimal("10"))
a == c  # False — different tree structure (addition is not reordered)
```

Note: equality compares **trees**, not **results**. Two different expressions that produce the same number are not equal as `QMoney` objects. To compare results, observe both and compare the `Decimal` values.

## Type safety

quantum-money is deliberately strict about types:

- **Requires `Decimal`** — prevents float precision bugs from entering the system
- **Blocks `QMoney * QMoney`** — dollars times dollars has no financial meaning
- **Blocks `float()` / `int()` / `bool()`** — forces explicit conversion through `.observe().to_decimal()`
- **Blocks comparisons** (`<`, `>`, etc.) — meaningless on unevaluated trees

These restrictions exist to catch bugs at the point where they're introduced, not downstream where they're harder to diagnose.
