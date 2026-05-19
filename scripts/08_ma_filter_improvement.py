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
    DEFAULT_FILTER_VARIANTS,
    evaluate_filter_variants,
    format_filter_variant_table,
    plot_filter_variant_comparison,
)


def main() -> None:
    symbol = "SPY"
    short_window = 10
    long_window = 200
    slippage_bps = 2.0
    commission_bps = 1.0
    transaction_cost_bps = slippage_bps + commission_bps

    df = download_ohlcv(symbol=symbol, start="2000-01-01", auto_adjust=True)
    results = evaluate_filter_variants(
        df,
        variants=DEFAULT_FILTER_VARIANTS,
        short_window=short_window,
        long_window=long_window,
        transaction_cost_bps=transaction_cost_bps,
        slippage_bps=slippage_bps,
        commission_bps=commission_bps,
    )

    output_dir = PROJECT_ROOT / "reports" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_csv = output_dir / "ma_filter_improvement.csv"
    output_png = output_dir / "ma_filter_improvement.png"
    results.to_csv(output_csv, index=False)
    plot_filter_variant_comparison(results, output_path=output_png)

    textbook_asset_dir = PROJECT_ROOT / "textbook" / "assets" / "08_ma_filter_improvement"
    textbook_asset_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output_png, textbook_asset_dir / output_png.name)

    print(f"Strategy: {symbol} MA {short_window}/{long_window}")
    print(f"Execution: next-open, slippage {slippage_bps:.1f} bps, commission {commission_bps:.1f} bps")
    print()
    print(format_filter_variant_table(results))
    print()
    print(f"Filter results saved to: {output_csv}")
    print(f"Filter chart saved to: {output_png}")

    plt.close("all")


if __name__ == "__main__":
    main()
