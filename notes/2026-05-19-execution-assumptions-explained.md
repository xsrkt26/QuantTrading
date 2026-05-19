# Execution Assumptions Explained

日期：2026-05-19

对应讲义：

- `notebooks/05_execution_assumptions.ipynb`
- `notes/2026-05-19-execution-assumptions.md`
- `reports/2026-05-19_execution_assumptions.md`

## 这一课到底在讲什么

前几节课我们已经做到了：

```text
收盘价 -> 均线 -> 信号 -> 仓位 -> 策略收益
```

但真实交易里还缺一个关键问题：

```text
信号出现以后，我到底用什么价格成交？
```

这就是执行假设。

量化回测不是只写一句“买入”就结束。任何策略都必须把下面几件事说清楚：

- 信号什么时候产生？
- 下单什么时候发生？
- 成交价格用开盘价、收盘价、bid、ask，还是 VWAP？
- 有没有滑点？
- 有没有无法成交的问题？
- 交易成本怎么算？

如果这些没有说清楚，回测结果很容易偏乐观。

## 为什么之前的回测还不够真实

之前我们已经用了：

```python
position = signal.shift(1)
```

这一步非常重要，因为它避免了直接用今天收盘后的信号去赚今天的钱。

但之前的策略收益还是基于：

```python
strategy_return = position * close_return
```

这里的 `close_return` 是：

```text
今天收盘价 / 昨天收盘价 - 1
```

这个模型叫 `close-to-close`。

它的意思大致是：

```text
昨天信号决定今天持仓，然后用今天收盘到昨天收盘的收益计算策略收益。
```

这个做法在教学和快速研究中很常见，但它没有完全回答一个现实问题：

```text
我昨天收盘后才知道信号，那我今天到底以什么价格买进去？
```

如果真实交易中只能今天开盘成交，那么收盘价回测和开盘价回测可能会有差异。

## close-to-close 是什么

在 notebook 里，close-to-close 模型调用的是：

```python
close_to_close = add_moving_average_strategy(...)
```

它的核心逻辑在：

```text
src/quant_trading/moving_average.py
```

关键链条是：

```python
result["return"] = result["Close"].pct_change()
result["position"] = result["signal"].shift(1).fillna(0)
result["strategy_return"] = result["position"] * result["return"]
```

它有两个含义：

1. `signal.shift(1)`：昨天的信号决定今天仓位。
2. `Close.pct_change()`：今天持仓收益用昨天收盘到今天收盘计算。

这种模型的优点是简单，适合第一版研究。

缺点是它仍然比较抽象，并没有模拟“开盘成交”这个实际动作。

## next-open 是什么

这节课新增了一个更接近真实交易的模型：

```python
next_open = add_moving_average_strategy_next_open(...)
```

它的执行逻辑是：

```text
今天收盘后计算均线信号
明天开盘执行买入或卖出
之后持有到下一次开盘
```

核心收益计算是：

```python
result["open_to_next_open_return"] = result["Open"].shift(-1) / result["Open"] - 1
```

这行代码的意思是：

```text
今天开盘买入，持有到下一个交易日开盘，收益是多少？
```

然后策略收益是：

```python
result["strategy_return_before_cost"] = (
    result["position"] * result["open_to_next_open_return"].fillna(0)
)
```

也就是：

```text
如果今天有仓位，就吃今天开盘到下一天开盘的收益。
如果今天没仓位，收益就是 0。
```

## 为什么 next-open 更接近真实交易

因为现实流程更像这样：

```text
15:59 还不知道最终收盘价
16:00 收盘后拿到完整日线数据
16:05 计算信号
第二天开盘附近执行
```

所以如果信号来自收盘价，下一交易日开盘成交是更自然的假设。

当然，next-open 也不是完美真实，因为真实交易还可能遇到：

- 开盘跳空
- 开盘流动性不足
- 市价单成交很差
- 限价单成交不了
- bid / ask 价差
- 盘前盘后价格变化

