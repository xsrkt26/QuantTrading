from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def build_order_fills(
    strategy: pd.DataFrame,
    slippage_bps: float = 0.0,
    commission_bps: float = 0.0,
) -> pd.DataFrame:
    """Convert position changes into next-open order fills."""
    _validate_costs(slippage_bps=slippage_bps, commission_bps=commission_bps)
    _require_columns(strategy, ["Open", "position", "trade"])

    previous_position = strategy["position"].shift(1).fillna(0).astype(float)
    rows = []

    for fill_date, row in strategy.loc[strategy["trade"] > 0].iterrows():
        position_before = float(previous_position.loc[fill_date])
        position_after = float(row["position"])
        position_change = position_after - position_before
        if np.isclose(position_change, 0.0):
            continue

        side = "buy" if position_change > 0 else "sell"
        open_price = float(row["Open"])
        if pd.isna(open_price):
            raise ValueError(f"Missing Open price on fill date {fill_date}.")

        fill_price = _slippage_adjusted_price(
            open_price=open_price,
            side=side,
            slippage_bps=slippage_bps,
        )
        rows.append(
            {
                "fill_date": fill_date,
                "signal_date": _previous_index_value(strategy.index, fill_date),
                "side": side,
                "position_before": position_before,
                "position_after": position_after,
                "position_change": position_change,
                "open_price": open_price,
                "fill_price": fill_price,
                "slippage_bps": slippage_bps,
                "commission_bps": commission_bps,
                "commission_rate": commission_bps / 10_000,
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "fill_date",
            "signal_date",
            "side",
            "position_before",
            "position_after",
            "position_change",
            "open_price",
            "fill_price",
            "slippage_bps",
            "commission_bps",
            "commission_rate",
        ],
    )


def build_round_trip_trade_log(
    strategy: pd.DataFrame,
    slippage_bps: float = 0.0,
    commission_bps: float = 0.0,
    close_open_position: bool = True,
) -> pd.DataFrame:
    """Pair buy and sell fills into long-only round-trip trades."""
    _require_columns(strategy, ["Open", "position", "trade"])
    fills = build_order_fills(
        strategy,
        slippage_bps=slippage_bps,
        commission_bps=commission_bps,
    )

    rows = []
    active_entry: dict[str, object] | None = None
    for fill in fills.to_dict("records"):
        if fill["side"] == "buy":
            if active_entry is not None:
                raise ValueError("Encountered a buy fill while another trade is open.")
            active_entry = fill
            continue

        if active_entry is None:
            raise ValueError("Encountered a sell fill without an active long trade.")

        rows.append(
            _round_trip_row(
                strategy=strategy,
                entry=active_entry,
                exit_fill=fill,
                commission_bps=commission_bps,
                status="closed",
            )
        )
        active_entry = None

    if active_entry is not None and close_open_position:
        final_date = strategy.index[-1]
        final_open = float(strategy.iloc[-1]["Open"])
        final_exit = {
            "fill_date": final_date,
            "signal_date": pd.NaT,
            "side": "sell",
            "position_before": 1.0,
            "position_after": 0.0,
            "position_change": -1.0,
            "open_price": final_open,
            "fill_price": _slippage_adjusted_price(
                open_price=final_open,
                side="sell",
                slippage_bps=slippage_bps,
            ),
            "slippage_bps": slippage_bps,
            "commission_bps": commission_bps,
            "commission_rate": commission_bps / 10_000,
        }
        rows.append(
            _round_trip_row(
                strategy=strategy,
                entry=active_entry,
                exit_fill=final_exit,
                commission_bps=commission_bps,
                status="open_marked_to_market",
            )
        )

    trade_log = pd.DataFrame(
        rows,
        columns=[
            "trade_number",
            "status",
            "entry_signal_date",
            "entry_date",
            "exit_signal_date",
            "exit_date",
            "holding_bars",
            "holding_days",
            "entry_open_price",
            "exit_open_price",
            "entry_fill_price",
            "exit_fill_price",
            "gross_return",
            "slippage_adjusted_return",
            "net_return",
            "cost_drag",
            "slippage_bps",
            "commission_bps",
            "net_equity",
            "win",
        ],
    )
    if trade_log.empty:
        return trade_log

    trade_log["trade_number"] = np.arange(1, len(trade_log) + 1)
    trade_log["net_equity"] = (1 + trade_log["net_return"]).cumprod()
    trade_log["win"] = trade_log["net_return"] > 0
    return trade_log


