import pandas as pd
import pytest

from quant_trading.strategy_improvement import (
    FilterVariant,
    add_filtered_moving_average_strategy_next_open,
    apply_band_filter,
    apply_confirmation_filter,
    evaluate_filter_variants,
)


def test_apply_confirmation_filter_requires_consecutive_days() -> None:
    raw = pd.Series([0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0])

    signal = apply_confirmation_filter(raw, days=3)

    assert signal.tolist() == [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0]


def test_apply_band_filter_holds_inside_band() -> None:
    index = pd.date_range("2024-01-01", periods=6)
    ma_long = pd.Series([100, 100, 100, 100, 100, 100], index=index)
    ma_short = pd.Series([100, 102, 100.5, 99.5, 98.5, 101.5], index=index)

    signal = apply_band_filter(ma_short, ma_long, band_pct=0.01)

    assert signal.tolist() == [0, 1, 1, 1, 0, 1]


def test_add_filtered_strategy_uses_variant_name() -> None:
    df = pd.DataFrame(
        {
            "Open": [100, 101, 102, 103, 104, 105],
            "Close": [100, 101, 102, 103, 104, 105],
        },
        index=pd.date_range("2024-01-01", periods=6),
    )
    variant = FilterVariant("confirm_2d", "confirmation", confirmation_days=2)

    strategy = add_filtered_moving_average_strategy_next_open(
        df,
        variant=variant,
        short_window=2,
        long_window=3,
        transaction_cost_bps=0,
    )

    assert strategy["filter_name"].unique().tolist() == ["confirm_2d"]
    assert "strategy_equity" in strategy.columns


def test_evaluate_filter_variants_returns_comparison_rows() -> None:
    df = pd.DataFrame(
        {
            "Open": [100, 101, 102, 103, 104, 105, 106, 107],
            "Close": [100, 101, 102, 103, 104, 105, 106, 107],
        },
        index=pd.date_range("2024-01-01", periods=8),
    )
    variants = [
        FilterVariant("baseline", "baseline"),
        FilterVariant("confirm_2d", "confirmation", confirmation_days=2),
    ]

    result = evaluate_filter_variants(
        df,
        variants=variants,
        short_window=2,
        long_window=3,
        transaction_cost_bps=0,
        slippage_bps=0,
        commission_bps=0,
    )

    assert result["variant"].tolist() == ["baseline", "confirm_2d"]
    assert "short_trade_contribution" in result.columns


def test_confirmation_filter_rejects_non_positive_days() -> None:
    with pytest.raises(ValueError, match="days"):
        apply_confirmation_filter(pd.Series([1, 0]), days=0)
