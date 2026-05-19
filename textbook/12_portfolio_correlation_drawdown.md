# 12 Portfolio Correlation and Drawdown

状态：预习版课本。正式上到本章时，会补充完整实跑结果、报告和必要测试。

对应 RoadMap：阶段 6：组合风险

## 本课问题

为什么单个资产表现一般，组合以后可能更稳？

## 为什么重要

这一章的目的不是多记一个术语，而是把前面学到的研究流程迁移到新的问题上。

你读这一章时要一直问：

```text
这个规则想解决什么问题？
它赚的是 beta、alpha、风险溢价，还是执行/约束优势？
它最容易在哪种市场环境失效？
```

## 核心概念

- 相关性
- 分散化
- 组合回撤
- 危机相关性上升
- 收益来源重叠

## 代码骨架

```python
corr = strategy_returns.corr()
portfolio_drawdown = equity / equity.cummax() - 1
rolling_corr = returns['SPY'].rolling(126).corr(returns['TLT'])
```

这段代码是本章的最小思想骨架。正式上课时，我们会把它扩展成可复用函数、脚本、notebook 和报告。

## 图示

![Portfolio Correlation and Drawdown](assets/12_portfolio_correlation_drawdown/12_portfolio_correlation_drawdown.png)

这张图是预习图，用来帮助你先建立直觉。正式实验图会在本章开讲时根据真实数据生成。

## 实验任务

- 计算策略收益相关性矩阵
- 比较单资产最大回撤和组合最大回撤
- 观察危机时期相关性变化

## 验收标准

- 能解释低相关性为什么有价值
- 能说明相关性不是常数
- 能判断组合是否真的分散

## 本课结论

本章预习阶段你要先掌握问题定义和研究框架。真正做实验时，不以“曲线好看”为标准，而以是否解决本章一开始定义的问题为标准。

## 下一步

第 13 章进入仓位管理和波动率目标。
