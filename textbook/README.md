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

## 目录

1. [01 Market Data Basics](01_market_data_basics.md)
2. [02 Moving Average Strategy](02_moving_average_strategy.md)
3. [03 Sample Split and Overfitting](03_sample_split_and_overfitting.md)
4. [04 Transaction Cost Sensitivity](04_transaction_cost_sensitivity.md)
5. [05 Execution Assumptions](05_execution_assumptions.md)
6. [06 Trade Log and Slippage](06_trade_log_and_slippage.md)
7. [07 Trade Review and Attribution](07_trade_review_and_attribution.md)
8. [08 MA Filter Improvement](08_ma_filter_improvement.md)
