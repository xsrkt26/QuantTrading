# QuantTrading

这个目录用于系统学习量化交易，沉淀后续的代码、策略、研究过程、学习路线图和总结笔记。

## 目录结构

```text
.
|-- ROADMAP.md              # 学习路线图
|-- notes/                  # 知识笔记、读书笔记、复盘总结
|-- research/               # 因子研究、数据探索、实验记录
|-- strategies/             # 策略设计、假设、参数和版本记录
|-- backtests/              # 回测脚本、配置、回测结果说明
|-- notebooks/              # Jupyter notebooks，用于探索和验证
|-- src/                    # 可复用代码模块
|-- tests/                  # 单元测试和回归测试
|-- data/                   # 本地数据目录，大型数据默认不提交
|-- reports/                # 研究报告、图表和阶段总结
`-- resources/              # 书籍、课程、论文、网站资源索引
```

## 建议工作流

1. 先在 `research/` 或 `notebooks/` 验证想法。
2. 将可复用逻辑沉淀到 `src/`。
3. 在 `strategies/` 写清楚策略假设、入场/出场规则、风险控制和失效条件。
4. 在 `backtests/` 保存回测配置和结果说明。
5. 在 `notes/` 记录复盘：做了什么、发现了什么、下一步是什么。

## 命名建议

- 笔记：`YYYY-MM-DD-topic.md`
- 策略：`strategy_name/README.md`
- 研究实验：`research/topic_name/`
- 回测结果：`backtests/YYYY-MM-DD_strategy_name.md`

## 初始目标

- 建立 Python 数据分析基础：`numpy`、`pandas`、`matplotlib`、`statsmodels`
- 理解市场数据：K 线、复权、成交量、滑点、手续费、幸存者偏差
- 完成第一个可复现回测：均线策略或动量策略
- 建立策略日志：每个策略都要记录假设、样本区间、评价指标和失败原因
