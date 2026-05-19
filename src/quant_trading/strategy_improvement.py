from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from quant_trading.attribution import add_trade_attribution, summarize_by_duration, summarize_trade_attribution
from quant_trading.execution import build_round_trip_trade_log, summarize_trade_log
from quant_trading.market_data import TRADING_DAYS_PER_YEAR, add_return_equity_drawdown


@dataclass(frozen=True)
class FilterVariant:
    name: str
    filter_type: str
    confirmation_days: int = 1
    band_pct: float = 0.0
    volatility_window: int = 20
    max_volatility: float | None = None


DEFAULT_FILTER_VARIANTS = [
    FilterVariant("baseline", "baseline"),
    FilterVariant("confirm_3d", "confirmation", confirmation_days=3),
    FilterVariant("confirm_5d", "confirmation", confirmation_days=5),
    FilterVariant("band_1pct", "band", band_pct=0.01),
    FilterVariant(
        "vol_cap_25pct",
        "volatility",
        volatility_window=20,
        max_volatility=0.25,
    ),
]


def add_filtered_moving_average_strategy_next_open(
    df: pd.DataFrame,
    variant: FilterVariant,
    short_window: int = 10,
    long_window: int = 200,
    transaction_cost_bps: float = 3.0,
) -> pd.DataFrame:
    """Add a next-open moving-average strategy with one simple signal filter."""
    _validate_windows(short_window, long_window)
    if transaction_cost_bps < 0:
        raise ValueError("transaction_cost_bps must be non-negative.")
    _require_columns(df, ["Open", "Close"])

    result = add_return_equity_drawdown(df)
    result["open_to_next_open_return"] = result["Open"].shift(-1) / result["Open"] - 1
    result["ma_short"] = (
        result["Close"].rolling(short_window, min_periods=short_window).mean()
    )
    result["ma_long"] = result["Close"].rolling(long_window, min_periods=long_window).mean()
    result["ma_ratio"] = result["ma_short"] / result["ma_long"] - 1
    result["realized_volatility"] = (
        result["return"].rolling(variant.volatility_window).std()
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )

    has_both_averages = result["ma_short"].notna() & result["ma_long"].notna()
    raw_signal = ((result["ma_short"] > result["ma_long"]) & has_both_averages).astype(
        int
    )
    result["raw_signal"] = raw_signal
    result["filter_name"] = variant.name
    result["signal"] = build_filtered_signal(
        result,
        raw_signal=raw_signal,
        variant=variant,
        has_both_averages=has_both_averages,
    )

    result["position"] = result["signal"].shift(1).fillna(0).astype(float)
    result["trade"] = result["position"].diff().abs().fillna(result["position"].abs())

    cost_rate = transaction_cost_bps / 10_000
    result["strategy_return_before_cost"] = (
        result["position"] * result["open_to_next_open_return"].fillna(0)
    )
    result["transaction_cost"] = result["trade"] * cost_rate
    result["strategy_return"] = (
        result["strategy_return_before_cost"] - result["transaction_cost"]
    )
    result["strategy_equity"] = (1 + result["strategy_return"]).cumprod()
    result["strategy_running_max"] = result["strategy_equity"].cummax()
    result["strategy_drawdown"] = (
        result["strategy_equity"] / result["strategy_running_max"] - 1
    )

    return result


def build_filtered_signal(
    strategy: pd.DataFrame,
    raw_signal: pd.Series,
    variant: FilterVariant,
    has_both_averages: pd.Series,
) -> pd.Series:
    """Build a filtered 0/1 signal from the raw moving-average signal."""
    if variant.filter_type == "baseline":
        return raw_signal.astype(int)
    if variant.filter_type == "confirmation":
        return apply_confirmation_filter(raw_signal, days=variant.confirmation_days)
    if variant.filter_type == "band":
        return apply_band_filter(
            strategy["ma_short"],
            strategy["ma_long"],
            band_pct=variant.band_pct,
            valid=has_both_averages,
        )
    if variant.filter_type == "volatility":
        if variant.max_volatility is None:
            raise ValueError("volatility filter requires max_volatility.")
        volatility_ok = strategy["realized_volatility"] <= variant.max_volatility
        return (raw_signal.astype(bool) & volatility_ok.fillna(False)).astype(int)
    raise ValueError(f"Unsupported filter_type: {variant.filter_type}")


