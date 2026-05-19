import pandas as pd
import pytest

from quant_trading.market_data import add_return_equity_drawdown, summarize_performance


def test_add_return_equity_drawdown() -> None:
    df = pd.DataFrame(
        {"Close": [100.0, 110.0, 99.0, 120.0]},
        index=pd.date_range("2024-01-01", periods=4),
    )

    result = add_return_equity_drawdown(df)

    assert pd.isna(result["return"].iloc[0])
    assert result["return"].iloc[1] == pytest.approx(0.10)
    assert result["equity"].iloc[-1] == pytest.approx(1.20)
    assert result["drawdown"].iloc[2] == pytest.approx(-0.10)
    assert result["drawdown"].min() == pytest.approx(-0.10)


def test_summarize_performance() -> None:
    df = pd.DataFrame(
        {"Close": [100.0, 110.0, 99.0, 120.0]},
        index=pd.date_range("2024-01-01", periods=4),
    )
    result = add_return_equity_drawdown(df)

    summary = summarize_performance(result, symbol="TEST")

    assert summary.symbol == "TEST"
    assert summary.rows == 4
    assert summary.final_equity == pytest.approx(1.20)
    assert summary.total_return == pytest.approx(0.20)
    assert summary.max_drawdown == pytest.approx(-0.10)
