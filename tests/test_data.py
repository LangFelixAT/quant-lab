from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_lab.data import fetch_price_data, normalize_price_data  # noqa: E402


def test_normalize_price_data_sorts_dedupes_and_drops_missing_close() -> None:
    index = pd.DatetimeIndex(
        [
            "2020-01-03 00:00:00+00:00",
            "2020-01-01 00:00:00+00:00",
            "2020-01-01 00:00:00+00:00",
            "2020-01-02 00:00:00+00:00",
        ]
    )
    raw = pd.DataFrame(
        {
            "Open": [3, 1, 99, 2],
            "High": [3, 1, 99, 2],
            "Low": [3, 1, 99, 2],
            "Close": [3, 1, 99, None],
            "Adj Close": [3, 1, 99, 2],
            "Volume": [30, 10, 990, 20],
        },
        index=index,
    )

    normalized = normalize_price_data(raw)

    assert list(normalized.columns) == [
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume",
    ]
    assert normalized.index.tz is None
    assert normalized.index.is_monotonic_increasing
    assert normalized.index.is_unique
    assert len(normalized) == 2
    assert normalized.iloc[0]["open"] == 1


def test_normalize_price_data_requires_expected_columns() -> None:
    raw = pd.DataFrame(
        {
            "Open": [1],
            "High": [1],
            "Low": [1],
            "Close": [1],
            "Volume": [1],
        },
        index=pd.to_datetime(["2020-01-01"]),
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        normalize_price_data(raw)


def test_normalize_price_data_accepts_multiindex_columns() -> None:
    raw = pd.DataFrame(
        [[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [10, 20, 30]],
        index=["Open", "High", "Low", "Close", "Adj Close", "Volume"],
        columns=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
    ).T
    raw.columns = pd.MultiIndex.from_product([raw.columns, ["SPY"]])

    normalized = normalize_price_data(raw)

    assert list(normalized.columns) == [
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume",
    ]
    assert len(normalized) == 3


def test_fetch_price_data_uses_downloader_and_normalizes() -> None:
    def fake_downloader(symbol: str, start: str, end: str) -> pd.DataFrame:
        assert symbol == "SPY"
        assert start == "2020-01-01"
        assert end == "2020-01-03"
        return pd.DataFrame(
            {
                "Open": [1, 2, 3],
                "High": [1, 2, 3],
                "Low": [1, 2, 3],
                "Close": [1, 2, 3],
                "Adj Close": [1, 2, 3],
                "Volume": [1, 2, 3],
            },
            index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
        )

    normalized = fetch_price_data(
        symbol=" SPY ",
        start="2020-01-01",
        end="2020-01-03",
        downloader=fake_downloader,
    )

    assert len(normalized) == 3
    assert normalized.index.name == "date"


def test_fetch_price_data_validates_inputs() -> None:
    with pytest.raises(ValueError, match="Symbol must be non-empty"):
        fetch_price_data(" ", "2020-01-01", "2020-01-03", downloader=lambda *_: None)

    with pytest.raises(ValueError, match="start date must be on or before end date"):
        fetch_price_data("SPY", "2020-01-03", "2020-01-01", downloader=lambda *_: None)
