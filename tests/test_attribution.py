import pandas as pd
import pytest

from quant_trading.attribution import (
    add_trade_attribution,
    format_attribution_summary_table,
    format_contributors_table,
    select_top_contributors,
    summarize_by_duration,
    summarize_trade_attribution,
)


def _sample_trade_log() -> pd.DataFrame:
    returns = pd.Series([0.10, -0.05, 0.20])
    return pd.DataFrame(
        {
            "trade_number": [1, 2, 3],
            "status": ["closed", "closed", "closed"],
            "entry_date": pd.date_range("2024-01-01", periods=3),
            "exit_date": pd.date_range("2024-01-11", periods=3),
            "holding_days": [10, 40, 300],
            "net_return": returns,
            "net_equity": (1 + returns).cumprod(),
        }
    )


def test_add_trade_attribution_uses_compounded_equity_gain() -> None:
    attributed = add_trade_attribution(_sample_trade_log())

    assert attributed.loc[0, "starting_equity"] == pytest.approx(1.0)
    assert attributed.loc[0, "equity_gain"] == pytest.approx(0.10)
    assert attributed.loc[1, "equity_gain"] == pytest.approx(1.10 * -0.05)
    assert attributed["equity_gain"].sum() == pytest.approx(
        attributed["net_equity"].iloc[-1] - 1
    )
    assert attributed["contribution_to_total_gain"].sum() == pytest.approx(1.0)


def test_summarize_trade_attribution() -> None:
    attributed = add_trade_attribution(_sample_trade_log())
    summary = summarize_trade_attribution(attributed, top_fraction=1 / 3)

    assert summary.loc[0, "trades"] == 3
    assert summary.loc[0, "top_trade_count"] == 1
    assert summary.loc[0, "total_equity_gain"] == pytest.approx(
        attributed["equity_gain"].sum()
    )
    assert summary.loc[0, "top_trade_share"] > 0
    assert "top_trade_share" in format_attribution_summary_table(summary)


def test_select_top_contributors() -> None:
    attributed = add_trade_attribution(_sample_trade_log())

    best = select_top_contributors(attributed, n=1, largest=True)
    worst = select_top_contributors(attributed, n=1, largest=False)

    assert int(best.iloc[0]["trade_number"]) == 3
    assert int(worst.iloc[0]["trade_number"]) == 2
    assert "equity_gain" in format_contributors_table(best)


def test_summarize_by_duration() -> None:
    attributed = add_trade_attribution(_sample_trade_log())
    summary = summarize_by_duration(attributed)

    assert summary["trades"].sum() == 3
    assert summary.loc[summary["duration_bucket"] == "<=30d", "trades"].iloc[0] == 1
    assert (
        summary["contribution_to_total_gain"].sum()
        == pytest.approx(1.0)
    )
