"""SMA crossover signal generation for Quant Lab v0."""

from __future__ import annotations

import pandas as pd


def _validate_windows(short_window: int, long_window: int) -> None:
    if short_window <= 0 or long_window <= 0:
        raise ValueError("short_window and long_window must be positive integers.")
    if short_window >= long_window:
        raise ValueError("short_window must be less than long_window.")


def generate_sma_signals(
    price_data: pd.DataFrame,
    short_window: int,
    long_window: int,
    price_column: str = "close",
) -> pd.Series:
    """Generate deterministic long/cash (1/0) SMA crossover signals."""
    _validate_windows(short_window=short_window, long_window=long_window)

    if price_column not in price_data.columns:
        raise ValueError(f"Missing required price column: {price_column}")
    if price_data.empty:
        raise ValueError("price_data cannot be empty.")

    prices = pd.to_numeric(price_data[price_column], errors="coerce")

    short_sma = prices.rolling(window=short_window, min_periods=short_window).mean()
    long_sma = prices.rolling(window=long_window, min_periods=long_window).mean()

    signal = (short_sma > long_sma).astype(int)
    signal = signal.fillna(0).astype(int)
    signal.name = "signal"
    return signal