def summarize_trade_log(trade_log: pd.DataFrame) -> pd.DataFrame:
    """Summarize a round-trip trade log."""
    columns = [
        "trades",
        "closed_trades",
        "marked_open_trades",
        "win_rate",
        "average_net_return",
        "median_net_return",
        "best_trade_return",
        "worst_trade_return",
        "average_holding_days",
        "profit_factor",
        "final_trade_equity",
        "total_cost_drag",
    ]
    if trade_log.empty:
        return pd.DataFrame(
            [
                {
                    "trades": 0,
                    "closed_trades": 0,
                    "marked_open_trades": 0,
                    "win_rate": np.nan,
                    "average_net_return": np.nan,
                    "median_net_return": np.nan,
                    "best_trade_return": np.nan,
                    "worst_trade_return": np.nan,
                    "average_holding_days": np.nan,
                    "profit_factor": np.nan,
                    "final_trade_equity": 1.0,
                    "total_cost_drag": 0.0,
                }
            ],
            columns=columns,
        )

    returns = trade_log["net_return"]
    winning_returns = returns.loc[returns > 0]
    losing_returns = returns.loc[returns < 0]
    gross_profit = float(winning_returns.sum())
    gross_loss = abs(float(losing_returns.sum()))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.nan

    return pd.DataFrame(
        [
            {
                "trades": int(len(trade_log)),
                "closed_trades": int((trade_log["status"] == "closed").sum()),
                "marked_open_trades": int(
                    (trade_log["status"] == "open_marked_to_market").sum()
                ),
                "win_rate": float((returns > 0).mean()),
                "average_net_return": float(returns.mean()),
                "median_net_return": float(returns.median()),
                "best_trade_return": float(returns.max()),
                "worst_trade_return": float(returns.min()),
                "average_holding_days": float(trade_log["holding_days"].mean()),
                "profit_factor": profit_factor,
                "final_trade_equity": float(trade_log["net_equity"].iloc[-1]),
                "total_cost_drag": float(trade_log["cost_drag"].sum()),
            }
        ],
        columns=columns,
    )


def format_trade_summary_table(summary: pd.DataFrame) -> str:
    """Format trade-log summary rows as a markdown table."""
    formatted = summary.copy()
    pct_columns = [
        "win_rate",
        "average_net_return",
        "median_net_return",
        "best_trade_return",
        "worst_trade_return",
        "total_cost_drag",
    ]
    for col in pct_columns:
        formatted[col] = formatted[col].map(_format_pct)

    formatted["final_trade_equity"] = formatted["final_trade_equity"].map(
        lambda value: f"{value:.4f}"
    )
    formatted["profit_factor"] = formatted["profit_factor"].map(_format_ratio)
    formatted["average_holding_days"] = formatted["average_holding_days"].map(
        lambda value: "nan" if pd.isna(value) else f"{value:.1f}"
    )

    for col in ["trades", "closed_trades", "marked_open_trades"]:
        formatted[col] = formatted[col].map(lambda value: f"{int(value)}")

    return _to_markdown_table(formatted)


def format_trade_log_table(trade_log: pd.DataFrame, n: int = 10) -> str:
    """Format the first n trade-log rows as a compact markdown table."""
    columns = [
        "trade_number",
        "status",
        "entry_date",
        "exit_date",
        "holding_days",
        "entry_fill_price",
        "exit_fill_price",
        "gross_return",
        "net_return",
        "cost_drag",
        "net_equity",
    ]
    formatted = trade_log.head(n)[columns].copy()
    for col in ["entry_date", "exit_date"]:
        formatted[col] = formatted[col].map(_format_date)
    for col in ["entry_fill_price", "exit_fill_price"]:
        formatted[col] = formatted[col].map(lambda value: f"{value:.2f}")
    for col in ["gross_return", "net_return", "cost_drag"]:
        formatted[col] = formatted[col].map(_format_pct)
    formatted["net_equity"] = formatted["net_equity"].map(lambda value: f"{value:.4f}")
    formatted["holding_days"] = formatted["holding_days"].map(lambda value: f"{value:.0f}")
    formatted["trade_number"] = formatted["trade_number"].map(lambda value: f"{int(value)}")
    return _to_markdown_table(formatted)


