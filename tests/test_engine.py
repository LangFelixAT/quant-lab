from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_lab.engine import run_backtest  # noqa: E402


def test_run_backtest_no_lookahead_and_alignment() -> None:
    price_data = pd.DataFrame(
        {"close": [100.0, 110.0, 110.0, 121.0]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04"]),
    )
    signals = pd.Series([1, 1, 0, 1], index=price_data.index, name="signal")

    result = run_backtest(price_data=price_data, signals=signals, initial_cash=100.0)

    assert result.equity_curve.index.equals(price_data.index)
    assert result.strategy_returns.index.equals(price_data.index)
    assert result.positions.index.equals(price_data.index)
    assert result.positions.tolist() == [0, 1, 1, 0]
    assert result.strategy_returns.round(6).tolist() == [0.0, 0.1, 0.0, 0.0]
    assert result.equity_curve.round(6).tolist() == [100.0, 110.0, 110.0, 110.0]


def test_run_backtest_rejects_invalid_signal_values() -> None:
    price_data = pd.DataFrame(
        {"close": [1.0, 2.0, 3.0]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
    )
    signals = pd.Series([0, 2, 1], index=price_data.index)

    with pytest.raises(ValueError, match="signals must contain only 0/1"):
        run_backtest(price_data=price_data, signals=signals, initial_cash=100.0)


def test_run_backtest_requires_sufficient_bars_when_configured() -> None:
    price_data = pd.DataFrame(
        {"close": [1.0, 2.0, 3.0]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
    )
    signals = pd.Series([0, 1, 1], index=price_data.index)

    with pytest.raises(ValueError, match="insufficient bars for configured windows"):
        run_backtest(
            price_data=price_data,
            signals=signals,
            initial_cash=100.0,
            min_required_bars=5,
        )


def test_run_backtest_validates_index_alignment() -> None:
    price_data = pd.DataFrame(
        {"close": [1.0, 2.0, 3.0]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
    )
    signals = pd.Series(
        [0, 1, 1], index=pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-04"])
    )

    with pytest.raises(ValueError, match="signals index must match price_data index"):
        run_backtest(price_data=price_data, signals=signals, initial_cash=100.0)
