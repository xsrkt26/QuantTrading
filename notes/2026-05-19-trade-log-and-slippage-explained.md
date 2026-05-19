# Trade Log and Slippage Explained

日期：2026-05-19

对应讲义：

- `notebooks/06_trade_log_and_slippage.ipynb`
- `notes/2026-05-19-trade-log-and-slippage.md`
- `reports/2026-05-19_trade_log_and_slippage.md`

## 这一课到底在讲什么？

前几课我们看到的是：

```text
价格数据 -> 均线 -> 信号 -> 仓位 -> 策略净值
```

但真实交易系统还要继续往下拆：

```text
信号 -> 订单 -> 成交 -> 持仓 -> 平仓 -> 单笔交易结果
```

如果只看净值曲线，你知道策略最后赚了还是亏了，但你不知道：

- 钱是由哪几笔交易赚出来的
- 亏损集中在哪些阶段
- 成本对每笔交易影响多大
- 策略是靠高胜率赚钱，还是靠少数大赢家赚钱

所以这一课开始建立 `trade log`，也就是交易明细。

## 第一步：生成 next-open 策略

脚本里先做：

```python
strategy = add_moving_average_strategy_next_open(
    df,
    short_window=10,
    long_window=200,
    transaction_cost_bps=0.0,
)
```

这里故意把 `transaction_cost_bps` 设成 `0.0`。

原因是：第 6 课不想让均线策略函数直接扣成本，而是把成本统一放到执行层处理。

也就是说：

```text
moving_average.py 负责产生信号和仓位
execution.py 负责模拟成交、滑点、佣金和交易日志
```

这个分层很重要。以后你换策略时，不应该重新写一套成交逻辑；你只要让新策略输出仓位，再交给执行层处理。

## 第二步：从仓位变化生成订单成交

核心函数是：

```python
fills = build_order_fills(
    strategy,
    slippage_bps=2.0,
    commission_bps=1.0,
)
```

它看的不是均线，而是这两列：

```python
position
trade
```

其中：

```text
position = 今天开盘后应该持有多少仓位
trade = 今天是否发生仓位变化
```

如果昨天仓位是 0，今天仓位变成 1：

```text
side = buy
```

如果昨天仓位是 1，今天仓位变成 0：

```text
side = sell
```

这一步产生的是单边成交明细，不是完整交易。

## 第三步：滑点如何进入成交价

代码里的核心逻辑是：

```python
if side == "buy":
    fill_price = open_price * (1 + slippage_rate)
if side == "sell":
    fill_price = open_price * (1 - slippage_rate)
```

这代表一个保守假设：

```text
买入时，你拿不到完美开盘价，要多付一点
卖出时，你拿不到完美开盘价，要少拿一点
```

本课设置：

```text
slippage_bps = 2.0
commission_bps = 1.0
```

也就是每次买入和卖出，都假设有 2 bps 滑点和 1 bps 佣金。

## 第四步：从单边成交配成完整交易

核心函数是：

```python
trade_log = build_round_trip_trade_log(
    strategy,
    slippage_bps=2.0,
    commission_bps=1.0,
)
```

它会把：

```text
一次 buy + 后面一次 sell
```

配成一笔完整交易。

这就是为什么之前报告里看到 `trades = 47`，这一课看到 `trades = 24`。

它们不是矛盾，而是口径不同：

```text
47 = 单边成交次数
24 = 完整交易笔数
```

如果最后还有持仓没有卖出，函数会用最新开盘价临时估值，并标记为：

```text
open_marked_to_market
```

这不是一笔真正已经结束的交易，而是为了让复盘表可以显示当前持仓盈亏。

## 第五步：每笔交易怎么算收益？

一笔交易有三个收益口径。

### 1. gross_return

```text
gross_return = exit_open / entry_open - 1
```

这是完全不考虑滑点和佣金的理论收益。

### 2. slippage_adjusted_return

```text
slippage_adjusted_return = exit_fill_price / entry_fill_price - 1
```

这是考虑滑点后的收益。

### 3. net_return

```text
net_return = (1 + slippage_adjusted_return) * (1 - commission_rate) ** 2 - 1
```

这是考虑滑点和买卖两边佣金后的净收益。

所以你以后看交易日志时，要优先看：

```text
net_return
```

因为它最接近你真正能拿到的结果。

## 第六步：汇总交易日志

脚本里调用：

```python
summary = summarize_trade_log(trade_log)
```

本课结果：

| trades | closed_trades | marked_open_trades | win_rate | average_net_return | median_net_return | best_trade_return | worst_trade_return | average_holding_days | profit_factor | final_trade_equity | total_cost_drag |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 24 | 23 | 1 | 62.50% | 10.36% | 5.15% | 64.78% | -5.74% | 284.8 | 9.85 | 8.2201 | 1.59% |

逐项解释：

- `trades`：完整交易笔数。
- `closed_trades`：已经完成买入和卖出的交易。
- `marked_open_trades`：仍持有但按当前价格估值的交易。
- `win_rate`：赚钱交易占比。
- `average_net_return`：每笔交易平均净收益。
- `median_net_return`：每笔交易净收益中位数。
- `best_trade_return`：历史最好一笔交易。
- `worst_trade_return`：历史最差一笔交易。
- `average_holding_days`：平均持有自然日。
- `profit_factor`：盈利交易总收益 / 亏损交易总亏损。
- `final_trade_equity`：按每笔完整交易复利后的最终净值。
- `total_cost_drag`：成本累计拖累。

## 第七步：如何读前 10 笔交易

脚本会打印：

```python
format_trade_log_table(trade_log, n=10)
```

你会看到类似字段：

```text
entry_date
exit_date
holding_days
entry_fill_price
exit_fill_price
gross_return
net_return
cost_drag
net_equity
```

读法是：

```text
我在哪天买入
在哪天卖出
持有多久
不考虑成本赚多少
考虑成本后赚多少
这一笔结束后累计净值到多少
```

这比只看一张净值曲线更接近真实复盘。

## 这一课你应该真正领悟什么？

策略研究不能只停留在：

```text
这条净值曲线看起来不错
```

你必须继续追问：

```text
它到底靠哪几笔交易赚钱？
亏损有没有集中爆发？
成本是否足以吃掉优势？
最后还持有什么仓位？
这些交易在真实市场中能不能成交？
```

从这一课开始，你已经不只是看“策略结果”，而是在看“策略行为”。

这是从初学回测进入真实量化研究的重要一步。
