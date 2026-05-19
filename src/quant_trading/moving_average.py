from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter

from quant_trading.market_data import TRADING_DAYS_PER_YEAR, add_return_equity_drawdown


@dataclass(frozen=True)
class MovingAverageSummary:
    symbol: str
    short_window: int
    long_window: int
    transaction_cost_bps: float
    start_date: str
    end_date: str
    rows: int
    buy_hold_final_equity: float
    strategy_final_equity: float
    buy_hold_total_return: float
    strategy_total_return: float
    buy_hold_annualized_return: float
    strategy_annualized_return: float
    buy_hold_max_drawdown: float
    strategy_max_drawdown: float
    trades: float
    time_in_market: float


def add_moving_average_strategy(
    df: pd.DataFrame,
    short_window: int = 20,
    long_window: int = 100,
    transaction_cost_bps: float = 1.0,
) -> pd.DataFrame:
    """Add a long/cash moving-average strategy to daily OHLCV data."""
    _validate_windows(short_window, long_window)
    if transaction_cost_bps < 0:
        raise ValueError("transaction_cost_bps must be non-negative.")

    result = add_return_equity_drawdown(df)
    result["ma_short"] = (
        result["Close"].rolling(short_window, min_periods=short_window).mean()
    )
    result["ma_long"] = result["Close"].rolling(long_window, min_periods=long_window).mean()

    has_both_averages = result["ma_short"].notna() & result["ma_long"].notna()
    result["signal"] = ((result["ma_short"] > result["ma_long"]) & has_both_averages).astype(
        int
    )

    # Today's signal is only tradable from the next trading day.
    result["position"] = result["signal"].shift(1).fillna(0).astype(float)
    result["trade"] = result["position"].diff().abs().fillna(result["position"].abs())

    cost_rate = transaction_cost_bps / 10_000
    result["strategy_return_before_cost"] = result["position"] * result["return"].fillna(0)
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


def add_moving_average_strategy_next_open(
    df: pd.DataFrame,
    short_window: int = 20,
    long_window: int = 100,
    transaction_cost_bps: float = 1.0,
) -> pd.DataFrame:
    """Add a moving-average strategy executed at the next trading day's open."""
    _validate_windows(short_window, long_window)
    if transaction_cost_bps < 0:
        raise ValueError("transaction_cost_bps must be non-negative.")
    for column in ["Open", "Close"]:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")

    result = add_return_equity_drawdown(df)
    result["open_to_next_open_return"] = result["Open"].shift(-1) / result["Open"] - 1
    result["ma_short"] = (
        result["Close"].rolling(short_window, min_periods=short_window).mean()
    )
    result["ma_long"] = result["Close"].rolling(long_window, min_periods=long_window).mean()

    has_both_averages = result["ma_short"].notna() & result["ma_long"].notna()
    result["signal"] = ((result["ma_short"] > result["ma_long"]) & has_both_averages).astype(
        int
    )

    # Signal from yesterday's close is executed at today's open.
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


def summarize_moving_average_strategy(
    df: pd.DataFrame,
    symbol: str,
    short_window: int,
    long_window: int,
    transaction_cost_bps: float,
) -> MovingAverageSummary:
    """Summarize buy-and-hold and moving-average strategy performance."""
    required_columns = [
        "return",
        "equity",
        "drawdown",
        "position",
        "trade",
        "strategy_return",
        "strategy_equity",
        "strategy_drawdown",
    ]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Data is missing strategy columns: {missing}")

    buy_hold_final_equity = float(df["equity"].iloc[-1])
    strategy_final_equity = float(df["strategy_equity"].iloc[-1])
    buy_hold_total_return = buy_hold_final_equity - 1
    strategy_total_return = strategy_final_equity - 1

    buy_hold_daily_returns = df["return"].dropna()
    strategy_daily_returns = df["strategy_return"].dropna()

    buy_hold_years = len(buy_hold_daily_returns) / TRADING_DAYS_PER_YEAR
    strategy_years = len(strategy_daily_returns) / TRADING_DAYS_PER_YEAR

    return MovingAverageSummary(
        symbol=symbol,
        short_window=short_window,
        long_window=long_window,
        transaction_cost_bps=transaction_cost_bps,
        start_date=df.index.min().strftime("%Y-%m-%d"),
        end_date=df.index.max().strftime("%Y-%m-%d"),
        rows=len(df),
        buy_hold_final_equity=buy_hold_final_equity,
        strategy_final_equity=strategy_final_equity,
        buy_hold_total_return=buy_hold_total_return,
        strategy_total_return=strategy_total_return,
        buy_hold_annualized_return=_annualized_return(
            buy_hold_final_equity, buy_hold_years
        ),
        strategy_annualized_return=_annualized_return(
            strategy_final_equity, strategy_years
        ),
        buy_hold_max_drawdown=float(df["drawdown"].min()),
        strategy_max_drawdown=float(df["strategy_drawdown"].min()),
        trades=float(df["trade"].sum()),
        time_in_market=float(df["position"].mean()),
    )


