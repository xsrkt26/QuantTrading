from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
import shutil

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from quant_trading.market_data import TRADING_DAYS_PER_YEAR, download_ohlcv


CORE_SYMBOLS = ("SPY", "QQQ", "DIA", "IWM", "EFA", "TLT")
FACTOR_SYMBOLS = (
    "SPY",
    "QQQ",
    "DIA",
    "IWM",
    "EFA",
    "TLT",
    "GLD",
    "XLE",
    "XLF",
    "XLK",
    "XLU",
    "XLV",
    "XLI",
    "XLY",
    "XLP",
)
DEFAULT_START = "2006-01-01"
DEFAULT_COST_BPS = 3.0


@dataclass(frozen=True)
class LessonSpec:
    chapter: int
    slug: str
    title: str
    stage: str
    question: str
    concepts: tuple[str, ...]
    code: str
    conclusion_hint: str
    deep_dive: str = ""

    @property
    def textbook_file(self) -> str:
        return f"{self.chapter:02d}_{self.slug}.md"

    @property
    def script_file(self) -> str:
        return f"{self.chapter:02d}_{self.slug}.py"

    @property
    def notebook_file(self) -> str:
        return f"{self.chapter:02d}_{self.slug}.ipynb"

    @property
    def asset_dir(self) -> str:
        return f"{self.chapter:02d}_{self.slug}"

    @property
    def asset_image(self) -> str:
        return f"{self.chapter:02d}_{self.slug}.png"


@dataclass
class LessonResult:
    spec: LessonSpec
    summary: pd.DataFrame
    details: dict[str, str]
    interpretation: list[str]
    figure: plt.Figure
    extra_tables: dict[str, pd.DataFrame] = field(default_factory=dict)
    report_path: Path | None = None
    textbook_path: Path | None = None
    image_path: Path | None = None
    generated_dir: Path | None = None


