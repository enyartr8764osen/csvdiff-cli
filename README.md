# csvdiff-cli

A command-line tool for diffing large CSV files with configurable key columns and output formats.

---

## Installation

```bash
pip install csvdiff-cli
```

Or install from source:

```bash
git clone https://github.com/yourname/csvdiff-cli.git
cd csvdiff-cli
pip install .
```

---

## Usage

```bash
csvdiff [OPTIONS] FILE_A FILE_B
```

**Basic example:**

```bash
csvdiff old_data.csv new_data.csv --key id
```

**Specify multiple key columns and output format:**

```bash
csvdiff old_data.csv new_data.csv --key id,date --output json
```

**Options:**

| Flag | Description |
|------|-------------|
| `--key` | Comma-separated column(s) to use as the row key |
| `--output` | Output format: `text` (default), `json`, or `csv` |
| `--ignore` | Comma-separated columns to ignore during comparison |
| `--added` | Show only added rows |
| `--removed` | Show only removed rows |
| `--changed` | Show only changed rows |

**Example output:**

```
[ADDED]   id=42  name=Alice  age=30
[REMOVED] id=7   name=Bob    age=25
[CHANGED] id=15  email: old@example.com -> new@example.com
```

---

## Requirements

- Python 3.8+
- No external dependencies for core functionality

---

## License

This project is licensed under the [MIT License](LICENSE).