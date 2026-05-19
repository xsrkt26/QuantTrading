from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DURATION_BINS = [-np.inf, 30, 90, 252, np.inf]
DURATION_LABELS = ["<=30d", "31-90d", "91-252d", ">252d"]


def add_trade_attribution(trade_log: pd.DataFrame) -> pd.DataFrame:
    """Add compounded equity contribution columns to a round-trip trade log."""
    if trade_log.empty:
        return _empty_attribution_frame()

    _require_columns(
        trade_log,
        ["trade_number", "net_return", "net_equity", "holding_days"],
    )

    result = trade_log.copy()
    result["starting_equity"] = result["net_equity"].shift(1).fillna(1.0)
    result["ending_equity"] = result["net_equity"]
    result["equity_gain"] = result["ending_equity"] - result["starting_equity"]
    result["cumulative_equity_gain"] = result["equity_gain"].cumsum()

    total_gain = float(result["equity_gain"].sum())
    if np.isclose(total_gain, 0.0):
        result["contribution_to_total_gain"] = np.nan
        result["cumulative_contribution"] = np.nan
    else:
        result["contribution_to_total_gain"] = result["equity_gain"] / total_gain
        result["cumulative_contribution"] = (
            result["cumulative_equity_gain"] / total_gain
        )

    result["contribution_rank"] = result["equity_gain"].rank(
        ascending=False,
        method="first",
    )
    result["return_rank"] = result["net_return"].rank(
        ascending=False,
        method="first",
    )
    result["duration_bucket"] = pd.cut(
        result["holding_days"],
        bins=DURATION_BINS,
        labels=DURATION_LABELS,
    )
    return result


def summarize_trade_attribution(
    attributed_trades: pd.DataFrame,
    top_fraction: float = 0.2,
) -> pd.DataFrame:
    """Summarize whether performance is concentrated in a few trades."""
    if attributed_trades.empty:
        return pd.DataFrame(
            [
                {
                    "trades": 0,
                    "top_trade_count": 0,
                    "final_equity": 1.0,
                    "total_equity_gain": 0.0,
                    "positive_equity_gain": 0.0,
                    "negative_equity_gain": 0.0,
                    "top_trade_gain": 0.0,
                    "top_trade_share": np.nan,
                    "largest_trade_share": np.nan,
                    "worst_trade_drag": np.nan,
                }
            ]
        )

    if not 0 < top_fraction <= 1:
        raise ValueError("top_fraction must be in the interval (0, 1].")

    _require_columns(attributed_trades, ["net_equity", "equity_gain"])

    trades = len(attributed_trades)
    top_trade_count = max(1, int(np.ceil(trades * top_fraction)))
    total_gain = float(attributed_trades["equity_gain"].sum())
    positive_gain = float(attributed_trades.loc[attributed_trades["equity_gain"] > 0, "equity_gain"].sum())
    negative_gain = float(attributed_trades.loc[attributed_trades["equity_gain"] < 0, "equity_gain"].sum())
    top_trade_gain = float(
        attributed_trades.nlargest(top_trade_count, "equity_gain")["equity_gain"].sum()
    )
    largest_gain = float(attributed_trades["equity_gain"].max())
    worst_gain = float(attributed_trades["equity_gain"].min())

    return pd.DataFrame(
        [
            {
                "trades": trades,
                "top_trade_count": top_trade_count,
                "final_equity": float(attributed_trades["net_equity"].iloc[-1]),
                "total_equity_gain": total_gain,
                "positive_equity_gain": positive_gain,
                "negative_equity_gain": negative_gain,
                "top_trade_gain": top_trade_gain,
                "top_trade_share": _safe_share(top_trade_gain, total_gain),
                "largest_trade_share": _safe_share(largest_gain, total_gain),
                "worst_trade_drag": _safe_share(worst_gain, total_gain),
            }
        ]
    )


