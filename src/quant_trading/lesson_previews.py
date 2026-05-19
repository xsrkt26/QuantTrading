from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_future_lesson_preview(chapter: int, output_path: str | Path) -> plt.Figure:
    """Generate a compact preview figure for a future textbook chapter."""
    if chapter not in range(11, 31):
        raise ValueError(f"Unknown future lesson chapter: {chapter}")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(10_000 + chapter)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))

    if chapter == 11:
        _plot_equal_weight_portfolio(axes, rng)
    elif chapter == 12:
        _plot_correlation_drawdown(axes, rng)
    elif chapter == 13:
        _plot_position_sizing(axes, rng)
    elif chapter == 14:
        _plot_rebalancing_turnover(axes, rng)
    elif chapter == 15:
        _plot_breakout(axes, rng)
    elif chapter == 16:
        _plot_time_series_momentum(axes, rng)
    elif chapter == 17:
        _plot_mean_reversion(axes, rng)
    elif chapter == 18:
        _plot_multi_strategy(axes, rng)
    elif chapter == 19:
        _plot_factor_layers(axes, rng)
    elif chapter == 20:
        _plot_factor_ic_turnover(axes, rng)
    elif chapter == 21:
        _plot_neutralization(axes, rng)
    elif chapter == 22:
        _plot_multi_factor(axes, rng)
    elif chapter == 23:
        _plot_time_series_stats(axes, rng)
    elif chapter == 24:
        _plot_pairs_trading(axes, rng)
    elif chapter == 25:
        _plot_ml_signal(axes, rng)
    elif chapter == 26:
        _plot_ml_validation(axes, rng)
    elif chapter == 27:
        _plot_research_pipeline(axes)
    elif chapter == 28:
        _plot_backtest_framework(axes)
    elif chapter == 29:
        _plot_paper_trading(axes, rng)
    elif chapter == 30:
        _plot_risk_policy(axes, rng)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    return fig


def _equity_from_returns(returns: np.ndarray) -> np.ndarray:
    return np.cumprod(1 + returns)


def _drawdown(equity: np.ndarray) -> np.ndarray:
    return equity / np.maximum.accumulate(equity) - 1


def _plot_equal_weight_portfolio(axes: np.ndarray, rng: np.random.Generator) -> None:
    returns = rng.normal([0.00035, 0.00025, 0.00015], [0.010, 0.008, 0.006], (252, 3))
    equities = np.apply_along_axis(_equity_from_returns, 0, returns)
    portfolio = _equity_from_returns(returns.mean(axis=1))
    for i, label in enumerate(["Asset A", "Asset B", "Asset C"]):
        axes[0].plot(equities[:, i], alpha=0.7, label=label)
    axes[0].plot(portfolio, color="black", linewidth=2, label="Equal weight")
    axes[0].set_title("Equal Weight Portfolio")
    axes[0].legend()
    axes[1].plot(_drawdown(portfolio), color="#d62728")
    axes[1].set_title("Portfolio Drawdown")
    _grid(axes)


def _plot_correlation_drawdown(axes: np.ndarray, rng: np.random.Generator) -> None:
    corr = np.array([[1.0, 0.65, 0.25], [0.65, 1.0, 0.10], [0.25, 0.10, 1.0]])
    image = axes[0].imshow(corr, vmin=-1, vmax=1, cmap="coolwarm")
    axes[0].set_xticks(range(3), ["Equity", "Small", "Bond"])
    axes[0].set_yticks(range(3), ["Equity", "Small", "Bond"])
    axes[0].set_title("Correlation Matrix")
    plt.colorbar(image, ax=axes[0], fraction=0.046)
    eq1 = _equity_from_returns(rng.normal(0.0003, 0.011, 252))
    eq2 = _equity_from_returns(rng.normal(0.00025, 0.007, 252))
    axes[1].plot(_drawdown(eq1), label="Single asset", color="#d62728")
    axes[1].plot(_drawdown((eq1 + eq2) / 2), label="Portfolio", color="#1f77b4")
    axes[1].set_title("Diversification and Drawdown")
    axes[1].legend()
    _grid(axes)


