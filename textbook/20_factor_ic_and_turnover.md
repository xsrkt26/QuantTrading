# 20 Factor IC and Turnover

状态：预习版课本。正式上到本章时，会补充完整实跑结果、报告和必要测试。

对应 RoadMap：阶段 5：因子检验

## 本课问题

因子排序和未来收益到底有没有稳定关系？

## 为什么重要

这一章的目的不是多记一个术语，而是把前面学到的研究流程迁移到新的问题上。

你读这一章时要一直问：

```text
这个规则想解决什么问题？
它赚的是 beta、alpha、风险溢价，还是执行/约束优势？
它最容易在哪种市场环境失效？
```

## 核心概念

- IC
- Rank IC
- ICIR
- 换手率
- 因子衰减

## 代码骨架

```python
ic = factor.corr(future_return)
rank_ic = factor.rank().corr(future_return.rank())
turnover = holdings.diff().abs().sum(axis=1) / 2
```

这段代码是本章的最小思想骨架。正式上课时，我们会把它扩展成可复用函数、脚本、notebook 和报告。

## 图示

![Factor IC and Turnover](assets/20_factor_ic_and_turnover/20_factor_ic_and_turnover.png)

这张图是预习图，用来帮助你先建立直觉。正式实验图会在本章开讲时根据真实数据生成。

## 实验任务

- 计算月度 Rank IC
- 计算 ICIR
- 比较不同持有期换手率

## 验收标准

- 能解释 IC 和收益的区别
- 能说明高 IC 但高换手的矛盾
- 能判断因子是否可交易

## 本课结论

本章预习阶段你要先掌握问题定义和研究框架。真正做实验时，不以“曲线好看”为标准，而以是否解决本章一开始定义的问题为标准。

## 下一步

第 21 章学习因子中性化。
