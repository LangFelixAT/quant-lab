from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_lab import BacktestResult, RunArtifacts, RunConfig  # noqa: E402


def test_scaffold_contracts_are_importable() -> None:
    config = RunConfig(
        symbol="SPY",
        start="2020-01-01",
        end="2020-12-31",
        short_window=20,
        long_window=50,
        initial_cash=10000.0,
        output_dir=Path("outputs/example"),
    )
    artifacts = RunArtifacts(
        metrics_path=Path("outputs/example/metrics.json"),
        equity_curve_path=Path("outputs/example/equity_curve.png"),
        metadata_path=Path("outputs/example/run_metadata.json"),
    )
    result = BacktestResult(equity_curve=[], strategy_returns=[], positions=[])

    assert config.symbol == "SPY"
    assert artifacts.metrics_path.name == "metrics.json"
    assert result.metrics is None
