# 25 Machine Learning Signal Baseline

状态：真实数据实跑版。

对应 RoadMap：阶段 8：机器学习量化

## 本课问题

机器学习能不能比简单规则更好？

## 必须理解的概念

- 特征
- 标签
- 训练集
- 基准模型
- 交易指标

## 真实数据设置

- symbols: SPY
- start_date: 2006-01-03
- end_date: 2026-05-18
- rows: 5125
- setup: Ridge linear baseline on SPY daily features

## 关键代码

```python
prediction = ridge_model.predict(features)
signal = prediction > 0
```

完整脚本：`scripts/25_ml_signal_baseline.py`

可运行 notebook：`notebooks/25_ml_signal_baseline.ipynb`

正式报告：`reports/`

## 实跑结果

| case | final_equity | ann_return | ann_vol | max_drawdown | sharpe | calmar | direction_accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ridge_features | 2.3072 | 12.63% | 16.42% | -22.24% | 0.7688 | 0.5676 | 50.68% |
| momentum_baseline | 2.2367 | 12.13% | 11.54% | -13.86% | 1.0514 | 0.8754 | 53.05% |
| buy_hold_test | 2.7888 | 15.70% | 19.79% | -33.72% | 0.7935 | 0.4657 | nan |

## 图示

![Machine Learning Signal Baseline](assets/25_ml_signal_baseline/25_ml_signal_baseline.png)

## 讲解

- 模型用训练集拟合，只在测试集评价，避免把未来信息带入训练。
- 机器学习策略必须和简单动量基准比较；如果赢不了基准，复杂度没有价值。
- 方向准确率和交易收益不是一回事，最终仍要看净值、回撤和成本。

## 本课结论

机器学习模型必须和简单规则比较，不能只汇报准确率。

## 复习问题

1. 本章策略或实验到底想解决什么问题？
2. 结果中最重要的风险指标是什么？
3. 如果换一个市场或成本假设，结论最可能在哪里变化？
4. 这个实验离真实交易还缺哪一步？
