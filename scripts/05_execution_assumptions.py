from __future__ import annotations

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
    add_moving_average_strategy_next_open,
)
from quant_trading.validation import (  # noqa: E402
    compare_execution_assumptions,
    format_execution_comparison_table,
    plot_execution_comparison,
)


def main() -> None:
    symbol = "SPY"
    short_window = 10
    long_window = 200
    transaction_cost_bps = 1.0

    df = download_ohlcv(symbol=symbol, start="2000-01-01", auto_adjust=True)
    close_to_close = add_moving_average_strategy(
        df,
        short_window=short_window,
        long_window=long_window,
        transaction_cost_bps=transaction_cost_bps,
    )
    next_open = add_moving_average_strategy_next_open(
        df,
        short_window=short_window,
        long_window=long_window,
        transaction_cost_bps=transaction_cost_bps,
    )
    comparison = compare_execution_assumptions(
        df,
        short_window=short_window,
        long_window=long_window,
        transaction_cost_bps=transaction_cost_bps,
    )

    output_csv = PROJECT_ROOT / "reports" / "generated" / "ma_execution_comparison.csv"
    output_png = PROJECT_ROOT / "reports" / "generated" / "ma_execution_comparison.png"
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(output_csv, index=False)
    plot_execution_comparison(close_to_close, next_open, output_path=output_png)

    print(f"Strategy: {symbol} MA {short_window}/{long_window}")
    print(format_execution_comparison_table(comparison))
    print()
    print(f"Execution comparison saved to: {output_csv}")
    print(f"Execution chart saved to: {output_png}")

    plt.close("all")


if __name__ == "__main__":
    main()
