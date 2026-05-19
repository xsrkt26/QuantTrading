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
    evaluate_transaction_cost_sensitivity,
    format_cost_sensitivity_table,
    plot_cost_sensitivity,
)


def main() -> None:
    symbol = "SPY"
    short_window = 10
    long_window = 200
    costs_bps = [0, 1, 5, 10, 25, 50]

    df = download_ohlcv(symbol=symbol, start="2000-01-01", auto_adjust=True)
    results = evaluate_transaction_cost_sensitivity(
        df,
        short_window=short_window,
        long_window=long_window,
        transaction_costs_bps=costs_bps,
    )

    output_csv = PROJECT_ROOT / "reports" / "generated" / "ma_cost_sensitivity.csv"
    output_png = PROJECT_ROOT / "reports" / "generated" / "ma_cost_sensitivity.png"
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_csv, index=False)
    plot_cost_sensitivity(results, output_path=output_png)

    print(f"Strategy: {symbol} MA {short_window}/{long_window}")
    print(format_cost_sensitivity_table(results))
    print()
    print(f"Cost sensitivity results saved to: {output_csv}")
    print(f"Cost sensitivity chart saved to: {output_png}")

    plt.close("all")


if __name__ == "__main__":
    main()
