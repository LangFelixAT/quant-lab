# Quant Lab v0 Architecture

## 1. Overview

Quant Lab v0 uses a modular, deterministic pipeline:

1. `data`: fetch and normalize historical daily bars.
2. `strategy`: generate `0/1` SMA crossover signals.
3. `engine`: simulate long/cash equity curve.
4. `metrics`: compute CAGR, Sharpe, and Max Drawdown.
5. `reporting`: persist metrics, metadata, and plot artifacts.
6. `cli`: validate user input and orchestrate end-to-end execution.

## 2. Component Model

### 2.1 `data`

Responsibilities:
- Load historical prices for one symbol over date range.
- Normalize schema, index, ordering, and missing values.

Inputs:
- `symbol`, `start`, `end`

Outputs:
- Normalized price `DataFrame`.

### 2.2 `strategy`

Responsibilities:
- Compute SMA-based `0/1` signal series from `close`.

Inputs:
- Price `DataFrame`
- `short_window`, `long_window`

Outputs:
- Signal `Series` (`0` cash / `1` long).

### 2.3 `engine`

Responsibilities:
- Convert signal + prices into strategy returns and equity curve.
- Enforce no-lookahead by shifting effective position.

Inputs:
- Price `DataFrame`
- Signal `Series`
- `initial_cash`

Outputs:
- Equity curve `Series`
- Strategy return `Series`
- Position `Series`

### 2.4 `metrics`

Responsibilities:
- Compute core performance metrics from equity/returns.

Inputs:
- Equity curve `Series`
- Strategy return `Series`

Outputs:
- Metrics dictionary (`cagr`, `sharpe`, `max_drawdown`).

### 2.5 `reporting`

Responsibilities:
- Save artifacts to output directory.
- Produce deterministic artifact names.

Inputs:
- Metrics dict
- Equity curve
- Run metadata
- Output directory

Outputs:
- `metrics.json`
- `equity_curve.png`
- `run_metadata.json`

### 2.6 `cli`

Responsibilities:
- Parse/validate command arguments.
- Call components in order.
- Map errors to user-facing messages and exit codes.

## 3. Data Flow

1. CLI receives backtest command and parameters.
2. CLI validates parameter constraints.
3. `data` fetches and normalizes price bars.
4. `strategy` computes SMA crossover `0/1` signals.
5. `engine` simulates returns and equity.
6. `metrics` computes summary values.
7. `reporting` writes artifacts.
8. CLI prints completion summary and output paths.

## 4. Interface Contracts

### 4.1 `data -> strategy`

- DataFrame with ascending unique date index.
- Must include `close` column.

### 4.2 `strategy -> engine`

- Series index must exactly match price DataFrame index.
- Allowed values only in `{0, 1}`.

### 4.3 `engine -> metrics/reporting`

- Equity and return series aligned to same index.
- Equity strictly positive from positive initial cash.

## 5. Determinism Rules

- Always sort index ascending before downstream processing.
- Remove duplicate timestamps deterministically.
- Use explicit NaN handling rules:
  - drop rows with missing `close` during normalization.
  - warm-up strategy signal defaults to `0`.
- Use fixed annualization convention (`252`) for Sharpe.
- Use deterministic output artifact names.

## 6. Error Handling Strategy

- CLI input validation errors:
  - Invalid windows, cash, or date range.
  - Exit non-zero with clear message.
- Data insufficiency:
  - If bars are fewer than `long_window`, fail with explicit reason.
- External fetch failures:
  - Surface data-source error in CLI with non-zero exit.
- Contract violations:
  - Raise typed runtime error with context for debug/test assertions.

## 7. Testing Strategy Map

### Unit tests

- `strategy`: crossover boundaries and warm-up signal behavior.
- `engine`: enter/exit transitions and no-lookahead behavior.
- `metrics`: exact values for synthetic known series.

### Validation tests

- CLI rejects invalid windows and date order.
- Engine or orchestration fails on insufficient bars.

### Offline integration

- Use fixed fixture dataset (CSV) without network.
- Run full pipeline and assert:
  - deterministic metrics,
  - artifact creation,
  - repeat-run output consistency.

## 8. Project Structure Target

Planned v0 module layout:

- `src/quant_lab/data/`
- `src/quant_lab/strategy/`
- `src/quant_lab/engine/`
- `src/quant_lab/metrics/`
- `src/quant_lab/reporting/`
- `src/quant_lab/cli.py`
- `tests/unit/`
- `tests/integration/`
- `outputs/` (runtime artifacts, not committed unless explicitly required)