def plot_moving_average_strategy(
    df: pd.DataFrame,
    symbol: str,
    short_window: int,
    long_window: int,
    output_path: str | Path | None = None,
) -> plt.Figure:
    """Plot price with moving averages, equity curves, and drawdowns."""
    required_columns = [
        "Close",
        "ma_short",
        "ma_long",
        "equity",
        "drawdown",
        "strategy_equity",
        "strategy_drawdown",
    ]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Data is missing plot columns: {missing}")

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    df["Close"].plot(ax=axes[0], color="#1f77b4", linewidth=1.0, label="Close")
    df["ma_short"].plot(
        ax=axes[0], color="#2ca02c", linewidth=1.0, label=f"MA {short_window}"
    )
    df["ma_long"].plot(
        ax=axes[0], color="#ff7f0e", linewidth=1.0, label=f"MA {long_window}"
    )
    axes[0].set_title(f"{symbol} Close and Moving Averages")
    axes[0].set_ylabel("Price")
    axes[0].legend(loc="best")
    axes[0].grid(True, alpha=0.25)

    df["equity"].plot(ax=axes[1], color="#7f7f7f", linewidth=1.0, label="Buy & Hold")
    df["strategy_equity"].plot(
        ax=axes[1], color="#2ca02c", linewidth=1.2, label="MA Strategy"
    )
    axes[1].set_title("Equity Curve Comparison")
    axes[1].set_ylabel("Equity")
    axes[1].legend(loc="best")
    axes[1].grid(True, alpha=0.25)

    df["drawdown"].plot(
        ax=axes[2], color="#7f7f7f", linewidth=1.0, label="Buy & Hold Drawdown"
    )
    df["strategy_drawdown"].plot(
        ax=axes[2], color="#d62728", linewidth=1.1, label="MA Strategy Drawdown"
    )
    axes[2].set_title("Drawdown Comparison")
    axes[2].set_ylabel("Drawdown")
    axes[2].yaxis.set_major_formatter(PercentFormatter(xmax=1))
    axes[2].legend(loc="best")
    axes[2].grid(True, alpha=0.25)

    fig.tight_layout()

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150)

    return fig


def format_moving_average_summary(summary: MovingAverageSummary) -> str:
    """Format the moving-average strategy summary for terminal output."""
    return "\n".join(
        [
            f"Symbol: {summary.symbol}",
            f"Date range: {summary.start_date} to {summary.end_date}",
            f"Windows: short={summary.short_window}, long={summary.long_window}",
            f"Transaction cost: {summary.transaction_cost_bps:.2f} bps per trade",
            f"Rows: {summary.rows}",
            f"Buy & hold final equity: {summary.buy_hold_final_equity:.4f}",
            f"Strategy final equity: {summary.strategy_final_equity:.4f}",
            f"Buy & hold total return: {_format_pct(summary.buy_hold_total_return)}",
            f"Strategy total return: {_format_pct(summary.strategy_total_return)}",
            "Buy & hold annualized return: "
            f"{_format_pct(summary.buy_hold_annualized_return)}",
            f"Strategy annualized return: {_format_pct(summary.strategy_annualized_return)}",
            f"Buy & hold max drawdown: {_format_pct(summary.buy_hold_max_drawdown)}",
            f"Strategy max drawdown: {_format_pct(summary.strategy_max_drawdown)}",
            f"Trades: {summary.trades:.0f}",
            f"Time in market: {_format_pct(summary.time_in_market)}",
        ]
    )


def _validate_windows(short_window: int, long_window: int) -> None:
    if short_window <= 0 or long_window <= 0:
        raise ValueError("Moving-average windows must be positive.")
    if short_window >= long_window:
        raise ValueError("short_window must be smaller than long_window.")


def _annualized_return(final_equity: float, years: float) -> float:
    if years <= 0:
        return np.nan
    return float(final_equity ** (1 / years) - 1)


def _format_pct(value: float) -> str:
    if pd.isna(value):
        return "nan"
    return f"{value:.2%}"