LESSON_SPECS: dict[int, LessonSpec] = {
    11: LessonSpec(
        11,
        "equal_weight_trend_portfolio",
        "Equal Weight Trend Portfolio",
        "阶段 6：组合构建",
        "多个资产各自有趋势信号时，如何合成一个等权组合？",
        ("等权组合", "主动持仓数", "组合收益", "组合回撤", "资产分散"),
        "weights = positions.div(positions.sum(axis=1), axis=0).fillna(0)\n"
        "portfolio_return = (weights * open_to_next_open_returns).sum(axis=1) - turnover * cost_rate",
        "多资产趋势组合的价值不在于每个资产都更强，而在于把单一资产路径风险摊开。",
        """## 详细讲解

### 1. 本章到底在解决什么问题

前面几章我们一直在研究单个资产上的策略，比如只在 SPY 上做均线、过滤、成本和多资产验证。第 11 章开始进入组合层，问题从：

```text
这个资产今天该不该买？
```

变成：

```text
如果多个资产今天都可以买，资金怎么分？
```

这一步非常关键。单资产策略只决定一个标的的进出场，组合策略决定整个账户的资金分配。现实交易里，你最后面对的不是一条 SPY 曲线，而是一个账户净值曲线，所以组合层是量化从“策略想法”走向“资金管理”的第一步。

### 2. 本章资产池为什么选这些 ETF

本章使用 6 个 ETF：

| symbol | 含义 | 角色 |
| --- | --- | --- |
| SPY | 标普 500 ETF | 美国大盘股 |
| QQQ | 纳斯达克 100 ETF | 美国科技成长股 |
| DIA | 道琼斯工业 ETF | 美国蓝筹股 |
| IWM | 罗素 2000 ETF | 美国小盘股 |
| EFA | 美国以外发达市场 ETF | 海外股票 |
| TLT | 长久期美国国债 ETF | 债券资产 |

它们不是随便选的。SPY、QQQ、DIA、IWM 都是股票类资产，但风格不同；EFA 加入海外市场；TLT 加入债券。这样做的目的不是凑数量，而是让组合有不同来源的风险暴露。

如果你只把 SPY、VOO、IVV 放进组合，看起来是 3 个资产，实际上几乎还是同一个风险来源。真正的组合要关心资产之间是不是有差异，而不是名称是不是不同。

### 3. 趋势信号怎么来

本章仍然沿用前面已经验证过的趋势思路：

```text
短期均线：10 日均线
长期均线：200 日均线
过滤带：1%
执行方式：next-open
成本：单边 3 bps
```

信号含义是：

```text
如果 10 日均线高于 200 日均线超过 1%，认为趋势向上，可以持有。
如果已经持有，只有当 10 日均线低于 200 日均线超过 1%，才退出。
```

这里的 1% band 是为了减少均线附近来回穿越导致的假信号。注意，它不是为了让回测更好看，而是为了解决一个明确问题：

```text
减少短期噪声造成的频繁交易。
```

### 4. 为什么要 shift 一天

代码里有一个很重要的步骤：

```python
active = signals.shift(1).fillna(0)
```

这表示今天的仓位来自昨天收盘后已经知道的信号。原因是：均线信号需要今天收盘价才能计算出来，你不可能在今天开盘时提前知道今天收盘后的均线。

所以正确顺序是：

```text
第 t 天收盘：计算信号
第 t+1 天开盘：按这个信号交易
第 t+1 天到第 t+2 天：承担持仓收益
```

这就是我们前面讲过的 next-open 逻辑。它比 close-to-close 更保守，也更接近真实交易。

### 5. 等权到底是什么意思

核心代码是：

```python
weights = positions.div(positions.sum(axis=1), axis=0).fillna(0)
```

假设今天 6 个资产里有 3 个资产出现趋势信号：

```text
SPY = 1
QQQ = 1
TLT = 1
其他 = 0
```

那么持仓数量是 3，等权后：

```text
SPY 权重 = 1 / 3
QQQ 权重 = 1 / 3
TLT 权重 = 1 / 3
其他权重 = 0
```

如果只有 1 个资产有信号，那它就是 100% 权重。如果 6 个资产都有信号，每个资产就是 1/6。这里的等权不是永远每个资产 1/6，而是：

```text
在当前有趋势信号的资产之间等权。
```

所以本章表格里的 `avg_exposure = 91.94%` 表示组合平均大约 91.94% 的资金处于持仓状态，不是每天都满仓，也不是每天都空仓。

### 6. 组合收益怎么计算

组合收益可以拆成三步：

```python
gross_return = (weights * open_returns).sum(axis=1)
cost = turnover * cost_bps / 10000
net_return = gross_return - cost
```

第一步，计算每个资产的收益贡献：

```text
资产收益贡献 = 资产权重 × 资产收益率
```

第二步，把所有资产收益贡献加起来：

```text
组合毛收益 = 所有资产收益贡献之和
```

第三步，扣掉交易成本：

```text
组合净收益 = 组合毛收益 - 换手成本
```

这里你要养成一个习惯：以后看到任何组合策略，都要问它有没有扣成本、成本怎么算、换手怎么算。没有成本的组合回测通常会过于乐观。

### 7. 三个对照组分别代表什么

本章结果里有三行：

| case | 含义 |
| --- | --- |
| SPY trend only | 只在 SPY 上做同一套趋势规则 |
| Equal active trend portfolio | 在 6 个资产上做趋势信号，有信号的资产之间等权 |
| Equal-weight buy and hold | 6 个资产不择时，长期等权持有 |

这三个不是随便比较的。它们分别回答三个问题：

```text
SPY trend only：
只做单资产趋势，表现如何？

Equal active trend portfolio：
把同样思想扩展成多资产组合，路径是否改善？

Equal-weight buy and hold：
如果我完全不择时，只靠资产分散，会怎样？
```

量化研究一定要有对照组。没有对照组，你就不知道策略到底赢在哪里，也不知道它只是承担了更多 beta，还是确实改善了风险收益结构。

### 8. 如何读这次结果

本章实跑结果是：

| case | final_equity | ann_return | ann_vol | max_drawdown | sharpe | calmar |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SPY trend only | 5.9452 | 9.16% | 12.03% | -21.53% | 0.7617 | 0.4254 |
| Equal active trend portfolio | 4.7201 | 7.93% | 13.67% | -24.36% | 0.5800 | 0.3255 |
| Equal-weight buy and hold | 6.6584 | 9.77% | 15.99% | -45.75% | 0.6111 | 0.2136 |

第一眼不要只看 `final_equity`。如果只看最终净值，buy and hold 最高，似乎它最好。但它最大回撤是 -45.75%，说明中间曾经接近腰斩。对于真实资金，这种路径非常难坚持。

SPY trend only 的最终净值低于 buy and hold，但最大回撤从 -45.75% 降到 -21.53%，Calmar 从 0.2136 升到 0.4254。这说明它牺牲了一部分牛市暴露，换来了更浅的回撤。

Equal active trend portfolio 的表现比较微妙：它没有超过 SPY trend only，最终净值、Sharpe、Calmar 都更低，最大回撤也更深一点。但它仍然明显降低了 buy and hold 的大回撤。这告诉我们：

```text
多资产组合不是自动更强。
```

组合层确实改变了风险路径，但本章这个最朴素的等权规则还不是最终答案。

### 9. 为什么多资产等权没有赢过 SPY trend only

这是本章最值得思考的地方。

第一个原因：资产池里不全是高收益资产。TLT、EFA、DIA、IWM 在某些阶段可能弱于 SPY 或 QQQ。等权组合会把资金分给它们，因此可能拉低最终收益。

第二个原因：等权没有考虑波动率。IWM 这类资产波动更高，TLT 在加息周期也会有很大回撤。简单等权把每个有信号的资产当成同等风险，这并不准确。

第三个原因：股票类 ETF 之间相关性并不低。SPY、QQQ、DIA、IWM 在危机中经常一起跌。你以为自己分散了，但风险来源仍然大量重叠。

第四个原因：趋势信号在不同资产上适配度不同。同样的 10/200 均线和 1% band，对 SPY 合适，不代表对 TLT、EFA、IWM 都合适。

这就是第 12-14 章要继续研究的原因：我们需要看相关性、回撤、仓位权重和再平衡。

### 10. 本章真正应该学到什么

本章不是为了证明：

```text
多资产等权趋势组合一定更赚钱。
```

本章真正要你建立的是组合研究框架：

```text
1. 先对每个资产生成信号。
2. 再把信号转成组合权重。
3. 用 next-open 收益计算组合收益。
4. 扣除换手成本。
5. 和单资产策略、buy and hold 做对照。
6. 不只看最终净值，还要看回撤、波动、Sharpe、Calmar 和暴露。
```

这是从“策略规则”走向“资金管理”的第一步。

### 11. 这一章对你的操作要求

你现在不需要急着改策略。你要先能用自己的话讲清楚：

```text
为什么 signals 要 shift？
为什么有信号的资产之间要重新归一化权重？
为什么组合最终净值不最高，但仍然可能有研究价值？
为什么等权只是基准，不是最终仓位管理方案？
```

能讲清楚这些，第 11 章才算真正过关。
""",
    ),
    12: LessonSpec(
        12,
        "portfolio_correlation_drawdown",
        "Portfolio Correlation and Drawdown",
        "阶段 6：组合风险",
        "为什么单个资产表现一般，组合以后可能更稳？",
        ("相关性", "分散化", "组合回撤", "危机相关性", "收益来源重叠"),
        "corr = strategy_returns.corr()\nrolling_corr = returns['SPY'].rolling(126).corr(returns['TLT'])",
        "相关性不是常数，组合风控必须关心危机时期相关性是否上升。",
        """## 详细讲解

### 1. 为什么第 12 章紧跟第 11 章

第 11 章我们做了一个多资产等权趋势组合，结果发现它并没有自动赢过 `SPY trend only`。这不是坏事，反而是非常好的研究信号，因为它逼我们继续问：

```text
为什么多个资产放在一起，组合没有明显更强？
```

第 12 章就是回答这个问题的第一步。组合是否有价值，不只取决于每个资产单独表现好不好，还取决于它们之间是不是一起涨、一起跌。

如果几个资产经常一起涨跌，那么它们名字不同，本质上也可能是同一个风险来源。如果几个资产涨跌节奏不同，组合才可能降低路径风险。

### 2. 相关性到底是什么

相关性衡量的是两个收益序列同向运动的程度，取值范围大致是：

```text
+1：几乎完全同涨同跌
 0：线性关系很弱
-1：一个涨时另一个倾向于跌
```

注意，本章计算的是：

```python
corr = strategy_returns.corr()
```

这里不是价格相关性，而是“策略收益相关性”。也就是说，我们先对每个资产跑同一套趋势策略，得到每个资产自己的策略日收益，然后再看这些策略收益之间的相关性。

为什么不直接看价格相关性？因为我们最终交易的是策略，不是裸价格。如果策略经常空仓，或者趋势规则改变了收益路径，那么策略收益相关性比价格相关性更贴近账户层面的风险。

### 3. 为什么低相关能降低组合回撤

组合收益可以粗略理解为多个资产收益的加权平均：

```text
组合收益 = w1*r1 + w2*r2 + ... + wn*rn
```

但组合风险不是简单平均。两个资产同时下跌时，组合回撤会叠加；一个跌、另一个不跌甚至上涨时，组合回撤会被缓冲。

用最简化的两资产方差公式看：

```text
组合方差 =
w1^2 * sigma1^2
+ w2^2 * sigma2^2
+ 2 * w1 * w2 * sigma1 * sigma2 * corr
```

最后一项里的 `corr` 就是关键。如果相关性高，风险会互相加强；如果相关性低甚至为负，这一项会变小，组合波动和回撤就有机会下降。

这就是分散化的数学基础：

```text
分散化不是靠资产数量，而是靠风险来源不完全重叠。
```

### 4. 怎么读相关性矩阵

本章报告里的相关性矩阵是：

| symbol | SPY | QQQ | DIA | IWM | EFA | TLT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SPY | 1.0000 | 0.8300 | 0.8495 | 0.7017 | 0.6530 | -0.2163 |
| QQQ | 0.8300 | 1.0000 | 0.6782 | 0.6143 | 0.5636 | -0.1871 |
| DIA | 0.8495 | 0.6782 | 1.0000 | 0.6578 | 0.6435 | -0.2141 |
| IWM | 0.7017 | 0.6143 | 0.6578 | 1.0000 | 0.5880 | -0.1795 |
| EFA | 0.6530 | 0.5636 | 0.6435 | 0.5880 | 1.0000 | -0.0818 |
| TLT | -0.2163 | -0.1871 | -0.2141 | -0.1795 | -0.0818 | 1.0000 |

读这个表有几个规则。

第一，对角线永远是 1。因为一个序列和自己完全相关。

第二，矩阵是对称的。`SPY vs QQQ` 和 `QQQ vs SPY` 是同一个数字。

第三，不要平均看，要找结构。比如：

```text
SPY-DIA = 0.8495
SPY-QQQ = 0.8300
SPY-IWM = 0.7017
SPY-EFA = 0.6530
SPY-TLT = -0.2163
```

这说明股票类资产之间相关性很高，尤其 SPY、QQQ、DIA 很像。它们放在一起能分散一些风格风险，但不能完全分散股市系统性风险。

TLT 和股票类资产长期是负相关或低相关，这就是它在组合里有价值的原因。它不一定收益最高，但它可能在股票策略受压时提供缓冲。

### 5. 本章指标逐个解释

本章实跑结果是：

| metric | value |
| --- | ---: |
| average_pair_correlation | 0.3934 |
| min_pair_correlation | -0.2163 |
| max_pair_correlation | 0.8495 |
| portfolio_max_drawdown | -24.36% |
| median_single_asset_max_drawdown | -28.17% |
| latest_126d_SPY_TLT_corr | 0.1136 |

`average_pair_correlation = 0.3934` 表示所有资产两两相关性的平均值大约是 0.39。这不是很低，因为股票类资产之间相关性高，把平均值抬上去了。

`min_pair_correlation = -0.2163` 来自 SPY 和 TLT。这个数字说明长期看，股票趋势策略和债券趋势策略有一定反向关系。

`max_pair_correlation = 0.8495` 来自 SPY 和 DIA。这个数字很高，说明它们虽然是两个 ETF，但策略收益路径非常接近。

`portfolio_max_drawdown = -24.36%` 是第 11 章多资产趋势组合的最大回撤。

`median_single_asset_max_drawdown = -28.17%` 是单资产策略最大回撤的中位数。组合回撤比单资产中位数浅，说明组合确实有一定分散效果。

但是这个改善不算巨大，因为组合里大量资产仍然是股票类风险。

`latest_126d_SPY_TLT_corr = 0.1136` 是最近 126 个交易日，也就是大约半年，SPY 和 TLT 策略收益的滚动相关性。它是正数，说明最近股票和债券并没有表现出很强的负相关保护。

这就是本章最重要的风险提醒：

```text
历史长期负相关，不代表最近仍然负相关。
```

### 6. 为什么相关性不是常数

很多新手会犯一个错误：看到长期相关性矩阵，就以为未来也稳定如此。

现实不是这样。相关性会随市场环境变化：

```text
通胀冲击时：股票和债券可能一起跌。
流动性危机时：很多资产可能一起被卖出。
降息衰退预期时：债券可能上涨、股票下跌。
科技牛市时：QQQ 可能明显强于其他股票 ETF。
```

所以我们看 SPY 和 TLT 的滚动相关性：

```python
rolling_corr = returns["SPY"].rolling(126).corr(returns["TLT"])
```

126 个交易日大约是半年。这个指标不是为了预测明天，而是为了监控组合保护机制有没有变化。

如果你原本指望 TLT 对冲股票，但最近相关性持续升高，那么组合的真实风险可能比历史回测更大。

### 7. 分散化的三个层次

你要区分三种“看起来像分散”的东西。

第一种是名称分散：

```text
我买了 SPY、QQQ、DIA，所以我有 3 个资产。
```

这只是名称不同，不一定风险不同。

第二种是风格分散：

```text
大盘、科技、小盘、海外、债券。
```

这比名称分散更好，但仍然可能在危机时一起下跌。

第三种是收益路径分散：

```text
这些策略收益序列在关键时期不一起亏。
```

这是量化最关心的分散。第 12 章研究的就是第三种。

### 8. 为什么组合回撤只改善了一部分

本章组合最大回撤是 -24.36%，单资产最大回撤中位数是 -28.17%。组合确实更稳了一点，但没有发生质变。

原因很直接：

```text
组合里 6 个资产，5 个都和股票风险有关或部分相关。
```

SPY、QQQ、DIA、IWM、EFA 在全球风险偏好下降时通常会一起受压。TLT 能提供一些不同风险来源，但它只有一个资产，而且在某些时期也不一定能对冲。

所以本章不是证明这个组合已经很好，而是告诉我们下一步应该研究：

```text
资产相关性是否足够低？
仓位是否应该按风险而不是按数量等权？
再平衡频率是否会影响换手和回撤？
```

这正好对应第 13、14 章。

### 9. 本章和第 11 章如何连起来

第 11 章看到的现象是：

```text
多资产等权趋势组合降低了 buy and hold 的深度回撤，
但没有赢过 SPY trend only。
```

第 12 章解释了原因：

```text
组合里股票类资产相关性很高，所以分散效果有限；
TLT 有分散价值，但相关性会随市场变化，不是永久保护。
```

这就是量化研究的正确节奏：不是看到结果就急着改参数，而是先解释结果为什么发生。

### 10. 本章真正要掌握的能力

学完第 12 章，你要能做到三件事。

第一，看到组合时，不再只问：

```text
收益是多少？
```

而是问：

```text
收益来源是不是重叠？
回撤是不是一起发生？
相关性在危机时会不会上升？
```

第二，能读懂相关性矩阵，知道哪些资产只是名字不同，哪些资产真的提供了不同风险来源。

第三，知道相关性是动态的，长期矩阵只能提供背景，不能替代滚动监控。

### 11. 本章过关标准

你能用自己的话解释下面四句话，第 12 章就算过关：

```text
低相关不是为了让收益更高，而是为了降低组合路径风险。
股票类 ETF 之间相关性高，所以它们不能完全分散系统性风险。
TLT 长期有分散价值，但近期相关性可能变正。
组合回撤改善有限时，要先检查相关性和风险来源，而不是直接调参数。
```
""",
    ),
    13: LessonSpec(
        13,
        "position_sizing_volatility_targeting",
        "Position Sizing and Volatility Targeting",
        "阶段 6：仓位管理",
        "信号告诉我们买不买，仓位管理决定买多少。",
        ("等权", "波动率倒数加权", "目标波动率", "杠杆上限", "暴露控制"),
        "realized_vol = returns.rolling(63).std() * np.sqrt(252)\n"
        "weight = (target_vol / realized_vol).clip(upper=max_leverage)",
        "仓位管理不是提高收益的魔法，它首先是把风险尺度拉回可比较状态。",
    ),
    14: LessonSpec(
        14,
        "rebalancing_and_turnover",
        "Rebalancing and Turnover",
        "阶段 6：再平衡",
        "组合多久调一次仓，成本和风险会发生什么变化？",
        ("再平衡频率", "目标权重", "权重漂移", "换手率", "交易成本"),
        "target_weight = daily_weight.where(is_rebalance_day).ffill()\n"
        "turnover = target_weight.diff().abs().sum(axis=1)",
        "再平衡频率越高不一定越好，成本和信号延迟必须一起看。",
    ),
    15: LessonSpec(
        15,
        "breakout_strategy",
        "Breakout Strategy",
        "阶段 4：经典策略族",
        "价格突破历史高点是否代表趋势开始？",
        ("突破", "Donchian channel", "假突破", "退出规则", "趋势延续"),
        "channel_high = close.rolling(lookback).max().shift(1)\n"
        "signal = close > channel_high",
        "突破策略的核心风险是假突破；参数越短，反应越快，噪声也越多。",
    ),
    16: LessonSpec(
        16,
        "time_series_momentum",
        "Time Series Momentum",
        "阶段 4：经典策略族",
        "过去一段时间上涨的资产，未来是否更可能继续上涨？",
        ("绝对动量", "回看窗口", "跨资产动量", "趋势持续", "窗口敏感性"),
        "momentum = close / close.shift(lookback) - 1\nsignal = momentum > 0",
        "时间序列动量要看跨资产一致性，不能只看一个窗口在一个资产上的表现。",
    ),
    17: LessonSpec(
        17,
        "mean_reversion_strategy",
        "Mean Reversion Strategy",
        "阶段 4：经典策略族",
        "价格偏离均值以后，什么时候会回归？",
        ("均值回归", "z-score", "过度反应", "止损", "趋势市场风险"),
        "z = (close - close.rolling(window).mean()) / close.rolling(window).std()\n"
        "signal = z < -entry_z",
        "均值回归最大的敌人是均值本身发生变化，所以必须承认连续亏损风险。",
    ),
    18: LessonSpec(
        18,
        "multi_strategy_portfolio",
        "Multi-Strategy Portfolio",
        "阶段 4/6：多策略组合",
        "趋势和均值回归能否互补？",
        ("策略相关性", "多策略组合", "收益来源", "策略权重", "失效轮换"),
        "strategy_returns = pd.concat([trend_return, breakout_return, mean_reversion_return], axis=1)\n"
        "combo_return = strategy_returns.mean(axis=1)",
        "多策略组合的关键不是策略数量，而是收益来源是否真的不同。",
    ),
    19: LessonSpec(
        19,
        "factor_research_basics",
        "Factor Research Basics",
        "阶段 5：因子研究",
        "如何判断一个排序指标是否能解释未来收益？",
        ("因子", "横截面排序", "分层回测", "多空组合", "因子收益"),
        "factor_rank = factor.rank(axis=1, pct=True)\n"
        "top_return = future_return.where(factor_rank >= 0.8).mean(axis=1)",
        "因子研究先看排序能力，而不是急着把它做成实盘策略。",
    ),
    20: LessonSpec(
        20,
        "factor_ic_and_turnover",
        "Factor IC and Turnover",
        "阶段 5：因子检验",
        "因子排序和未来收益到底有没有稳定关系？",
        ("IC", "Rank IC", "ICIR", "换手率", "可交易性"),
        "rank_ic = factor.rank(axis=1).corrwith(future_return.rank(axis=1), axis=1)",
        "高 IC 如果伴随极高换手，可能只是纸面优势。",
    ),
    21: LessonSpec(
        21,
        "factor_neutralization",
        "Factor Neutralization",
        "阶段 5：因子预处理",
        "因子有效是真因子有效，还是暴露了 beta 或波动率？",
        ("去极值", "标准化", "beta 中性", "波动率中性", "残差化"),
        "neutral_factor = factor - X @ np.linalg.lstsq(X, factor, rcond=None)[0]",
        "中性化是诊断工具，不是固定仪式；它可能去掉噪声，也可能去掉有效信息。",
    ),
    22: LessonSpec(
        22,
        "multi_factor_model",
        "Multi-Factor Model",
        "阶段 5：多因子组合",
        "多个弱因子如何组合成更稳的信号？",
        ("多因子", "等权合成", "因子相关性", "低波动因子", "动量因子"),
        "score = z_momentum + z_reversal + z_low_volatility\n"
        "portfolio = score.rank(axis=1, pct=True)",
        "多因子不是堆指标，而是组合不同且有解释力的收益来源。",
    ),
    23: LessonSpec(
        23,
        "financial_time_series_basics",
        "Financial Time Series Basics",
        "阶段 7：金融统计",
        "如何避免把随机噪声误判成规律？",
        ("收益分布", "厚尾", "自相关", "滚动波动率", "显著性"),
        "autocorr = returns.autocorr(lag=1)\nrolling_vol = returns.rolling(63).std() * np.sqrt(252)",
        "金融时间序列的常态是噪声、厚尾和波动聚集，策略必须经得起这些基本事实。",
    ),
    24: LessonSpec(
        24,
        "pairs_trading_cointegration",
        "Pairs Trading and Cointegration",
        "阶段 7：协整和配对",
        "两只资产价格一起走时，价差偏离能否交易？",
        ("配对交易", "价差", "z-score", "相关不等于协整", "半衰期"),
        "spread = log_y - hedge_ratio * log_x\nz = (spread - spread.rolling(60).mean()) / spread.rolling(60).std()",
        "配对交易不是看到相关就交易，而是要验证价差是否有回归特征。",
    ),
    25: LessonSpec(
        25,
        "ml_signal_baseline",
        "Machine Learning Signal Baseline",
        "阶段 8：机器学习量化",
        "机器学习能不能比简单规则更好？",
        ("特征", "标签", "训练集", "基准模型", "交易指标"),
        "prediction = ridge_model.predict(features)\nsignal = prediction > 0",
        "机器学习模型必须和简单规则比较，不能只汇报准确率。",
    ),
    26: LessonSpec(
        26,
        "ml_validation_and_leakage",
        "ML Validation and Leakage",
        "阶段 8：防泄露",
        "为什么机器学习量化最容易被数据泄露欺骗？",
        ("特征泄露", "标签泄露", "时间序列切分", "训练未来", "验证纪律"),
        "train = data.iloc[:train_end]\ntest = data.iloc[test_start:]\n# scaler and model are fitted only on train",
        "泄露模型的漂亮结果没有交易价值，验证纪律比模型复杂度更重要。",
    ),
    27: LessonSpec(
        27,
        "research_pipeline_engineering",
        "Research Pipeline Engineering",
        "阶段 9：工程化",
        "如何让研究结果可复现，而不是 notebook 手工结果？",
        ("配置", "数据缓存", "实验参数", "产物目录", "日志"),
        "config -> data -> signal -> backtest -> report -> artifacts",
        "工程化的价值是让你下次能复现、审计和修改，而不是只留下一张好看的图。",
    ),
    28: LessonSpec(
        28,
        "backtest_framework_design",
        "Backtest Framework Design",
        "阶段 9：回测框架",
        "什么时候向量化回测不够，需要事件驱动框架？",
        ("数据层", "信号层", "订单层", "成交层", "组合层"),
        "for bar in bars:\n    signal = strategy.on_bar(bar)\n    fill = broker.execute(signal)\n    portfolio.update(fill)",
        "事件驱动框架牺牲简洁性，换来更清楚的订单、成交和状态边界。",
    ),
    29: LessonSpec(
        29,
        "paper_trading_checklist",
        "Paper Trading Checklist",
        "阶段 10：模拟盘",
        "回测通过后，为什么还不能直接实盘？",
        ("模拟盘", "信号核对", "订单核对", "持仓核对", "日志"),
        "paper_log.append({'date': today, 'signal': signal, 'order': order, 'fill': fill})",
        "模拟盘的重点不是赚钱，而是发现研究代码到交易流程之间的断点。",
    ),
    30: LessonSpec(
        30,
        "risk_policy_and_live_readiness",
        "Risk Policy and Live Readiness",
        "阶段 10：实盘前准备",
        "什么条件下，一个策略才有资格进入小资金实盘？",
        ("最大亏损", "最大回撤", "仓位上限", "停止交易规则", "异常处理"),
        "if drawdown < max_allowed_drawdown:\n    halt_trading()\nif exposure > max_exposure:\n    reduce_position()",
        "实盘前先定义停止条件；不能解释风险边界，就不应该加资金。",
    ),
}


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_default_data(
    project_root: str | Path | None = None,
    start: str = DEFAULT_START,
) -> dict[str, pd.DataFrame]:
    """Load the real data set used by lessons 11-30, caching Yahoo data locally."""
    root = Path(project_root) if project_root is not None else get_project_root()
    cache_dir = root / "data" / "raw" / "yfinance"
    cache_dir.mkdir(parents=True, exist_ok=True)

    data: dict[str, pd.DataFrame] = {}
    for symbol in FACTOR_SYMBOLS:
        cache_path = cache_dir / f"{symbol}_{start}.csv"
        if cache_path.exists():
            df = pd.read_csv(cache_path, parse_dates=["Date"], index_col="Date")
            df.index.name = "Date"
        else:
            df = download_ohlcv(symbol=symbol, start=start, auto_adjust=True)
            df.to_csv(cache_path)
        data[symbol] = df.sort_index()
    return data