def _plot_position_sizing(axes: np.ndarray, rng: np.random.Generator) -> None:
    vol = np.linspace(0.08, 0.32, 8)
    inv_vol_weight = (1 / vol) / (1 / vol).sum()
    axes[0].bar(range(len(vol)), inv_vol_weight, color="#1f77b4")
    axes[0].set_title("Inverse Volatility Weights")
    axes[0].set_xlabel("Asset")
    axes[1].plot(vol, 0.12 / vol, marker="o", color="#2ca02c")
    axes[1].set_title("Volatility Target Leverage")
    axes[1].set_xlabel("Realized Volatility")
    axes[1].set_ylabel("Target / Realized")
    _grid(axes)


def _plot_rebalancing_turnover(axes: np.ndarray, rng: np.random.Generator) -> None:
    months = np.arange(12)
    weights = 0.5 + np.cumsum(rng.normal(0, 0.04, 12))
    weights = np.clip(weights, 0.2, 0.8)
    axes[0].plot(months, weights, marker="o", label="Asset A weight")
    axes[0].axhline(0.5, linestyle="--", color="black", label="Target")
    axes[0].set_title("Weight Drift")
    axes[0].legend()
    turnover = np.abs(np.diff(weights, prepend=0.5))
    axes[1].bar(months, turnover, color="#9467bd")
    axes[1].set_title("Turnover by Rebalance")
    _grid(axes)


def _plot_breakout(axes: np.ndarray, rng: np.random.Generator) -> None:
    price = 100 + np.cumsum(rng.normal(0.08, 1.0, 180))
    high = pd.Series(price).rolling(40).max().shift(1)
    low = pd.Series(price).rolling(40).min().shift(1)
    axes[0].plot(price, label="Price")
    axes[0].plot(high, label="40d high", color="#2ca02c")
    axes[0].plot(low, label="40d low", color="#d62728")
    axes[0].set_title("Breakout Channels")
    axes[0].legend()
    signal = (price > high.fillna(np.inf)).astype(int)
    axes[1].step(range(len(signal)), signal, where="post")
    axes[1].set_title("Breakout Signal")
    _grid(axes)


def _plot_time_series_momentum(axes: np.ndarray, rng: np.random.Generator) -> None:
    returns = rng.normal(0.0003, 0.01, 252)
    price = _equity_from_returns(returns)
    momentum = pd.Series(price).pct_change(60)
    axes[0].plot(price, label="Price")
    axes[0].set_title("Price")
    axes[1].plot(momentum, color="#1f77b4", label="60d momentum")
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_title("Time Series Momentum")
    _grid(axes)


def _plot_mean_reversion(axes: np.ndarray, rng: np.random.Generator) -> None:
    z = np.zeros(220)
    for i in range(1, len(z)):
        z[i] = 0.92 * z[i - 1] + rng.normal(0, 0.35)
    axes[0].plot(z, color="#1f77b4")
    axes[0].axhline(1.5, color="#d62728", linestyle="--")
    axes[0].axhline(-1.5, color="#2ca02c", linestyle="--")
    axes[0].set_title("Mean-Reversion Z-Score")
    signal = np.where(z < -1.5, 1, np.where(z > 1.5, -1, 0))
    axes[1].step(range(len(signal)), signal, where="post")
    axes[1].set_title("Contrarian Signal")
    _grid(axes)


def _plot_multi_strategy(axes: np.ndarray, rng: np.random.Generator) -> None:
    strategies = rng.normal([0.00025, 0.00015, 0.00020], [0.008, 0.006, 0.005], (252, 3))
    for i, label in enumerate(["Trend", "Mean rev", "Carry"]):
        axes[0].plot(_equity_from_returns(strategies[:, i]), label=label)
    combined = _equity_from_returns(strategies.mean(axis=1))
    axes[0].plot(combined, color="black", linewidth=2, label="Combined")
    axes[0].set_title("Strategy Equity")
    axes[0].legend()
    axes[1].plot(_drawdown(combined), color="#d62728")
    axes[1].set_title("Combined Drawdown")
    _grid(axes)