但它比完全围绕收盘价计算更具体。

## 这节课的结果怎么读

本课用的是：

```text
SPY
10/200 双均线
1 bps 单边交易成本
```

结果是：

| execution_model | 最终净值 | 年化收益 | 最大回撤 | Calmar | 交易次数 | 在场时间 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| close_to_close | 8.0332 | 8.24% | -20.27% | 0.41 | 47 | 70.99% |
| next_open | 8.3003 | 8.37% | -21.46% | 0.39 | 47 | 70.99% |

有三个观察：

1. `next_open` 最终净值略高。
2. `next_open` 最大回撤更深。
3. `next_open` Calmar 更低。

这说明执行假设不一定总是让收益变差。

有时候开盘成交可能刚好更有利，有时候更不利。重点不是哪个结果更好，而是：

```text
执行假设会改变策略画像。
```

## 为什么交易次数和在场时间一样

因为两种模型使用的是同一个信号：

```text
10 日均线 > 200 日均线 -> 持有
否则空仓
```

所以买入卖出的日期基本一致。

不同的是：

```text
持有期间用 close-to-close 收益计算
还是用 open-to-open 收益计算
```

因此交易次数和在场时间一样，但收益、回撤、Calmar 会不同。

## 这节课最重要的观念

一个策略至少有三层：

```text
信号层：什么时候想买？
执行层：用什么价格买？
组合层：买多少？
```

之前我们主要在信号层。

这节课开始进入执行层。

很多新手只写：

```text
均线金叉，买入。
```

但专业回测必须写成：

```text
收盘后计算均线。
如果短均线高于长均线，下一交易日开盘买入。
成交价用开盘价，并扣除 1 bps 成本。
```

这才是可复现、可审查的规则。

## 看 notebook 时应该怎么读

### 第一段：导入模块

这部分只是加载工具函数。

你重点看这些函数名：

```python
add_moving_average_strategy
add_moving_average_strategy_next_open
compare_execution_assumptions
plot_execution_comparison
```

它们分别表示：

- close-to-close 回测
- next-open 回测
- 两种执行假设对比
- 画图比较

### 第二段：下载数据和设置参数

```python
SYMBOL = "SPY"
SHORT_WINDOW = 10
LONG_WINDOW = 200
TRANSACTION_COST_BPS = 1.0
```

这表示：

- 标的是 SPY
- 短均线是 10 日
- 长均线是 200 日
- 每次买入或卖出扣 1 bps 成本

### 第三段：close-to-close

```python
close_to_close = add_moving_average_strategy(...)
```

这会产生老版本策略结果。

你重点看输出表里的：

```text
Close
signal
position
return
strategy_return
```

`return` 是收盘到收盘收益。

### 第四段：next-open

```python
next_open = add_moving_average_strategy_next_open(...)
```

你重点看：

```text
Open
Close
signal
position
open_to_next_open_return
strategy_return
```

`open_to_next_open_return` 是这节课的新概念。

它代表：

```text
今天开盘到下一交易日开盘的收益。
```

### 第五段：比较结果

```python
comparison = compare_execution_assumptions(...)
print(format_execution_comparison_table(comparison))
```

这一步把两种模型放到同一张表里，方便比较。

真正要看的不是某一个数，而是：

```text
执行假设改变后，策略结果是否大幅变化？
```

如果变化很大，说明策略对成交假设很敏感，需要更谨慎。

## 本课检查问题

学完这一课，你应该能回答：

- 为什么 `signal` 不等于真实成交？
- 为什么 close-to-close 是一种简化？
- next-open 为什么更贴近真实交易？
- 为什么 next-open 结果不一定比 close-to-close 差？
- 为什么回测报告必须写清楚成交价假设？

## 记住一句话

```text
没有执行假设的策略，只是一个信号；写清楚如何成交，才是一个可回测的交易规则。
```
