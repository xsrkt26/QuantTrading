import pandas as pd

from quant_trading.validation import (
    DateSplit,
    compare_execution_assumptions,
    compare_parameter_across_periods,
    evaluate_moving_average_grid,
    evaluate_transaction_cost_sensitivity,
    pivot_metric,
    select_top_parameters,
)


def test_evaluate_moving_average_grid_returns_split_rows() -> None:
    df = pd.DataFrame(
        {"Close": [100, 101, 102, 103, 104, 105, 106, 107]},
        index=pd.date_range("2024-01-01", periods=8),
    )
    splits = [
        DateSplit("train", "2024-01-01", "2024-01-04"),
        DateSplit("test", "2024-01-05", None),
    ]

    result = evaluate_moving_average_grid(
        df,
        short_windows=[2],
        long_windows=[3],
        splits=splits,
        transaction_cost_bps=0,
    )

    assert set(result["period"]) == {"train", "test"}
    assert result["short_window"].unique().tolist() == [2]
    assert result["long_window"].unique().tolist() == [3]
    assert "strategy_calmar" in result.columns


def test_select_top_and_compare_parameters() -> None:
    results = pd.DataFrame(
        [
            {
                "period": "train",
                "short_window": 2,
                "long_window": 5,
                "strategy_calmar": 0.5,
                "strategy_annualized_return": 0.10,
            },
            {
                "period": "train",
                "short_window": 3,
                "long_window": 6,
                "strategy_calmar": 0.8,
                "strategy_annualized_return": 0.12,
            },
            {
                "period": "test",
                "short_window": 3,
                "long_window": 6,
                "strategy_calmar": 0.1,
                "strategy_annualized_return": 0.03,
            },
        ]
    )

    top = select_top_parameters(results, period="train", metric="strategy_calmar", n=1)
    selected = compare_parameter_across_periods(results, short_window=3, long_window=6)

    assert int(top.iloc[0]["short_window"]) == 3
    assert selected["period"].tolist() == ["train", "test"]


def test_pivot_metric() -> None:
    results = pd.DataFrame(
        [
            {
                "period": "train",
                "short_window": 2,
                "long_window": 5,
                "strategy_annualized_return": 0.10,
            },
            {
                "period": "train",
                "short_window": 2,
                "long_window": 10,
                "strategy_annualized_return": 0.15,
            },
        ]
    )

    table = pivot_metric(results, period="train")

    assert table.loc[2, 5] == 0.10
    assert table.loc[2, 10] == 0.15


def test_evaluate_transaction_cost_sensitivity() -> None:
    df = pd.DataFrame(
        {"Close": [100, 101, 102, 103, 104, 105, 106, 107]},
        index=pd.date_range("2024-01-01", periods=8),
    )

    result = evaluate_transaction_cost_sensitivity(
        df,
        short_window=2,
        long_window=3,
        transaction_costs_bps=[0, 10],
    )

    assert result["transaction_cost_bps"].tolist() == [0, 10]
    assert result.loc[0, "trades"] == result.loc[1, "trades"]
    assert result.loc[1, "total_transaction_cost"] > result.loc[0, "total_transaction_cost"]
    assert result.loc[1, "strategy_final_equity"] < result.loc[0, "strategy_final_equity"]


def test_compare_execution_assumptions() -> None:
    df = pd.DataFrame(
        {
            "Open": [100, 101, 102, 103, 104, 105, 106, 107],
            "Close": [100, 101, 102, 103, 104, 105, 106, 107],
        },
        index=pd.date_range("2024-01-01", periods=8),
    )

    result = compare_execution_assumptions(
        df,
        short_window=2,
        long_window=3,
        transaction_cost_bps=0,
    )

    assert set(result["execution_model"]) == {"close_to_close", "next_open"}
    assert result["trades"].nunique() == 1
