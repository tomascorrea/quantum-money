# API reference

## Money

```python
from quantum_money import Money
```

Eager monetary value with high internal precision. Computes immediately on every operation.

### Constructor

```python
Money(amount: Decimal | str | int | float)
```

Creates a Money from any numeric type. Floats are converted via `str()` to avoid precision issues.

```python
Money(Decimal("10.33"))   # From Decimal
Money("10.33")            # From string
Money(10)                 # From int
Money(10.33)              # From float (safe — goes through str)
```

---

### Factory methods

#### `Money.zero() -> Money`

Creates a Money with amount 0.

#### `Money.from_cents(cents: int) -> Money`

Creates a Money from an integer cent amount.

```python
Money.from_cents(1050)  # Money(10.50)
```

---

### Properties

#### `raw_amount -> Decimal`

The high-precision internal amount, exactly as stored.

#### `real_amount -> Decimal`

The amount rounded to 2 decimal places using `ROUND_HALF_UP`. Used for display and comparisons.

#### `cents -> int`

The `real_amount` expressed in cents.

```python
m = Money("10.335")
m.raw_amount    # Decimal('10.335')
m.real_amount   # Decimal('10.34')
m.cents         # 1034
```

---

### Arithmetic operators

| Operator | Expression | Description |
|---|---|---|
| `+` | `a + b` | Addition (Money + Money) |
| `-` | `a - b` | Subtraction (Money - Money) |
| `*` | `a * n` or `n * a` | Multiplication by scalar |
| `/` | `a / n` | Division by scalar |
| `-` | `-a` | Negation |
| `abs()` | `abs(a)` | Absolute value |
| `+` | `+a` | Identity (returns self) |

```python
sum([a, b, c])  # Works — uses __radd__ with 0
```

Scalars can be `int`, `float`, or `Decimal`.

---

### Comparisons

All comparisons use `real_amount` (2 decimal places):

| Operator | Description |
|---|---|
| `==` | Equal (at real_amount precision) |
| `<` | Less than |
| `<=` | Less than or equal |
| `>` | Greater than |
| `>=` | Greater than or equal |

```python
Money("10.334") == Money("10.33")   # True — same real_amount
Money("1.00") < Money("2.00")       # True
```

---

### Methods

#### `to_real_money() -> Money`

Returns a new Money rounded to 2 decimal places.

```python
Money("10.335").to_real_money()  # Money(10.34)
```

#### `is_positive() -> bool`

#### `is_negative() -> bool`

#### `is_zero() -> bool`

---

### Conversions

```python
float(money)   # Float representation
str(money)     # Display string (e.g., "10.33")
repr(money)    # "Money(10.33)"
```

---

## QMoney

```python
from quantum_money import QMoney
```

Lazy monetary value backed by an expression tree. All operations are deferred until `.observe()` is called.

### Constructor

```python
QMoney(value: Decimal)
```

Creates a `QMoney` from a `Decimal` value.

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

#### `observe() -> Money`

Evaluates the expression tree and returns a `Money` object containing the computed result.

```python
expr = QMoney(Decimal("10")) * 3
result = expr.observe()
# result is Money(30)
result.raw_amount  # Decimal('30')
```

Calling `.observe()` on the same expression multiple times is safe and produces the same result.

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

```python
val = QMoney(Decimal("16"))
val.root(2).observe().raw_amount  # Decimal('4') — square root
val.root(4).observe().raw_amount  # Decimal('2') — fourth root
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
| `float(qmoney)` | `TypeError` | Use `.observe()` instead |
| `int(qmoney)` | `TypeError` | Use `.observe()` instead |
| `bool(qmoney)` | `TypeError` | Observe and compare explicitly |
| `a < b`, `a <= b`, `a > b`, `a >= b` | `TypeError` | Observe first, then compare Money values |

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

Raised for observation-related errors.

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

Expression tree node types. All are NamedTuples (immutable and hashable). These are internal to the library but available for advanced use cases like custom tree walkers or serializers.

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
