# QuantTrading Course Catalog

这个目录用于快速查看完整课程路线。

课程分两类：

- 已讲解课本：已经在对话中逐课讲过。
- 真实数据实跑版课本：已经生成脚本、notebook、报告和图示，可以先自学阅读，正式上课时再逐章讲解。

## 已讲解

| 章节 | 课本 | RoadMap 阶段 |
| ---: | --- | --- |
| 01 | [Market Data Basics](01_market_data_basics.md) | 阶段 1：数据分析基础 |
| 02 | [Moving Average Strategy](02_moving_average_strategy.md) | 阶段 3：第一个回测 |
| 03 | [Sample Split and Overfitting](03_sample_split_and_overfitting.md) | 阶段 3：样本外验证 |
| 04 | [Transaction Cost Sensitivity](04_transaction_cost_sensitivity.md) | 阶段 2/3：成本与绩效 |
| 05 | [Execution Assumptions](05_execution_assumptions.md) | 阶段 3：执行假设 |
| 06 | [Trade Log and Slippage](06_trade_log_and_slippage.md) | 阶段 3：交易日志 |
| 07 | [Trade Review and Attribution](07_trade_review_and_attribution.md) | 阶段 3：交易复盘 |
| 08 | [MA Filter Improvement](08_ma_filter_improvement.md) | 阶段 3/4：策略改进 |
| 09 | [Band Robustness](09_band_robustness.md) | 阶段 3：稳健性验证 |
| 10 | [Multi-Asset Validation](10_multi_asset_validation.md) | 阶段 4/6：多资产验证 |

## 已生成真实数据实跑版，待逐章讲解

| 章节 | 课本 | RoadMap 阶段 |
| ---: | --- | --- |
| 11 | [Equal Weight Trend Portfolio](11_equal_weight_trend_portfolio.md) | 阶段 6：组合构建 |
| 12 | [Portfolio Correlation and Drawdown](12_portfolio_correlation_drawdown.md) | 阶段 6：组合风险 |
| 13 | [Position Sizing and Volatility Targeting](13_position_sizing_volatility_targeting.md) | 阶段 6：仓位管理 |
| 14 | [Rebalancing and Turnover](14_rebalancing_and_turnover.md) | 阶段 6：再平衡 |
| 15 | [Breakout Strategy](15_breakout_strategy.md) | 阶段 4：经典策略族 |
| 16 | [Time Series Momentum](16_time_series_momentum.md) | 阶段 4：经典策略族 |
| 17 | [Mean Reversion Strategy](17_mean_reversion_strategy.md) | 阶段 4：经典策略族 |
| 18 | [Multi-Strategy Portfolio](18_multi_strategy_portfolio.md) | 阶段 4/6：多策略组合 |
| 19 | [Factor Research Basics](19_factor_research_basics.md) | 阶段 5：因子研究 |
| 20 | [Factor IC and Turnover](20_factor_ic_and_turnover.md) | 阶段 5：因子检验 |
| 21 | [Factor Neutralization](21_factor_neutralization.md) | 阶段 5：因子预处理 |
| 22 | [Multi-Factor Model](22_multi_factor_model.md) | 阶段 5：多因子组合 |
| 23 | [Financial Time Series Basics](23_financial_time_series_basics.md) | 阶段 7：金融统计 |
| 24 | [Pairs Trading and Cointegration](24_pairs_trading_cointegration.md) | 阶段 7：协整和配对 |
| 25 | [Machine Learning Signal Baseline](25_ml_signal_baseline.md) | 阶段 8：机器学习量化 |
| 26 | [ML Validation and Leakage](26_ml_validation_and_leakage.md) | 阶段 8：防泄露 |
| 27 | [Research Pipeline Engineering](27_research_pipeline_engineering.md) | 阶段 9：工程化 |
| 28 | [Backtest Framework Design](28_backtest_framework_design.md) | 阶段 9：回测框架 |
| 29 | [Paper Trading Checklist](29_paper_trading_checklist.md) | 阶段 10：模拟盘 |
| 30 | [Risk Policy and Live Readiness](30_risk_policy_and_live_readiness.md) | 阶段 10：实盘前准备 |

## 学习节奏

建议顺序：

```text
11-14：先把组合层学完
15-18：再扩展策略族
19-22：进入因子研究
23-24：补金融统计和时间序列
25-26：谨慎进入机器学习
27-30：工程化、模拟盘和实盘前风控
```
