from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from quant_trading.real_lessons import (
    FACTOR_SYMBOLS,
    build_trend_signals,
    portfolio_returns_from_signals,
    run_real_lesson,
)


def test_trend_signals_require_valid_windows() -> None:
    close = pd.DataFrame({"SPY": [100, 101, 102]})

    with pytest.raises(ValueError, match="short_window"):
        build_trend_signals(close, short_window=10, long_window=5)


def test_portfolio_returns_keep_weighted_exposure_bounded() -> None:
    index = pd.bdate_range("2024-01-01", periods=8)
    open_prices = pd.DataFrame(
        {
            "AAA": [100, 101, 102, 103, 104, 105, 106, 107],
            "BBB": [50, 49, 50, 51, 52, 51, 52, 53],
        },
        index=index,
    )
    signals = pd.DataFrame(
        {
            "AAA": [0, 1, 1, 1, 0, 0, 1, 1],
            "BBB": [0, 0, 1, 1, 1, 0, 0, 1],
        },
        index=index,
    )

    result = portfolio_returns_from_signals(open_prices, signals, cost_bps=1.0)

    assert len(result) == len(index)
    assert (result["turnover"] >= 0).all()
    assert result["exposure"].max() <= 1.0
    assert "return" in result.columns


def test_all_real_lessons_run_on_synthetic_data() -> None:
    data = _synthetic_market_data()

    for chapter in range(11, 31):
        result = run_real_lesson(chapter, data, write_outputs=False)
        try:
            assert not result.summary.empty
            assert result.figure is not None
            if chapter == 28:
                max_diff = float(result.summary.loc[0, "max_equity_difference"])
                assert max_diff < 1e-10
        finally:
            plt.close(result.figure)


def test_unknown_real_lesson_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown lesson chapter"):
        run_real_lesson(99, _synthetic_market_data(), write_outputs=False)


def _synthetic_market_data() -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(7)
    index = pd.bdate_range("2016-01-01", periods=900)
    data = {}
    for offset, symbol in enumerate(FACTOR_SYMBOLS):
        daily_returns = rng.normal(
            0.0002 + offset * 0.00001,
            0.009 + (offset % 5) * 0.001,
            len(index),
        )
        close = 100 * np.cumprod(1 + daily_returns)
        open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.001, len(index)))
        high = np.maximum(open_, close) * 1.002
        low = np.minimum(open_, close) * 0.998
        volume = rng.integers(1_000_000, 5_000_000, len(index))
        data[symbol] = pd.DataFrame(
            {
                "Open": open_,
                "High": high,
                "Low": low,
                "Close": close,
                "Volume": volume,
            },
            index=index,
        )
    return data