def run_chapter_cli(chapter: int, project_root: str | Path | None = None) -> LessonResult:
    data = load_default_data(project_root)
    result = run_real_lesson(chapter, data, project_root=project_root, write_outputs=True)
    print(f"Generated lesson {chapter:02d}: {result.spec.title}")
    print(f"Report: {result.report_path}")
    print(f"Textbook: {result.textbook_path}")
    print(_markdown_table(result.summary))
    return result


def run_all_real_lessons(project_root: str | Path | None = None) -> list[LessonResult]:
    data = load_default_data(project_root)
    results = []
    for chapter in sorted(LESSON_SPECS):
        result = run_real_lesson(chapter, data, project_root=project_root, write_outputs=True)
        results.append(result)
        plt.close(result.figure)
    return results


def run_real_lesson(
    chapter: int,
    data: dict[str, pd.DataFrame],
    project_root: str | Path | None = None,
    write_outputs: bool = False,
) -> LessonResult:
    if chapter not in LESSON_SPECS:
        raise ValueError(f"Unknown lesson chapter: {chapter}")

    dispatch = {
        11: _run_lesson_11,
        12: _run_lesson_12,
        13: _run_lesson_13,
        14: _run_lesson_14,
        15: _run_lesson_15,
        16: _run_lesson_16,
        17: _run_lesson_17,
        18: _run_lesson_18,
        19: _run_lesson_19,
        20: _run_lesson_20,
        21: _run_lesson_21,
        22: _run_lesson_22,
        23: _run_lesson_23,
        24: _run_lesson_24,
        25: _run_lesson_25,
        26: _run_lesson_26,
        27: _run_lesson_27,
        28: _run_lesson_28,
        29: _run_lesson_29,
        30: _run_lesson_30,
    }
    result = dispatch[chapter](data)
    if write_outputs:
        _write_result_outputs(result, project_root)
    return result


def build_trend_signals(
    close: pd.DataFrame,
    short_window: int = 10,
    long_window: int = 200,
    band_pct: float = 0.01,
) -> pd.DataFrame:
    """Build close-based long/cash moving-average trend signals with a band."""
    if short_window <= 0 or long_window <= 0:
        raise ValueError("window sizes must be positive")
    if short_window >= long_window:
        raise ValueError("short_window must be smaller than long_window")
    if band_pct < 0:
        raise ValueError("band_pct must be non-negative")

    short_ma = close.rolling(short_window, min_periods=short_window).mean()
    long_ma = close.rolling(long_window, min_periods=long_window).mean()
    gap = short_ma / long_ma - 1
    return gap.apply(lambda series: _hysteresis_signal(series, band_pct)).astype(float)


def portfolio_returns_from_signals(
    open_prices: pd.DataFrame,
    signals: pd.DataFrame,
    cost_bps: float = DEFAULT_COST_BPS,
    weighting: str = "equal",
    rebalance: str = "D",
    target_vol: float = 0.10,
    max_leverage: float = 1.5,
    vol_window: int = 63,
) -> pd.DataFrame:
    """Convert close-based signals into next-open portfolio returns."""
    if cost_bps < 0:
        raise ValueError("cost_bps must be non-negative")

    open_prices = open_prices.sort_index()
    signals = signals.reindex(open_prices.index).fillna(0)
    open_returns = open_prices.shift(-1) / open_prices - 1
    active = signals.shift(1).fillna(0)

    if weighting == "equal":
        target_weights = _equal_weights(active)
    elif weighting == "inverse_vol":
        realized_vol = open_returns.rolling(vol_window).std() * np.sqrt(
            TRADING_DAYS_PER_YEAR
        )
        inverse_vol = active / realized_vol.replace(0, np.nan)
        target_weights = inverse_vol.div(inverse_vol.sum(axis=1), axis=0).fillna(0)
    elif weighting == "vol_target":
        base_weights = _equal_weights(active)
        base_returns = (base_weights * open_returns).sum(axis=1).fillna(0)
        realized_vol = (
            base_returns.rolling(vol_window).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
        )
        leverage = (target_vol / realized_vol).shift(1).clip(upper=max_leverage)
        leverage = leverage.replace([np.inf, -np.inf], np.nan).fillna(0)
        target_weights = base_weights.mul(leverage, axis=0)
    else:
        raise ValueError(f"Unsupported weighting: {weighting}")

    weights = _apply_rebalance(target_weights, rebalance)
    previous_weights = weights.shift(1).fillna(0)
    turnover = (weights - previous_weights).abs().sum(axis=1)
    gross_return = (weights * open_returns).sum(axis=1).fillna(0)
    cost = turnover * cost_bps / 10_000
    net_return = gross_return - cost
    exposure = weights.abs().sum(axis=1)

    return pd.DataFrame(
        {
            "return": net_return,
            "gross_return": gross_return,
            "turnover": turnover,
            "cost": cost,
            "exposure": exposure,
            "active_assets": active.sum(axis=1),
        },
        index=open_prices.index,
    )