def _plot_factor_layers(axes: np.ndarray, rng: np.random.Generator) -> None:
    layers = ["Q1 low", "Q2", "Q3", "Q4", "Q5 high"]
    returns = np.array([-0.02, 0.01, 0.03, 0.05, 0.08]) + rng.normal(0, 0.005, 5)
    axes[0].bar(layers, returns, color="#1f77b4")
    axes[0].set_title("Forward Return by Factor Layer")
    axes[0].tick_params(axis="x", rotation=20)
    long_short = returns[-1] - returns[0]
    axes[1].bar(["Q5-Q1"], [long_short], color="#2ca02c")
    axes[1].set_title("Long-Short Spread")
    _grid(axes)


def _plot_factor_ic_turnover(axes: np.ndarray, rng: np.random.Generator) -> None:
    ic = rng.normal(0.04, 0.12, 60)
    axes[0].plot(ic, color="#1f77b4")
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("Monthly Rank IC")
    turnover = np.clip(rng.normal(0.35, 0.08, 12), 0, 1)
    axes[1].bar(range(12), turnover, color="#9467bd")
    axes[1].set_title("Factor Portfolio Turnover")
    _grid(axes)


def _plot_neutralization(axes: np.ndarray, rng: np.random.Generator) -> None:
    size = rng.normal(0, 1, 120)
    raw_factor = 0.7 * size + rng.normal(0, 0.7, 120)
    neutral = raw_factor - np.polyval(np.polyfit(size, raw_factor, 1), size)
    axes[0].scatter(size, raw_factor, alpha=0.6)
    axes[0].set_title("Raw Factor vs Size")
    axes[1].scatter(size, neutral, alpha=0.6, color="#2ca02c")
    axes[1].set_title("Neutralized Factor vs Size")
    _grid(axes)


def _plot_multi_factor(axes: np.ndarray, rng: np.random.Generator) -> None:
    names = ["Value", "Momentum", "Quality", "Low vol"]
    weights = np.array([0.25, 0.35, 0.20, 0.20])
    axes[0].bar(names, weights, color="#1f77b4")
    axes[0].set_title("Factor Weights")
    corr = np.array([[1, .1, .3, -.2], [.1, 1, .2, -.1], [.3, .2, 1, .0], [-.2, -.1, .0, 1]])
    image = axes[1].imshow(corr, vmin=-1, vmax=1, cmap="coolwarm")
    axes[1].set_xticks(range(4), names, rotation=20)
    axes[1].set_yticks(range(4), names)
    axes[1].set_title("Factor Correlation")
    plt.colorbar(image, ax=axes[1], fraction=0.046)


def _plot_time_series_stats(axes: np.ndarray, rng: np.random.Generator) -> None:
    returns = rng.standard_t(df=5, size=800) * 0.01
    axes[0].hist(returns, bins=40, color="#1f77b4", alpha=0.8)
    axes[0].set_title("Return Distribution")
    ac = [pd.Series(returns).autocorr(lag=i) for i in range(1, 11)]
    axes[1].bar(range(1, 11), ac, color="#9467bd")
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_title("Autocorrelation")
    _grid(axes)


def _plot_pairs_trading(axes: np.ndarray, rng: np.random.Generator) -> None:
    x = np.cumsum(rng.normal(0, 1, 250))
    spread = np.zeros(250)
    for i in range(1, len(spread)):
        spread[i] = 0.95 * spread[i - 1] + rng.normal(0, 0.4)
    y = x + spread
    axes[0].plot(x, label="Asset X")
    axes[0].plot(y, label="Asset Y")
    axes[0].set_title("Cointegrated Pair")
    axes[0].legend()
    z = (spread - pd.Series(spread).rolling(40).mean()) / pd.Series(spread).rolling(40).std()
    axes[1].plot(z, color="#1f77b4")
    axes[1].axhline(2, color="#d62728", linestyle="--")
    axes[1].axhline(-2, color="#2ca02c", linestyle="--")
    axes[1].set_title("Spread Z-Score")
    _grid(axes)


