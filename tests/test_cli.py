from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import quant_lab.cli as cli  # noqa: E402
from quant_lab.contracts import RunArtifacts  # noqa: E402


def _valid_argv() -> list[str]:
    return [
        "backtest",
        "--symbol",
        "SPY",
        "--start",
        "2020-01-01",
        "--end",
        "2020-01-05",
        "--short-window",
        "2",
        "--long-window",
        "3",
        "--initial-cash",
        "10000",
        "--output-dir",
        "outputs/verify_cli",
    ]


def test_cli_backtest_success_orchestrates_pipeline(monkeypatch, capsys) -> None:
    index = pd.to_datetime(
        ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"]
    )
    price_data = pd.DataFrame(
        {
            "open": [1, 2, 3, 4, 5],
            "high": [1, 2, 3, 4, 5],
            "low": [1, 2, 3, 4, 5],
            "close": [1, 2, 3, 4, 5],
            "adj_close": [1, 2, 3, 4, 5],
            "volume": [1, 2, 3, 4, 5],
        },
        index=index,
    )
    signal = pd.Series([0, 0, 1, 1, 1], index=index)
    strategy_returns = pd.Series([0.0, 0.0, 0.1, 0.0, 0.1], index=index)
    equity_curve = pd.Series([10000.0, 10000.0, 11000.0, 11000.0, 12100.0], index=index)
    artifacts = RunArtifacts(
        metrics_path=Path("outputs/verify_cli/metrics.json"),
        equity_curve_path=Path("outputs/verify_cli/equity_curve.png"),
        metadata_path=Path("outputs/verify_cli/run_metadata.json"),
    )

    class _Result:
        def __init__(self) -> None:
            self.equity_curve = equity_curve
            self.strategy_returns = strategy_returns
            self.positions = signal

    monkeypatch.setattr(cli, "fetch_price_data", lambda **_: price_data)
    monkeypatch.setattr(cli, "generate_sma_signals", lambda **_: signal)
    monkeypatch.setattr(cli, "run_backtest", lambda **_: _Result())
    monkeypatch.setattr(
        cli,
        "compute_performance_metrics",
        lambda **_: {"cagr": 0.1, "sharpe": 1.2, "max_drawdown": -0.05},
    )
    monkeypatch.setattr(cli, "write_run_artifacts", lambda **_: artifacts)

    exit_code = cli.main(_valid_argv())
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Backtest complete." in output
    assert "metrics:" in output


def test_cli_backtest_rejects_invalid_window_relationship(capsys) -> None:
    argv = _valid_argv()
    argv[argv.index("--short-window") + 1] = "5"
    argv[argv.index("--long-window") + 1] = "3"

    exit_code = cli.main(argv)
    error_output = capsys.readouterr().err

    assert exit_code == 1
    assert "short_window must be less than long_window" in error_output


def test_cli_backtest_rejects_invalid_date_order(capsys) -> None:
    argv = _valid_argv()
    argv[argv.index("--start") + 1] = "2020-01-10"
    argv[argv.index("--end") + 1] = "2020-01-01"

    exit_code = cli.main(argv)
    error_output = capsys.readouterr().err

    assert exit_code == 1
    assert "start date must be on or before end date" in error_output


def test_cli_backtest_fails_when_bars_are_insufficient(monkeypatch, capsys) -> None:
    index = pd.to_datetime(["2020-01-01", "2020-01-02"])
    price_data = pd.DataFrame(
        {
            "open": [1, 2],
            "high": [1, 2],
            "low": [1, 2],
            "close": [1, 2],
            "adj_close": [1, 2],
            "volume": [1, 2],
        },
        index=index,
    )

    monkeypatch.setattr(cli, "fetch_price_data", lambda **_: price_data)

    exit_code = cli.main(_valid_argv())
    error_output = capsys.readouterr().err

    assert exit_code == 1
    assert "insufficient bars for configured windows" in error_output
