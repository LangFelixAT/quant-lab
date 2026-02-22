from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_lab.strategy import generate_sma_signals  # noqa: E402


def test_generate_sma_signals_boundary_behavior() -> None:
    price_data = pd.DataFrame(
        {"close": [1, 1, 1, 1, 3, 5, 1]},
        index=pd.to_datetime(
            [
                "2020-01-01",
                "2020-01-02",
                "2020-01-03",
                "2020-01-04",
                "2020-01-05",
                "2020-01-06",
                "2020-01-07",
            ]
        ),
    )

    signal = generate_sma_signals(price_data=price_data, short_window=2, long_window=3)

    assert signal.index.equals(price_data.index)
    assert set(signal.unique()) <= {0, 1}
    assert signal.tolist() == [0, 0, 0, 0, 1, 1, 0]


def test_generate_sma_signals_uses_custom_price_column() -> None:
    price_data = pd.DataFrame(
        {"adj_close": [10, 10, 10, 12, 14]},
        index=pd.to_datetime(
            ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"]
        ),
    )

    signal = generate_sma_signals(
        price_data=price_data,
        short_window=2,
        long_window=3,
        price_column="adj_close",
    )

    assert signal.index.equals(price_data.index)
    assert signal.dtype == int


@pytest.mark.parametrize(
    ("short_window", "long_window"),
    [(0, 3), (2, 0), (3, 3), (4, 3)],
)
def test_generate_sma_signals_validates_window_inputs(
    short_window: int, long_window: int
) -> None:
    price_data = pd.DataFrame(
        {"close": [1, 2, 3]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
    )

    with pytest.raises(ValueError):
        generate_sma_signals(
            price_data=price_data,
            short_window=short_window,
            long_window=long_window,
        )


def test_generate_sma_signals_requires_column_and_non_empty_data() -> None:
    with pytest.raises(ValueError, match="Missing required price column"):
        generate_sma_signals(
            price_data=pd.DataFrame({"open": [1]}),
            short_window=1,
            long_window=2,
        )

    with pytest.raises(ValueError, match="price_data cannot be empty"):
        generate_sma_signals(
            price_data=pd.DataFrame({"close": []}),
            short_window=1,
            long_window=2,
        )
