# QuantTrading Textbook

这个目录保存课本式讲义。

从后续课程开始，每节课优先生成一份可以直接阅读的主课本：

```text
textbook/NN_topic.md
```

课本需要同时包含：

- 本课要解决的问题
- 必须理解的概念
- 关键代码片段
- 代码运行结果
- 图表和截图
- 结果解读
- 本课结论
- 下一课衔接

图片和图表统一放在：

```text
textbook/assets/NN_topic/
```

代码仍然保留在 `src/`、`scripts/` 和 `notebooks/` 中。课本负责把学习体验串起来，避免只看代码或只看零散笔记。

第 11-30 章已经升级为真实数据实跑版：每章都有脚本、notebook、报告和课本图示。

## 目录

完整目录见：[Course Catalog](COURSE_CATALOG.md)

1. [01 Market Data Basics](01_market_data_basics.md)
2. [02 Moving Average Strategy](02_moving_average_strategy.md)
3. [03 Sample Split and Overfitting](03_sample_split_and_overfitting.md)
4. [04 Transaction Cost Sensitivity](04_transaction_cost_sensitivity.md)
5. [05 Execution Assumptions](05_execution_assumptions.md)
6. [06 Trade Log and Slippage](06_trade_log_and_slippage.md)
7. [07 Trade Review and Attribution](07_trade_review_and_attribution.md)
8. [08 MA Filter Improvement](08_ma_filter_improvement.md)
9. [09 Band Robustness](09_band_robustness.md)
10. [10 Multi-Asset Validation](10_multi_asset_validation.md)
11. [11 Equal Weight Trend Portfolio](11_equal_weight_trend_portfolio.md)
12. [12 Portfolio Correlation and Drawdown](12_portfolio_correlation_drawdown.md)
13. [13 Position Sizing and Volatility Targeting](13_position_sizing_volatility_targeting.md)
14. [14 Rebalancing and Turnover](14_rebalancing_and_turnover.md)
15. [15 Breakout Strategy](15_breakout_strategy.md)
16. [16 Time Series Momentum](16_time_series_momentum.md)
17. [17 Mean Reversion Strategy](17_mean_reversion_strategy.md)
18. [18 Multi-Strategy Portfolio](18_multi_strategy_portfolio.md)
19. [19 Factor Research Basics](19_factor_research_basics.md)
20. [20 Factor IC and Turnover](20_factor_ic_and_turnover.md)
21. [21 Factor Neutralization](21_factor_neutralization.md)
22. [22 Multi-Factor Model](22_multi_factor_model.md)
23. [23 Financial Time Series Basics](23_financial_time_series_basics.md)
24. [24 Pairs Trading and Cointegration](24_pairs_trading_cointegration.md)
25. [25 Machine Learning Signal Baseline](25_ml_signal_baseline.md)
26. [26 ML Validation and Leakage](26_ml_validation_and_leakage.md)
27. [27 Research Pipeline Engineering](27_research_pipeline_engineering.md)
28. [28 Backtest Framework Design](28_backtest_framework_design.md)
29. [29 Paper Trading Checklist](29_paper_trading_checklist.md)
30. [30 Risk Policy and Live Readiness](30_risk_policy_and_live_readiness.md)
