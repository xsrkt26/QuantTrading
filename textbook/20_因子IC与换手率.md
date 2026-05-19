# 20 Factor IC and Turnover

状态：真实数据实跑版。

对应 RoadMap：阶段 5：因子检验

## 本课问题

因子排序和未来收益到底有没有稳定关系？

## 必须理解的概念

- IC
- Rank IC
- ICIR
- 换手率
- 可交易性

## 真实数据设置

- symbols: SPY, QQQ, DIA, IWM, EFA, TLT, GLD, XLE, XLF, XLK, XLU, XLV, XLI, XLY, XLP
- start_date: 2006-01-03
- end_date: 2026-05-18
- rows: 5125
- setup: Rank IC and top-bucket turnover for 6-month momentum

## 关键代码

```python
rank_ic = factor.rank(axis=1).corrwith(future_return.rank(axis=1), axis=1)
```

完整脚本：`scripts/20_factor_ic_and_turnover.py`

可运行 notebook：`notebooks/20_factor_ic_and_turnover.ipynb`

正式报告：`reports/`

## 实跑结果

| metric | value |
| --- | --- |
| months | 238 |
| mean_rank_ic | -0.0171 |
| rank_ic_std | 0.3995 |
| icir | -0.0428 |
| positive_ic_rate | 0.4694 |
| average_top_bucket_turnover | 0.3051 |

## 图示

![Factor IC and Turnover](assets/20_factor_ic_and_turnover/20_factor_ic_and_turnover.png)

## 讲解

- Rank IC 衡量的是横截面排序和未来收益排序的关系。
- ICIR 比单个月 IC 更重要，因为它观察稳定性。
- 换手率高会让因子收益更难落地。

## 本课结论

高 IC 如果伴随极高换手，可能只是纸面优势。

## 复习问题

1. 本章策略或实验到底想解决什么问题？
2. 结果中最重要的风险指标是什么？
3. 如果换一个市场或成本假设，结论最可能在哪里变化？
4. 这个实验离真实交易还缺哪一步？
