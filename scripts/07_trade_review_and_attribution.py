from __future__ import annotations

import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_trading.attribution import (  # noqa: E402
    add_trade_attribution,
    format_attribution_summary_table,
    format_contributors_table,
    format_duration_summary_table,
    plot_trade_attribution,
    select_top_contributors,
    summarize_by_duration,
    summarize_trade_attribution,
)
from quant_trading.execution import build_round_trip_trade_log  # noqa: E402
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
    trade_log = build_round_trip_trade_log(
        strategy,
        slippage_bps=slippage_bps,
        commission_bps=commission_bps,
    )
    attributed = add_trade_attribution(trade_log)
    summary = summarize_trade_attribution(attributed)
    duration_summary = summarize_by_duration(attributed)
    top_winners = select_top_contributors(attributed, n=5, largest=True)
    worst_losers = select_top_contributors(attributed, n=5, largest=False)

    output_dir = PROJECT_ROOT / "reports" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    attributed_csv = output_dir / "ma_trade_attribution.csv"
    summary_csv = output_dir / "ma_trade_attribution_summary.csv"
    duration_csv = output_dir / "ma_trade_duration_attribution.csv"
    chart_path = output_dir / "ma_trade_attribution.png"

    attributed.to_csv(attributed_csv, index=False)
    summary.to_csv(summary_csv, index=False)
    duration_summary.to_csv(duration_csv, index=False)
    plot_trade_attribution(attributed, duration_summary, output_path=chart_path)

    textbook_asset_dir = PROJECT_ROOT / "textbook" / "assets" / "07_trade_review_and_attribution"
    textbook_asset_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(chart_path, textbook_asset_dir / chart_path.name)

    print(f"Strategy: {symbol} MA {short_window}/{long_window}")
    print(f"Execution: next-open, slippage {slippage_bps:.1f} bps, commission {commission_bps:.1f} bps")
    print()
    print("Attribution summary:")
    print(format_attribution_summary_table(summary))
    print()
    print("Top 5 contributors:")
    print(format_contributors_table(top_winners))
    print()
    print("Worst 5 contributors:")
    print(format_contributors_table(worst_losers))
    print()
    print("Holding-period attribution:")
    print(format_duration_summary_table(duration_summary))
    print()
    print(f"Trade attribution saved to: {attributed_csv}")
    print(f"Attribution summary saved to: {summary_csv}")
    print(f"Duration attribution saved to: {duration_csv}")
    print(f"Attribution chart saved to: {chart_path}")

    plt.close("all")


if __name__ == "__main__":
    main()
