import pandas as pd
import pytest

from quant_trading.execution import (
    build_order_fills,
    build_round_trip_trade_log,
    format_trade_summary_table,
    summarize_trade_log,
)


def _sample_strategy() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": [100.0, 110.0, 121.0, 120.0, 132.0],
            "position": [0.0, 1.0, 1.0, 0.0, 0.0],
            "trade": [0.0, 1.0, 0.0, 1.0, 0.0],
        },
        index=pd.date_range("2024-01-01", periods=5),
    )


def test_build_order_fills_applies_side_specific_slippage() -> None:
    fills = build_order_fills(
        _sample_strategy(),
        slippage_bps=10,
        commission_bps=5,
    )

    assert fills["side"].tolist() == ["buy", "sell"]
    assert fills.loc[0, "fill_price"] == pytest.approx(110.0 * 1.001)
    assert fills.loc[1, "fill_price"] == pytest.approx(120.0 * 0.999)
    assert fills.loc[0, "signal_date"] == pd.Timestamp("2024-01-01")


def test_build_round_trip_trade_log_pairs_entry_and_exit() -> None:
    trade_log = build_round_trip_trade_log(
        _sample_strategy(),
        slippage_bps=0,
        commission_bps=0,
    )

    assert len(trade_log) == 1
    assert trade_log.loc[0, "entry_date"] == pd.Timestamp("2024-01-02")
    assert trade_log.loc[0, "exit_date"] == pd.Timestamp("2024-01-04")
    assert trade_log.loc[0, "holding_bars"] == 2
    assert trade_log.loc[0, "gross_return"] == pytest.approx(120.0 / 110.0 - 1)
    assert trade_log.loc[0, "net_return"] == pytest.approx(120.0 / 110.0 - 1)


def test_trade_log_costs_reduce_net_return() -> None:
    no_cost = build_round_trip_trade_log(
        _sample_strategy(),
        slippage_bps=0,
        commission_bps=0,
    )
    with_cost = build_round_trip_trade_log(
        _sample_strategy(),
        slippage_bps=10,
        commission_bps=5,
    )

    assert with_cost.loc[0, "net_return"] < no_cost.loc[0, "net_return"]
    assert with_cost.loc[0, "cost_drag"] > 0


def test_summarize_trade_log() -> None:
    trade_log = build_round_trip_trade_log(
        _sample_strategy(),
        slippage_bps=0,
        commission_bps=0,
    )

    summary = summarize_trade_log(trade_log)

    assert summary.loc[0, "trades"] == 1
    assert summary.loc[0, "closed_trades"] == 1
    assert summary.loc[0, "win_rate"] == pytest.approx(1.0)
    assert summary.loc[0, "final_trade_equity"] == pytest.approx(
        1 + trade_log.loc[0, "net_return"]
    )
    assert "win_rate" in format_trade_summary_table(summary)
