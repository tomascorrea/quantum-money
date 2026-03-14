# API reference

## QMoney

::: quantum_money.QMoney

```python
from quantum_money import QMoney
```

The main class. Represents a lazy monetary value backed by an expression tree.

### Constructor

```python
QMoney(value: Decimal)
```

Creates a `QMoney` from a `Decimal` value.

| Parameter | Type | Description |
|---|---|---|
| `value` | `Decimal` | The monetary amount. Must be a `Decimal`. |

**Raises:** `TypeError` if `value` is not a `Decimal`.

```python
from decimal import Decimal

price = QMoney(Decimal("10.33"))
zero = QMoney(Decimal("0"))

QMoney(10.33)  # TypeError: QMoney requires a Decimal
QMoney(10)     # TypeError: QMoney requires a Decimal
```

---

### Methods

#### `observe() -> QMoney`

Evaluates the expression tree and returns a new `QMoney` containing the computed result as a single `Value` node.

```python
expr = QMoney(Decimal("10")) * 3
result = expr.observe()
# result contains Value(Decimal('30'))
```

Idempotent — calling `.observe()` on an already-observed value is safe.

---

#### `to_decimal() -> Decimal`

Extracts the `Decimal` value. Only works on observed (single-value) `QMoney` instances.

**Raises:** `NotObservedError` if called on an unevaluated expression tree.

```python
value = expr.observe().to_decimal()
# Decimal('30')
```

---

#### `round(rounding: str = ROUND_HALF_UP, places: int = 2) -> QMoney`

Adds a rounding node to the expression tree. Does not evaluate — rounding is applied lazily during `.observe()`.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `rounding` | `str` | `ROUND_HALF_UP` | Rounding strategy. Any `decimal` module constant. |
| `places` | `int` | `2` | Number of decimal places. |

```python
from decimal import ROUND_HALF_UP, ROUND_DOWN, ROUND_HALF_EVEN

price = QMoney(Decimal("1.345"))

price.round()                            # ROUND_HALF_UP, 2 places
price.round(ROUND_DOWN)                  # ROUND_DOWN, 2 places
price.round(ROUND_HALF_EVEN, places=4)   # ROUND_HALF_EVEN, 4 places
price.round(ROUND_HALF_UP, places=0)     # Round to whole number
```

---

#### `root(n: int | Decimal) -> QMoney`

Adds an nth-root node to the expression tree.

| Parameter | Type | Description |
|---|---|---|
| `n` | `int \| Decimal` | The root index. |

```python
val = QMoney(Decimal("16"))
val.root(2).observe().to_decimal()  # Square root → 4
val.root(4).observe().to_decimal()  # Fourth root → 2
```

---

### Arithmetic operators

#### QMoney with QMoney

| Operator | Expression | Description |
|---|---|---|
| `+` | `a + b` | Addition |
| `-` | `a - b` | Subtraction |

Both operands must be `QMoney`.

#### QMoney with scalars

| Operator | Expression | Description |
|---|---|---|
| `*` | `a * n` or `n * a` | Multiplication by `int` or `Decimal` |
| `/` | `a / n` | Division by `int` or `Decimal` |
| `**` | `a ** n` | Power with `int` or `Decimal` exponent |

#### Unary operators

| Operator | Expression | Description |
|---|---|---|
| `-` | `-a` | Negation (equivalent to `a * -1`) |
| `+` | `+a` | Identity (returns `self`) |

#### Built-in support

```python
sum([a, b, c])  # Works — uses __radd__ with 0
```

---

### Blocked operations

These raise `TypeError` or `InvalidOperationError`:

| Operation | Error | Reason |
|---|---|---|
| `QMoney * QMoney` | `InvalidOperationError` | No financial meaning |
| `QMoney / QMoney` | `InvalidOperationError` | No financial meaning |
| `QMoney ** QMoney` | `InvalidOperationError` | No financial meaning |
| `float(qmoney)` | `TypeError` | Use `.observe().to_decimal()` |
| `int(qmoney)` | `TypeError` | Use `.observe().to_decimal()` |
| `bool(qmoney)` | `TypeError` | Observe and compare explicitly |
| `a < b`, `a <= b`, `a > b`, `a >= b` | `TypeError` | Observe first, then compare decimals |

---

### Equality and hashing

```python
a == b     # Compares expression trees structurally
hash(a)    # Hashable — can be used in sets/dicts
```

Equality compares tree structure, not computed values. Two different expressions that produce the same result are **not** equal.

---

### repr

```python
repr(a)    # Human-readable expression tree
# "QMoney((10.33 * 3))"
```

---

## Exceptions

```python
from quantum_money import QuantumMoneyError, NotObservedError, InvalidOperationError
```

### QuantumMoneyError

```python
class QuantumMoneyError(Exception)
```

Base exception for all quantum-money errors. Catch this to handle any library error.

---

### NotObservedError

```python
class NotObservedError(QuantumMoneyError)
```

Raised when `.to_decimal()` is called on a `QMoney` with an unevaluated expression tree. Fix by calling `.observe()` first.

```python
expr = QMoney(Decimal("10")) + QMoney(Decimal("5"))
expr.to_decimal()  # Raises NotObservedError
```

---

### InvalidOperationError

```python
class InvalidOperationError(QuantumMoneyError)
```

Raised when an unsupported operation is attempted, such as multiplying two `QMoney` values.

```python
a = QMoney(Decimal("10"))
b = QMoney(Decimal("5"))
a * b  # Raises InvalidOperationError
```

---

## Node types

```python
from quantum_money.nodes import Value, Add, Sub, Mul, Div, Pow, Root, Round, Node
```

Expression tree node types. All are frozen dataclasses (immutable and hashable). These are internal to the library but available for advanced use cases like custom tree walkers or serializers.

| Node | Fields | Description |
|---|---|---|
| `Value` | `amount: Decimal` | A literal monetary value |
| `Add` | `left: Node`, `right: Node` | Addition |
| `Sub` | `left: Node`, `right: Node` | Subtraction |
| `Mul` | `node: Node`, `factor: Decimal` | Scalar multiplication |
| `Div` | `node: Node`, `divisor: Decimal` | Scalar division |
| `Pow` | `node: Node`, `exponent: Decimal` | Exponentiation |
| `Root` | `node: Node`, `index: Decimal` | Nth root |
| `Round` | `node: Node`, `rounding: str`, `places: int` | Rounding |

The `Node` type alias is:

```python
Node = Value | Add | Sub | Mul | Div | Pow | Root | Round
```
