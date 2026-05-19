# 14 Rebalancing and Turnover

状态：预习版课本。正式上到本章时，会补充完整实跑结果、报告和必要测试。

对应 RoadMap：阶段 6：再平衡

## 本课问题

组合多久调一次仓，成本和风险会发生什么变化？

## 为什么重要

这一章的目的不是多记一个术语，而是把前面学到的研究流程迁移到新的问题上。

你读这一章时要一直问：

```text
这个规则想解决什么问题？
它赚的是 beta、alpha、风险溢价，还是执行/约束优势？
它最容易在哪种市场环境失效？
```

## 核心概念

- 再平衡频率
- 目标权重
- 权重漂移
- 换手率
- 交易成本

## 代码骨架

```python
target_weight = signal_weight.resample('M').last().reindex(index).ffill()
turnover = target_weight.diff().abs().sum(axis=1)
cost = turnover * cost_bps / 10000
```

这段代码是本章的最小思想骨架。正式上课时，我们会把它扩展成可复用函数、脚本、notebook 和报告。

## 图示

![Rebalancing and Turnover](assets/14_rebalancing_and_turnover/14_rebalancing_and_turnover.png)

这张图是预习图，用来帮助你先建立直觉。正式实验图会在本章开讲时根据真实数据生成。

## 实验任务

- 比较周度、月度、季度再平衡
- 计算换手率和交易成本
- 观察再平衡频率对回撤的影响

## 验收标准

- 能解释再平衡不是越频繁越好
- 能计算组合换手率
- 能说明成本如何吞噬组合收益

## 本课结论

本章预习阶段你要先掌握问题定义和研究框架。真正做实验时，不以“曲线好看”为标准，而以是否解决本章一开始定义的问题为标准。

## 下一步

第 15 章开始扩展经典策略族：突破策略。
