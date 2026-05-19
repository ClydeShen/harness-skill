# Python Snippets

Paste-ready configs for Python projects. Uses `uv` for package management,
`ruff` for linting/formatting, and `mypy` for type checking.

---

## pyproject.toml — ruff + mypy baseline

Add to your existing `pyproject.toml`, or create it if absent.

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]  # line length handled by formatter

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
```

---

## .pre-commit-config.yaml — pre-commit hooks

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4  # update to latest: https://github.com/astral-sh/ruff-pre-commit/releases
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0  # update to latest: https://github.com/pre-commit/mirrors-mypy/releases
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]  # add your type stubs here
```

Install pre-commit and activate:

```bash
pip install pre-commit   # or: uv add --dev pre-commit
pre-commit install
```

---

## Makefile — key targets

```makefile
.PHONY: lint typecheck build test

lint:
	ruff check . --fix
	ruff format .

typecheck:
	mypy .

build:
	python -m build   # or your actual build command

test:
	pytest tests/ -v --tb=short
```

---

## .claude/settings.json PostToolUse hook (Python)

Replace the Node default in `universal-snippets.md` with:

```json
{
  "type": "command",
  "command": "ruff check --fix \"$CLAUDE_FILE_PATH\" && ruff format \"$CLAUDE_FILE_PATH\""
}
```
