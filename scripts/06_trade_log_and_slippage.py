from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_trading.execution import (  # noqa: E402
    build_order_fills,
    build_round_trip_trade_log,
    format_trade_log_table,
    format_trade_summary_table,
    plot_trade_log,
    summarize_trade_log,
)
from quant_trading.market_data import download_ohlcv  # noqa: E402
from quant_trading.moving_average import add_moving_average_strategy_next_open  # noqa: E402


def main() -> None:
    symbol = "SPY"
    short_window = 10
    long_window = 200
    slippage_bps = 2.0
    commission_bps = 1.0

    df = download_ohlcv(symbol=symbol, start="2000-01-01", auto_adjust=True)
    strategy = add_moving_average_strategy_next_open(
        df,
        short_window=short_window,
        long_window=long_window,
        transaction_cost_bps=0.0,
    )

    fills = build_order_fills(
        strategy,
        slippage_bps=slippage_bps,
        commission_bps=commission_bps,
    )
    trade_log = build_round_trip_trade_log(
        strategy,
        slippage_bps=slippage_bps,
        commission_bps=commission_bps,
    )
    summary = summarize_trade_log(trade_log)

    output_dir = PROJECT_ROOT / "reports" / "generated"
    fills_csv = output_dir / "ma_order_fills.csv"
    trade_log_csv = output_dir / "ma_trade_log.csv"
    summary_csv = output_dir / "ma_trade_log_summary.csv"
    chart_path = output_dir / "ma_trade_log.png"
    output_dir.mkdir(parents=True, exist_ok=True)

    fills.to_csv(fills_csv, index=False)
    trade_log.to_csv(trade_log_csv, index=False)
    summary.to_csv(summary_csv, index=False)
    plot_trade_log(trade_log, output_path=chart_path)

    print(f"Strategy: {symbol} MA {short_window}/{long_window}")
    print(f"Execution: next-open, slippage {slippage_bps:.1f} bps, commission {commission_bps:.1f} bps")
    print()
    print(format_trade_summary_table(summary))
    print()
    print("First 10 round-trip trades:")
    print(format_trade_log_table(trade_log, n=10))
    print()
    print(f"Order fills saved to: {fills_csv}")
    print(f"Trade log saved to: {trade_log_csv}")
    print(f"Summary saved to: {summary_csv}")
    print(f"Trade chart saved to: {chart_path}")

    plt.close("all")


if __name__ == "__main__":
    main()
