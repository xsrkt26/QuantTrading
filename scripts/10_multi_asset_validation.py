from __future__ import annotations

import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_trading.market_data import download_ohlcv  # noqa: E402
from quant_trading.strategy_improvement import (  # noqa: E402
    evaluate_multi_asset_band_filter,
    format_multi_asset_results_table,
    format_multi_asset_summary_table,
    plot_multi_asset_band_filter,
    summarize_multi_asset_band_filter,
)


def main() -> None:
    symbols = ["SPY", "QQQ", "DIA", "IWM", "EFA", "TLT"]
    start = "2005-01-01"
    short_window = 10
    long_window = 200
    band_pct = 0.01
    slippage_bps = 2.0
    commission_bps = 1.0
    transaction_cost_bps = slippage_bps + commission_bps

    data_by_symbol = {
        symbol: download_ohlcv(symbol=symbol, start=start, auto_adjust=True)
        for symbol in symbols
    }
    results = evaluate_multi_asset_band_filter(
        data_by_symbol,
        band_pct=band_pct,
        short_window=short_window,
        long_window=long_window,
        transaction_cost_bps=transaction_cost_bps,
        slippage_bps=slippage_bps,
        commission_bps=commission_bps,
    )
    comparison = summarize_multi_asset_band_filter(results)

    output_dir = PROJECT_ROOT / "reports" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_csv = output_dir / "ma_multi_asset_band_results.csv"
    comparison_csv = output_dir / "ma_multi_asset_band_comparison.csv"
    output_png = output_dir / "ma_multi_asset_band_comparison.png"
    results.to_csv(raw_csv, index=False)
    comparison.to_csv(comparison_csv, index=False)
    plot_multi_asset_band_filter(comparison, output_path=output_png)

    textbook_asset_dir = PROJECT_ROOT / "textbook" / "assets" / "10_multi_asset_validation"
    textbook_asset_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output_png, textbook_asset_dir / output_png.name)

    print(f"Symbols: {', '.join(symbols)}")
    print(f"Strategy: MA {short_window}/{long_window}, band {band_pct:.2%}")
    print(f"Sample start: {start}")
    print(f"Execution: next-open, slippage {slippage_bps:.1f} bps, commission {commission_bps:.1f} bps")
    print()
    print("Raw results:")
    print(format_multi_asset_results_table(results))
    print()
    print("Band vs baseline comparison:")
    print(format_multi_asset_summary_table(comparison))
    print()
    print(f"Raw results saved to: {raw_csv}")
    print(f"Comparison saved to: {comparison_csv}")
    print(f"Comparison chart saved to: {output_png}")

    plt.close("all")


if __name__ == "__main__":
    main()
