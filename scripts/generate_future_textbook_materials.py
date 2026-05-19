from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_trading.lesson_previews import plot_future_lesson_preview  # noqa: E402


CHAPTERS = [
    {
        "id": 11,
        "file": "11_equal_weight_trend_portfolio.md",
        "asset_dir": "11_equal_weight_trend_portfolio",
        "title": "Equal Weight Trend Portfolio",
        "stage": "阶段 6：组合构建",
        "question": "多个资产各自有趋势信号时，如何把它们合成一个等权组合？",
        "concepts": ["组合不是把单资产结果相加", "等权组合", "组合收益", "组合回撤", "资产相关性"],
        "code": "weights = positions.div(positions.sum(axis=1), axis=0).fillna(0)\nportfolio_return = (weights.shift(1) * asset_returns).sum(axis=1)\nportfolio_equity = (1 + portfolio_return).cumprod()",
        "experiments": ["使用 SPY、QQQ、DIA、IWM、EFA、TLT 的趋势信号", "比较单资产 SPY 与多资产等权组合", "输出组合净值、回撤和持仓数量"],
        "acceptance": ["能解释等权组合如何计算收益", "能说明组合为什么可能降低回撤", "能指出等权组合的缺陷"],
        "next": "第 12 章继续研究组合相关性和组合回撤。",
    },
    {
        "id": 12,
        "file": "12_portfolio_correlation_drawdown.md",
        "asset_dir": "12_portfolio_correlation_drawdown",
        "title": "Portfolio Correlation and Drawdown",
        "stage": "阶段 6：组合风险",
        "question": "为什么单个资产表现一般，组合以后可能更稳？",
        "concepts": ["相关性", "分散化", "组合回撤", "危机相关性上升", "收益来源重叠"],
        "code": "corr = strategy_returns.corr()\nportfolio_drawdown = equity / equity.cummax() - 1\nrolling_corr = returns['SPY'].rolling(126).corr(returns['TLT'])",
        "experiments": ["计算策略收益相关性矩阵", "比较单资产最大回撤和组合最大回撤", "观察危机时期相关性变化"],
        "acceptance": ["能解释低相关性为什么有价值", "能说明相关性不是常数", "能判断组合是否真的分散"],
        "next": "第 13 章进入仓位管理和波动率目标。",
    },
    {
        "id": 13,
        "file": "13_position_sizing_volatility_targeting.md",
        "asset_dir": "13_position_sizing_volatility_targeting",
        "title": "Position Sizing and Volatility Targeting",
        "stage": "阶段 6：仓位管理",
        "question": "信号告诉我们买不买，仓位管理决定买多少。",
        "concepts": ["等权", "波动率倒数加权", "风险目标", "杠杆上限", "仓位上限"],
        "code": "realized_vol = returns.rolling(63).std() * np.sqrt(252)\nraw_weight = target_vol / realized_vol\nweight = raw_weight.clip(upper=max_leverage)",
        "experiments": ["比较等权和波动率倒数权重", "加入目标波动率", "检查杠杆上限对回撤的影响"],
        "acceptance": ["能解释为什么高波动资产不一定该重仓", "能说明波动率目标的风险", "能识别杠杆带来的尾部风险"],
        "next": "第 14 章研究再平衡和换手率。",
    },
    {
        "id": 14,
        "file": "14_rebalancing_and_turnover.md",
        "asset_dir": "14_rebalancing_and_turnover",
        "title": "Rebalancing and Turnover",
        "stage": "阶段 6：再平衡",
        "question": "组合多久调一次仓，成本和风险会发生什么变化？",
        "concepts": ["再平衡频率", "目标权重", "权重漂移", "换手率", "交易成本"],
        "code": "target_weight = signal_weight.resample('M').last().reindex(index).ffill()\nturnover = target_weight.diff().abs().sum(axis=1)\ncost = turnover * cost_bps / 10000",
        "experiments": ["比较周度、月度、季度再平衡", "计算换手率和交易成本", "观察再平衡频率对回撤的影响"],
        "acceptance": ["能解释再平衡不是越频繁越好", "能计算组合换手率", "能说明成本如何吞噬组合收益"],
        "next": "第 15 章开始扩展经典策略族：突破策略。",
    },
    {
        "id": 15,
        "file": "15_breakout_strategy.md",
        "asset_dir": "15_breakout_strategy",
        "title": "Breakout Strategy",
        "stage": "阶段 4：经典策略族",
        "question": "价格突破历史高点是否代表趋势开始？",
        "concepts": ["突破", "Donchian channel", "假突破", "止损", "趋势延续"],
        "code": "channel_high = close.rolling(lookback).max().shift(1)\nsignal = (close > channel_high).astype(int)\nposition = signal.shift(1).fillna(0)",
        "experiments": ["实现 20/60/120 日突破", "比较突破和均线策略", "用交易日志观察假突破"],
        "acceptance": ["能解释突破策略赚什么钱", "能说明假突破为什么常见", "能比较突破和均线的差异"],
        "next": "第 16 章研究时间序列动量。",
    },
    {
        "id": 16,
        "file": "16_time_series_momentum.md",
        "asset_dir": "16_time_series_momentum",
        "title": "Time Series Momentum",
        "stage": "阶段 4：经典策略族",
        "question": "过去一段时间上涨的资产，未来是否更可能继续上涨？",
        "concepts": ["绝对动量", "回看窗口", "持有窗口", "趋势持续", "跨资产动量"],
        "code": "momentum = close / close.shift(lookback) - 1\nsignal = (momentum > 0).astype(int)\nstrategy_return = signal.shift(1) * next_return",
        "experiments": ["测试 1、3、6、12 个月动量", "比较不同资产上的动量效果", "检查动量崩溃阶段"],
        "acceptance": ["能区分时间序列动量和横截面动量", "能解释动量策略的失效环境", "能做窗口敏感性检查"],
        "next": "第 17 章转向均值回归。",
    },
    {
        "id": 17,
        "file": "17_mean_reversion_strategy.md",
        "asset_dir": "17_mean_reversion_strategy",
        "title": "Mean Reversion Strategy",
        "stage": "阶段 4：经典策略族",
        "question": "价格偏离均值以后，什么时候会回归？",
        "concepts": ["均值回归", "z-score", "过度反应", "止损", "半衰期"],
        "code": "z = (close - close.rolling(window).mean()) / close.rolling(window).std()\nsignal = np.where(z < -entry_z, 1, np.where(z > exit_z, 0, np.nan))",
        "experiments": ["实现 z-score 均值回归", "比较不同 entry_z", "观察趋势市场中的连续亏损"],
        "acceptance": ["能解释均值回归和趋势策略的冲突", "能说明为什么均值回归必须止损", "能识别均值变了的风险"],
        "next": "第 18 章把趋势和均值回归放进多策略组合。",
    },
    {
        "id": 18,
        "file": "18_multi_strategy_portfolio.md",
        "asset_dir": "18_multi_strategy_portfolio",
        "title": "Multi-Strategy Portfolio",
        "stage": "阶段 4/6：多策略组合",
        "question": "趋势和均值回归能否互补？",
        "concepts": ["策略相关性", "多策略组合", "收益来源", "策略权重", "策略失效轮换"],
        "code": "strategy_returns = pd.concat([trend_return, mean_reversion_return], axis=1)\ncombo_return = strategy_returns.mean(axis=1)\ncombo_equity = (1 + combo_return).cumprod()",
        "experiments": ["组合趋势和均值回归", "比较单策略和组合回撤", "检查策略相关性"],
        "acceptance": ["能说明多策略组合为什么可能更稳", "能识别同质化策略", "能计算策略层权重"],
        "next": "第 19 章进入因子研究。",
    },
    {
        "id": 19,
        "file": "19_factor_research_basics.md",
        "asset_dir": "19_factor_research_basics",
        "title": "Factor Research Basics",
        "stage": "阶段 5：因子研究",
        "question": "如何判断一个排序指标是否能解释未来收益？",
        "concepts": ["因子", "横截面排序", "分层回测", "多空组合", "因子收益"],
        "code": "factor_rank = factor.groupby(date).rank(pct=True)\nquantile = pd.qcut(factor_rank, 5, labels=False)\nlayer_return = future_return.groupby([date, quantile]).mean()",
        "experiments": ["构造动量因子", "按因子分 5 层", "观察高低层未来收益差异"],
        "acceptance": ["能解释分层回测", "能区分因子收益和单资产择时", "能指出幸存者偏差风险"],
        "next": "第 20 章学习 IC、Rank IC 和换手率。",
    },
    {
        "id": 20,
        "file": "20_factor_ic_and_turnover.md",
        "asset_dir": "20_factor_ic_and_turnover",
        "title": "Factor IC and Turnover",
        "stage": "阶段 5：因子检验",
        "question": "因子排序和未来收益到底有没有稳定关系？",
        "concepts": ["IC", "Rank IC", "ICIR", "换手率", "因子衰减"],
        "code": "ic = factor.corr(future_return)\nrank_ic = factor.rank().corr(future_return.rank())\nturnover = holdings.diff().abs().sum(axis=1) / 2",
        "experiments": ["计算月度 Rank IC", "计算 ICIR", "比较不同持有期换手率"],
        "acceptance": ["能解释 IC 和收益的区别", "能说明高 IC 但高换手的矛盾", "能判断因子是否可交易"],
        "next": "第 21 章学习因子中性化。",
    },
    {
        "id": 21,
        "file": "21_factor_neutralization.md",
        "asset_dir": "21_factor_neutralization",
        "title": "Factor Neutralization",
        "stage": "阶段 5：因子预处理",
        "question": "因子有效，是真的因子有效，还是暴露了规模、行业或 beta？",
        "concepts": ["去极值", "标准化", "行业中性", "市值中性", "残差化"],
        "code": "X = pd.concat([industry_dummies, size, beta], axis=1)\nneutral_factor = factor - LinearRegression().fit(X, factor).predict(X)",
        "experiments": ["对因子做去极值和标准化", "用回归残差做中性化", "比较中性化前后 IC"],
        "acceptance": ["能解释为什么要中性化", "能说明中性化可能损失有效信息", "能检查因子暴露"],
        "next": "第 22 章组合多个因子。",
    },
    {
        "id": 22,
        "file": "22_multi_factor_model.md",
        "asset_dir": "22_multi_factor_model",
        "title": "Multi-Factor Model",
        "stage": "阶段 5：多因子组合",
        "question": "多个弱因子如何组合成更稳的信号？",
        "concepts": ["多因子", "等权合成", "IC 加权", "因子相关性", "风险约束"],
        "code": "score = z_value + z_momentum + z_quality - z_volatility\nportfolio = score.groupby(date).rank(pct=True)",
        "experiments": ["组合 3 个简单因子", "比较单因子和多因子", "检查因子相关性"],
        "acceptance": ["能说明多因子不是简单堆指标", "能识别重复因子", "能解释因子权重来源"],
        "next": "第 23 章补金融时间序列基础。",
    },
    {
        "id": 23,
        "file": "23_financial_time_series_basics.md",
        "asset_dir": "23_financial_time_series_basics",
        "title": "Financial Time Series Basics",
        "stage": "阶段 7：金融统计",
        "question": "如何避免把随机噪声误判成规律？",
        "concepts": ["分布", "厚尾", "自相关", "平稳性", "显著性"],
        "code": "autocorr = returns.autocorr(lag=1)\nrolling_vol = returns.rolling(63).std() * np.sqrt(252)\nshuffled = returns.sample(frac=1)",
        "experiments": ["画收益率分布", "计算自相关", "比较真实序列和打乱序列"],
        "acceptance": ["能解释厚尾", "能说明自相关为什么重要", "能区分统计显著和可交易"],
        "next": "第 24 章学习协整和配对交易。",
    },
    {
        "id": 24,
        "file": "24_pairs_trading_cointegration.md",
        "asset_dir": "24_pairs_trading_cointegration",
        "title": "Pairs Trading and Cointegration",
        "stage": "阶段 7：协整和配对",
        "question": "两只资产价格一起走时，价差偏离能否交易？",
        "concepts": ["配对交易", "价差", "z-score", "协整", "半衰期"],
        "code": "spread = y - hedge_ratio * x\nz = (spread - spread.rolling(60).mean()) / spread.rolling(60).std()\nsignal = np.where(z < -2, 1, np.where(z > 2, -1, 0))",
        "experiments": ["构造 SPY/QQQ 价差", "计算 z-score", "模拟价差回归交易"],
        "acceptance": ["能解释相关不等于协整", "能说明价差失效风险", "能处理双腿交易成本"],
        "next": "第 25 章进入机器学习基线。",
    },
    {
        "id": 25,
        "file": "25_ml_signal_baseline.md",
        "asset_dir": "25_ml_signal_baseline",
        "title": "Machine Learning Signal Baseline",
        "stage": "阶段 8：机器学习量化",
        "question": "机器学习能不能比简单规则更好？",
        "concepts": ["特征", "标签", "训练集", "基准模型", "交易指标"],
        "code": "features = pd.concat([momentum, volatility, volume_change], axis=1)\nlabel = (future_return > 0).astype(int)\n# train only on past data, compare with simple momentum baseline",
        "experiments": ["构造价格特征", "预测未来收益方向", "和动量基准比较"],
        "acceptance": ["能说明准确率不是交易收益", "能避免未来函数", "能和简单基准比较"],
        "next": "第 26 章专门讲机器学习泄露和验证。",
    },
    {
        "id": 26,
        "file": "26_ml_validation_and_leakage.md",
        "asset_dir": "26_ml_validation_and_leakage",
        "title": "ML Validation and Leakage",
        "stage": "阶段 8：防泄露",
        "question": "为什么机器学习量化最容易被数据泄露骗？",
        "concepts": ["特征泄露", "标签泄露", "时间序列切分", "purge", "embargo"],
        "code": "train = data.loc[:train_end]\nvalid = data.loc[valid_start:valid_end]\ntest = data.loc[test_start:]\n# never fit scaler or selector on future data",
        "experiments": ["故意制造泄露案例", "对比泄露和无泄露表现", "写检查清单"],
        "acceptance": ["能识别常见泄露", "能设计时间序列验证", "能解释为什么随机 KFold 危险"],
        "next": "第 27 章进入研究管线工程化。",
    },
    {
        "id": 27,
        "file": "27_research_pipeline_engineering.md",
        "asset_dir": "27_research_pipeline_engineering",
        "title": "Research Pipeline Engineering",
        "stage": "阶段 9：工程化",
        "question": "如何让研究结果可复现，而不是 notebook 手工结果？",
        "concepts": ["配置文件", "数据缓存", "实验参数", "产物目录", "日志"],
        "code": "config = load_config(path)\ndata = load_or_download(config.symbols)\nresult = run_backtest(data, config)\nsave_report(result, output_dir)",
        "experiments": ["把参数移到配置", "固定输出目录", "保存数据版本和运行时间"],
        "acceptance": ["换机器能复现", "每次实验有参数记录", "图表和 CSV 自动输出"],
        "next": "第 28 章设计更通用的回测框架。",
    },
    {
        "id": 28,
        "file": "28_backtest_framework_design.md",
        "asset_dir": "28_backtest_framework_design",
        "title": "Backtest Framework Design",
        "stage": "阶段 9：回测框架",
        "question": "什么时候向量化回测不够，需要事件驱动框架？",
        "concepts": ["数据层", "信号层", "订单层", "成交层", "组合层"],
        "code": "for event in events:\n    signal = strategy.on_bar(event)\n    order = broker.create_order(signal)\n    fill = execution_model.fill(order)\n    portfolio.update(fill)",
        "experiments": ["拆分信号和执行", "模拟订单状态", "比较向量化和事件驱动"],
        "acceptance": ["能解释回测模块边界", "能说明事件驱动的优势", "能写最小订单模拟"],
        "next": "第 29 章进入模拟盘检查清单。",
    },
    {
        "id": 29,
        "file": "29_paper_trading_checklist.md",
        "asset_dir": "29_paper_trading_checklist",
        "title": "Paper Trading Checklist",
        "stage": "阶段 10：模拟盘",
        "question": "回测通过后，为什么还不能直接实盘？",
        "concepts": ["模拟盘", "信号核对", "订单核对", "持仓核对", "日志"],
        "code": "record = {'date': today, 'signal': signal, 'order': order, 'fill': fill, 'position': position}\npaper_log.append(record)",
        "experiments": ["设计每日模拟盘日志", "记录信号和订单差异", "统计模拟盘偏差"],
        "acceptance": ["能每天复盘信号", "能解释回测和模拟盘差异", "能发现执行问题"],
        "next": "第 30 章建立实盘前风险政策。",
    },
    {
        "id": 30,
        "file": "30_risk_policy_and_live_readiness.md",
        "asset_dir": "30_risk_policy_and_live_readiness",
        "title": "Risk Policy and Live Readiness",
        "stage": "阶段 10：实盘前准备",
        "question": "什么条件下，一个策略才有资格进入小资金实盘？",
        "concepts": ["最大亏损", "最大回撤", "仓位上限", "停止交易规则", "异常处理"],
        "code": "if drawdown < max_allowed_drawdown:\n    halt_trading()\nif position > max_position:\n    reduce_position()",
        "experiments": ["写风险政策", "定义停止交易条件", "设计异常处理流程"],
        "acceptance": ["能说清最大可亏损", "有明确停手机制", "有模拟盘记录和复盘报告"],
        "next": "完成 30 章后，进入实盘前专项审查，而不是盲目加资金。",
    },
]