def plot_trade_log(
    trade_log: pd.DataFrame,
    output_path: str | Path | None = None,
) -> plt.Figure:
    """Plot round-trip returns and cumulative trade equity."""
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    if trade_log.empty:
        for axis in axes:
            axis.text(0.5, 0.5, "No trades", ha="center", va="center")
            axis.set_axis_off()
    else:
        x = trade_log["trade_number"]
        colors = np.where(trade_log["net_return"] >= 0, "#2ca02c", "#d62728")
        axes[0].bar(x, trade_log["net_return"], color=colors)
        axes[0].axhline(0, color="#222222", linewidth=0.8)
        axes[0].set_ylabel("Net Return")
        axes[0].set_title("Round-Trip Trade Returns")
        axes[0].grid(True, axis="y", alpha=0.25)

        axes[1].plot(x, trade_log["net_equity"], marker="o", color="#1f77b4")
        axes[1].set_ylabel("Trade Equity")
        axes[1].set_xlabel("Trade Number")
        axes[1].set_title("Cumulative Equity from Closed Trades")
        axes[1].grid(True, alpha=0.25)

    fig.tight_layout()
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")

    return fig


def _round_trip_row(
    strategy: pd.DataFrame,
    entry: dict[str, object],
    exit_fill: dict[str, object],
    commission_bps: float,
    status: str,
) -> dict[str, object]:
    entry_date = entry["fill_date"]
    exit_date = exit_fill["fill_date"]
    entry_loc = strategy.index.get_loc(entry_date)
    exit_loc = strategy.index.get_loc(exit_date)
    if not isinstance(entry_loc, int) or not isinstance(exit_loc, int):
        raise ValueError("Strategy index must be unique.")

    entry_open = float(entry["open_price"])
    exit_open = float(exit_fill["open_price"])
    entry_fill_price = float(entry["fill_price"])
    exit_fill_price = float(exit_fill["fill_price"])
    commission_rate = commission_bps / 10_000

    gross_return = exit_open / entry_open - 1
    slippage_adjusted_return = exit_fill_price / entry_fill_price - 1
    net_return = (1 + slippage_adjusted_return) * (1 - commission_rate) ** 2 - 1

    return {
        "trade_number": 0,
        "status": status,
        "entry_signal_date": entry["signal_date"],
        "entry_date": entry_date,
        "exit_signal_date": exit_fill["signal_date"],
        "exit_date": exit_date,
        "holding_bars": int(exit_loc - entry_loc),
        "holding_days": _calendar_days(entry_date, exit_date),
        "entry_open_price": entry_open,
        "exit_open_price": exit_open,
        "entry_fill_price": entry_fill_price,
        "exit_fill_price": exit_fill_price,
        "gross_return": gross_return,
        "slippage_adjusted_return": slippage_adjusted_return,
        "net_return": net_return,
        "cost_drag": gross_return - net_return,
        "slippage_bps": entry["slippage_bps"],
        "commission_bps": commission_bps,
        "net_equity": np.nan,
        "win": False,
    }


def _slippage_adjusted_price(
    open_price: float,
    side: str,
    slippage_bps: float,
) -> float:
    slippage_rate = slippage_bps / 10_000
    if side == "buy":
        return open_price * (1 + slippage_rate)
    if side == "sell":
        return open_price * (1 - slippage_rate)
    raise ValueError(f"Unsupported side: {side}")


def _previous_index_value(index: pd.Index, value: object) -> object:
    loc = index.get_loc(value)
    if not isinstance(loc, int):
        raise ValueError("Strategy index must be unique.")
    return index[loc - 1] if loc > 0 else pd.NaT


def _calendar_days(start: object, end: object) -> int:
    if isinstance(start, pd.Timestamp) and isinstance(end, pd.Timestamp):
        return int((end - start).days)
    return 0


def _validate_costs(slippage_bps: float, commission_bps: float) -> None:
    if slippage_bps < 0:
        raise ValueError("slippage_bps must be non-negative.")
    if commission_bps < 0:
        raise ValueError("commission_bps must be non-negative.")


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


def _format_date(value: object) -> str:
    if pd.isna(value):
        return "nan"
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    return str(value)
