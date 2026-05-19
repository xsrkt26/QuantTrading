# 24 Pairs Trading and Cointegration

状态：真实数据实跑版。

对应 RoadMap：阶段 7：协整和配对

## 本课问题

两只资产价格一起走时，价差偏离能否交易？

## 必须理解的概念

- 配对交易
- 价差
- z-score
- 相关不等于协整
- 半衰期

## 真实数据设置

- symbols: SPY, QQQ
- start_date: 2006-01-03
- end_date: 2026-05-18
- rows: 5125
- setup: OLS hedge ratio on first 60% sample; z-score spread trading

## 关键代码

```python
spread = log_y - hedge_ratio * log_x
z = (spread - spread.rolling(60).mean()) / spread.rolling(60).std()
```

完整脚本：`scripts/24_pairs_trading_cointegration.py`

可运行 notebook：`notebooks/24_pairs_trading_cointegration.ipynb`

正式报告：`reports/`

## 实跑结果

| case | final_equity | ann_return | ann_vol | max_drawdown | sharpe | calmar | hedge_ratio | half_life_days | trades |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SPY_QQQ_spread_reversion | 1.7046 | 2.66% | 7.41% | -22.79% | 0.3584 | 0.1166 | 1.3529 | 258.6158 | 213 |

## 图示

![Pairs Trading and Cointegration](assets/24_pairs_trading_cointegration/24_pairs_trading_cointegration.png)

## 讲解

- SPY 和 QQQ 高相关，但价差交易真正关心的是 spread 是否会回归。
- 半衰期只是粗略估计，不代表每次偏离都能按时回归。
- 双腿交易必须考虑两边成本和对冲比例误差。

## 本课结论

配对交易不是看到相关就交易，而是要验证价差是否有回归特征。

## 复习问题

1. 本章策略或实验到底想解决什么问题？
2. 结果中最重要的风险指标是什么？
3. 如果换一个市场或成本假设，结论最可能在哪里变化？
4. 这个实验离真实交易还缺哪一步？
