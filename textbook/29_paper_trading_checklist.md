# 29 Paper Trading Checklist

状态：真实数据实跑版。

对应 RoadMap：阶段 10：模拟盘

## 本课问题

回测通过后，为什么还不能直接实盘？

## 必须理解的概念

- 模拟盘
- 信号核对
- 订单核对
- 持仓核对
- 日志

## 真实数据设置

- symbols: SPY
- start_date: 2006-01-03
- end_date: 2026-05-18
- rows: 5125
- setup: Last 80 trading days simulated from real SPY signals

## 关键代码

```python
paper_log.append({'date': today, 'signal': signal, 'order': order, 'fill': fill})
```

完整脚本：`scripts/29_paper_trading_checklist.py`

可运行 notebook：`notebooks/29_paper_trading_checklist.ipynb`

正式报告：`reports/`

## 实跑结果

| metric | value |
| --- | --- |
| paper_days | 80.0000 |
| orders | 3.0000 |
| average_slippage_bps | 45.0539 |
| checklist_completion_rate | 1.0000 |
| paper_final_equity | 0.9898 |

## 图示

![Paper Trading Checklist](assets/29_paper_trading_checklist/29_paper_trading_checklist.png)

## 讲解

- 模拟盘日志要记录信号、订单、成交、持仓和检查项。
- 模拟盘不是为了证明能赚钱，而是验证流程是否稳定可复盘。
- 一旦日志字段缺失，实盘后就很难解释错误来自信号还是执行。

## 本课结论

模拟盘的重点不是赚钱，而是发现研究代码到交易流程之间的断点。

## 复习问题

1. 本章策略或实验到底想解决什么问题？
2. 结果中最重要的风险指标是什么？
3. 如果换一个市场或成本假设，结论最可能在哪里变化？
4. 这个实验离真实交易还缺哪一步？
