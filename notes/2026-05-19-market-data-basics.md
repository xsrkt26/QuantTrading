# Market Data Basics

日期：2026-05-19

## 本课目标

用 SPY 日线数据理解第一条量化研究主链：

```text
Close 收盘价 -> return 日收益率 -> equity 净值曲线 -> drawdown 回撤曲线
```

## 数据来源

本课使用 `yfinance` 从 Yahoo Finance 下载 SPY 日线数据。

- 标的：SPY
- 含义：跟踪标普 500 指数的 ETF
- 起始日期：2000-01-01
- 价格处理：`auto_adjust=True`，使用复权价格

## 字段含义

- `Open`：开盘价
- `High`：最高价
- `Low`：最低价
- `Close`：收盘价
- `Volume`：成交量

## 核心计算

日收益率：

```text
return_t = Close_t / Close_{t-1} - 1
```

净值曲线：

```text
equity_t = equity_{t-1} * (1 + return_t)
```

回撤：

```text
drawdown_t = equity_t / historical_max_equity_t - 1
```

最大回撤：

```text
max_drawdown = min(drawdown)
```

## 需要掌握的问题

- SPY 是什么？
- 为什么长期收益计算要优先使用复权价格？
- 为什么第一天的收益率是空值？
- 为什么净值曲线用累计连乘？
- 为什么回撤通常是 0 或负数？
- 为什么最大回撤是 `drawdown` 这一列的最小值？