def main() -> None:
    for chapter in CHAPTERS:
        write_chapter(chapter)
        asset_path = (
            PROJECT_ROOT
            / "textbook"
            / "assets"
            / chapter["asset_dir"]
            / f"{chapter['asset_dir']}.png"
        )
        fig = plot_future_lesson_preview(chapter["id"], asset_path)
        plt.close(fig)
        print(f"generated chapter {chapter['id']:02d}: {chapter['file']}")


def write_chapter(chapter: dict[str, object]) -> None:
    chapter_id = int(chapter["id"])
    asset_dir = str(chapter["asset_dir"])
    markdown_path = PROJECT_ROOT / "textbook" / str(chapter["file"])
    markdown_path.write_text(render_chapter(chapter_id, chapter, asset_dir), encoding="utf-8")


def render_chapter(chapter_id: int, chapter: dict[str, object], asset_dir: str) -> str:
    concepts = "\n".join(f"- {item}" for item in chapter["concepts"])
    experiments = "\n".join(f"- {item}" for item in chapter["experiments"])
    acceptance = "\n".join(f"- {item}" for item in chapter["acceptance"])
    return f"""# {chapter_id:02d} {chapter['title']}

状态：预习版课本。正式上到本章时，会补充完整实跑结果、报告和必要测试。

对应 RoadMap：{chapter['stage']}

## 本课问题

{chapter['question']}

## 为什么重要

这一章的目的不是多记一个术语，而是把前面学到的研究流程迁移到新的问题上。

你读这一章时要一直问：

```text
这个规则想解决什么问题？
它赚的是 beta、alpha、风险溢价，还是执行/约束优势？
它最容易在哪种市场环境失效？
```

## 核心概念

{concepts}

## 代码骨架

```python
{chapter['code']}
```

这段代码是本章的最小思想骨架。正式上课时，我们会把它扩展成可复用函数、脚本、notebook 和报告。

## 图示

![{chapter['title']}](assets/{asset_dir}/{asset_dir}.png)

这张图是预习图，用来帮助你先建立直觉。正式实验图会在本章开讲时根据真实数据生成。

## 实验任务

{experiments}

## 验收标准

{acceptance}

## 本课结论

本章预习阶段你要先掌握问题定义和研究框架。真正做实验时，不以“曲线好看”为标准，而以是否解决本章一开始定义的问题为标准。

## 下一步

{chapter['next']}
"""


if __name__ == "__main__":
    main()