def apply_confirmation_filter(raw_signal: pd.Series, days: int) -> pd.Series:
    """Require consecutive raw-signal days before changing state."""
    if days <= 0:
        raise ValueError("days must be positive.")

    state = 0
    true_streak = 0
    false_streak = 0
    values = []

    for raw_value in raw_signal.fillna(0).astype(int):
        if raw_value == 1:
            true_streak += 1
            false_streak = 0
        else:
            false_streak += 1
            true_streak = 0

        if state == 0 and true_streak >= days:
            state = 1
        elif state == 1 and false_streak >= days:
            state = 0

        values.append(state)

    return pd.Series(values, index=raw_signal.index, dtype=int)


def apply_band_filter(
    ma_short: pd.Series,
    ma_long: pd.Series,
    band_pct: float,
    valid: pd.Series | None = None,
) -> pd.Series:
    """Use a moving-average gap band to reduce small crossover flips."""
    if band_pct < 0:
        raise ValueError("band_pct must be non-negative.")

    valid = valid if valid is not None else ma_short.notna() & ma_long.notna()
    ratio = ma_short / ma_long - 1
    state = 0
    values = []

    for is_valid, gap in zip(valid.fillna(False), ratio):
        if not is_valid or pd.isna(gap):
            state = 0
        elif state == 0 and gap > band_pct:
            state = 1
        elif state == 1 and gap < -band_pct:
            state = 0
        values.append(state)

    return pd.Series(values, index=ma_short.index, dtype=int)


def evaluate_filter_variants(
    df: pd.DataFrame,
    variants: list[FilterVariant] | None = None,
    short_window: int = 10,
    long_window: int = 200,
    transaction_cost_bps: float = 3.0,
    slippage_bps: float = 2.0,
    commission_bps: float = 1.0,
) -> pd.DataFrame:
    """Evaluate simple moving-average filters with trade-log attribution metrics."""
    variants = variants or DEFAULT_FILTER_VARIANTS
    rows = []

    for variant in variants:
        strategy = add_filtered_moving_average_strategy_next_open(
            df,
            variant=variant,
            short_window=short_window,
            long_window=long_window,
            transaction_cost_bps=transaction_cost_bps,
        )
        trade_log = build_round_trip_trade_log(
            strategy,
            slippage_bps=slippage_bps,
            commission_bps=commission_bps,
        )
        trade_summary = summarize_trade_log(trade_log)
        attributed = add_trade_attribution(trade_log)
        attribution_summary = summarize_trade_attribution(attributed)
        duration_summary = summarize_by_duration(attributed)
        daily_metrics = _performance_metrics(strategy["strategy_return"])

        short_duration = duration_summary.loc[
            duration_summary["duration_bucket"] == "<=30d"
        ]
        short_trade_contribution = (
            float(short_duration["contribution_to_total_gain"].iloc[0])
            if not short_duration.empty
            else np.nan
        )
        short_trade_count = (
            int(short_duration["trades"].iloc[0]) if not short_duration.empty else 0
        )

        rows.append(
            {
                "variant": variant.name,
                "filter_type": variant.filter_type,
                "final_trade_equity": float(trade_summary.loc[0, "final_trade_equity"]),
                "daily_final_equity": daily_metrics["final_equity"],
                "annualized_return": daily_metrics["annualized_return"],
                "max_drawdown": daily_metrics["max_drawdown"],
                "calmar": daily_metrics["calmar"],
                "single_side_trades": float(strategy["trade"].sum()),
                "round_trip_trades": int(trade_summary.loc[0, "trades"]),
                "win_rate": float(trade_summary.loc[0, "win_rate"]),
                "average_holding_days": float(
                    trade_summary.loc[0, "average_holding_days"]
                ),
                "top_trade_share": float(
                    attribution_summary.loc[0, "top_trade_share"]
                ),
                "largest_trade_share": float(
                    attribution_summary.loc[0, "largest_trade_share"]
                ),
                "short_trade_count": short_trade_count,
                "short_trade_contribution": short_trade_contribution,
                "time_in_market": float(strategy["position"].mean()),
            }
        )

    return pd.DataFrame(rows)


