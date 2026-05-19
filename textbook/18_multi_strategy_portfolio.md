# 18 Multi-Strategy Portfolio

状态：预习版课本。正式上到本章时，会补充完整实跑结果、报告和必要测试。

对应 RoadMap：阶段 4/6：多策略组合

## 本课问题

趋势和均值回归能否互补？

## 为什么重要

这一章的目的不是多记一个术语，而是把前面学到的研究流程迁移到新的问题上。

你读这一章时要一直问：

```text
这个规则想解决什么问题？
它赚的是 beta、alpha、风险溢价，还是执行/约束优势？
它最容易在哪种市场环境失效？
```

## 核心概念

- 策略相关性
- 多策略组合
- 收益来源
- 策略权重
- 策略失效轮换

## 代码骨架

```python
strategy_returns = pd.concat([trend_return, mean_reversion_return], axis=1)
combo_return = strategy_returns.mean(axis=1)
combo_equity = (1 + combo_return).cumprod()
```

这段代码是本章的最小思想骨架。正式上课时，我们会把它扩展成可复用函数、脚本、notebook 和报告。

## 图示

![Multi-Strategy Portfolio](assets/18_multi_strategy_portfolio/18_multi_strategy_portfolio.png)

这张图是预习图，用来帮助你先建立直觉。正式实验图会在本章开讲时根据真实数据生成。

## 实验任务

- 组合趋势和均值回归
- 比较单策略和组合回撤
- 检查策略相关性

## 验收标准

- 能说明多策略组合为什么可能更稳
- 能识别同质化策略
- 能计算策略层权重

## 本课结论

本章预习阶段你要先掌握问题定义和研究框架。真正做实验时，不以“曲线好看”为标准，而以是否解决本章一开始定义的问题为标准。

## 下一步

第 19 章进入因子研究。
