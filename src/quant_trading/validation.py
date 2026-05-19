from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from quant_trading.market_data import TRADING_DAYS_PER_YEAR
from quant_trading.moving_average import (
    add_moving_average_strategy,
    add_moving_average_strategy_next_open,
)


@dataclass(frozen=True)
class DateSplit:
    name: str
    start: str
    end: str | None = None


DEFAULT_DATE_SPLITS = [
    DateSplit("train", "2000-01-01", "2014-12-31"),
    DateSplit("valid", "2015-01-01", "2019-12-31"),
    DateSplit("test", "2020-01-01", None),
]


def evaluate_moving_average_grid(
    df: pd.DataFrame,
    short_windows: list[int],
    long_windows: list[int],
    splits: list[DateSplit] | None = None,
    transaction_cost_bps: float = 1.0,
) -> pd.DataFrame:
    """Evaluate moving-average parameters across train/valid/test splits."""
    splits = splits or DEFAULT_DATE_SPLITS
    rows = []

    for short_window in short_windows:
        for long_window in long_windows:
            if short_window >= long_window:
                continue

            strategy = add_moving_average_strategy(
                df,
                short_window=short_window,
                long_window=long_window,
                transaction_cost_bps=transaction_cost_bps,
            )

            for split in splits:
                period = _slice_period(strategy, split)
                if period.empty:
                    continue

                buy_hold = _period_metrics(period["return"])
                strategy_metrics = _period_metrics(period["strategy_return"])

                rows.append(
                    {
                        "short_window": short_window,
                        "long_window": long_window,
                        "period": split.name,
                        "start_date": period.index.min().strftime("%Y-%m-%d"),
                        "end_date": period.index.max().strftime("%Y-%m-%d"),
                        "rows": len(period),
                        "buy_hold_final_equity": buy_hold["final_equity"],
                        "strategy_final_equity": strategy_metrics["final_equity"],
                        "buy_hold_annualized_return": buy_hold["annualized_return"],
                        "strategy_annualized_return": strategy_metrics[
                            "annualized_return"
                        ],
                        "buy_hold_max_drawdown": buy_hold["max_drawdown"],
                        "strategy_max_drawdown": strategy_metrics["max_drawdown"],
                        "strategy_calmar": strategy_metrics["calmar"],
                        "trades": float(period["trade"].sum()),
                        "time_in_market": float(period["position"].mean()),
                    }
                )

    return pd.DataFrame(rows)


def pivot_metric(
    results: pd.DataFrame,
    period: str,
    metric: str = "strategy_annualized_return",
) -> pd.DataFrame:
    """Build a short-window by long-window metric table for one period."""
    period_results = results.loc[results["period"] == period]
    return period_results.pivot(
        index="short_window",
        columns="long_window",
        values=metric,
    ).sort_index().sort_index(axis=1)


def select_top_parameters(
    results: pd.DataFrame,
    period: str,
    metric: str = "strategy_calmar",
    n: int = 5,
) -> pd.DataFrame:
    """Select top parameter rows from a specific period."""
    period_results = results.loc[results["period"] == period].copy()
    return period_results.sort_values(metric, ascending=False).head(n)


def compare_parameter_across_periods(
    results: pd.DataFrame,
    short_window: int,
    long_window: int,
) -> pd.DataFrame:
    """Return train/valid/test rows for one parameter pair."""
    selected = results.loc[
        (results["short_window"] == short_window)
        & (results["long_window"] == long_window)
    ].copy()
    period_order = {"train": 0, "valid": 1, "test": 2}
    selected["period_order"] = selected["period"].map(period_order).fillna(99)
    return selected.sort_values("period_order").drop(columns=["period_order"])


def evaluate_transaction_cost_sensitivity(
    df: pd.DataFrame,
    short_window: int,
    long_window: int,
    transaction_costs_bps: list[float],
) -> pd.DataFrame:
    """Evaluate one moving-average strategy under different cost assumptions."""
    rows = []
    for cost_bps in transaction_costs_bps:
        strategy = add_moving_average_strategy(
            df,
            short_window=short_window,
            long_window=long_window,
            transaction_cost_bps=cost_bps,
        )
        strategy_metrics = _period_metrics(strategy["strategy_return"])
        buy_hold_metrics = _period_metrics(strategy["return"])
        total_cost = float(strategy["transaction_cost"].sum())

        rows.append(
            {
                "short_window": short_window,
                "long_window": long_window,
                "transaction_cost_bps": cost_bps,
                "start_date": strategy.index.min().strftime("%Y-%m-%d"),
                "end_date": strategy.index.max().strftime("%Y-%m-%d"),
                "rows": len(strategy),
                "buy_hold_final_equity": buy_hold_metrics["final_equity"],
                "strategy_final_equity": strategy_metrics["final_equity"],
                "buy_hold_annualized_return": buy_hold_metrics["annualized_return"],
                "strategy_annualized_return": strategy_metrics["annualized_return"],
                "buy_hold_max_drawdown": buy_hold_metrics["max_drawdown"],
                "strategy_max_drawdown": strategy_metrics["max_drawdown"],
                "strategy_calmar": strategy_metrics["calmar"],
                "trades": float(strategy["trade"].sum()),
                "time_in_market": float(strategy["position"].mean()),
                "total_transaction_cost": total_cost,
            }
        )

    return pd.DataFrame(rows)


