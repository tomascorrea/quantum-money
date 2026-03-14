# quantum-money

Like a quantum object that can be in many states before observation, quantum-money only performs its calculations when someone tries to observe the value.

## Installation

```bash
pip install quantum-money
```

Or with uv:

```bash
uv add quantum-money
```

## Usage

```python
import quantum_money
```

## Development

### Setup

```bash
git clone https://github.com/your-username/quantum-money.git
cd quantum-money
uv sync --dev
```

### Run tests

```bash
uv run pytest
```

### Lint and format

```bash
uv run ruff check .
uv run black .
```

### Build docs

```bash
uv run mkdocs serve
```

## License

MIT
