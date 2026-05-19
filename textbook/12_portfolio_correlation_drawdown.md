# 12 Portfolio Correlation and Drawdown

状态：真实数据实跑版。

对应 RoadMap：阶段 6：组合风险

## 本课问题

为什么单个资产表现一般，组合以后可能更稳？

## 必须理解的概念

- 相关性
- 分散化
- 组合回撤
- 危机相关性
- 收益来源重叠

## 真实数据设置

- symbols: SPY, QQQ, DIA, IWM, EFA, TLT
- start_date: 2006-01-03
- end_date: 2026-05-18
- rows: 5125
- setup: MA 10/200 band 1%; correlation on strategy returns

## 关键代码

```python
corr = strategy_returns.corr()
rolling_corr = returns['SPY'].rolling(126).corr(returns['TLT'])
```

完整脚本：`scripts/12_portfolio_correlation_drawdown.py`

可运行 notebook：`notebooks/12_portfolio_correlation_drawdown.ipynb`

正式报告：`reports/`

## 实跑结果

| metric | value |
| --- | --- |
| average_pair_correlation | 0.3934 |
| min_pair_correlation | -0.2163 |
| max_pair_correlation | 0.8495 |
| portfolio_max_drawdown | -0.2436 |
| median_single_asset_max_drawdown | -0.2817 |
| latest_126d_SPY_TLT_corr | 0.1136 |

## 图示

![Portfolio Correlation and Drawdown](assets/12_portfolio_correlation_drawdown/12_portfolio_correlation_drawdown.png)

## 讲解

- 低相关资产能降低组合回撤，但相关性会随市场环境变化。
- SPY 与 TLT 的滚动相关性是观察股票/债券分散效果的重要窗口。
- 如果组合最大回撤没有明显低于单资产中位数，就要怀疑分散是否真实有效。

## 本课结论

相关性不是常数，组合风控必须关心危机时期相关性是否上升。

## 复习问题

1. 本章策略或实验到底想解决什么问题？
2. 结果中最重要的风险指标是什么？
3. 如果换一个市场或成本假设，结论最可能在哪里变化？
4. 这个实验离真实交易还缺哪一步？
