from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib.ticker import PercentFormatter


TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class PerformanceSummary:
    symbol: str
    start_date: str
    end_date: str
    rows: int
    final_equity: float
    total_return: float
    annualized_return: float
    annualized_volatility: float
    max_drawdown: float


def download_ohlcv(
    symbol: str = "SPY",
    start: str = "2000-01-01",
    auto_adjust: bool = True,
) -> pd.DataFrame:
    """Download daily OHLCV data from Yahoo Finance."""
    df = yf.download(
        symbol,
        start=start,
        auto_adjust=auto_adjust,
        progress=False,
        threads=False,
    )

    if df.empty:
        raise ValueError(f"No data returned for symbol={symbol!r}.")

    df = _normalize_yfinance_columns(df, symbol)
    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Downloaded data is missing columns: {missing}")

    df = df[required_columns].dropna(subset=["Close"]).sort_index()
    df.index.name = "Date"
    return df


def add_return_equity_drawdown(
    df: pd.DataFrame,
    price_col: str = "Close",
) -> pd.DataFrame:
    """Add daily return, equity curve, running high, and drawdown columns."""
    if price_col not in df.columns:
        raise ValueError(f"Missing price column: {price_col}")

    result = df.copy()
    result["return"] = result[price_col].pct_change()
    result["equity"] = (1 + result["return"].fillna(0)).cumprod()
    result["running_max"] = result["equity"].cummax()
    result["drawdown"] = result["equity"] / result["running_max"] - 1
    return result


def summarize_performance(df: pd.DataFrame, symbol: str) -> PerformanceSummary:
    """Calculate a compact buy-and-hold performance summary."""
    required_columns = ["return", "equity", "drawdown"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Data is missing analysis columns: {missing}")

    daily_returns = df["return"].dropna()
    final_equity = float(df["equity"].iloc[-1])
    years = len(daily_returns) / TRADING_DAYS_PER_YEAR

    total_return = final_equity - 1
    annualized_return = final_equity ** (1 / years) - 1 if years > 0 else np.nan
    annualized_volatility = (
        float(daily_returns.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR))
        if len(daily_returns) > 1
        else np.nan
    )
    max_drawdown = float(df["drawdown"].min())

    return PerformanceSummary(
        symbol=symbol,
        start_date=df.index.min().strftime("%Y-%m-%d"),
        end_date=df.index.max().strftime("%Y-%m-%d"),
        rows=len(df),
        final_equity=final_equity,
        total_return=total_return,
        annualized_return=float(annualized_return),
        annualized_volatility=annualized_volatility,
        max_drawdown=max_drawdown,
    )


def plot_price_equity_drawdown(
    df: pd.DataFrame,
    symbol: str,
    output_path: str | Path | None = None,
) -> plt.Figure:
    """Plot close price, equity curve, and drawdown curve."""
    required_columns = ["Close", "equity", "drawdown"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Data is missing plot columns: {missing}")

    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

    df["Close"].plot(ax=axes[0], color="#1f77b4", linewidth=1.2)
    axes[0].set_title(f"{symbol} Adjusted Close")
    axes[0].set_ylabel("Price")
    axes[0].grid(True, alpha=0.25)

    df["equity"].plot(ax=axes[1], color="#2ca02c", linewidth=1.2)
    axes[1].set_title("Buy-and-Hold Equity Curve")
    axes[1].set_ylabel("Equity")
    axes[1].grid(True, alpha=0.25)

    df["drawdown"].plot(ax=axes[2], color="#d62728", linewidth=1.2)
    axes[2].set_title("Drawdown")
    axes[2].set_ylabel("Drawdown")
    axes[2].yaxis.set_major_formatter(PercentFormatter(xmax=1))
    axes[2].grid(True, alpha=0.25)

    fig.tight_layout()

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150)

    return fig


def format_summary(summary: PerformanceSummary) -> str:
    """Format a summary for terminal output."""
    return "\n".join(
        [
            f"Symbol: {summary.symbol}",
            f"Date range: {summary.start_date} to {summary.end_date}",
            f"Rows: {summary.rows}",
            f"Final equity: {summary.final_equity:.4f}",
            f"Total return: {_format_pct(summary.total_return)}",
            f"Annualized return: {_format_pct(summary.annualized_return)}",
            f"Annualized volatility: {_format_pct(summary.annualized_volatility)}",
            f"Max drawdown: {_format_pct(summary.max_drawdown)}",
        ]
    )


def _normalize_yfinance_columns(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if not isinstance(df.columns, pd.MultiIndex):
        return df

    if symbol in df.columns.get_level_values(-1):
        return df.xs(symbol, axis=1, level=-1)

    if symbol in df.columns.get_level_values(0):
        return df.xs(symbol, axis=1, level=0)

    normalized = df.copy()
    normalized.columns = [
        "_".join(str(part) for part in column if part) for column in normalized.columns
    ]
    return normalized


def _format_pct(value: float) -> str:
    if pd.isna(value):
        return "nan"
    return f"{value:.2%}"
