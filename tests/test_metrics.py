from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_lab.metrics import compute_performance_metrics  # noqa: E402


def test_compute_performance_metrics_known_values() -> None:
    index = pd.to_datetime(
        ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"]
    )
    equity_curve = pd.Series([100.0, 110.0, 99.0, 118.8, 130.68], index=index)
    strategy_returns = pd.Series([0.0, 0.1, -0.1, 0.2, 0.1], index=index)

    metrics = compute_performance_metrics(
        equity_curve=equity_curve,
        strategy_returns=strategy_returns,
    )

    periods = len(equity_curve) - 1
    expected_cagr = (130.68 / 100.0) ** (1.0 / (periods / 252.0)) - 1.0
    expected_sharpe = (
        strategy_returns.mean() / strategy_returns.std(ddof=0)
    ) * math.sqrt(252.0)
    expected_max_drawdown = -0.1

    assert pytest.approx(metrics["cagr"], rel=1e-9) == expected_cagr
    assert pytest.approx(metrics["sharpe"], rel=1e-9) == expected_sharpe
    assert pytest.approx(metrics["max_drawdown"], rel=1e-12) == expected_max_drawdown


def test_compute_performance_metrics_returns_zero_sharpe_on_zero_volatility() -> None:
    index = pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"])
    equity_curve = pd.Series([100.0, 100.0, 100.0], index=index)
    strategy_returns = pd.Series([0.0, 0.0, 0.0], index=index)

    metrics = compute_performance_metrics(
        equity_curve=equity_curve,
        strategy_returns=strategy_returns,
    )

    assert metrics["sharpe"] == 0.0
    assert metrics["cagr"] == 0.0
    assert metrics["max_drawdown"] == 0.0


def test_compute_performance_metrics_validates_inputs() -> None:
    index = pd.to_datetime(["2020-01-01", "2020-01-02"])
    good_equity = pd.Series([100.0, 101.0], index=index)
    good_returns = pd.Series([0.0, 0.01], index=index)

    with pytest.raises(ValueError, match="must be non-empty"):
        compute_performance_metrics(pd.Series(dtype=float), good_returns)

    with pytest.raises(ValueError, match="must share the same index"):
        compute_performance_metrics(
            good_equity,
            pd.Series([0.0, 0.01], index=pd.to_datetime(["2020-01-02", "2020-01-03"])),
        )

    with pytest.raises(ValueError, match="must start above zero"):
        compute_performance_metrics(
            pd.Series([0.0, 1.0], index=index),
            good_returns,
        )

    with pytest.raises(ValueError, match="must remain positive"):
        compute_performance_metrics(
            pd.Series([100.0, -1.0], index=index),
            good_returns,
        )
