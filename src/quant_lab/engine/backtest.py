"""Deterministic long/cash backtest engine for Quant Lab v0."""

from __future__ import annotations

import pandas as pd

from quant_lab.contracts import BacktestResult


def _validate_inputs(
    price_data: pd.DataFrame,
    signals: pd.Series,
    initial_cash: float,
    min_required_bars: int | None,
    price_column: str,
) -> None:
    if initial_cash <= 0:
        raise ValueError("initial_cash must be positive.")
    if price_data.empty:
        raise ValueError("price_data cannot be empty.")
    if price_column not in price_data.columns:
        raise ValueError(f"Missing required price column: {price_column}")
    if not price_data.index.equals(signals.index):
        raise ValueError("signals index must match price_data index.")

    signal_values = set(pd.to_numeric(signals, errors="coerce").dropna().astype(int))
    if not signal_values.issubset({0, 1}):
        raise ValueError("signals must contain only 0/1 values.")

    if min_required_bars is not None:
        if min_required_bars <= 0:
            raise ValueError("min_required_bars must be positive when provided.")
        if len(price_data) < min_required_bars:
            raise ValueError(
                "insufficient bars for configured windows: "
                f"need at least {min_required_bars}, got {len(price_data)}"
            )


def run_backtest(
    price_data: pd.DataFrame,
    signals: pd.Series,
    initial_cash: float,
    min_required_bars: int | None = None,
    price_column: str = "close",
) -> BacktestResult:
    """Run a deterministic long/cash backtest with no-lookahead execution."""
    _validate_inputs(
        price_data=price_data,
        signals=signals,
        initial_cash=initial_cash,
        min_required_bars=min_required_bars,
        price_column=price_column,
    )

    prices = pd.to_numeric(price_data[price_column], errors="coerce")
    asset_returns = prices.pct_change().fillna(0.0)

    raw_positions = pd.to_numeric(signals, errors="coerce").fillna(0).astype(int)
    raw_positions = raw_positions.clip(lower=0, upper=1)
    executed_positions = raw_positions.shift(1, fill_value=0).astype(int)
    executed_positions.name = "position"

    strategy_returns = (asset_returns * executed_positions).fillna(0.0)
    strategy_returns.name = "strategy_return"

    equity_curve = (1.0 + strategy_returns).cumprod() * float(initial_cash)
    equity_curve.name = "equity"

    return BacktestResult(
        equity_curve=equity_curve,
        strategy_returns=strategy_returns,
        positions=executed_positions,
    )
