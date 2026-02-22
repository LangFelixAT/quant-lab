"""CLI scaffold for Quant Lab v0."""

from __future__ import annotations

import argparse
from collections.abc import Sequence


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


def main(argv: Sequence[str] | None = None) -> int:
    """Execute CLI entrypoint for scaffold-only v0 package."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "backtest":
        parser.print_help()
        return 2

    print(
        "Backtest command scaffolded. Functional implementation is tracked in QL-007."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
