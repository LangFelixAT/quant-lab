"""Performance metrics for Quant Lab v0 backtests."""

from __future__ import annotations

import math

import pandas as pd


def _compute_cagr(equity_curve: pd.Series) -> float:
    start_value = float(equity_curve.iloc[0])
    end_value = float(equity_curve.iloc[-1])
    periods = len(equity_curve) - 1
    if periods <= 0:
        return 0.0

    years = periods / 252.0
    if years <= 0:
        return 0.0
    return (end_value / start_value) ** (1.0 / years) - 1.0


def _compute_sharpe(strategy_returns: pd.Series) -> float:
    clean_returns = pd.to_numeric(strategy_returns, errors="coerce").fillna(0.0)
    std = float(clean_returns.std(ddof=0))
    if std == 0.0:
        return 0.0
    mean = float(clean_returns.mean())
    return (mean / std) * math.sqrt(252.0)


def _compute_max_drawdown(equity_curve: pd.Series) -> float:
    running_peak = equity_curve.cummax()
    drawdown = (equity_curve / running_peak) - 1.0
    return float(drawdown.min())


def compute_performance_metrics(
    equity_curve: pd.Series,
    strategy_returns: pd.Series,
) -> dict[str, float]:
    """Compute core v0 metrics from equity curve and strategy returns."""
    if equity_curve.empty or strategy_returns.empty:
        raise ValueError("equity_curve and strategy_returns must be non-empty.")
    if not equity_curve.index.equals(strategy_returns.index):
        raise ValueError("equity_curve and strategy_returns must share the same index.")

    equity_numeric = pd.to_numeric(equity_curve, errors="coerce")
    if equity_numeric.isna().any():
        raise ValueError("equity_curve contains non-numeric values.")
    if float(equity_numeric.iloc[0]) <= 0:
        raise ValueError("equity_curve must start above zero.")
    if (equity_numeric <= 0).any():
        raise ValueError("equity_curve must remain positive.")

    return {
        "cagr": float(_compute_cagr(equity_numeric)),
        "sharpe": float(_compute_sharpe(strategy_returns)),
        "max_drawdown": float(_compute_max_drawdown(equity_numeric)),
    }
