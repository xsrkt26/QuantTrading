# 28 Backtest Framework Design

状态：预习版课本。正式上到本章时，会补充完整实跑结果、报告和必要测试。

对应 RoadMap：阶段 9：回测框架

## 本课问题

什么时候向量化回测不够，需要事件驱动框架？

## 为什么重要

这一章的目的不是多记一个术语，而是把前面学到的研究流程迁移到新的问题上。

你读这一章时要一直问：

```text
这个规则想解决什么问题？
它赚的是 beta、alpha、风险溢价，还是执行/约束优势？
它最容易在哪种市场环境失效？
```

## 核心概念

- 数据层
- 信号层
- 订单层
- 成交层
- 组合层

## 代码骨架

```python
for event in events:
    signal = strategy.on_bar(event)
    order = broker.create_order(signal)
    fill = execution_model.fill(order)
    portfolio.update(fill)
```

这段代码是本章的最小思想骨架。正式上课时，我们会把它扩展成可复用函数、脚本、notebook 和报告。

## 图示

![Backtest Framework Design](assets/28_backtest_framework_design/28_backtest_framework_design.png)

这张图是预习图，用来帮助你先建立直觉。正式实验图会在本章开讲时根据真实数据生成。

## 实验任务

- 拆分信号和执行
- 模拟订单状态
- 比较向量化和事件驱动

## 验收标准

- 能解释回测模块边界
- 能说明事件驱动的优势
- 能写最小订单模拟

## 本课结论

本章预习阶段你要先掌握问题定义和研究框架。真正做实验时，不以“曲线好看”为标准，而以是否解决本章一开始定义的问题为标准。

## 下一步

第 29 章进入模拟盘检查清单。
