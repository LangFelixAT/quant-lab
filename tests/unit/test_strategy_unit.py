from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_lab.strategy import generate_sma_signals  # noqa: E402


def test_strategy_warmup_and_equality_stay_in_cash() -> None:
    price_data = pd.DataFrame(
        {"close": [100, 100, 100, 100, 100]},
        index=pd.to_datetime(
            ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"]
        ),
    )

    signals = generate_sma_signals(price_data=price_data, short_window=2, long_window=3)

    assert signals.tolist() == [0, 0, 0, 0, 0]
    assert set(signals.unique()) == {0}
