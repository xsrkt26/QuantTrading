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
    evaluate_band_cost_sensitivity,
    evaluate_band_sensitivity,
    format_band_cost_sensitivity_table,
    format_band_sensitivity_table,
    plot_band_sensitivity,
)


def main() -> None:
    symbol = "SPY"
    short_window = 10
    long_window = 200
    band_pcts = [0.0, 0.005, 0.01, 0.015, 0.02]
    slippage_bps = 2.0
    commission_bps = 1.0
    transaction_cost_bps = slippage_bps + commission_bps

    df = download_ohlcv(symbol=symbol, start="2000-01-01", auto_adjust=True)
    results = evaluate_band_sensitivity(
        df,
        band_pcts=band_pcts,
        short_window=short_window,
        long_window=long_window,
        transaction_cost_bps=transaction_cost_bps,
        slippage_bps=slippage_bps,
        commission_bps=commission_bps,
    )
    cost_results = evaluate_band_cost_sensitivity(
        df,
        band_pcts=[0.0, 0.01],
        cost_bps_values=[0, 3, 10, 25, 50],
        short_window=short_window,
        long_window=long_window,
    )

    output_dir = PROJECT_ROOT / "reports" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_csv = output_dir / "ma_band_sensitivity.csv"
    cost_output_csv = output_dir / "ma_band_cost_sensitivity.csv"
    output_png = output_dir / "ma_band_sensitivity.png"
    results.to_csv(output_csv, index=False)
    cost_results.to_csv(cost_output_csv, index=False)
    plot_band_sensitivity(results, output_path=output_png)

    textbook_asset_dir = PROJECT_ROOT / "textbook" / "assets" / "09_band_robustness"
    textbook_asset_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output_png, textbook_asset_dir / output_png.name)

    print(f"Strategy: {symbol} MA {short_window}/{long_window}")
    print(f"Execution: next-open, slippage {slippage_bps:.1f} bps, commission {commission_bps:.1f} bps")
    print()
    for period in ["train", "valid", "test"]:
        print(f"{period.upper()} band sensitivity:")
        print(format_band_sensitivity_table(results, period=period))
        print()
    print("Cost sensitivity: baseline vs band_1pct")
    print(format_band_cost_sensitivity_table(cost_results))
    print()
    print(f"Band sensitivity saved to: {output_csv}")
    print(f"Band cost sensitivity saved to: {cost_output_csv}")
    print(f"Band sensitivity chart saved to: {output_png}")

    plt.close("all")


if __name__ == "__main__":
    main()
