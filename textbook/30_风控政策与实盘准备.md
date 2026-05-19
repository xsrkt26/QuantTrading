# 30 Risk Policy and Live Readiness

状态：真实数据实跑版。

对应 RoadMap：阶段 10：实盘前准备

## 本课问题

什么条件下，一个策略才有资格进入小资金实盘？

## 必须理解的概念

- 最大亏损
- 最大回撤
- 仓位上限
- 停止交易规则
- 异常处理

## 真实数据设置

- symbols: SPY, QQQ, DIA, IWM, EFA, TLT
- start_date: 2006-01-03
- end_date: 2026-05-18
- rows: 5125
- setup: 10% vol-target trend portfolio risk policy check

## 关键代码

```python
if drawdown < max_allowed_drawdown:
    halt_trading()
if exposure > max_exposure:
    reduce_position()
```

完整脚本：`scripts/30_risk_policy_and_live_readiness.py`

可运行 notebook：`notebooks/30_risk_policy_and_live_readiness.ipynb`

正式报告：`reports/`

## 实跑结果

| risk_rule | limit | observed | breach_count |
| --- | --- | --- | --- |
| max_drawdown_warning | -10% | -19.11% | 1200 |
| max_drawdown_stop | -20% | -19.11% | 0 |
| daily_loss_warning | -3% | -6.34% | 9 |
| max_exposure | 120% | 150.00% | 543 |

## 图示

![Risk Policy and Live Readiness](assets/30_risk_policy_and_live_readiness/30_risk_policy_and_live_readiness.png)

## 讲解

- 风险政策要写在实盘之前，不能亏损后再临时解释。
- 最大回撤、单日亏损和仓位暴露都需要明确阈值。
- 出现停止交易条件时，正确动作是降风险和复盘，而不是加倍下注。

## 本课结论

实盘前先定义停止条件；不能解释风险边界，就不应该加资金。

## 复习问题

1. 本章策略或实验到底想解决什么问题？
2. 结果中最重要的风险指标是什么？
3. 如果换一个市场或成本假设，结论最可能在哪里变化？
4. 这个实验离真实交易还缺哪一步？
