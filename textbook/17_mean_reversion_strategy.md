# 17 Mean Reversion Strategy

状态：预习版课本。正式上到本章时，会补充完整实跑结果、报告和必要测试。

对应 RoadMap：阶段 4：经典策略族

## 本课问题

价格偏离均值以后，什么时候会回归？

## 为什么重要

这一章的目的不是多记一个术语，而是把前面学到的研究流程迁移到新的问题上。

你读这一章时要一直问：

```text
这个规则想解决什么问题？
它赚的是 beta、alpha、风险溢价，还是执行/约束优势？
它最容易在哪种市场环境失效？
```

## 核心概念

- 均值回归
- z-score
- 过度反应
- 止损
- 半衰期

## 代码骨架

```python
z = (close - close.rolling(window).mean()) / close.rolling(window).std()
signal = np.where(z < -entry_z, 1, np.where(z > exit_z, 0, np.nan))
```

这段代码是本章的最小思想骨架。正式上课时，我们会把它扩展成可复用函数、脚本、notebook 和报告。

## 图示

![Mean Reversion Strategy](assets/17_mean_reversion_strategy/17_mean_reversion_strategy.png)

这张图是预习图，用来帮助你先建立直觉。正式实验图会在本章开讲时根据真实数据生成。

## 实验任务

- 实现 z-score 均值回归
- 比较不同 entry_z
- 观察趋势市场中的连续亏损

## 验收标准

- 能解释均值回归和趋势策略的冲突
- 能说明为什么均值回归必须止损
- 能识别均值变了的风险

## 本课结论

本章预习阶段你要先掌握问题定义和研究框架。真正做实验时，不以“曲线好看”为标准，而以是否解决本章一开始定义的问题为标准。

## 下一步

第 18 章把趋势和均值回归放进多策略组合。