def compare_execution_assumptions(
    df: pd.DataFrame,
    short_window: int,
    long_window: int,
    transaction_cost_bps: float = 1.0,
) -> pd.DataFrame:
    """Compare close-to-close and next-open execution assumptions."""
    models = [
        ("close_to_close", add_moving_average_strategy(df, short_window, long_window, transaction_cost_bps)),
        (
            "next_open",
            add_moving_average_strategy_next_open(
                df,
                short_window=short_window,
                long_window=long_window,
                transaction_cost_bps=transaction_cost_bps,
            ),
        ),
    ]

    rows = []
    for execution_model, strategy in models:
        strategy_metrics = _period_metrics(strategy["strategy_return"])
        rows.append(
            {
                "execution_model": execution_model,
                "short_window": short_window,
                "long_window": long_window,
                "transaction_cost_bps": transaction_cost_bps,
                "start_date": strategy.index.min().strftime("%Y-%m-%d"),
                "end_date": strategy.index.max().strftime("%Y-%m-%d"),
                "rows": len(strategy),
                "strategy_final_equity": strategy_metrics["final_equity"],
                "strategy_annualized_return": strategy_metrics["annualized_return"],
                "strategy_max_drawdown": strategy_metrics["max_drawdown"],
                "strategy_calmar": strategy_metrics["calmar"],
                "trades": float(strategy["trade"].sum()),
                "time_in_market": float(strategy["position"].mean()),
            }
        )

    return pd.DataFrame(rows)


def plot_parameter_heatmaps(
    results: pd.DataFrame,
    metric: str = "strategy_annualized_return",
    output_path: str | Path | None = None,
) -> plt.Figure:
    """Plot train/valid/test heatmaps for one metric."""
    periods = list(results["period"].drop_duplicates())
    fig, axes = plt.subplots(1, len(periods), figsize=(5 * len(periods), 4), sharey=True)
    if len(periods) == 1:
        axes = [axes]

    metric_values = results[metric].replace([np.inf, -np.inf], np.nan)
    vmin = float(metric_values.min())
    vmax = float(metric_values.max())

    for axis, period in zip(axes, periods):
        table = pivot_metric(results, period=period, metric=metric)
        image = axis.imshow(table.values, aspect="auto", cmap="RdYlGn", vmin=vmin, vmax=vmax)
        axis.set_title(period)
        axis.set_xlabel("long_window")
        axis.set_xticks(range(len(table.columns)))
        axis.set_xticklabels(table.columns)
        axis.set_yticks(range(len(table.index)))
        axis.set_yticklabels(table.index)
        axis.set_ylabel("short_window")

        for row_index in range(table.shape[0]):
            for col_index in range(table.shape[1]):
                value = table.iloc[row_index, col_index]
                if pd.notna(value):
                    axis.text(
                        col_index,
                        row_index,
                        f"{value:.1%}",
                        ha="center",
                        va="center",
                        fontsize=8,
                    )

    fig.colorbar(image, ax=axes, fraction=0.025, pad=0.04)
    fig.suptitle(metric)

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")

    return fig


def plot_cost_sensitivity(
    results: pd.DataFrame,
    output_path: str | Path | None = None,
) -> plt.Figure:
    """Plot annualized return, max drawdown, and Calmar against costs."""
    required_columns = [
        "transaction_cost_bps",
        "strategy_annualized_return",
        "strategy_max_drawdown",
        "strategy_calmar",
    ]
    missing = [col for col in required_columns if col not in results.columns]
    if missing:
        raise ValueError(f"Cost sensitivity results are missing columns: {missing}")

    x = results["transaction_cost_bps"]
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)

    axes[0].plot(x, results["strategy_annualized_return"], marker="o", color="#2ca02c")
    axes[0].set_ylabel("Annual Return")
    axes[0].grid(True, alpha=0.25)

    axes[1].plot(x, results["strategy_max_drawdown"], marker="o", color="#d62728")
    axes[1].set_ylabel("Max Drawdown")
    axes[1].grid(True, alpha=0.25)

    axes[2].plot(x, results["strategy_calmar"], marker="o", color="#1f77b4")
    axes[2].set_ylabel("Calmar")
    axes[2].set_xlabel("Transaction Cost (bps)")
    axes[2].grid(True, alpha=0.25)

    fig.suptitle("Transaction Cost Sensitivity")
    fig.tight_layout()

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")

    return fig