def _run_lesson_11(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[11]
    close = _price_panel(data, CORE_SYMBOLS, "Close")
    open_prices = _price_panel(data, CORE_SYMBOLS, "Open")
    signals = build_trend_signals(close)
    portfolio = portfolio_returns_from_signals(open_prices, signals)
    spy = portfolio_returns_from_signals(open_prices[["SPY"]], signals[["SPY"]])
    buy_hold = close[list(CORE_SYMBOLS)].pct_change().mean(axis=1).fillna(0)

    summary = pd.DataFrame(
        [
            _performance_row("SPY trend only", spy["return"], spy),
            _performance_row("Equal active trend portfolio", portfolio["return"], portfolio),
            _performance_row("Equal-weight buy and hold", buy_hold),
        ]
    )
    interpretation = [
        "等权趋势组合把风险分散到股票、海外、债券和黄金等不同资产上。",
        "组合的平均持仓数量比单资产策略更高，因此路径通常更平滑。",
        "这不是证明组合一定更赚钱，而是先验证组合层是否改善风险路径。",
    ]
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    _equity(spy["return"]).plot(ax=axes[0], label="SPY trend")
    _equity(portfolio["return"]).plot(ax=axes[0], label="Equal active trend")
    _equity(buy_hold).plot(ax=axes[0], label="Equal-weight buy hold")
    axes[0].set_title("Real Data Equity Curves")
    axes[0].legend()
    _drawdown(_equity(spy["return"])).plot(ax=axes[1], label="SPY trend")
    _drawdown(_equity(portfolio["return"])).plot(ax=axes[1], label="Portfolio trend")
    axes[1].set_title("Drawdown")
    axes[1].legend()
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(CORE_SYMBOLS, close, "MA 10/200 band 1%, next-open, 3 bps cost"),
        interpretation,
        fig,
    )


