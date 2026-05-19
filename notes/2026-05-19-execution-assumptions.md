# Execution Assumptions

日期：2026-05-19

## 本课目标

理解信号和成交之间的差异。

一个策略不是只要写出买卖信号就结束了，还必须回答：

- 信号什么时候产生？
- 什么时候下单？
- 用什么价格成交？
- 买入看 ask 还是 close？
- 卖出看 bid 还是 close？
- 滑点和交易成本如何处理？

## close-to-close 执行假设

之前的双均线策略使用：

```python
position = signal.shift(1)
strategy_return = position * close_return
```

其中：

```text
close_return = 今天收盘价 / 昨天收盘价 - 1
```

这避免了直接用今天信号赚今天收益，但仍然隐含一个偏理想的假设：信号生成和持仓收益都围绕收盘价计算。

这种方式适合快速研究，但正式报告必须说明执行假设。

## next-open 执行假设

更接近真实交易的版本是：

```text
今天收盘后计算信号
明天开盘执行
之后持有到下一次开盘
```

代码中使用：

```python
open_to_next_open_return = Open.shift(-1) / Open - 1
position = signal.shift(1)
strategy_return = position * open_to_next_open_return
```

含义是：

- 今天的 `position` 来自昨天收盘后的信号
- 今天开盘执行
- 收益从今天开盘算到下一交易日开盘

## bid / ask 和回测价格

真实交易中：

- 立刻买入通常按 ask 或更差价格成交
- 立刻卖出通常按 bid 或更差价格成交
- 行情软件里的 last price 不一定是你能成交的价格

日线回测用 `Close` 或 `Open` 都是简化。

流动性好的标的，如 SPY，这个简化通常还能接受；流动性差的小盘股，简化会明显乐观。

## 本课结果

策略：SPY `10/200` 双均线，交易成本 1 bps。

| execution_model | 最终净值 | 年化收益 | 最大回撤 | Calmar | 交易次数 | 在场时间 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| close_to_close | 8.0332 | 8.24% | -20.27% | 0.41 | 47 | 70.99% |
| next_open | 8.3003 | 8.37% | -21.46% | 0.39 | 47 | 70.99% |

## 如何解读

这次 next-open 最终净值略高，但最大回撤也更深，Calmar 反而略低。

这说明执行假设不一定总是让收益变差，但它会改变策略的收益和风险画像。

重要的不是哪一个结果更好，而是：

```text
回测必须清楚写出执行假设。
```

## 需要掌握的问题

- 为什么信号不等于成交？
- 为什么今天收盘后的信号不能用于今天收盘前的交易？
- close-to-close 和 next-open 有什么区别？
- 为什么 low liquidity 标的不能简单相信 close 回测？
- 为什么回测报告必须写清楚成交价格假设？
