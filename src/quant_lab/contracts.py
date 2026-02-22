"""Shared core contracts for Quant Lab v0 module boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

PriceFrameLike = Any
"""Placeholder type alias for a normalized market-data table (pandas DataFrame in v0)."""

SignalSeriesLike = Any
"""Placeholder type alias for strategy signals (pandas Series in v0)."""


@dataclass(frozen=True, slots=True)
class RunConfig:
    """Immutable run parameters shared by pipeline modules."""

    symbol: str
    start: str
    end: str
    short_window: int
    long_window: int
    initial_cash: float
    output_dir: Path


@dataclass(frozen=True, slots=True)
class RunArtifacts:
    """Deterministic output file locations produced by a run."""

    metrics_path: Path
    equity_curve_path: Path
    metadata_path: Path


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """Backtest outputs exchanged between engine, metrics, and reporting."""

    equity_curve: SignalSeriesLike
    strategy_returns: SignalSeriesLike
    positions: SignalSeriesLike
    metrics: Mapping[str, float] | None = None