def summarize_by_duration(attributed_trades: pd.DataFrame) -> pd.DataFrame:
    """Summarize contribution by holding-period bucket."""
    if attributed_trades.empty:
        return pd.DataFrame(
            columns=[
                "duration_bucket",
                "trades",
                "win_rate",
                "average_net_return",
                "total_equity_gain",
                "contribution_to_total_gain",
            ]
        )

    _require_columns(
        attributed_trades,
        ["duration_bucket", "net_return", "equity_gain"],
    )

    total_gain = float(attributed_trades["equity_gain"].sum())
    grouped = attributed_trades.groupby("duration_bucket", observed=False)
    rows = []
    for bucket, group in grouped:
        if group.empty:
            rows.append(
                {
                    "duration_bucket": str(bucket),
                    "trades": 0,
                    "win_rate": np.nan,
                    "average_net_return": np.nan,
                    "total_equity_gain": 0.0,
                    "contribution_to_total_gain": 0.0,
                }
            )
            continue

        equity_gain = float(group["equity_gain"].sum())
        rows.append(
            {
                "duration_bucket": str(bucket),
                "trades": int(len(group)),
                "win_rate": float((group["net_return"] > 0).mean()),
                "average_net_return": float(group["net_return"].mean()),
                "total_equity_gain": equity_gain,
                "contribution_to_total_gain": _safe_share(equity_gain, total_gain),
            }
        )

    return pd.DataFrame(rows)


def select_top_contributors(
    attributed_trades: pd.DataFrame,
    n: int = 5,
    largest: bool = True,
) -> pd.DataFrame:
    """Select the largest or smallest equity contributors."""
    if attributed_trades.empty:
        return attributed_trades.copy()
    if n <= 0:
        raise ValueError("n must be positive.")

    sorted_trades = attributed_trades.sort_values(
        "equity_gain",
        ascending=not largest,
    )
    return sorted_trades.head(n).copy()


def format_attribution_summary_table(summary: pd.DataFrame) -> str:
    """Format attribution summary as markdown."""
    formatted = summary.copy()
    for col in ["final_equity"]:
        formatted[col] = formatted[col].map(lambda value: f"{value:.4f}")
    for col in [
        "total_equity_gain",
        "positive_equity_gain",
        "negative_equity_gain",
        "top_trade_gain",
    ]:
        formatted[col] = formatted[col].map(lambda value: f"{value:.4f}")
    for col in ["top_trade_share", "largest_trade_share", "worst_trade_drag"]:
        formatted[col] = formatted[col].map(_format_pct)
    for col in ["trades", "top_trade_count"]:
        formatted[col] = formatted[col].map(lambda value: f"{int(value)}")
    return _to_markdown_table(formatted)


def format_contributors_table(trades: pd.DataFrame) -> str:
    """Format selected trade contributors as markdown."""
    columns = [
        "trade_number",
        "status",
        "entry_date",
        "exit_date",
        "holding_days",
        "net_return",
        "equity_gain",
        "contribution_to_total_gain",
        "net_equity",
    ]
    formatted = trades[columns].copy()
    for col in ["entry_date", "exit_date"]:
        formatted[col] = formatted[col].map(_format_date)
    formatted["holding_days"] = formatted["holding_days"].map(
        lambda value: f"{value:.0f}"
    )
    formatted["net_return"] = formatted["net_return"].map(_format_pct)
    formatted["equity_gain"] = formatted["equity_gain"].map(lambda value: f"{value:.4f}")
    formatted["contribution_to_total_gain"] = formatted[
        "contribution_to_total_gain"
    ].map(_format_pct)
    formatted["net_equity"] = formatted["net_equity"].map(lambda value: f"{value:.4f}")
    formatted["trade_number"] = formatted["trade_number"].map(
        lambda value: f"{int(value)}"
    )
    return _to_markdown_table(formatted)


