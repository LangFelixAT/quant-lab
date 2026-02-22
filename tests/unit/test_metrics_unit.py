from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_lab.metrics import compute_performance_metrics  # noqa: E402


def test_metrics_known_synthetic_series_outputs_expected_keys() -> None:
    index = pd.to_datetime(
        ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"]
    )
    equity_curve = pd.Series([100.0, 105.0, 102.9, 108.045, 113.44725], index=index)
    strategy_returns = pd.Series([0.0, 0.05, -0.02, 0.05, 0.05], index=index)

    metrics = compute_performance_metrics(
        equity_curve=equity_curve, strategy_returns=strategy_returns
    )

    assert set(metrics.keys()) == {"cagr", "sharpe", "max_drawdown"}
    assert metrics["max_drawdown"] == pytest.approx(-0.02)
