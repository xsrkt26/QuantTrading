# 24 Pairs Trading and Cointegration

状态：预习版课本。正式上到本章时，会补充完整实跑结果、报告和必要测试。

对应 RoadMap：阶段 7：协整和配对

## 本课问题

两只资产价格一起走时，价差偏离能否交易？

## 为什么重要

这一章的目的不是多记一个术语，而是把前面学到的研究流程迁移到新的问题上。

你读这一章时要一直问：

```text
这个规则想解决什么问题？
它赚的是 beta、alpha、风险溢价，还是执行/约束优势？
它最容易在哪种市场环境失效？
```

## 核心概念

- 配对交易
- 价差
- z-score
- 协整
- 半衰期

## 代码骨架

```python
spread = y - hedge_ratio * x
z = (spread - spread.rolling(60).mean()) / spread.rolling(60).std()
signal = np.where(z < -2, 1, np.where(z > 2, -1, 0))
```

这段代码是本章的最小思想骨架。正式上课时，我们会把它扩展成可复用函数、脚本、notebook 和报告。

## 图示

![Pairs Trading and Cointegration](assets/24_pairs_trading_cointegration/24_pairs_trading_cointegration.png)

这张图是预习图，用来帮助你先建立直觉。正式实验图会在本章开讲时根据真实数据生成。

## 实验任务

- 构造 SPY/QQQ 价差
- 计算 z-score
- 模拟价差回归交易

## 验收标准

- 能解释相关不等于协整
- 能说明价差失效风险
- 能处理双腿交易成本

## 本课结论

本章预习阶段你要先掌握问题定义和研究框架。真正做实验时，不以“曲线好看”为标准，而以是否解决本章一开始定义的问题为标准。

## 下一步

第 25 章进入机器学习基线。
