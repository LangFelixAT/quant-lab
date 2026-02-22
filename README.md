# Quant Lab

Quant Lab is a deterministic, single-asset backtesting lab for systematic strategy experimentation.

The `v0` scope is a minimal vertical slice: daily historical data ingestion, SMA crossover signals, long/cash portfolio simulation, core metrics, and an equity curve plot.

## v0 Capabilities

- Download and normalize OHLCV daily price history for one symbol.
- Generate SMA crossover trade signals.
- Run a deterministic long/cash backtest.
- Compute and report:
  - CAGR
  - Sharpe Ratio
  - Maximum Drawdown
- Save run artifacts (metrics and equity curve plot).

## Non-Goals

- Live trading execution.
- Broker integrations.
- Real-time data streaming.
- Investment advice or alpha claims.

## Quickstart

### Environment

- Python `3.11+` (CI currently uses Python `3.12`).
- Recommended: virtual environment.

Install core dev tooling:

```powershell
python -m pip install --upgrade pip
python -m pip install ruff pytest pandas numpy matplotlib yfinance
```

### Quality Gate

Primary:

```powershell
make check
```

Fallback when `make` is unavailable:

```powershell
ruff format --check .
ruff check .
pytest -q
```

### Example v0 Backtest Command

```powershell
python -m quant_lab.cli backtest --symbol SPY --start 2020-01-01 --end 2021-12-31 --short-window 20 --long-window 50 --initial-cash 10000 --output-dir outputs/example
```

Expected outputs:

- A metrics artifact containing CAGR, Sharpe Ratio, and Max Drawdown.
- An equity curve plot image.
- Run metadata (parameters and run context).

## Repository Map

- `src/quant_lab/`: backtesting package (data, strategy, engine, metrics, reporting, cli).
- `tests/`: unit and integration tests.
- `planning/`: brief, lifecycle docs, schema, and issue planning files.
- `automation/`: issue automation scripts.

## Development Workflow

- One issue equals one PR.
- Create an issue-scoped branch using conventions in `AGENTS.md`.
- Keep PR scope atomic and limited to the linked issue.
- Run `make check` before push/PR update.
- Use PR body format from `.github/pull_request_template.md` with `Fixes #<issue-number>`.

## Planning and Issue Automation

- Planning schema: `planning/ISSUE_SCHEMA.md`
- Example issues file: `planning/examples/issues.v0.example.json`
- Planned backlog: `planning/issues/v0.json`

Dry run issue generation:

```powershell
python automation/create_issues.py --input planning/issues/v0.json --mode dry-run --milestone v0
```

Apply issue generation:

```powershell
python automation/create_issues.py --input planning/issues/v0.json --mode apply --milestone v0
```
