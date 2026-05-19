# 13 Position Sizing and Volatility Targeting

状态：预习版课本。正式上到本章时，会补充完整实跑结果、报告和必要测试。

对应 RoadMap：阶段 6：仓位管理

## 本课问题

信号告诉我们买不买，仓位管理决定买多少。

## 为什么重要

这一章的目的不是多记一个术语，而是把前面学到的研究流程迁移到新的问题上。

你读这一章时要一直问：

```text
这个规则想解决什么问题？
它赚的是 beta、alpha、风险溢价，还是执行/约束优势？
它最容易在哪种市场环境失效？
```

## 核心概念

- 等权
- 波动率倒数加权
- 风险目标
- 杠杆上限
- 仓位上限

## 代码骨架

```python
realized_vol = returns.rolling(63).std() * np.sqrt(252)
raw_weight = target_vol / realized_vol
weight = raw_weight.clip(upper=max_leverage)
```

这段代码是本章的最小思想骨架。正式上课时，我们会把它扩展成可复用函数、脚本、notebook 和报告。

## 图示

![Position Sizing and Volatility Targeting](assets/13_position_sizing_volatility_targeting/13_position_sizing_volatility_targeting.png)

这张图是预习图，用来帮助你先建立直觉。正式实验图会在本章开讲时根据真实数据生成。

## 实验任务

- 比较等权和波动率倒数权重
- 加入目标波动率
- 检查杠杆上限对回撤的影响

## 验收标准

- 能解释为什么高波动资产不一定该重仓
- 能说明波动率目标的风险
- 能识别杠杆带来的尾部风险

## 本课结论

本章预习阶段你要先掌握问题定义和研究框架。真正做实验时，不以“曲线好看”为标准，而以是否解决本章一开始定义的问题为标准。

## 下一步

第 14 章研究再平衡和换手率。
