# 15 Breakout Strategy

状态：真实数据实跑版。

对应 RoadMap：阶段 4：经典策略族

## 本课问题

价格突破历史高点是否代表趋势开始？

## 必须理解的概念

- 突破
- Donchian channel
- 假突破
- 退出规则
- 趋势延续

## 真实数据设置

- symbols: SPY
- start_date: 2006-01-03
- end_date: 2026-05-18
- rows: 5125
- setup: Donchian breakout, next-open, 3 bps cost

## 关键代码

```python
channel_high = close.rolling(lookback).max().shift(1)
signal = close > channel_high
```

完整脚本：`scripts/15_breakout_strategy.py`

可运行 notebook：`notebooks/15_breakout_strategy.ipynb`

正式报告：`reports/`

## 实跑结果

| case | final_equity | ann_return | ann_vol | max_drawdown | sharpe | calmar | turnover | avg_exposure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| breakout_20d | 3.7889 | 6.77% | 10.52% | -24.37% | 0.6435 | 0.2778 | 153 | 65.58% |
| breakout_60d | 4.8283 | 8.05% | 11.09% | -23.02% | 0.7256 | 0.3496 | 47.0000 | 71.38% |
| breakout_120d | 5.2796 | 8.53% | 11.44% | -19.37% | 0.7450 | 0.4401 | 19.0000 | 71.36% |
| ma_10_200_band | 5.9452 | 9.16% | 12.03% | -21.53% | 0.7617 | 0.4254 | 23.0000 | 75.24% |

## 图示

![Breakout Strategy](assets/15_breakout_strategy/15_breakout_strategy.png)

## 讲解

- 短周期突破更敏感，也更容易被假突破反复打脸。
- 长周期突破更慢，但通常能过滤更多噪声。
- 突破和均线都是趋势思想，差异主要在信号定义和反应速度。

## 本课结论

突破策略的核心风险是假突破；参数越短，反应越快，噪声也越多。

## 复习问题

1. 本章策略或实验到底想解决什么问题？
2. 结果中最重要的风险指标是什么？
3. 如果换一个市场或成本假设，结论最可能在哪里变化？
4. 这个实验离真实交易还缺哪一步？
