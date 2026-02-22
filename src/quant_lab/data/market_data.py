"""Deterministic single-symbol historical data ingestion for Quant Lab v0."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

REQUIRED_COLUMNS: tuple[str, ...] = (
    "open",
    "high",
    "low",
    "close",
    "adj_close",
    "volume",
)


def _default_downloader(symbol: str, start: str, end: str) -> pd.DataFrame:
    import yfinance as yf

    return yf.download(
        symbol,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
    )


def normalize_price_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Normalize raw market data into a deterministic v0 schema."""
    if raw_data.empty:
        raise ValueError("No price data returned.")

    normalized = raw_data.copy()
    normalized.columns = [
        str(col).strip().lower().replace(" ", "_") for col in normalized.columns
    ]

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in normalized.columns]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns: {missing_text}")

    if not isinstance(normalized.index, pd.DatetimeIndex):
        normalized.index = pd.to_datetime(normalized.index)

    if normalized.index.tz is not None:
        normalized.index = normalized.index.tz_convert("UTC").tz_localize(None)

    normalized = normalized.sort_index(kind="mergesort")
    normalized = normalized.loc[~normalized.index.duplicated(keep="first")]

    for column in REQUIRED_COLUMNS:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

    normalized = normalized.dropna(subset=["close"])
    normalized = normalized.loc[:, list(REQUIRED_COLUMNS)]
    normalized.index.name = "date"
    return normalized


def fetch_price_data(
    symbol: str,
    start: str,
    end: str,
    downloader: Callable[[str, str, str], pd.DataFrame] | None = None,
) -> pd.DataFrame:
    """Fetch and normalize daily historical prices for a single symbol."""
    cleaned_symbol = symbol.strip()
    if not cleaned_symbol:
        raise ValueError("Symbol must be non-empty.")

    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    if start_ts > end_ts:
        raise ValueError("start date must be on or before end date.")

    fetcher = downloader or _default_downloader
    raw = fetcher(cleaned_symbol, str(start_ts.date()), str(end_ts.date()))
    if not isinstance(raw, pd.DataFrame):
        raise TypeError("Downloader must return a pandas DataFrame.")

    return normalize_price_data(raw)
