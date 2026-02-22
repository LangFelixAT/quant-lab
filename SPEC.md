# Quant Lab v0 Specification

## 1. Scope

Quant Lab v0 delivers a deterministic, single-asset backtesting workflow.

In scope:
- Single asset only.
- Daily bars only.
- Long/cash execution model only (position is either `0` or `1` unit-weight exposure).
- Deterministic outputs for identical inputs and parameters.

Out of scope for v0:
- Multi-asset portfolios.
- Intraday or real-time data.
- Fees, slippage, leverage, shorting, or borrow costs.
- Live execution and broker APIs.

## 2. Functional Requirements

### FR-1 Data Ingestion and Normalization

- Input parameters:
  - `symbol` (string, non-empty)
  - `start` (ISO date)
  - `end` (ISO date)
- Data source for default implementation: public historical market data (yfinance).
- Normalized output must be a date-indexed table sorted ascending with canonical columns:
  - `open`, `high`, `low`, `close`, `adj_close`, `volume`
- Time handling:
  - Normalize timestamps to timezone-naive UTC-equivalent daily dates.
  - Remove duplicate index rows by keeping the first deterministic occurrence.
- Missing data policy:
  - Drop rows where `close` is missing.
  - Preserve deterministic row order and index continuity as returned after filtering.

### FR-2 Strategy Signal Generation

- v0 signal contract is `0/1`:
  - `1` means long.
  - `0` means cash.
- Strategy: SMA crossover on `close`:
  - `short_sma = SMA(close, short_window)`
  - `long_sma = SMA(close, long_window)`
  - signal is `1` when `short_sma > long_sma`, else `0`.
- Warm-up behavior:
  - Prior to full window availability, signal defaults to `0`.

### FR-3 Backtest Engine

- Inputs:
  - normalized price table including `close`
  - signal series aligned to index
  - `initial_cash` (positive float)
- Accounting model:
  - Portfolio return at day `t` is `signal[t-1] * asset_return[t]` to avoid same-bar lookahead.
  - Equity starts at `initial_cash`.
  - Equity curve is compounded multiplicatively from daily strategy returns.
- Outputs:
  - equity curve series
  - daily strategy returns series
  - optional position series (0/1)

### FR-4 Metrics

- Required metrics:
  - CAGR
  - Sharpe Ratio
  - Maximum Drawdown
- Definitions:
  - `CAGR = (ending_equity / starting_equity) ** (1 / years) - 1`
  - Sharpe uses mean and standard deviation of daily returns with annualization factor `sqrt(252)`.
  - Max Drawdown is the minimum of `(equity / rolling_peak) - 1`.
- If volatility is zero, Sharpe must return `0.0` deterministically.

### FR-5 Reporting Artifacts

Each run must produce:
- Metrics artifact (machine-readable, e.g. JSON).
- Equity curve plot image (e.g. PNG).
- Run metadata artifact capturing run parameters used for reproducibility.

### FR-6 CLI Public Interface

Primary entry point:

```text
python -m quant_lab.cli backtest --symbol ... --start ... --end ... --short-window ... --long-window ... --initial-cash ... --output-dir ...
```

Required validations:
- `short_window` and `long_window` are positive integers.
- `short_window < long_window`.
- `initial_cash > 0`.
- `start <= end`.
- Post-fetch bar count must be sufficient for `long_window`; otherwise exit with a clear error.

CLI behavior:
- Exit code `0` on success.
- Non-zero exit code with explicit error message on validation/fetch/runtime failures.

## 3. Data Contracts

### 3.1 Price Frame Contract

- Type: pandas `DataFrame`.
- Index: pandas `DatetimeIndex`, ascending, unique, timezone-naive.
- Required columns: `open`, `high`, `low`, `close`, `adj_close`, `volume`.
- Numeric columns must be coercible to float except `volume` (int/float accepted).

### 3.2 Signal Contract

- Type: pandas `Series`.
- Same index as normalized price frame.
- Values restricted to `{0, 1}`.

### 3.3 Backtest Output Contract

- `equity_curve`: pandas `Series`, strictly positive values.
- `strategy_returns`: pandas `Series`, aligned to equity index.
- `positions`: pandas `Series` with `{0, 1}`.

### 3.4 Deterministic Output Naming

- Output directory is user-provided.
- Artifact filenames must be deterministic from run parameters, e.g.:
  - `metrics.json`
  - `equity_curve.png`
  - `run_metadata.json`

## 4. Non-Functional Requirements

- Reproducibility:
  - No hidden randomness.
  - Stable ordering and explicit transformation rules.
- Design:
  - No global mutable state in core modules.
  - Pure computation preferred for strategy/engine/metrics.
- Testing:
  - Tests are deterministic and network-independent by default.
  - Network fetch behavior is tested through mocks or optional manual checks.
- CI compatibility:
  - All changes must pass `make check`.

## 5. Verification Scenarios

### Unit

- SMA crossover edge behavior around crossover boundaries.
- Engine position and equity transitions for enter/exit sequences.
- Metrics exactness on synthetic fixed equity series.

### Validation

- CLI rejects `short_window >= long_window`.
- CLI rejects invalid date ordering.
- Engine/CLI fail fast on insufficient bars for requested long window.

### Integration (Offline)

- Fixed CSV fixture run produces deterministic metrics values.
- Fixed CSV fixture run creates equity plot artifact.
- Re-running same command produces identical metrics artifact contents.

### Quality Gate

- `make check` passes locally and in CI when `make` is available.
- Equivalent fallback commands pass in environments without `make`:
  - `ruff format --check .`
  - `ruff check .`
  - `pytest -q`
