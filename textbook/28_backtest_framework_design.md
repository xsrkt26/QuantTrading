# 28 Backtest Framework Design

状态：真实数据实跑版。

对应 RoadMap：阶段 9：回测框架

## 本课问题

什么时候向量化回测不够，需要事件驱动框架？

## 必须理解的概念

- 数据层
- 信号层
- 订单层
- 成交层
- 组合层

## 真实数据设置

- symbols: SPY
- start_date: 2006-01-03
- end_date: 2026-05-18
- rows: 5125
- setup: Same MA strategy implemented by vectorized and event-driven loops

## 关键代码

```python
for bar in bars:
    signal = strategy.on_bar(bar)
    fill = broker.execute(signal)
    portfolio.update(fill)
```

完整脚本：`scripts/28_backtest_framework_design.py`

可运行 notebook：`notebooks/28_backtest_framework_design.ipynb`

正式报告：`reports/`

## 实跑结果

| case | vectorized_final_equity | event_final_equity | max_equity_difference | orders |
| --- | --- | --- | --- | --- |
| vectorized_vs_event | 5.9452 | 5.9452 | 0.0000 | 23.0000 |

## 图示

![Backtest Framework Design](assets/28_backtest_framework_design/28_backtest_framework_design.png)

## 讲解

- 向量化回测适合快速研究，但订单、成交和状态边界不够显式。
- 事件驱动回测更接近实盘流程，能检查订单和持仓变化。
- 两者结果接近时，说明框架拆分没有改变策略逻辑。

## 本课结论

事件驱动框架牺牲简洁性，换来更清楚的订单、成交和状态边界。

## 复习问题

1. 本章策略或实验到底想解决什么问题？
2. 结果中最重要的风险指标是什么？
3. 如果换一个市场或成本假设，结论最可能在哪里变化？
4. 这个实验离真实交易还缺哪一步？