def plot_execution_comparison(
    close_to_close: pd.DataFrame,
    next_open: pd.DataFrame,
    output_path: str | Path | None = None,
) -> plt.Figure:
    """Plot equity and drawdown for two execution assumptions."""
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    close_to_close["strategy_equity"].plot(
        ax=axes[0], color="#2ca02c", label="Close-to-close"
    )
    next_open["strategy_equity"].plot(ax=axes[0], color="#1f77b4", label="Next open")
    axes[0].set_title("Strategy Equity by Execution Assumption")
    axes[0].set_ylabel("Equity")
    axes[0].legend(loc="best")
    axes[0].grid(True, alpha=0.25)

    close_to_close["strategy_drawdown"].plot(
        ax=axes[1], color="#d62728", label="Close-to-close drawdown"
    )
    next_open["strategy_drawdown"].plot(
        ax=axes[1], color="#9467bd", label="Next-open drawdown"
    )
    axes[1].set_title("Strategy Drawdown by Execution Assumption")
    axes[1].set_ylabel("Drawdown")
    axes[1].legend(loc="best")
    axes[1].grid(True, alpha=0.25)

    fig.tight_layout()

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")

    return fig


def format_parameter_table(df: pd.DataFrame) -> str:
    """Format selected parameter rows as a compact markdown table."""
    columns = [
        "period",
        "short_window",
        "long_window",
        "strategy_annualized_return",
        "strategy_max_drawdown",
        "strategy_calmar",
        "trades",
        "time_in_market",
    ]
    formatted = df[columns].copy()
    for col in [
        "strategy_annualized_return",
        "strategy_max_drawdown",
        "time_in_market",
    ]:
        formatted[col] = formatted[col].map(_format_pct)
    formatted["strategy_calmar"] = formatted["strategy_calmar"].map(_format_ratio)
    formatted["trades"] = formatted["trades"].map(lambda value: f"{value:.0f}")

    header = "| " + " | ".join(formatted.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(formatted.columns)) + " |"
    body = [
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in formatted.itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator, *body])


def format_cost_sensitivity_table(df: pd.DataFrame) -> str:
    """Format cost sensitivity rows as a compact markdown table."""
    columns = [
        "transaction_cost_bps",
        "strategy_final_equity",
        "strategy_annualized_return",
        "strategy_max_drawdown",
        "strategy_calmar",
        "trades",
        "total_transaction_cost",
    ]
    formatted = df[columns].copy()
    formatted["transaction_cost_bps"] = formatted["transaction_cost_bps"].map(
        lambda value: f"{value:.1f}"
    )
    formatted["strategy_final_equity"] = formatted["strategy_final_equity"].map(
        lambda value: f"{value:.4f}"
    )
    formatted["strategy_annualized_return"] = formatted[
        "strategy_annualized_return"
    ].map(_format_pct)
    formatted["strategy_max_drawdown"] = formatted["strategy_max_drawdown"].map(
        _format_pct
    )
    formatted["strategy_calmar"] = formatted["strategy_calmar"].map(_format_ratio)
    formatted["trades"] = formatted["trades"].map(lambda value: f"{value:.0f}")
    formatted["total_transaction_cost"] = formatted["total_transaction_cost"].map(
        _format_pct
    )

    header = "| " + " | ".join(formatted.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(formatted.columns)) + " |"
    body = [
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in formatted.itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator, *body])


def format_execution_comparison_table(df: pd.DataFrame) -> str:
    """Format execution comparison rows as a compact markdown table."""
    columns = [
        "execution_model",
        "strategy_final_equity",
        "strategy_annualized_return",
        "strategy_max_drawdown",
        "strategy_calmar",
        "trades",
        "time_in_market",
    ]
    formatted = df[columns].copy()
    formatted["strategy_final_equity"] = formatted["strategy_final_equity"].map(
        lambda value: f"{value:.4f}"
    )
    formatted["strategy_annualized_return"] = formatted[
        "strategy_annualized_return"
    ].map(_format_pct)
    formatted["strategy_max_drawdown"] = formatted["strategy_max_drawdown"].map(
        _format_pct
    )
    formatted["strategy_calmar"] = formatted["strategy_calmar"].map(_format_ratio)
    formatted["trades"] = formatted["trades"].map(lambda value: f"{value:.0f}")
    formatted["time_in_market"] = formatted["time_in_market"].map(_format_pct)

    header = "| " + " | ".join(formatted.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(formatted.columns)) + " |"
    body = [
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in formatted.itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator, *body])


def _slice_period(df: pd.DataFrame, split: DateSplit) -> pd.DataFrame:
    if split.end is None:
        return df.loc[split.start :]
    return df.loc[split.start : split.end]


def _period_metrics(returns: pd.Series) -> dict[str, float]:
    clean_returns = returns.fillna(0)
    equity = (1 + clean_returns).cumprod()
    final_equity = float(equity.iloc[-1])
    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    years = len(clean_returns) / TRADING_DAYS_PER_YEAR
    annualized_return = (
        float(final_equity ** (1 / years) - 1) if years > 0 else np.nan
    )
    max_drawdown = float(drawdown.min())
    calmar = (
        annualized_return / abs(max_drawdown)
        if max_drawdown < 0 and pd.notna(annualized_return)
        else np.nan
    )
    return {
        "final_equity": final_equity,
        "annualized_return": annualized_return,
        "max_drawdown": max_drawdown,
        "calmar": calmar,
    }


def _format_pct(value: float) -> str:
    if pd.isna(value):
        return "nan"
    return f"{value:.2%}"


def _format_ratio(value: float) -> str:
    if pd.isna(value):
        return "nan"
    return f"{value:.2f}"
