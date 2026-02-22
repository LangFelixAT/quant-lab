"""Artifact persistence utilities for Quant Lab v0 reporting."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from quant_lab.contracts import RunArtifacts


def build_run_artifacts(output_dir: str | Path) -> RunArtifacts:
    """Build deterministic artifact paths for a reporting run."""
    base_dir = Path(output_dir)
    return RunArtifacts(
        metrics_path=base_dir / "metrics.json",
        equity_curve_path=base_dir / "equity_curve.png",
        metadata_path=base_dir / "run_metadata.json",
    )


def _ensure_output_dir(paths: RunArtifacts) -> None:
    paths.metrics_path.parent.mkdir(parents=True, exist_ok=True)


def _write_metrics(metrics: Mapping[str, float], metrics_path: Path) -> None:
    payload = {key: float(value) for key, value in sorted(metrics.items())}
    metrics_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )


def _write_metadata(metadata: Mapping[str, Any], metadata_path: Path) -> None:
    metadata_path.write_text(
        json.dumps(dict(metadata), indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )


def _write_equity_curve_plot(equity_curve: pd.Series, equity_curve_path: Path) -> None:
    figure, axis = plt.subplots(figsize=(10, 4))
    axis.plot(equity_curve.index, equity_curve.values, label="equity")
    axis.set_title("Equity Curve")
    axis.set_xlabel("Date")
    axis.set_ylabel("Equity")
    axis.grid(True, alpha=0.3)
    axis.legend()
    figure.tight_layout()
    figure.savefig(equity_curve_path, dpi=144)
    plt.close(figure)


def write_run_artifacts(
    metrics: Mapping[str, float],
    equity_curve: pd.Series,
    metadata: Mapping[str, Any],
    output_dir: str | Path,
) -> RunArtifacts:
    """Write metrics, metadata, and equity curve plot artifacts."""
    if equity_curve.empty:
        raise ValueError("equity_curve must be non-empty.")

    artifacts = build_run_artifacts(output_dir=output_dir)
    _ensure_output_dir(artifacts)
    _write_metrics(metrics=metrics, metrics_path=artifacts.metrics_path)
    _write_metadata(metadata=metadata, metadata_path=artifacts.metadata_path)
    _write_equity_curve_plot(
        equity_curve=equity_curve,
        equity_curve_path=artifacts.equity_curve_path,
    )
    return artifacts
