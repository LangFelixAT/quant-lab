from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_lab.reporting import build_run_artifacts, write_run_artifacts  # noqa: E402


def _output_dir(test_name: str) -> Path:
    output_dir = PROJECT_ROOT / "outputs" / "tests" / test_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def test_build_run_artifacts_uses_deterministic_filenames() -> None:
    output_dir = _output_dir("reporting_filenames")
    artifacts = build_run_artifacts(output_dir=output_dir)

    assert artifacts.metrics_path == output_dir / "metrics.json"
    assert artifacts.equity_curve_path == output_dir / "equity_curve.png"
    assert artifacts.metadata_path == output_dir / "run_metadata.json"


def test_write_run_artifacts_writes_expected_files() -> None:
    index = pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"])
    equity_curve = pd.Series([100.0, 105.0, 103.0], index=index)
    metrics = {"sharpe": 1.2, "cagr": 0.15, "max_drawdown": -0.02}
    metadata = {"symbol": "SPY", "short_window": 20, "long_window": 50}

    output_dir = _output_dir("reporting_write")
    artifacts = write_run_artifacts(
        metrics=metrics,
        equity_curve=equity_curve,
        metadata=metadata,
        output_dir=output_dir,
    )

    assert artifacts.metrics_path.exists()
    assert artifacts.metadata_path.exists()
    assert artifacts.equity_curve_path.exists()

    metrics_payload = json.loads(artifacts.metrics_path.read_text(encoding="utf-8"))
    metadata_payload = json.loads(artifacts.metadata_path.read_text(encoding="utf-8"))

    assert list(metrics_payload.keys()) == ["cagr", "max_drawdown", "sharpe"]
    assert metrics_payload["cagr"] == pytest.approx(0.15)
    assert metadata_payload["symbol"] == "SPY"


def test_write_run_artifacts_rejects_empty_equity_curve() -> None:
    with pytest.raises(ValueError, match="equity_curve must be non-empty"):
        write_run_artifacts(
            metrics={"cagr": 0.0, "sharpe": 0.0, "max_drawdown": 0.0},
            equity_curve=pd.Series(dtype=float),
            metadata={},
            output_dir=_output_dir("reporting_empty_equity"),
        )
