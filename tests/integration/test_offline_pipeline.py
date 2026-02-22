from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_lab.data import normalize_price_data  # noqa: E402
from quant_lab.engine import run_backtest  # noqa: E402
from quant_lab.metrics import compute_performance_metrics  # noqa: E402
from quant_lab.reporting import write_run_artifacts  # noqa: E402
from quant_lab.strategy import generate_sma_signals  # noqa: E402


def test_offline_fixture_pipeline_is_deterministic_and_writes_artifacts() -> None:
    fixture_path = PROJECT_ROOT / "tests" / "fixtures" / "offline_prices.csv"
    raw = pd.read_csv(fixture_path, parse_dates=["date"], index_col="date")
    price_data = normalize_price_data(raw)

    output_dir = PROJECT_ROOT / "outputs" / "integration_offline_fixture"
    if output_dir.exists():
        shutil.rmtree(output_dir, ignore_errors=True)

    signals = generate_sma_signals(price_data=price_data, short_window=3, long_window=5)
    result = run_backtest(
        price_data=price_data,
        signals=signals,
        initial_cash=10000.0,
        min_required_bars=5,
    )
    metrics = compute_performance_metrics(
        equity_curve=result.equity_curve,
        strategy_returns=result.strategy_returns,
    )
    artifacts_first = write_run_artifacts(
        metrics=metrics,
        equity_curve=result.equity_curve,
        metadata={"fixture": fixture_path.name, "run": 1},
        output_dir=output_dir,
    )

    metrics_first = json.loads(artifacts_first.metrics_path.read_text(encoding="utf-8"))

    artifacts_second = write_run_artifacts(
        metrics=metrics,
        equity_curve=result.equity_curve,
        metadata={"fixture": fixture_path.name, "run": 2},
        output_dir=output_dir,
    )
    metrics_second = json.loads(
        artifacts_second.metrics_path.read_text(encoding="utf-8")
    )

    assert artifacts_first.metrics_path.exists()
    assert artifacts_first.metadata_path.exists()
    assert artifacts_first.equity_curve_path.exists()
    assert set(metrics_first.keys()) == {"cagr", "sharpe", "max_drawdown"}
    assert metrics_first == metrics_second

    shutil.rmtree(output_dir, ignore_errors=True)