def format_duration_summary_table(summary: pd.DataFrame) -> str:
    """Format duration attribution rows as markdown."""
    formatted = summary.copy()
    formatted["trades"] = formatted["trades"].map(lambda value: f"{int(value)}")
    formatted["win_rate"] = formatted["win_rate"].map(_format_pct)
    formatted["average_net_return"] = formatted["average_net_return"].map(_format_pct)
    formatted["total_equity_gain"] = formatted["total_equity_gain"].map(
        lambda value: f"{value:.4f}"
    )
    formatted["contribution_to_total_gain"] = formatted[
        "contribution_to_total_gain"
    ].map(_format_pct)
    return _to_markdown_table(formatted)


def plot_trade_attribution(
    attributed_trades: pd.DataFrame,
    duration_summary: pd.DataFrame,
    output_path: str | Path | None = None,
) -> plt.Figure:
    """Plot per-trade contribution and holding-period attribution."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    if attributed_trades.empty:
        for axis in axes.ravel():
            axis.text(0.5, 0.5, "No trades", ha="center", va="center")
            axis.set_axis_off()
    else:
        colors = np.where(attributed_trades["equity_gain"] >= 0, "#2ca02c", "#d62728")
        axes[0, 0].bar(
            attributed_trades["trade_number"],
            attributed_trades["equity_gain"],
            color=colors,
        )
        axes[0, 0].axhline(0, color="#222222", linewidth=0.8)
        axes[0, 0].set_title("Equity Gain by Trade")
        axes[0, 0].set_xlabel("Trade Number")
        axes[0, 0].set_ylabel("Equity Gain")
        axes[0, 0].grid(True, axis="y", alpha=0.25)

        axes[0, 1].plot(
            attributed_trades["trade_number"],
            attributed_trades["cumulative_contribution"],
            marker="o",
            color="#1f77b4",
        )
        axes[0, 1].axhline(1.0, color="#222222", linewidth=0.8, linestyle="--")
        axes[0, 1].set_title("Cumulative Contribution to Total Gain")
        axes[0, 1].set_xlabel("Trade Number")
        axes[0, 1].set_ylabel("Contribution")
        axes[0, 1].grid(True, alpha=0.25)

        top = select_top_contributors(attributed_trades, n=5, largest=True).sort_values(
            "equity_gain",
        )
        axes[1, 0].barh(
            top["trade_number"].astype(str),
            top["equity_gain"],
            color="#2ca02c",
        )
        axes[1, 0].set_title("Top 5 Equity Contributors")
        axes[1, 0].set_xlabel("Equity Gain")
        axes[1, 0].set_ylabel("Trade Number")
        axes[1, 0].grid(True, axis="x", alpha=0.25)

        duration_colors = np.where(
            duration_summary["total_equity_gain"] >= 0,
            "#2ca02c",
            "#d62728",
        )
        axes[1, 1].bar(
            duration_summary["duration_bucket"],
            duration_summary["total_equity_gain"],
            color=duration_colors,
        )
        axes[1, 1].axhline(0, color="#222222", linewidth=0.8)
        axes[1, 1].set_title("Equity Gain by Holding Period")
        axes[1, 1].set_xlabel("Holding Period")
        axes[1, 1].set_ylabel("Equity Gain")
        axes[1, 1].grid(True, axis="y", alpha=0.25)

    fig.tight_layout()
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")

    return fig


def _safe_share(numerator: float, denominator: float) -> float:
    if np.isclose(denominator, 0.0):
        return np.nan
    return numerator / denominator


def _empty_attribution_frame() -> pd.DataFrame:
    columns = [
        "trade_number",
        "net_return",
        "net_equity",
        "holding_days",
        "starting_equity",
        "ending_equity",
        "equity_gain",
        "cumulative_equity_gain",
        "contribution_to_total_gain",
        "cumulative_contribution",
        "contribution_rank",
        "return_rank",
        "duration_bucket",
    ]
    return pd.DataFrame(columns=columns)


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


def _format_date(value: object) -> str:
    if pd.isna(value):
        return "nan"
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    return str(value)
