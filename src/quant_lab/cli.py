"""CLI entrypoint for Quant Lab v0 backtest orchestration."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

import pandas as pd

from quant_lab.data import fetch_price_data
from quant_lab.engine import run_backtest
from quant_lab.metrics import compute_performance_metrics
from quant_lab.reporting import write_run_artifacts
from quant_lab.strategy import generate_sma_signals


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser and v0 command surface."""
    parser = argparse.ArgumentParser(prog="quant_lab")
    subparsers = parser.add_subparsers(dest="command")

    backtest = subparsers.add_parser("backtest", help="Run a backtest.")
    backtest.add_argument("--symbol", required=True)
    backtest.add_argument("--start", required=True)
    backtest.add_argument("--end", required=True)
    backtest.add_argument("--short-window", type=int, required=True)
    backtest.add_argument("--long-window", type=int, required=True)
    backtest.add_argument("--initial-cash", type=float, required=True)
    backtest.add_argument("--output-dir", required=True)
    return parser


def _validate_backtest_args(args: argparse.Namespace) -> None:
    if args.short_window <= 0 or args.long_window <= 0:
        raise ValueError("short_window and long_window must be positive integers.")
    if args.short_window >= args.long_window:
        raise ValueError("short_window must be less than long_window.")
    if args.initial_cash <= 0:
        raise ValueError("initial_cash must be positive.")

    parsed_start = pd.Timestamp(args.start)
    parsed_end = pd.Timestamp(args.end)
    if parsed_start > parsed_end:
        raise ValueError("start date must be on or before end date.")


def _run_backtest_command(args: argparse.Namespace) -> int:
    _validate_backtest_args(args)

    price_data = fetch_price_data(symbol=args.symbol, start=args.start, end=args.end)
    if len(price_data) < args.long_window:
        raise ValueError(
            "insufficient bars for configured windows: "
            f"need at least {args.long_window}, got {len(price_data)}"
        )

    signals = generate_sma_signals(
        price_data=price_data,
        short_window=args.short_window,
        long_window=args.long_window,
    )
    result = run_backtest(
        price_data=price_data,
        signals=signals,
        initial_cash=args.initial_cash,
        min_required_bars=args.long_window,
    )
    metrics = compute_performance_metrics(
        equity_curve=result.equity_curve,
        strategy_returns=result.strategy_returns,
    )
    artifacts = write_run_artifacts(
        metrics=metrics,
        equity_curve=result.equity_curve,
        metadata={
            "symbol": args.symbol,
            "start": args.start,
            "end": args.end,
            "short_window": args.short_window,
            "long_window": args.long_window,
            "initial_cash": args.initial_cash,
            "output_dir": args.output_dir,
        },
        output_dir=args.output_dir,
    )

    print("Backtest complete.")
    print(f"metrics: {artifacts.metrics_path}")
    print(f"equity_curve: {artifacts.equity_curve_path}")
    print(f"run_metadata: {artifacts.metadata_path}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Execute CLI entrypoint for Quant Lab workflows."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "backtest":
        parser.print_help()
        return 2

    try:
        return _run_backtest_command(args)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
