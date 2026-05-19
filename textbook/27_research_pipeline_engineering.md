# 27 Research Pipeline Engineering

状态：预习版课本。正式上到本章时，会补充完整实跑结果、报告和必要测试。

对应 RoadMap：阶段 9：工程化

## 本课问题

如何让研究结果可复现，而不是 notebook 手工结果？

## 为什么重要

这一章的目的不是多记一个术语，而是把前面学到的研究流程迁移到新的问题上。

你读这一章时要一直问：

```text
这个规则想解决什么问题？
它赚的是 beta、alpha、风险溢价，还是执行/约束优势？
它最容易在哪种市场环境失效？
```

## 核心概念

- 配置文件
- 数据缓存
- 实验参数
- 产物目录
- 日志

## 代码骨架

```python
config = load_config(path)
data = load_or_download(config.symbols)
result = run_backtest(data, config)
save_report(result, output_dir)
```

这段代码是本章的最小思想骨架。正式上课时，我们会把它扩展成可复用函数、脚本、notebook 和报告。

## 图示

![Research Pipeline Engineering](assets/27_research_pipeline_engineering/27_research_pipeline_engineering.png)

这张图是预习图，用来帮助你先建立直觉。正式实验图会在本章开讲时根据真实数据生成。

## 实验任务

- 把参数移到配置
- 固定输出目录
- 保存数据版本和运行时间

## 验收标准

- 换机器能复现
- 每次实验有参数记录
- 图表和 CSV 自动输出

## 本课结论

本章预习阶段你要先掌握问题定义和研究框架。真正做实验时，不以“曲线好看”为标准，而以是否解决本章一开始定义的问题为标准。

## 下一步

第 28 章设计更通用的回测框架。
