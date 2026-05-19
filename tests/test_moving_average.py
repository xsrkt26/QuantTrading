import pandas as pd
import pytest

from quant_trading.moving_average import (
    add_moving_average_strategy,
    summarize_moving_average_strategy,
)


def test_moving_average_strategy_uses_next_day_position() -> None:
    df = pd.DataFrame(
        {"Close": [100.0, 101.0, 102.0, 103.0, 104.0]},
        index=pd.date_range("2024-01-01", periods=5),
    )

    result = add_moving_average_strategy(
        df, short_window=2, long_window=3, transaction_cost_bps=0
    )

    assert result["signal"].iloc[2] == 1
    assert result["position"].iloc[2] == 0
    assert result["position"].iloc[3] == 1
    assert result["position"].iloc[3] == result["signal"].iloc[2]


def test_moving_average_strategy_applies_transaction_cost() -> None:
    df = pd.DataFrame(
        {"Close": [100.0, 101.0, 102.0, 103.0]},
        index=pd.date_range("2024-01-01", periods=4),
    )

    result = add_moving_average_strategy(
        df, short_window=2, long_window=3, transaction_cost_bps=10
    )

    assert result["trade"].iloc[3] == pytest.approx(1.0)
    assert result["transaction_cost"].iloc[3] == pytest.approx(0.001)
    assert result["strategy_return"].iloc[3] == pytest.approx(
        (103.0 / 102.0 - 1) - 0.001
    )


def test_summarize_moving_average_strategy() -> None:
    df = pd.DataFrame(
        {"Close": [100.0, 101.0, 102.0, 103.0, 104.0]},
        index=pd.date_range("2024-01-01", periods=5),
    )
    result = add_moving_average_strategy(
        df, short_window=2, long_window=3, transaction_cost_bps=0
    )

    summary = summarize_moving_average_strategy(
        result,
        symbol="TEST",
        short_window=2,
        long_window=3,
        transaction_cost_bps=0,
    )

    assert summary.symbol == "TEST"
    assert summary.short_window == 2
    assert summary.long_window == 3
    assert summary.rows == 5
    assert summary.trades == pytest.approx(1.0)
    assert summary.time_in_market == pytest.approx(0.4)


def test_moving_average_rejects_invalid_windows() -> None:
    df = pd.DataFrame(
        {"Close": [100.0, 101.0, 102.0]},
        index=pd.date_range("2024-01-01", periods=3),
    )

    with pytest.raises(ValueError, match="short_window"):
        add_moving_average_strategy(df, short_window=3, long_window=3)