def _plot_ml_signal(axes: np.ndarray, rng: np.random.Generator) -> None:
    feature = rng.normal(0, 1, 240)
    future_return = 0.002 * feature + rng.normal(0, 0.02, 240)
    axes[0].scatter(feature, future_return, alpha=0.6)
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("Feature vs Future Return")
    model = _equity_from_returns(np.where(feature > 0, future_return, 0))
    baseline = _equity_from_returns(future_return)
    axes[1].plot(model, label="Model rule")
    axes[1].plot(baseline, label="Buy hold")
    axes[1].set_title("Model Baseline")
    axes[1].legend()
    _grid(axes)


def _plot_ml_validation(axes: np.ndarray, rng: np.random.Generator) -> None:
    axes[0].broken_barh([(0, 60), (70, 20), (100, 30)], (0, 8), facecolors=["#1f77b4", "#ff7f0e", "#2ca02c"])
    axes[0].set_yticks([4], ["time"])
    axes[0].set_title("Train / Valid / Test Split")
    axes[0].set_xlabel("Time")
    leak = ["feature leak", "label leak", "selection bias", "overfit"]
    risk = [0.8, 0.9, 0.7, 0.85]
    axes[1].barh(leak, risk, color="#d62728")
    axes[1].set_title("Leakage Risks")
    _grid(axes)


def _plot_research_pipeline(axes: np.ndarray) -> None:
    _flowchart(axes[0], ["Data", "Clean", "Signal", "Backtest", "Report"], "Research Pipeline")
    _flowchart(axes[1], ["Config", "Run", "Artifact", "Review"], "Reproducible Run")


def _plot_backtest_framework(axes: np.ndarray) -> None:
    _flowchart(axes[0], ["Market data", "Signal", "Order", "Fill", "Portfolio"], "Backtest Engine")
    _flowchart(axes[1], ["Unit tests", "Regression", "Data checks"], "Testing Layers")


def _plot_paper_trading(axes: np.ndarray, rng: np.random.Generator) -> None:
    days = np.arange(30)
    pnl = np.cumsum(rng.normal(0.001, 0.01, 30))
    axes[0].plot(days, pnl, marker="o")
    axes[0].set_title("Paper Trading PnL")
    checks = ["signal", "order", "fill", "position", "cash"]
    axes[1].bar(checks, [1, 1, .8, 1, .9], color="#2ca02c")
    axes[1].set_title("Daily Checklist Completion")
    axes[1].tick_params(axis="x", rotation=20)
    _grid(axes)


def _plot_risk_policy(axes: np.ndarray, rng: np.random.Generator) -> None:
    equity = _equity_from_returns(rng.normal(0.0004, 0.012, 252))
    dd = _drawdown(equity)
    axes[0].plot(dd, color="#d62728")
    axes[0].axhline(-0.1, color="black", linestyle="--", label="warning")
    axes[0].axhline(-0.2, color="red", linestyle="--", label="stop")
    axes[0].set_title("Drawdown Risk Limits")
    axes[0].legend()
    exposure = np.clip(rng.normal(0.65, 0.18, 60), 0, 1)
    axes[1].plot(exposure, marker="o")
    axes[1].axhline(0.8, color="red", linestyle="--")
    axes[1].set_title("Exposure Monitoring")
    _grid(axes)


def _flowchart(axis: plt.Axes, labels: list[str], title: str) -> None:
    axis.set_axis_off()
    axis.set_title(title)
    xs = np.linspace(0.1, 0.9, len(labels))
    for x, label in zip(xs, labels):
        axis.text(
            x,
            0.5,
            label,
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.35", "fc": "#e8f1fb", "ec": "#1f77b4"},
            transform=axis.transAxes,
        )
    for left, right in zip(xs[:-1], xs[1:]):
        axis.annotate(
            "",
            xy=(right - 0.06, 0.5),
            xytext=(left + 0.06, 0.5),
            arrowprops={"arrowstyle": "->", "color": "#333333"},
            xycoords=axis.transAxes,
        )


def _grid(axes: np.ndarray) -> None:
    for axis in np.ravel(axes):
        axis.grid(True, alpha=0.25)
