from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_lab.engine import run_backtest  # noqa: E402


def test_engine_position_transitions_enter_and_exit() -> None:
    price_data = pd.DataFrame(
        {"close": [100.0, 105.0, 95.0, 96.0, 97.0]},
        index=pd.to_datetime(
            ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"]
        ),
    )
    signals = pd.Series([0, 1, 1, 0, 1], index=price_data.index)

    result = run_backtest(
        price_data=price_data,
        signals=signals,
        initial_cash=1000.0,
        min_required_bars=3,
    )

    assert result.positions.tolist() == [0, 0, 1, 1, 0]
    assert result.equity_curve.iloc[0] == 1000.0
    assert len(result.equity_curve) == len(price_data)
