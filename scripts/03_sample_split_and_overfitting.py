from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_trading.market_data import download_ohlcv  # noqa: E402
from quant_trading.validation import (  # noqa: E402
    compare_parameter_across_periods,
    evaluate_moving_average_grid,
    format_parameter_table,
    plot_parameter_heatmaps,
    select_top_parameters,
)


def main() -> None:
    symbol = "SPY"
    short_windows = [10, 20, 50]
    long_windows = [50, 100, 200]
    transaction_cost_bps = 1.0

    df = download_ohlcv(symbol=symbol, start="2000-01-01", auto_adjust=True)
    results = evaluate_moving_average_grid(
        df,
        short_windows=short_windows,
        long_windows=long_windows,
        transaction_cost_bps=transaction_cost_bps,
    )

    output_csv = PROJECT_ROOT / "reports" / "generated" / "ma_parameter_grid.csv"
    output_png = PROJECT_ROOT / "reports" / "generated" / "ma_parameter_heatmap.png"
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_csv, index=False)
    plot_parameter_heatmaps(
        results,
        metric="strategy_annualized_return",
        output_path=output_png,
    )

    top_train = select_top_parameters(
        results,
        period="train",
        metric="strategy_calmar",
        n=3,
    )
    best = top_train.iloc[0]
    selected = compare_parameter_across_periods(
        results,
        short_window=int(best["short_window"]),
        long_window=int(best["long_window"]),
    )

    print("Top train parameters by strategy_calmar:")
    print(format_parameter_table(top_train))
    print()
    print(
        "Best train parameter across train/valid/test: "
        f"{int(best['short_window'])}/{int(best['long_window'])}"
    )
    print(format_parameter_table(selected))
    print()
    print(f"Grid results saved to: {output_csv}")
    print(f"Heatmap saved to: {output_png}")

    plt.close("all")


if __name__ == "__main__":
    main()
