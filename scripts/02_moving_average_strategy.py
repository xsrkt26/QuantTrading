from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_trading.market_data import download_ohlcv  # noqa: E402
from quant_trading.moving_average import (  # noqa: E402
    add_moving_average_strategy,
    format_moving_average_summary,
    plot_moving_average_strategy,
    summarize_moving_average_strategy,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a long/cash moving-average strategy on daily data."
    )
    parser.add_argument("--symbol", default="SPY", help="Ticker symbol, default: SPY")
    parser.add_argument(
        "--start", default="2000-01-01", help="Start date, default: 2000-01-01"
    )
    parser.add_argument(
        "--short-window",
        type=int,
        default=20,
        help="Short moving-average window, default: 20",
    )
    parser.add_argument(
        "--long-window",
        type=int,
        default=100,
        help="Long moving-average window, default: 100",
    )
    parser.add_argument(
        "--transaction-cost-bps",
        type=float,
        default=1.0,
        help="One-way transaction cost in basis points, default: 1.0",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show the chart window after saving the figure.",
    )
    args = parser.parse_args()

    symbol = args.symbol.upper()
    df = download_ohlcv(symbol=symbol, start=args.start, auto_adjust=True)
    strategy = add_moving_average_strategy(
        df,
        short_window=args.short_window,
        long_window=args.long_window,
        transaction_cost_bps=args.transaction_cost_bps,
    )
    summary = summarize_moving_average_strategy(
        strategy,
        symbol=symbol,
        short_window=args.short_window,
        long_window=args.long_window,
        transaction_cost_bps=args.transaction_cost_bps,
    )

    suffix = f"ma_{args.short_window}_{args.long_window}"
    data_path = PROJECT_ROOT / "data" / "processed" / f"{symbol}_{suffix}.csv"
    chart_path = PROJECT_ROOT / "reports" / "generated" / f"{symbol}_{suffix}.png"

    data_path.parent.mkdir(parents=True, exist_ok=True)
    strategy.to_csv(data_path)
    plot_moving_average_strategy(
        strategy,
        symbol=symbol,
        short_window=args.short_window,
        long_window=args.long_window,
        output_path=chart_path,
    )

    print(format_moving_average_summary(summary))
    print(f"Data saved to: {data_path}")
    print(f"Chart saved to: {chart_path}")

    if args.show:
        plt.show()
    else:
        plt.close("all")


if __name__ == "__main__":
    main()
