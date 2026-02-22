from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import quant_lab.cli as cli  # noqa: E402


def _argv(short_window: str = "2", long_window: str = "3") -> list[str]:
    return [
        "backtest",
        "--symbol",
        "SPY",
        "--start",
        "2020-01-01",
        "--end",
        "2020-01-05",
        "--short-window",
        short_window,
        "--long-window",
        long_window,
        "--initial-cash",
        "10000",
        "--output-dir",
        "outputs/verify_cli_validation",
    ]


def test_cli_validation_rejects_invalid_window_relationship(capsys) -> None:
    exit_code = cli.main(_argv(short_window="5", long_window="3"))
    err = capsys.readouterr().err
    assert exit_code == 1
    assert "short_window must be less than long_window" in err


def test_cli_validation_rejects_invalid_date_order(capsys) -> None:
    args = _argv()
    args[args.index("--start") + 1] = "2020-01-10"
    args[args.index("--end") + 1] = "2020-01-01"

    exit_code = cli.main(args)
    err = capsys.readouterr().err
    assert exit_code == 1
    assert "start date must be on or before end date" in err
