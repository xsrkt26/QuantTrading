# 23 Financial Time Series Basics

状态：真实数据实跑版。

对应 RoadMap：阶段 7：金融统计

## 本课问题

如何避免把随机噪声误判成规律？

## 必须理解的概念

- 收益分布
- 厚尾
- 自相关
- 滚动波动率
- 显著性

## 真实数据设置

- symbols: SPY
- start_date: 2006-01-03
- end_date: 2026-05-18
- rows: 5125
- setup: Daily return distribution and rolling statistics

## 关键代码

```python
autocorr = returns.autocorr(lag=1)
rolling_vol = returns.rolling(63).std() * np.sqrt(252)
```

完整脚本：`scripts/23_financial_time_series_basics.py`

可运行 notebook：`notebooks/23_financial_time_series_basics.ipynb`

正式报告：`reports/`

## 实跑结果

| metric | value |
| --- | --- |
| daily_mean | 0.0005 |
| annualized_volatility | 0.1930 |
| skewness | -0.0018 |
| excess_kurtosis | 15.0166 |
| autocorr_1d | -0.1039 |
| autocorr_5d | -0.0130 |
| best_day | 0.1452 |
| worst_day | -0.1094 |

## 图示

![Financial Time Series Basics](assets/23_financial_time_series_basics/23_financial_time_series_basics.png)

## 讲解

- SPY 日收益不是正态分布，厚尾和极端日会显著影响回撤。
- 自相关很弱时，不要轻易把短期涨跌解释成可预测规律。
- 滚动波动率说明市场风险状态会聚集，而不是每天独立同分布。

## 本课结论

金融时间序列的常态是噪声、厚尾和波动聚集，策略必须经得起这些基本事实。

## 复习问题

1. 本章策略或实验到底想解决什么问题？
2. 结果中最重要的风险指标是什么？
3. 如果换一个市场或成本假设，结论最可能在哪里变化？
4. 这个实验离真实交易还缺哪一步？
