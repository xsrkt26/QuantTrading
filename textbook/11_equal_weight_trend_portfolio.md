# 11 Equal Weight Trend Portfolio

状态：预习版课本。正式上到本章时，会补充完整实跑结果、报告和必要测试。

对应 RoadMap：阶段 6：组合构建

## 本课问题

多个资产各自有趋势信号时，如何把它们合成一个等权组合？

## 为什么重要

这一章的目的不是多记一个术语，而是把前面学到的研究流程迁移到新的问题上。

你读这一章时要一直问：

```text
这个规则想解决什么问题？
它赚的是 beta、alpha、风险溢价，还是执行/约束优势？
它最容易在哪种市场环境失效？
```

## 核心概念

- 组合不是把单资产结果相加
- 等权组合
- 组合收益
- 组合回撤
- 资产相关性

## 代码骨架

```python
weights = positions.div(positions.sum(axis=1), axis=0).fillna(0)
portfolio_return = (weights.shift(1) * asset_returns).sum(axis=1)
portfolio_equity = (1 + portfolio_return).cumprod()
```

这段代码是本章的最小思想骨架。正式上课时，我们会把它扩展成可复用函数、脚本、notebook 和报告。

## 图示

![Equal Weight Trend Portfolio](assets/11_equal_weight_trend_portfolio/11_equal_weight_trend_portfolio.png)

这张图是预习图，用来帮助你先建立直觉。正式实验图会在本章开讲时根据真实数据生成。

## 实验任务

- 使用 SPY、QQQ、DIA、IWM、EFA、TLT 的趋势信号
- 比较单资产 SPY 与多资产等权组合
- 输出组合净值、回撤和持仓数量

## 验收标准

- 能解释等权组合如何计算收益
- 能说明组合为什么可能降低回撤
- 能指出等权组合的缺陷

## 本课结论

本章预习阶段你要先掌握问题定义和研究框架。真正做实验时，不以“曲线好看”为标准，而以是否解决本章一开始定义的问题为标准。

## 下一步

第 12 章继续研究组合相关性和组合回撤。
