from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_trading.market_data import (  # noqa: E402
    add_return_equity_drawdown,
    download_ohlcv,
    format_summary,
    plot_price_equity_drawdown,
    summarize_performance,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download SPY daily data and calculate return, equity, drawdown."
    )
    parser.add_argument("--symbol", default="SPY", help="Ticker symbol, default: SPY")
    parser.add_argument(
        "--start", default="2000-01-01", help="Start date, default: 2000-01-01"
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show the chart window after saving the figure.",
    )
    args = parser.parse_args()

    symbol = args.symbol.upper()
    df = download_ohlcv(symbol=symbol, start=args.start, auto_adjust=True)
    analyzed = add_return_equity_drawdown(df)
    summary = summarize_performance(analyzed, symbol=symbol)

    data_path = PROJECT_ROOT / "data" / "processed" / f"{symbol}_market_data_basics.csv"
    chart_path = (
        PROJECT_ROOT / "reports" / "generated" / f"{symbol}_market_data_basics.png"
    )

    data_path.parent.mkdir(parents=True, exist_ok=True)
    analyzed.to_csv(data_path)
    plot_price_equity_drawdown(analyzed, symbol=symbol, output_path=chart_path)

    print(format_summary(summary))
    print(f"Data saved to: {data_path}")
    print(f"Chart saved to: {chart_path}")

    if args.show:
        plt.show()
    else:
        plt.close("all")


if __name__ == "__main__":
    main()
