# 19 Factor Research Basics

状态：真实数据实跑版。

对应 RoadMap：阶段 5：因子研究

## 本课问题

如何判断一个排序指标是否能解释未来收益？

## 必须理解的概念

- 因子
- 横截面排序
- 分层回测
- 多空组合
- 因子收益

## 真实数据设置

- symbols: SPY, QQQ, DIA, IWM, EFA, TLT, GLD, XLE, XLF, XLK, XLU, XLV, XLI, XLY, XLP
- start_date: 2006-01-03
- end_date: 2026-05-18
- rows: 5125
- setup: 6-month momentum factor, monthly ETF cross-section

## 关键代码

```python
factor_rank = factor.rank(axis=1, pct=True)
top_return = future_return.where(factor_rank >= 0.8).mean(axis=1)
```

完整脚本：`scripts/19_factor_research_basics.py`

可运行 notebook：`notebooks/19_factor_research_basics.ipynb`

正式报告：`reports/`

## 实跑结果

| case | final_equity | ann_return | ann_vol | max_drawdown | sharpe | calmar |
| --- | --- | --- | --- | --- | --- | --- |
| Q1_low | 4.9448 | 8.14% | 16.30% | -54.28% | 0.4995 | 0.1500 |
| Q2 | 13.2301 | 13.48% | 14.91% | -45.77% | 0.9044 | 0.2946 |
| Q3 | 6.0354 | 9.20% | 14.79% | -46.62% | 0.6224 | 0.1974 |
| Q4 | 5.0756 | 8.28% | 14.83% | -46.79% | 0.5583 | 0.1770 |
| Q5_high | 7.1986 | 10.15% | 13.83% | -29.53% | 0.7341 | 0.3438 |
| high_minus_low | 1.0368 | 0.18% | 16.18% | -46.15% | 0.0110 | 0.0038 |

## 图示

![Factor Research Basics](assets/19_factor_research_basics/19_factor_research_basics.png)

## 讲解

- 分层回测先回答排序有没有方向性，而不是直接承诺可交易收益。
- 如果高分层和低分层没有稳定差异，因子继续复杂化意义不大。
- ETF 横截面样本较小，本章重点是掌握研究流程。

## 本课结论

因子研究先看排序能力，而不是急着把它做成实盘策略。

## 复习问题

1. 本章策略或实验到底想解决什么问题？
2. 结果中最重要的风险指标是什么？
3. 如果换一个市场或成本假设，结论最可能在哪里变化？
4. 这个实验离真实交易还缺哪一步？
