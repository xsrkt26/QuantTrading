# Trade Log and Slippage

日期：2026-05-19

## 本课目标

把策略从“净值曲线”拆成“每一笔真实交易”。

前面我们已经知道：

```text
收盘后产生信号
下一个交易日开盘执行
```

但这还不够。真正复盘一个策略时，必须回答：

- 哪一天发出了订单？
- 哪一天成交？
- 买入成交价是多少？
- 卖出成交价是多少？
- 滑点和佣金吃掉了多少收益？
- 每一笔交易持有了多久？
- 哪些交易贡献了主要利润，哪些交易造成了亏损？

这就是交易日志，也就是 `trade log`。

## 核心概念

### 信号不是订单

`signal` 只是策略判断：

```text
我想持有，还是不想持有？
```

它不是交易本身。

### 订单不是成交

订单是你向市场发出的请求：

```text
我要买入
我要卖出
```

但真实市场中，订单可能：

- 按预期价格成交
- 以更差价格成交
- 部分成交
- 完全没有成交

本课先用简化模型：只要发生仓位变化，就假设在 next-open 成交。

### 成交价格要考虑滑点

日线回测里我们经常用 `Open` 代表成交价，但真实成交通常会差一点。

本课使用：

```text
买入成交价 = Open * (1 + slippage_bps / 10000)
卖出成交价 = Open * (1 - slippage_bps / 10000)
```

含义是：

- 买入通常要付出更高价格
- 卖出通常只能拿到更低价格

这是一种非常简单但必要的保守假设。

## 本课代码结构

新增文件：

- `src/quant_trading/execution.py`
- `scripts/06_trade_log_and_slippage.py`
- `notebooks/06_trade_log_and_slippage.ipynb`
- `reports/2026-05-19_trade_log_and_slippage.md`

核心函数：

```python
build_order_fills(...)
build_round_trip_trade_log(...)
summarize_trade_log(...)
plot_trade_log(...)
```

## 本课策略设置

- 标的：SPY
- 数据源：Yahoo Finance，经 `yfinance` 下载
- 数据区间：2000-01-03 至 2026-05-18
- 策略：10/200 双均线
- 方向：只做多，不做空
- 执行模型：next-open
- 滑点：单边 2 bps
- 佣金：单边 1 bps

注意：本课在 `add_moving_average_strategy_next_open(...)` 中把 `transaction_cost_bps=0`，因为成本由新的执行层统一计算。

## 结果

| trades | closed_trades | marked_open_trades | win_rate | average_net_return | median_net_return | best_trade_return | worst_trade_return | average_holding_days | profit_factor | final_trade_equity | total_cost_drag |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 24 | 23 | 1 | 62.50% | 10.36% | 5.15% | 64.78% | -5.74% | 284.8 | 9.85 | 8.2201 | 1.59% |

## 如何解读

之前我们说策略有 47 次交易，那是单边动作：

```text
买入算 1 次
卖出算 1 次
```

本课的 24 笔交易是 round-trip：

```text
一次买入 + 一次卖出 = 一笔完整交易
```

因为最后还有一笔持仓没有真正卖出，所以它被标记为：

```text
open_marked_to_market
```

意思是：这笔交易仍然开着，但为了复盘，暂时用最新开盘价按市值估算。

## 关键结论

1. 净值曲线只能告诉你最终结果，交易日志能告诉你结果从哪里来。
2. 胜率不是唯一指标。这个策略胜率 62.50%，但更重要的是盈利交易的平均空间大于亏损交易。
3. `profit_factor = 9.85` 说明盈利交易总额远大于亏损交易总额，但这仍然只是历史样本结果。
4. 成本拖累为 1.59%，这说明对低频 SPY 双均线来说，2 bps 滑点和 1 bps 佣金影响不算致命。
5. 如果换成高频、小盘股或低流动性股票，成本拖累可能完全改变策略结论。

## 需要掌握的问题

- 为什么信号不是订单？
- 为什么订单不是成交？
- 单边交易和完整交易有什么区别？
- 为什么买入滑点是加价，卖出滑点是减价？
- 为什么交易日志比净值曲线更适合复盘策略？
- 为什么最后一笔未平仓交易要标记为 `open_marked_to_market`？