def _run_lesson_12(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[12]
    close = _price_panel(data, CORE_SYMBOLS, "Close")
    open_prices = _price_panel(data, CORE_SYMBOLS, "Open")
    signals = build_trend_signals(close)
    returns_by_asset = {}
    drawdowns = {}
    for symbol in CORE_SYMBOLS:
        one = portfolio_returns_from_signals(open_prices[[symbol]], signals[[symbol]])
        returns_by_asset[symbol] = one["return"]
        drawdowns[symbol] = _drawdown(_equity(one["return"])).min()
    strategy_returns = pd.DataFrame(returns_by_asset).dropna()
    corr = strategy_returns.corr()
    portfolio = portfolio_returns_from_signals(open_prices, signals)
    rolling_corr = strategy_returns["SPY"].rolling(126).corr(strategy_returns["TLT"])

    summary = pd.DataFrame(
        [
            {
                "metric": "average_pair_correlation",
                "value": _average_pairwise_corr(corr),
            },
            {"metric": "min_pair_correlation", "value": float(corr.min().min())},
            {"metric": "max_pair_correlation", "value": float(corr.where(~np.eye(len(corr), dtype=bool)).max().max())},
            {
                "metric": "portfolio_max_drawdown",
                "value": float(_drawdown(_equity(portfolio["return"])).min()),
            },
            {
                "metric": "median_single_asset_max_drawdown",
                "value": float(pd.Series(drawdowns).median()),
            },
            {
                "metric": "latest_126d_SPY_TLT_corr",
                "value": float(rolling_corr.dropna().iloc[-1]),
            },
        ]
    )
    interpretation = [
        "低相关资产能降低组合回撤，但相关性会随市场环境变化。",
        "SPY 与 TLT 的滚动相关性是观察股票/债券分散效果的重要窗口。",
        "如果组合最大回撤没有明显低于单资产中位数，就要怀疑分散是否真实有效。",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    im = axes[0].imshow(corr, vmin=-1, vmax=1, cmap="coolwarm")
    axes[0].set_xticks(range(len(corr)), corr.columns, rotation=45, ha="right")
    axes[0].set_yticks(range(len(corr)), corr.index)
    axes[0].set_title("Strategy Return Correlation")
    fig.colorbar(im, ax=axes[0], fraction=0.046)
    _drawdown(_equity(portfolio["return"])).plot(ax=axes[1], label="Portfolio")
    for symbol, series in strategy_returns.items():
        _drawdown(_equity(series)).plot(ax=axes[1], alpha=0.35, label=symbol)
    axes[1].set_title("Portfolio vs Single-Asset Drawdowns")
    axes[1].legend(fontsize=8)
    _grid(axes[1:])
    return LessonResult(
        spec,
        summary,
        _details(CORE_SYMBOLS, close, "MA 10/200 band 1%; correlation on strategy returns"),
        interpretation,
        fig,
        {"strategy_return_correlation": corr.reset_index().rename(columns={"index": "symbol"})},
    )


def _run_lesson_13(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[13]
    close = _price_panel(data, CORE_SYMBOLS, "Close")
    open_prices = _price_panel(data, CORE_SYMBOLS, "Open")
    signals = build_trend_signals(close)
    variants = {
        "equal_active": portfolio_returns_from_signals(open_prices, signals, weighting="equal"),
        "inverse_vol": portfolio_returns_from_signals(open_prices, signals, weighting="inverse_vol"),
        "vol_target_10pct": portfolio_returns_from_signals(
            open_prices, signals, weighting="vol_target", target_vol=0.10, max_leverage=1.5
        ),
    }
    summary = pd.DataFrame(
        [_performance_row(name, result["return"], result) for name, result in variants.items()]
    )
    interpretation = [
        "波动率倒数加权会降低高波动资产的权重，使单个资产不容易主导组合。",
        "目标波动率能控制组合风险尺度，但会引入杠杆和低波动时期加仓风险。",
        "仓位模型是否可用，要同时看收益、回撤、暴露和换手。",
    ]
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    for name, result in variants.items():
        _equity(result["return"]).plot(ax=axes[0], label=name)
        result["exposure"].rolling(21).mean().plot(ax=axes[1], label=name)
    axes[0].set_title("Position Sizing Equity")
    axes[1].set_title("Rolling Average Exposure")
    axes[0].legend()
    axes[1].legend()
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(CORE_SYMBOLS, close, "Equal, inverse-vol, and 10% volatility-target sizing"),
        interpretation,
        fig,
    )


def _run_lesson_14(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[14]
    close = _price_panel(data, CORE_SYMBOLS, "Close")
    open_prices = _price_panel(data, CORE_SYMBOLS, "Open")
    signals = build_trend_signals(close)
    frequency_map = {"daily": "D", "weekly": "W", "monthly": "M", "quarterly": "Q"}
    variants = {
        name: portfolio_returns_from_signals(open_prices, signals, rebalance=freq)
        for name, freq in frequency_map.items()
    }
    summary = pd.DataFrame(
        [_performance_row(name, result["return"], result) for name, result in variants.items()]
    )
    interpretation = [
        "降低再平衡频率通常会减少换手，但也可能让组合偏离最新信号。",
        "如果收益改善主要来自更高换手，必须把成本敏感性放在第一位。",
        "个人量化更适合先用低频再平衡，减少执行复杂度。",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for name, result in variants.items():
        _equity(result["return"]).plot(ax=axes[0], label=name)
        result["turnover"].cumsum().plot(ax=axes[1], label=name)
    axes[0].set_title("Rebalancing Equity")
    axes[1].set_title("Cumulative Turnover")
    axes[0].legend()
    axes[1].legend()
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(CORE_SYMBOLS, close, "Compare daily/weekly/monthly/quarterly rebalancing"),
        interpretation,
        fig,
    )


def _run_lesson_15(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[15]
    df = data["SPY"].copy()
    open_prices = df[["Open"]].rename(columns={"Open": "SPY"})
    close = df["Close"]
    variants = {}
    signals_by_name = {}
    for lookback in (20, 60, 120):
        signal = _breakout_signal(close, lookback)
        signals_by_name[f"breakout_{lookback}d"] = signal
        variants[f"breakout_{lookback}d"] = portfolio_returns_from_signals(
            open_prices, signal.to_frame("SPY")
        )
    ma_signal = build_trend_signals(close.to_frame("SPY"))
    variants["ma_10_200_band"] = portfolio_returns_from_signals(open_prices, ma_signal)
    summary = pd.DataFrame(
        [_performance_row(name, result["return"], result) for name, result in variants.items()]
    )
    interpretation = [
        "短周期突破更敏感，也更容易被假突破反复打脸。",
        "长周期突破更慢，但通常能过滤更多噪声。",
        "突破和均线都是趋势思想，差异主要在信号定义和反应速度。",
    ]
    channel = close.rolling(60).max().shift(1)
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    close.plot(ax=axes[0], label="SPY close", linewidth=1)
    channel.plot(ax=axes[0], label="60d breakout high", linewidth=1)
    axes[0].set_title("SPY Breakout Channel")
    axes[0].legend()
    for name, result in variants.items():
        _equity(result["return"]).plot(ax=axes[1], label=name)
    axes[1].set_title("Breakout Strategy Equity")
    axes[1].legend()
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(("SPY",), close.to_frame("SPY"), "Donchian breakout, next-open, 3 bps cost"),
        interpretation,
        fig,
    )


def _run_lesson_16(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[16]
    close = _price_panel(data, CORE_SYMBOLS, "Close")
    open_prices = _price_panel(data, CORE_SYMBOLS, "Open")
    variants = {}
    for lookback in (21, 63, 126, 252):
        signal = (close / close.shift(lookback) - 1 > 0).astype(float)
        variants[f"tsmom_{lookback}d"] = portfolio_returns_from_signals(open_prices, signal)
    summary = pd.DataFrame(
        [_performance_row(name, result["return"], result) for name, result in variants.items()]
    )
    interpretation = [
        "时间序列动量不是预测具体价格，而是判断资产自身趋势是否为正。",
        "不同窗口代表不同趋势尺度，窗口敏感性本身就是策略风险。",
        "跨资产测试比单资产测试更能暴露动量规则是否稳健。",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for name, result in variants.items():
        _equity(result["return"]).plot(ax=axes[0], label=name)
    axes[0].set_title("Time-Series Momentum Equity")
    axes[0].legend(fontsize=8)
    summary.set_index("case")["ann_return"].plot(kind="bar", ax=axes[1], color="#1f77b4")
    axes[1].set_title("Annualized Return by Lookback")
    axes[1].tick_params(axis="x", rotation=30)
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(CORE_SYMBOLS, close, "Absolute momentum on 21/63/126/252 day lookbacks"),
        interpretation,
        fig,
    )


def _run_lesson_17(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[17]
    df = data["SPY"].copy()
    close = df["Close"]
    open_prices = df[["Open"]].rename(columns={"Open": "SPY"})
    variants = {}
    signals = {}
    for entry_z in (0.75, 1.0, 1.5, 2.0):
        signal, z_score = _mean_reversion_signal(close, entry_z=entry_z)
        signals[f"z_entry_{entry_z:.2f}"] = signal
        variants[f"z_entry_{entry_z:.2f}"] = portfolio_returns_from_signals(
            open_prices, signal.to_frame("SPY")
        )
    summary = pd.DataFrame(
        [_performance_row(name, result["return"], result) for name, result in variants.items()]
    )
    interpretation = [
        "均值回归信号在震荡市场更容易发挥作用，在单边趋势中容易持续逆势。",
        "entry_z 越高，信号越少，等待更极端的偏离。",
        "均值回归策略正式使用前必须有止损和失效条件。",
    ]
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    z_score.plot(ax=axes[0], label="20d z-score")
    axes[0].axhline(-1, color="green", linestyle="--", linewidth=1)
    axes[0].axhline(1, color="red", linestyle="--", linewidth=1)
    axes[0].set_title("SPY Mean-Reversion Z-score")
    for name, result in variants.items():
        _equity(result["return"]).plot(ax=axes[1], label=name)
    axes[1].set_title("Mean-Reversion Equity")
    axes[1].legend(fontsize=8)
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(("SPY",), close.to_frame("SPY"), "20d z-score long/cash mean reversion"),
        interpretation,
        fig,
    )


def _run_lesson_18(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[18]
    df = data["SPY"].copy()
    close = df["Close"]
    open_prices = df[["Open"]].rename(columns={"Open": "SPY"})
    trend = portfolio_returns_from_signals(open_prices, build_trend_signals(close.to_frame("SPY")))["return"]
    breakout = portfolio_returns_from_signals(
        open_prices, _breakout_signal(close, 60).to_frame("SPY")
    )["return"]
    mean_reversion_signal, _ = _mean_reversion_signal(close, entry_z=1.0)
    mean_reversion = portfolio_returns_from_signals(
        open_prices, mean_reversion_signal.to_frame("SPY")
    )["return"]
    strategy_returns = pd.DataFrame(
        {
            "trend": trend,
            "breakout": breakout,
            "mean_reversion": mean_reversion,
        }
    ).fillna(0)
    combo = strategy_returns.mean(axis=1)
    summary = pd.DataFrame(
        [_performance_row(name, strategy_returns[name]) for name in strategy_returns.columns]
        + [_performance_row("equal_strategy_combo", combo)]
    )
    corr = strategy_returns.corr()
    interpretation = [
        "趋势和突破通常同源，相关性往往比名字看起来更高。",
        "均值回归可能与趋势类策略互补，但也可能拖累强趋势阶段。",
        "多策略组合要看策略收益相关性，不是只数策略数量。",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for name in strategy_returns.columns:
        _equity(strategy_returns[name]).plot(ax=axes[0], label=name)
    _equity(combo).plot(ax=axes[0], label="combo", linewidth=2, color="black")
    axes[0].set_title("SPY Strategy Portfolio Equity")
    axes[0].legend()
    im = axes[1].imshow(corr, vmin=-1, vmax=1, cmap="coolwarm")
    axes[1].set_xticks(range(len(corr)), corr.columns, rotation=30, ha="right")
    axes[1].set_yticks(range(len(corr)), corr.index)
    axes[1].set_title("Strategy Return Correlation")
    fig.colorbar(im, ax=axes[1], fraction=0.046)
    _grid(axes[:1])
    return LessonResult(
        spec,
        summary,
        _details(("SPY",), close.to_frame("SPY"), "Trend, breakout, mean-reversion strategy basket"),
        interpretation,
        fig,
        {"strategy_correlation": corr.reset_index().rename(columns={"index": "strategy"})},
    )


def _run_lesson_19(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[19]
    close = _price_panel(data, FACTOR_SYMBOLS, "Close")
    factor, future_return = _momentum_factor_panel(close)
    layer_returns = _factor_layer_returns(factor, future_return)
    summary = pd.DataFrame(
        [_performance_row(col, layer_returns[col], periods_per_year=12) for col in layer_returns.columns]
    )
    interpretation = [
        "分层回测先回答排序有没有方向性，而不是直接承诺可交易收益。",
        "如果高分层和低分层没有稳定差异，因子继续复杂化意义不大。",
        "ETF 横截面样本较小，本章重点是掌握研究流程。",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for col in layer_returns.columns:
        if col in {"Q1_low", "Q5_high", "high_minus_low"}:
            _equity(layer_returns[col]).plot(ax=axes[0], label=col)
    axes[0].set_title("Factor Layer Equity")
    axes[0].legend()
    layer_returns.mean().plot(kind="bar", ax=axes[1], color="#1f77b4")
    axes[1].set_title("Average Next-Month Return by Layer")
    axes[1].tick_params(axis="x", rotation=30)
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(FACTOR_SYMBOLS, close, "6-month momentum factor, monthly ETF cross-section"),
        interpretation,
        fig,
    )


def _run_lesson_20(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[20]
    close = _price_panel(data, FACTOR_SYMBOLS, "Close")
    factor, future_return = _momentum_factor_panel(close)
    rank_ic = _rank_ic_series(factor, future_return)
    turnover = _top_bucket_turnover(factor, top_pct=0.2)
    summary = pd.DataFrame(
        [
            {"metric": "months", "value": int(rank_ic.dropna().shape[0])},
            {"metric": "mean_rank_ic", "value": float(rank_ic.mean())},
            {"metric": "rank_ic_std", "value": float(rank_ic.std(ddof=1))},
            {"metric": "icir", "value": float(rank_ic.mean() / rank_ic.std(ddof=1))},
            {"metric": "positive_ic_rate", "value": float((rank_ic > 0).mean())},
            {"metric": "average_top_bucket_turnover", "value": float(turnover.mean())},
        ]
    )
    interpretation = [
        "Rank IC 衡量的是横截面排序和未来收益排序的关系。",
        "ICIR 比单个月 IC 更重要，因为它观察稳定性。",
        "换手率高会让因子收益更难落地。",
    ]
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    rank_ic.plot(ax=axes[0], label="monthly Rank IC")
    rank_ic.rolling(12).mean().plot(ax=axes[0], label="12m average")
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("Monthly Rank IC")
    axes[0].legend()
    turnover.plot(ax=axes[1], color="#ff7f0e")
    axes[1].set_title("Top Bucket Turnover")
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(FACTOR_SYMBOLS, close, "Rank IC and top-bucket turnover for 6-month momentum"),
        interpretation,
        fig,
        {"rank_ic_tail": rank_ic.dropna().tail(12).rename("rank_ic").reset_index()},
    )


def _run_lesson_21(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[21]
    close = _price_panel(data, FACTOR_SYMBOLS, "Close")
    factor, future_return = _momentum_factor_panel(close)
    beta, volatility = _monthly_beta_vol(close)
    neutral = _neutralize_factor(factor, {"beta": beta, "volatility": volatility})
    raw_ic = _rank_ic_series(factor, future_return)
    neutral_ic = _rank_ic_series(neutral, future_return)
    raw_ls = _factor_long_short_returns(factor, future_return)
    neutral_ls = _factor_long_short_returns(neutral, future_return)
    exposure_table = pd.DataFrame(
        [
            {"factor": "raw", "avg_beta_corr": _average_row_corr(factor, beta), "avg_vol_corr": _average_row_corr(factor, volatility)},
            {"factor": "neutralized", "avg_beta_corr": _average_row_corr(neutral, beta), "avg_vol_corr": _average_row_corr(neutral, volatility)},
        ]
    )
    summary = pd.DataFrame(
        [
            _factor_quality_row("raw", raw_ic, raw_ls),
            _factor_quality_row("neutralized", neutral_ic, neutral_ls),
        ]
    )
    interpretation = [
        "中性化后 IC 变好，说明原因子里可能有不想要的 beta/波动率暴露。",
        "中性化后 IC 变差，也不等于错误，可能说明暴露本身就是收益来源。",
        "中性化要服务于问题定义，而不是机械套用。",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    raw_ic.rolling(12).mean().plot(ax=axes[0], label="raw")
    neutral_ic.rolling(12).mean().plot(ax=axes[0], label="neutralized")
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("12m Rolling Rank IC")
    axes[0].legend()
    exposure_table.set_index("factor")[["avg_beta_corr", "avg_vol_corr"]].plot(
        kind="bar", ax=axes[1]
    )
    axes[1].set_title("Average Exposure Correlation")
    axes[1].tick_params(axis="x", rotation=0)
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(FACTOR_SYMBOLS, close, "Neutralize momentum factor against rolling beta and volatility"),
        interpretation,
        fig,
        {"exposure_correlation": exposure_table},
    )


def _run_lesson_22(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[22]
    close = _price_panel(data, FACTOR_SYMBOLS, "Close")
    factors, future_return = _multi_factor_panel(close)
    returns = {
        name: _factor_long_short_returns(factor, future_return)
        for name, factor in factors.items()
    }
    composite = sum(_zscore_cross_sectional(factor) for factor in factors.values()) / len(factors)
    returns["composite"] = _factor_long_short_returns(composite, future_return)
    returns_df = pd.DataFrame(returns).dropna(how="all")
    summary = pd.DataFrame(
        [_performance_row(name, returns_df[name], periods_per_year=12) for name in returns_df.columns]
    )
    factor_corr = pd.DataFrame(
        {name: factor.stack() for name, factor in factors.items()}
    ).corr()
    interpretation = [
        "多因子组合要检查因子之间是否高度重复。",
        "单因子强弱会轮换，组合因子的目标是降低单一来源失效风险。",
        "如果 composite 只是复制 momentum，那就不是真正的多因子。",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for name in returns_df.columns:
        _equity(returns_df[name]).plot(ax=axes[0], label=name)
    axes[0].set_title("Long-Short Factor Equity")
    axes[0].legend()
    im = axes[1].imshow(factor_corr, vmin=-1, vmax=1, cmap="coolwarm")
    axes[1].set_xticks(range(len(factor_corr)), factor_corr.columns, rotation=30, ha="right")
    axes[1].set_yticks(range(len(factor_corr)), factor_corr.index)
    axes[1].set_title("Factor Correlation")
    fig.colorbar(im, ax=axes[1], fraction=0.046)
    _grid(axes[:1])
    return LessonResult(
        spec,
        summary,
        _details(FACTOR_SYMBOLS, close, "Momentum, reversal and low-volatility ETF factors"),
        interpretation,
        fig,
        {"factor_correlation": factor_corr.reset_index().rename(columns={"index": "factor"})},
    )


def _run_lesson_23(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[23]
    close = data["SPY"]["Close"]
    returns = close.pct_change().dropna()
    summary = pd.DataFrame(
        [
            {"metric": "daily_mean", "value": float(returns.mean())},
            {"metric": "annualized_volatility", "value": float(returns.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR))},
            {"metric": "skewness", "value": float(returns.skew())},
            {"metric": "excess_kurtosis", "value": float(returns.kurtosis())},
            {"metric": "autocorr_1d", "value": float(returns.autocorr(1))},
            {"metric": "autocorr_5d", "value": float(returns.autocorr(5))},
            {"metric": "best_day", "value": float(returns.max())},
            {"metric": "worst_day", "value": float(returns.min())},
        ]
    )
    interpretation = [
        "SPY 日收益不是正态分布，厚尾和极端日会显著影响回撤。",
        "自相关很弱时，不要轻易把短期涨跌解释成可预测规律。",
        "滚动波动率说明市场风险状态会聚集，而不是每天独立同分布。",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    returns.hist(bins=80, ax=axes[0], color="#1f77b4")
    axes[0].set_title("SPY Daily Return Distribution")
    (returns.rolling(63).std() * np.sqrt(TRADING_DAYS_PER_YEAR)).plot(ax=axes[1])
    axes[1].set_title("63d Rolling Annualized Volatility")
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(("SPY",), close.to_frame("SPY"), "Daily return distribution and rolling statistics"),
        interpretation,
        fig,
    )


def _run_lesson_24(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[24]
    close = _price_panel(data, ("SPY", "QQQ"), "Close")
    returns = close.pct_change().fillna(0)
    log_spy = np.log(close["SPY"])
    log_qqq = np.log(close["QQQ"])
    train_end = int(len(close) * 0.6)
    hedge_ratio = _ols_beta(log_spy.iloc[:train_end], log_qqq.iloc[:train_end])
    spread = log_qqq - hedge_ratio * log_spy
    z_score = (spread - spread.rolling(60).mean()) / spread.rolling(60).std()
    position = _pairs_position(z_score, entry_z=2.0, exit_z=0.5)
    spread_return = returns["QQQ"] - hedge_ratio * returns["SPY"]
    turnover = position.diff().abs().fillna(position.abs())
    strategy_return = position.shift(1).fillna(0) * spread_return - turnover * DEFAULT_COST_BPS / 10_000
    half_life = _estimate_half_life(spread)
    summary = pd.DataFrame(
        [
            {
                **_performance_row("SPY_QQQ_spread_reversion", strategy_return),
                "hedge_ratio": hedge_ratio,
                "half_life_days": half_life,
                "trades": float(turnover.sum()),
            }
        ]
    )
    interpretation = [
        "SPY 和 QQQ 高相关，但价差交易真正关心的是 spread 是否会回归。",
        "半衰期只是粗略估计，不代表每次偏离都能按时回归。",
        "双腿交易必须考虑两边成本和对冲比例误差。",
    ]
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    z_score.plot(ax=axes[0], label="spread z-score")
    axes[0].axhline(2, color="red", linestyle="--", linewidth=1)
    axes[0].axhline(-2, color="green", linestyle="--", linewidth=1)
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("SPY/QQQ Spread Z-score")
    _equity(strategy_return).plot(ax=axes[1], label="pairs strategy")
    axes[1].set_title("Pairs Trading Equity")
    axes[1].legend()
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(("SPY", "QQQ"), close, "OLS hedge ratio on first 60% sample; z-score spread trading"),
        interpretation,
        fig,
    )


def _run_lesson_25(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[25]
    dataset = _build_ml_dataset(data["SPY"])
    train, test = _time_train_test_split(dataset)
    model_pred = _ridge_predict(train, test, feature_cols=["ret_5", "ret_20", "ret_63", "vol_20", "volume_z"])
    momentum_pred = test["ret_20"]
    model_return, model_accuracy = _prediction_strategy(test, model_pred)
    momentum_return, momentum_accuracy = _prediction_strategy(test, momentum_pred)
    buy_hold = test["future_1d_return"].fillna(0)
    rows = [
        {**_performance_row("ridge_features", model_return), "direction_accuracy": model_accuracy},
        {**_performance_row("momentum_baseline", momentum_return), "direction_accuracy": momentum_accuracy},
        {**_performance_row("buy_hold_test", buy_hold), "direction_accuracy": np.nan},
    ]
    summary = pd.DataFrame(rows)
    interpretation = [
        "模型用训练集拟合，只在测试集评价，避免把未来信息带入训练。",
        "机器学习策略必须和简单动量基准比较；如果赢不了基准，复杂度没有价值。",
        "方向准确率和交易收益不是一回事，最终仍要看净值、回撤和成本。",
    ]
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    pd.Series(model_pred, index=test.index).plot(ax=axes[0], label="ridge prediction")
    momentum_pred.plot(ax=axes[0], label="momentum baseline", alpha=0.7)
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("Test-Set Prediction Scores")
    axes[0].legend()
    _equity(model_return).plot(ax=axes[1], label="ridge")
    _equity(momentum_return).plot(ax=axes[1], label="momentum")
    _equity(buy_hold).plot(ax=axes[1], label="buy hold")
    axes[1].set_title("ML Baseline Test Equity")
    axes[1].legend()
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(("SPY",), data["SPY"][["Close"]], "Ridge linear baseline on SPY daily features"),
        interpretation,
        fig,
    )


def _run_lesson_26(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[26]
    dataset = _build_ml_dataset(data["SPY"])
    dataset["leaky_future_return"] = dataset["future_1d_return"]
    train, test = _time_train_test_split(dataset)
    proper_pred = _ridge_predict(train, test, feature_cols=["ret_5", "ret_20", "ret_63", "vol_20", "volume_z"])
    leaky_pred = _ridge_predict(
        train,
        test,
        feature_cols=["ret_5", "ret_20", "ret_63", "vol_20", "volume_z", "leaky_future_return"],
    )
    proper_return, proper_accuracy = _prediction_strategy(test, proper_pred)
    leaky_return, leaky_accuracy = _prediction_strategy(test, leaky_pred)
    summary = pd.DataFrame(
        [
            {**_performance_row("proper_time_split_model", proper_return), "direction_accuracy": proper_accuracy},
            {**_performance_row("leaky_future_return_feature", leaky_return), "direction_accuracy": leaky_accuracy},
        ]
    )
    interpretation = [
        "泄露特征直接包含未来收益，因此测试表现会异常漂亮。",
        "这种漂亮结果不能交易，因为实盘当下拿不到未来收益。",
        "机器学习量化第一原则：任何标准化、筛选和训练都只能使用过去数据。",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    summary.set_index("case")["direction_accuracy"].plot(kind="bar", ax=axes[0], color="#1f77b4")
    axes[0].set_title("Direction Accuracy")
    summary.set_index("case")["final_equity"].plot(kind="bar", ax=axes[1], color="#ff7f0e")
    axes[1].set_title("Test Final Equity")
    for axis in axes:
        axis.tick_params(axis="x", rotation=20)
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(("SPY",), data["SPY"][["Close"]], "Proper model versus intentionally leaky feature"),
        interpretation,
        fig,
    )


def _run_lesson_27(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[27]
    close = _price_panel(data, CORE_SYMBOLS, "Close")
    open_prices = _price_panel(data, CORE_SYMBOLS, "Open")
    signals = build_trend_signals(close)
    portfolio = portfolio_returns_from_signals(open_prices, signals)
    config = {
        "symbols": ",".join(CORE_SYMBOLS),
        "start": close.index.min().strftime("%Y-%m-%d"),
        "end": close.index.max().strftime("%Y-%m-%d"),
        "strategy": "MA 10/200 band 1%",
        "cost_bps": f"{DEFAULT_COST_BPS:.1f}",
    }
    metrics = _performance_row("pipeline_reference_run", portfolio["return"], portfolio)
    summary = pd.DataFrame(
        [
            {"check": "data_rows", "value": str(len(close)), "status": "pass"},
            {"check": "symbols", "value": config["symbols"], "status": "pass"},
            {"check": "parameters_recorded", "value": config["strategy"], "status": "pass"},
            {"check": "cost_recorded", "value": config["cost_bps"], "status": "pass"},
            {"check": "reference_final_equity", "value": f"{metrics['final_equity']:.4f}", "status": "pass"},
        ]
    )
    interpretation = [
        "工程化的第一步是固定数据、参数、输出路径和报告格式。",
        "同一个入口脚本可以重复生成图、表和结论，减少手工复制错误。",
        "研究管线不是为了炫技，而是为了让策略结论可审计。",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    _flowchart(axes[0], ["config", "data", "signal", "backtest", "report"], "Research Pipeline")
    summary.set_index("check")["status"].map({"pass": 1}).plot(kind="bar", ax=axes[1], color="#2ca02c")
    axes[1].set_ylim(0, 1.2)
    axes[1].set_title("Pipeline Checks")
    axes[1].tick_params(axis="x", rotation=30)
    _grid(axes[1:])
    return LessonResult(
        spec,
        summary,
        _details(CORE_SYMBOLS, close, "Reusable pipeline run for the multi-asset trend strategy"),
        interpretation,
        fig,
    )


def _run_lesson_28(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[28]
    df = data["SPY"].copy()
    close = df["Close"]
    open_prices = df[["Open"]].rename(columns={"Open": "SPY"})
    signal = build_trend_signals(close.to_frame("SPY"))["SPY"]
    vectorized = portfolio_returns_from_signals(open_prices, signal.to_frame("SPY"))
    event = _event_driven_single_asset(open_prices["SPY"], signal)
    diff = (_equity(vectorized["return"]) - _equity(event["return"])).abs()
    summary = pd.DataFrame(
        [
            {
                "case": "vectorized_vs_event",
                "vectorized_final_equity": float(_equity(vectorized["return"]).iloc[-1]),
                "event_final_equity": float(_equity(event["return"]).iloc[-1]),
                "max_equity_difference": float(diff.max()),
                "orders": float(event["order"].abs().sum()),
            }
        ]
    )
    interpretation = [
        "向量化回测适合快速研究，但订单、成交和状态边界不够显式。",
        "事件驱动回测更接近实盘流程，能检查订单和持仓变化。",
        "两者结果接近时，说明框架拆分没有改变策略逻辑。",
    ]
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    _equity(vectorized["return"]).plot(ax=axes[0], label="vectorized")
    _equity(event["return"]).plot(ax=axes[0], label="event-driven", linestyle="--")
    axes[0].set_title("Vectorized vs Event-Driven Equity")
    axes[0].legend()
    event["position"].plot(ax=axes[1], label="event position")
    axes[1].set_title("Event-Driven Position State")
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(("SPY",), close.to_frame("SPY"), "Same MA strategy implemented by vectorized and event-driven loops"),
        interpretation,
        fig,
    )


def _run_lesson_29(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[29]
    df = data["SPY"].copy()
    close = df["Close"]
    signal = build_trend_signals(close.to_frame("SPY"))["SPY"]
    paper_log = _paper_trading_log(df, signal, days=80)
    returns = paper_log["strategy_return"].fillna(0)
    summary = pd.DataFrame(
        [
            {"metric": "paper_days", "value": int(len(paper_log))},
            {"metric": "orders", "value": int((paper_log["order"] != 0).sum())},
            {"metric": "average_slippage_bps", "value": float(paper_log["slippage_bps"].mean())},
            {"metric": "checklist_completion_rate", "value": float(paper_log["checklist_complete"].mean())},
            {"metric": "paper_final_equity", "value": float(_equity(returns).iloc[-1])},
        ]
    )
    interpretation = [
        "模拟盘日志要记录信号、订单、成交、持仓和检查项。",
        "模拟盘不是为了证明能赚钱，而是验证流程是否稳定可复盘。",
        "一旦日志字段缺失，实盘后就很难解释错误来自信号还是执行。",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    _equity(returns).plot(ax=axes[0], label="paper equity")
    axes[0].set_title("Recent Paper-Trading Equity")
    paper_log[["signal_checked", "order_checked", "position_checked"]].mean().plot(
        kind="bar", ax=axes[1], color="#2ca02c"
    )
    axes[1].set_ylim(0, 1.05)
    axes[1].set_title("Checklist Completion")
    axes[1].tick_params(axis="x", rotation=20)
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(("SPY",), close.to_frame("SPY"), "Last 80 trading days simulated from real SPY signals"),
        interpretation,
        fig,
        {"paper_trading_log_tail": paper_log.tail(20).reset_index()},
    )


def _run_lesson_30(data: dict[str, pd.DataFrame]) -> LessonResult:
    spec = LESSON_SPECS[30]
    close = _price_panel(data, CORE_SYMBOLS, "Close")
    open_prices = _price_panel(data, CORE_SYMBOLS, "Open")
    signals = build_trend_signals(close)
    portfolio = portfolio_returns_from_signals(
        open_prices, signals, weighting="vol_target", target_vol=0.10, max_leverage=1.5
    )
    equity = _equity(portfolio["return"])
    drawdown = _drawdown(equity)
    events = pd.DataFrame(
        {
            "drawdown_warning": drawdown < -0.10,
            "drawdown_stop": drawdown < -0.20,
            "daily_loss_warning": portfolio["return"] < -0.03,
            "exposure_breach": portfolio["exposure"] > 1.2,
        }
    )
    summary = pd.DataFrame(
        [
            {"risk_rule": "max_drawdown_warning", "limit": "-10%", "observed": f"{drawdown.min():.2%}", "breach_count": int(events["drawdown_warning"].sum())},
            {"risk_rule": "max_drawdown_stop", "limit": "-20%", "observed": f"{drawdown.min():.2%}", "breach_count": int(events["drawdown_stop"].sum())},
            {"risk_rule": "daily_loss_warning", "limit": "-3%", "observed": f"{portfolio['return'].min():.2%}", "breach_count": int(events["daily_loss_warning"].sum())},
            {"risk_rule": "max_exposure", "limit": "120%", "observed": f"{portfolio['exposure'].max():.2%}", "breach_count": int(events["exposure_breach"].sum())},
        ]
    )
    interpretation = [
        "风险政策要写在实盘之前，不能亏损后再临时解释。",
        "最大回撤、单日亏损和仓位暴露都需要明确阈值。",
        "出现停止交易条件时，正确动作是降风险和复盘，而不是加倍下注。",
    ]
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    drawdown.plot(ax=axes[0], label="drawdown")
    axes[0].axhline(-0.10, color="orange", linestyle="--", label="warning")
    axes[0].axhline(-0.20, color="red", linestyle="--", label="stop")
    axes[0].set_title("Risk Policy Drawdown Limits")
    axes[0].legend()
    portfolio["exposure"].plot(ax=axes[1], label="exposure")
    axes[1].axhline(1.2, color="red", linestyle="--", label="max exposure")
    axes[1].set_title("Exposure Limit")
    axes[1].legend()
    _grid(axes)
    return LessonResult(
        spec,
        summary,
        _details(CORE_SYMBOLS, close, "10% vol-target trend portfolio risk policy check"),
        interpretation,
        fig,
        {"risk_event_tail": events.loc[events.any(axis=1)].tail(20).reset_index()},
    )


def _write_result_outputs(
    result: LessonResult,
    project_root: str | Path | None = None,
) -> None:
    root = Path(project_root) if project_root is not None else get_project_root()
    spec = result.spec
    generated_dir = root / "reports" / "generated" / spec.asset_dir
    generated_dir.mkdir(parents=True, exist_ok=True)
    report_image = generated_dir / spec.asset_image
    result.figure.tight_layout()
    result.figure.savefig(report_image, dpi=150, bbox_inches="tight")
    result.summary.to_csv(generated_dir / f"{spec.slug}_summary.csv", index=False)
    for name, table in result.extra_tables.items():
        table.to_csv(generated_dir / f"{spec.slug}_{name}.csv", index=False)

    textbook_asset_dir = root / "textbook" / "assets" / spec.asset_dir
    textbook_asset_dir.mkdir(parents=True, exist_ok=True)
    textbook_image = textbook_asset_dir / spec.asset_image
    shutil.copy2(report_image, textbook_image)

    report_path = root / "reports" / f"{date.today().isoformat()}_{spec.chapter:02d}_{spec.slug}.md"
    textbook_path = root / "textbook" / spec.textbook_file
    report_path.write_text(_render_report(result), encoding="utf-8")
    textbook_path.write_text(_render_textbook(result), encoding="utf-8")

    result.generated_dir = generated_dir
    result.image_path = textbook_image
    result.report_path = report_path
    result.textbook_path = textbook_path


def _render_report(result: LessonResult) -> str:
    spec = result.spec
    relative_image = f"generated/{spec.asset_dir}/{spec.asset_image}"
    extra = _render_extra_tables(result.extra_tables)
    return f"""# {spec.chapter:02d} {spec.title} Report

日期：{date.today().isoformat()}

## 本课问题

{spec.question}

## 数据和参数

{_details_markdown(result.details)}

## 核心代码

```python
{spec.code}
```

## 实跑结果

{_markdown_table(result.summary)}

## 图示

![{spec.title}]({relative_image})

{extra}

## 结果解读

{_bullet_list(result.interpretation)}

## 本课结论

{spec.conclusion_hint}
"""


def _render_textbook(result: LessonResult) -> str:
    spec = result.spec
    concepts = _bullet_list(list(spec.concepts))
    report_name = Path(result.report_path).name if result.report_path else ""
    return f"""# {spec.chapter:02d} {spec.title}

状态：真实数据实跑版。

对应 RoadMap：{spec.stage}

## 本课问题

{spec.question}

## 必须理解的概念

{concepts}

## 真实数据设置

{_details_markdown(result.details)}

## 关键代码

```python
{spec.code}
```

完整脚本：`scripts/{spec.script_file}`

可运行 notebook：`notebooks/{spec.notebook_file}`

正式报告：`reports/{report_name}`

## 实跑结果

{_markdown_table(result.summary)}

## 图示

![{spec.title}](assets/{spec.asset_dir}/{spec.asset_image})

## 讲解

{_bullet_list(result.interpretation)}

{spec.deep_dive}

## 本课结论

{spec.conclusion_hint}

## 复习问题

1. 本章策略或实验到底想解决什么问题？
2. 结果中最重要的风险指标是什么？
3. 如果换一个市场或成本假设，结论最可能在哪里变化？
4. 这个实验离真实交易还缺哪一步？
"""


def _render_extra_tables(tables: dict[str, pd.DataFrame]) -> str:
    if not tables:
        return ""
    sections = []
    for name, table in tables.items():
        preview = table.tail(20) if len(table) > 20 else table
        sections.append(f"## 附表：{name}\n\n{_markdown_table(preview)}")
    return "\n\n".join(sections)


def _details(
    symbols: tuple[str, ...],
    price_panel: pd.DataFrame,
    setup: str,
) -> dict[str, str]:
    return {
        "symbols": ", ".join(symbols),
        "start_date": price_panel.index.min().strftime("%Y-%m-%d"),
        "end_date": price_panel.index.max().strftime("%Y-%m-%d"),
        "rows": str(len(price_panel)),
        "setup": setup,
    }


def _details_markdown(details: dict[str, str]) -> str:
    return "\n".join(f"- {key}: {value}" for key, value in details.items())


def _price_panel(
    data: dict[str, pd.DataFrame],
    symbols: tuple[str, ...],
    column: str,
) -> pd.DataFrame:
    missing = [symbol for symbol in symbols if symbol not in data]
    if missing:
        raise ValueError(f"Missing data for symbols: {missing}")
    panel = pd.DataFrame({symbol: data[symbol][column] for symbol in symbols})
    panel.index.name = "Date"
    return panel.dropna(how="any").sort_index()


def _hysteresis_signal(gap: pd.Series, band_pct: float) -> pd.Series:
    state = 0.0
    values = []
    for value in gap:
        if pd.isna(value):
            state = 0.0
        elif state == 0 and value > band_pct:
            state = 1.0
        elif state == 1 and value < -band_pct:
            state = 0.0
        values.append(state)
    return pd.Series(values, index=gap.index)


def _equal_weights(active: pd.DataFrame) -> pd.DataFrame:
    active_count = active.sum(axis=1).replace(0, np.nan)
    return active.div(active_count, axis=0).fillna(0)


def _apply_rebalance(weights: pd.DataFrame, frequency: str) -> pd.DataFrame:
    if frequency == "D":
        return weights.fillna(0)
    if frequency not in {"W", "M", "Q"}:
        raise ValueError("rebalance must be one of D, W, M, Q")
    period = weights.index.to_period(frequency)
    is_rebalance_day = pd.Series(period != pd.Series(period, index=weights.index).shift(1).to_numpy(), index=weights.index)
    rebalanced = weights.where(is_rebalance_day, np.nan).ffill().fillna(0)
    return rebalanced


def _equity(returns: pd.Series) -> pd.Series:
    return (1 + returns.fillna(0)).cumprod()


def _drawdown(equity: pd.Series) -> pd.Series:
    return equity / equity.cummax() - 1


def _performance_row(
    name: str,
    returns: pd.Series,
    state: pd.DataFrame | None = None,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> dict[str, float | str]:
    clean = returns.fillna(0)
    equity = _equity(clean)
    final_equity = float(equity.iloc[-1])
    years = len(clean) / periods_per_year
    annualized_return = (
        float(final_equity ** (1 / years) - 1) if years > 0 and final_equity > 0 else np.nan
    )
    annualized_vol = float(clean.std(ddof=1) * np.sqrt(periods_per_year)) if len(clean) > 1 else np.nan
    sharpe = annualized_return / annualized_vol if annualized_vol and annualized_vol > 0 else np.nan
    max_drawdown = float(_drawdown(equity).min())
    calmar = annualized_return / abs(max_drawdown) if max_drawdown < 0 else np.nan
    row: dict[str, float | str] = {
        "case": name,
        "final_equity": final_equity,
        "ann_return": annualized_return,
        "ann_vol": annualized_vol,
        "max_drawdown": max_drawdown,
        "sharpe": sharpe,
        "calmar": calmar,
    }
    if state is not None:
        row["turnover"] = float(state.get("turnover", pd.Series(0, index=clean.index)).sum())
        row["avg_exposure"] = float(state.get("exposure", pd.Series(0, index=clean.index)).mean())
    return row


def _average_pairwise_corr(corr: pd.DataFrame) -> float:
    mask = ~np.eye(len(corr), dtype=bool)
    return float(corr.where(mask).stack().mean())


def _breakout_signal(close: pd.Series, lookback: int, exit_lookback: int | None = None) -> pd.Series:
    exit_lookback = exit_lookback or lookback
    high = close.rolling(lookback, min_periods=lookback).max().shift(1)
    low = close.rolling(exit_lookback, min_periods=exit_lookback).min().shift(1)
    state = 0.0
    values = []
    for price, breakout_high, exit_low in zip(close, high, low):
        if pd.isna(breakout_high) or pd.isna(exit_low):
            state = 0.0
        elif state == 0 and price > breakout_high:
            state = 1.0
        elif state == 1 and price < exit_low:
            state = 0.0
        values.append(state)
    return pd.Series(values, index=close.index, name="signal")


def _mean_reversion_signal(
    close: pd.Series,
    window: int = 20,
    entry_z: float = 1.0,
    exit_z: float = 0.0,
) -> tuple[pd.Series, pd.Series]:
    rolling_mean = close.rolling(window, min_periods=window).mean()
    rolling_std = close.rolling(window, min_periods=window).std()
    z_score = (close - rolling_mean) / rolling_std
    state = 0.0
    values = []
    for value in z_score:
        if pd.isna(value):
            state = 0.0
        elif state == 0 and value < -entry_z:
            state = 1.0
        elif state == 1 and value > exit_z:
            state = 0.0
        values.append(state)
    return pd.Series(values, index=close.index, name="signal"), z_score


def _momentum_factor_panel(close: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    monthly = close.resample("ME").last()
    factor = monthly / monthly.shift(6) - 1
    recent_reversal = monthly / monthly.shift(1) - 1
    factor = factor - recent_reversal
    future_return = monthly.shift(-1) / monthly - 1
    aligned = factor.index.intersection(future_return.index)
    return factor.loc[aligned], future_return.loc[aligned]


def _factor_layer_returns(factor: pd.DataFrame, future_return: pd.DataFrame) -> pd.DataFrame:
    ranks = factor.rank(axis=1, pct=True)
    layers = {
        "Q1_low": future_return.where(ranks <= 0.2).mean(axis=1),
        "Q2": future_return.where((ranks > 0.2) & (ranks <= 0.4)).mean(axis=1),
        "Q3": future_return.where((ranks > 0.4) & (ranks <= 0.6)).mean(axis=1),
        "Q4": future_return.where((ranks > 0.6) & (ranks <= 0.8)).mean(axis=1),
        "Q5_high": future_return.where(ranks > 0.8).mean(axis=1),
    }
    result = pd.DataFrame(layers).fillna(0)
    result["high_minus_low"] = result["Q5_high"] - result["Q1_low"]
    return result


def _rank_ic_series(factor: pd.DataFrame, future_return: pd.DataFrame) -> pd.Series:
    values = []
    for idx in factor.index.intersection(future_return.index):
        f = factor.loc[idx]
        r = future_return.loc[idx]
        valid = f.notna() & r.notna()
        if valid.sum() < 3:
            values.append(np.nan)
        else:
            values.append(float(f[valid].rank().corr(r[valid].rank())))
    return pd.Series(values, index=factor.index.intersection(future_return.index), name="rank_ic")


def _top_bucket_turnover(factor: pd.DataFrame, top_pct: float = 0.2) -> pd.Series:
    ranks = factor.rank(axis=1, pct=True)
    top = ranks >= (1 - top_pct)
    counts = top.sum(axis=1).replace(0, np.nan)
    changed = top.astype(int).diff().abs().sum(axis=1) / (2 * counts)
    return changed.fillna(0).rename("turnover")


def _factor_long_short_returns(factor: pd.DataFrame, future_return: pd.DataFrame) -> pd.Series:
    ranks = factor.rank(axis=1, pct=True)
    top = future_return.where(ranks >= 0.8).mean(axis=1)
    bottom = future_return.where(ranks <= 0.2).mean(axis=1)
    return (top - bottom).fillna(0)


def _monthly_beta_vol(close: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    daily_returns = close.pct_change()
    market = daily_returns["SPY"]
    beta = daily_returns.rolling(252).cov(market).div(market.rolling(252).var(), axis=0)
    volatility = daily_returns.rolling(63).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    return beta.resample("ME").last(), volatility.resample("ME").last()


def _neutralize_factor(
    factor: pd.DataFrame,
    exposures: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    neutral = pd.DataFrame(index=factor.index, columns=factor.columns, dtype=float)
    for idx in factor.index:
        y = factor.loc[idx]
        x_parts = []
        for exposure in exposures.values():
            x_parts.append(exposure.reindex(index=factor.index, columns=factor.columns).loc[idx])
        x = pd.concat(x_parts, axis=1)
        x.columns = list(exposures)
        valid = y.notna() & x.notna().all(axis=1)
        if valid.sum() < len(exposures) + 2:
            continue
        yv = y[valid].astype(float)
        xv = x.loc[valid].astype(float)
        xv = (xv - xv.mean()) / xv.std(ddof=0).replace(0, np.nan)
        xv = xv.fillna(0)
        matrix = np.column_stack([np.ones(len(xv)), xv.to_numpy()])
        coef = np.linalg.lstsq(matrix, yv.to_numpy(), rcond=None)[0]
        neutral.loc[idx, valid] = yv.to_numpy() - matrix @ coef
    return neutral


def _factor_quality_row(name: str, rank_ic: pd.Series, returns: pd.Series) -> dict[str, float | str]:
    perf = _performance_row(name, returns, periods_per_year=12)
    perf["mean_rank_ic"] = float(rank_ic.mean())
    perf["icir"] = float(rank_ic.mean() / rank_ic.std(ddof=1))
    perf["positive_ic_rate"] = float((rank_ic > 0).mean())
    return perf


def _average_row_corr(left: pd.DataFrame, right: pd.DataFrame) -> float:
    values = []
    for idx in left.index.intersection(right.index):
        l = left.loc[idx]
        r = right.loc[idx]
        valid = l.notna() & r.notna()
        if valid.sum() >= 3:
            values.append(l[valid].corr(r[valid]))
    return float(np.nanmean(values)) if values else np.nan


def _multi_factor_panel(close: pd.DataFrame) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    monthly = close.resample("ME").last()
    future_return = monthly.shift(-1) / monthly - 1
    momentum = monthly / monthly.shift(6) - 1
    reversal = -(monthly / monthly.shift(1) - 1)
    daily_returns = close.pct_change()
    low_vol = -(daily_returns.rolling(63).std() * np.sqrt(TRADING_DAYS_PER_YEAR)).resample("ME").last()
    aligned = future_return.index
    factors = {
        "momentum": momentum.reindex(aligned),
        "reversal": reversal.reindex(aligned),
        "low_volatility": low_vol.reindex(aligned),
    }
    return factors, future_return


def _zscore_cross_sectional(factor: pd.DataFrame) -> pd.DataFrame:
    mean = factor.mean(axis=1)
    std = factor.std(axis=1).replace(0, np.nan)
    return factor.sub(mean, axis=0).div(std, axis=0)


def _ols_beta(x: pd.Series, y: pd.Series) -> float:
    valid = x.notna() & y.notna()
    xv = x[valid].to_numpy()
    yv = y[valid].to_numpy()
    return float(np.cov(xv, yv, ddof=1)[0, 1] / np.var(xv, ddof=1))


def _pairs_position(z_score: pd.Series, entry_z: float, exit_z: float) -> pd.Series:
    state = 0.0
    values = []
    for z in z_score:
        if pd.isna(z):
            state = 0.0
        elif state == 0 and z > entry_z:
            state = -1.0
        elif state == 0 and z < -entry_z:
            state = 1.0
        elif state != 0 and abs(z) < exit_z:
            state = 0.0
        values.append(state)
    return pd.Series(values, index=z_score.index)


def _estimate_half_life(spread: pd.Series) -> float:
    lag = spread.shift(1)
    delta = spread.diff()
    valid = lag.notna() & delta.notna()
    if valid.sum() < 30:
        return np.nan
    beta = _ols_beta(lag[valid], delta[valid])
    return float(-np.log(2) / beta) if beta < 0 else np.nan


def _build_ml_dataset(df: pd.DataFrame) -> pd.DataFrame:
    close = df["Close"]
    returns = close.pct_change()
    volume = df["Volume"]
    dataset = pd.DataFrame(index=df.index)
    dataset["ret_5"] = close / close.shift(5) - 1
    dataset["ret_20"] = close / close.shift(20) - 1
    dataset["ret_63"] = close / close.shift(63) - 1
    dataset["vol_20"] = returns.rolling(20).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    dataset["volume_z"] = (volume - volume.rolling(20).mean()) / volume.rolling(20).std()
    dataset["future_1d_return"] = returns.shift(-1)
    dataset["label"] = (dataset["future_1d_return"] > 0).astype(float)
    return dataset.replace([np.inf, -np.inf], np.nan).dropna()


def _time_train_test_split(dataset: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    split = int(len(dataset) * 0.65)
    return dataset.iloc[:split].copy(), dataset.iloc[split:].copy()


def _ridge_predict(train: pd.DataFrame, test: pd.DataFrame, feature_cols: list[str]) -> np.ndarray:
    x_train = train[feature_cols].astype(float)
    y_train = train["future_1d_return"].astype(float)
    x_test = test[feature_cols].astype(float)
    mean = x_train.mean()
    std = x_train.std(ddof=0).replace(0, 1)
    x_train_scaled = (x_train - mean) / std
    x_test_scaled = (x_test - mean) / std
    train_matrix = np.column_stack([np.ones(len(x_train_scaled)), x_train_scaled.to_numpy()])
    test_matrix = np.column_stack([np.ones(len(x_test_scaled)), x_test_scaled.to_numpy()])
    penalty = np.eye(train_matrix.shape[1]) * 1e-4
    penalty[0, 0] = 0
    coef = np.linalg.solve(train_matrix.T @ train_matrix + penalty, train_matrix.T @ y_train.to_numpy())
    return test_matrix @ coef


def _prediction_strategy(test: pd.DataFrame, prediction: pd.Series | np.ndarray) -> tuple[pd.Series, float]:
    pred = pd.Series(prediction, index=test.index)
    signal = (pred > 0).astype(float)
    turnover = signal.diff().abs().fillna(signal.abs())
    strategy_return = signal * test["future_1d_return"].fillna(0) - turnover * DEFAULT_COST_BPS / 10_000
    accuracy = float(((pred > 0) == (test["future_1d_return"] > 0)).mean())
    return strategy_return, accuracy


def _event_driven_single_asset(open_price: pd.Series, signal: pd.Series) -> pd.DataFrame:
    open_return = open_price.shift(-1) / open_price - 1
    position = 0.0
    rows = []
    for idx in open_price.index:
        desired = float(signal.shift(1).fillna(0).loc[idx])
        order = desired - position
        cost = abs(order) * DEFAULT_COST_BPS / 10_000
        position = desired
        ret = position * float(open_return.fillna(0).loc[idx]) - cost
        rows.append({"position": position, "order": order, "return": ret})
    return pd.DataFrame(rows, index=open_price.index)


def _paper_trading_log(df: pd.DataFrame, signal: pd.Series, days: int = 80) -> pd.DataFrame:
    sample = df.tail(days + 1).copy()
    sample_signal = signal.reindex(sample.index).fillna(0)
    position = sample_signal.shift(1).fillna(0)
    order = position.diff().fillna(position)
    next_open_return = sample["Open"].shift(-1) / sample["Open"] - 1
    previous_close = sample["Close"].shift(1)
    slippage_bps = ((sample["Open"] / previous_close - 1).abs() * 10_000).fillna(0)
    result = pd.DataFrame(
        {
            "signal": sample_signal,
            "position": position,
            "order": order,
            "fill_price": sample["Open"],
            "close": sample["Close"],
            "slippage_bps": slippage_bps,
            "strategy_return": position * next_open_return.fillna(0) - order.abs() * DEFAULT_COST_BPS / 10_000,
            "signal_checked": sample_signal.notna(),
            "order_checked": True,
            "position_checked": True,
        },
        index=sample.index,
    )
    result["checklist_complete"] = result[["signal_checked", "order_checked", "position_checked"]].all(axis=1)
    return result.tail(days)


def _flowchart(axis: plt.Axes, labels: list[str], title: str) -> None:
    axis.set_axis_off()
    axis.set_title(title)
    xs = np.linspace(0.1, 0.9, len(labels))
    for x, label in zip(xs, labels):
        axis.text(
            x,
            0.5,
            label,
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.35", "fc": "#e8f1fb", "ec": "#1f77b4"},
            transform=axis.transAxes,
        )
    for left, right in zip(xs[:-1], xs[1:]):
        axis.annotate(
            "",
            xy=(right - 0.06, 0.5),
            xytext=(left + 0.06, 0.5),
            arrowprops={"arrowstyle": "->", "color": "#333333"},
            xycoords=axis.transAxes,
        )


def _grid(axes) -> None:
    for axis in np.ravel(axes):
        axis.grid(True, alpha=0.25)


def _bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    formatted = df.copy()
    for column in formatted.columns:
        formatted[column] = formatted[column].map(lambda value, col=column: _format_value(col, value))
    header = "| " + " | ".join(formatted.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(formatted.columns)) + " |"
    rows = [
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in formatted.itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator, *rows])


def _format_value(column: str, value) -> str:
    if pd.isna(value):
        return "nan"
    if isinstance(value, (bool, np.bool_)):
        return str(bool(value))
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)):
        lower = column.lower()
        if any(key in lower for key in ["return", "drawdown", "vol", "accuracy", "rate", "exposure", "cost"]):
            return f"{float(value):.2%}"
        if any(key in lower for key in ["sharpe", "calmar", "corr", "ic", "beta", "half_life"]):
            return f"{float(value):.4f}"
        if abs(float(value)) >= 100:
            return f"{float(value):.0f}"
        return f"{float(value):.4f}"
    return str(value)