def plot_filter_variant_comparison(
    results: pd.DataFrame,
    output_path: str | Path | None = None,
) -> plt.Figure:
    """Plot key metrics for moving-average filter variants."""
    required_columns = [
        "variant",
        "final_trade_equity",
        "max_drawdown",
        "single_side_trades",
        "short_trade_contribution",
    ]
    _require_columns(results, required_columns)

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    x = np.arange(len(results))
    labels = results["variant"]

    axes[0, 0].bar(x, results["final_trade_equity"], color="#1f77b4")
    axes[0, 0].set_title("Final Trade Equity")
    axes[0, 0].set_ylabel("Equity")
    axes[0, 0].grid(True, axis="y", alpha=0.25)

    axes[0, 1].bar(x, results["max_drawdown"], color="#d62728")
    axes[0, 1].set_title("Daily Max Drawdown")
    axes[0, 1].set_ylabel("Drawdown")
    axes[0, 1].grid(True, axis="y", alpha=0.25)

    axes[1, 0].bar(x, results["single_side_trades"], color="#9467bd")
    axes[1, 0].set_title("Single-Side Trades")
    axes[1, 0].set_ylabel("Trades")
    axes[1, 0].grid(True, axis="y", alpha=0.25)

    colors = np.where(results["short_trade_contribution"] >= 0, "#2ca02c", "#d62728")
    axes[1, 1].bar(x, results["short_trade_contribution"], color=colors)
    axes[1, 1].axhline(0, color="#222222", linewidth=0.8)
    axes[1, 1].set_title("<=30d Trade Contribution")
    axes[1, 1].set_ylabel("Contribution")
    axes[1, 1].grid(True, axis="y", alpha=0.25)

    for axis in axes.ravel():
        axis.set_xticks(x)
        axis.set_xticklabels(labels, rotation=20, ha="right")

    fig.tight_layout()
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")

    return fig


def format_filter_variant_table(results: pd.DataFrame) -> str:
    """Format filter-variant results as markdown."""
    columns = [
        "variant",
        "final_trade_equity",
        "annualized_return",
        "max_drawdown",
        "calmar",
        "single_side_trades",
        "round_trip_trades",
        "win_rate",
        "top_trade_share",
        "short_trade_count",
        "short_trade_contribution",
    ]
    formatted = results[columns].copy()
    formatted["final_trade_equity"] = formatted["final_trade_equity"].map(
        lambda value: f"{value:.4f}"
    )
    for col in [
        "annualized_return",
        "max_drawdown",
        "win_rate",
        "top_trade_share",
        "short_trade_contribution",
    ]:
        formatted[col] = formatted[col].map(_format_pct)
    formatted["calmar"] = formatted["calmar"].map(_format_ratio)
    for col in ["single_side_trades", "round_trip_trades", "short_trade_count"]:
        formatted[col] = formatted[col].map(lambda value: f"{value:.0f}")
    return _to_markdown_table(formatted)


def _performance_metrics(returns: pd.Series) -> dict[str, float]:
    clean_returns = returns.fillna(0)
    equity = (1 + clean_returns).cumprod()
    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    years = len(clean_returns) / TRADING_DAYS_PER_YEAR
    final_equity = float(equity.iloc[-1])
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


def _validate_windows(short_window: int, long_window: int) -> None:
    if short_window <= 0 or long_window <= 0:
        raise ValueError("window sizes must be positive.")
    if short_window >= long_window:
        raise ValueError("short_window must be smaller than long_window.")


def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"DataFrame is missing columns: {missing}")


def _to_markdown_table(df: pd.DataFrame) -> str:
    header = "| " + " | ".join(df.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    body = [
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in df.itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator, *body])


def _format_pct(value: float) -> str:
    if pd.isna(value):
        return "nan"
    return f"{value:.2%}"


def _format_ratio(value: float) -> str:
    if pd.isna(value):
        return "nan"
    return f"{value:.2f}"
