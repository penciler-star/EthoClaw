# GLM and GLMM Reference

在用户询问 GLM、GLMM、logistic regression、Poisson regression、mixed model、random effect、link function 时读取本文件。

## 一句话定位

- GLM：广义线性模型，用于非正态响应变量。
- GLMM：广义线性混合模型，在 GLM 基础上加入随机效应（random effects），适合重复测量、层级结构或个体差异明显的数据。

## 什么时候优先考虑这些模型

如果响应变量不是“近似正态、独立、连续”的普通数据，优先考虑 GLM / GLMM。例如：

- 是否发生某行为：二分类，常用 binomial / logistic。
- 行为发生次数：计数型，常用 Poisson 或 negative binomial。
- 成功次数 / 总次数：比例型，常用 binomial。
- 同一只动物被重复观察：通常需要 mixed model 处理个体内相关性。
- 数据来自不同笼位、群组、批次、观察者：可能需要随机效应。

## 解释顺序

解释 GLM / GLMM 时，优先按这个顺序输出：

1. 响应变量是什么。
2. 响应变量的数据类型是什么。
3. 固定效应（fixed effects）是什么。
4. 随机效应（random effects）是什么。
5. 分布族（family）和链接函数（link function）是什么。
6. 模型为什么适合这个问题。
7. 参数如何解释。
8. 有哪些常见诊断或限制。

## 核心概念

### Response Variable

模型要解释或预测的结果变量，例如：

- 某行为是否发生。
- 某时间窗内叫声次数。
- 某行为持续时间占比。

### Fixed Effects

研究者主要关心的解释变量，例如：

- 处理组别
- 性别
- 年龄
- 时间阶段
- 环境条件

固定效应回答的是：“这些变量和结果之间的系统性关系是什么？”

### Random Effects

用于表示分层结构或重复测量来源，例如：

- individual ID
- group ID
- session ID
- observer ID
- batch

随机效应回答的是：“不同个体或群组之间的基线差异，是否需要单独建模而不是硬塞进误差项？”

## 常见 family 与典型场景

### Gaussian

- 适用：近似连续正态的响应变量。
- 常见例子：某连续测量值，且残差近似正态。
- 说明：这时模型更接近普通线性模型。

### Binomial with logit link

- 适用：二分类结果或成功次数 / 总次数。
- 常见例子：某行为是否发生、是否成功选择某食物。
- 解释：系数是在 log-odds 尺度上，需要说明是否转换为 odds ratio 或预测概率。

### Poisson with log link

- 适用：计数数据。
- 常见例子：攻击次数、叫声次数、接触次数。
- 注意：如果方差明显大于均值，可能存在 overdispersion。

### Negative Binomial

- 适用：过度离散（overdispersed）的计数数据。
- 常见例子：大量零值且个体差异大的行为次数数据。
- 解释：通常是 Poisson 不够灵活时的替代。

## 为什么用 GLMM 而不是只用 GLM

当数据存在重复测量或层级结构时，只用 GLM 往往会把本来相关的观测当成独立样本，导致标准误偏小、显著性被夸大。

典型场景：

- 同一只动物在多个 trial 中被重复观察。
- 多个个体来自同一群组或笼位。
- 同一观察者对多个视频打分。

此时常见写法是：

- fixed effects：处理、时间、性别等。
- random effects：individual ID、group ID 等。

## 参数解释提醒

### Logistic 回归

- 系数增加 1，不表示概率直接增加固定值。
- 系数首先作用在 log-odds 上。
- 如果需要给初学者解释，优先转成“更可能 / 更不可能”或给预测概率示例。

### Poisson / Negative Binomial

- 系数通常作用在 log count 或 log rate 上。
- 解释时可转成倍数变化，例如 exp(beta)。

### Random Effect

- 不要把 random effect coefficient 解释成和 fixed effect 同等含义的主效应。
- 更准确的说法是：它反映不同个体或群组之间的变异结构。

## 常见诊断与限制

解释模型时，优先检查文中是否提到：

- overdispersion
- zero inflation
- convergence warning
- singular fit
- residual diagnostics
- collinearity
- model comparison

如果论文没有写，不要假装做过诊断，只能写 `Unconfirmed`。

## 常见坑

- 把 repeated measures 数据直接当独立样本。
- 计数数据还用普通线性回归。
- 只报告 p 值，不说明 family、link 和 random effect。
- 把 odds ratio 误写成概率差。
- 不说明 offset，例如观测时长不同却直接比次数。

## 建议输出句式

### 模型卡最小模板

- 响应变量：
- 数据类型：
- 固定效应：
- 随机效应：
- family / link：
- 选择理由：
- 参数解释：
- 诊断或限制：

### Methods 写法提示

中文：

“采用广义线性混合模型（GLMM）分析……，其中……作为响应变量，……作为固定效应，个体 ID 作为随机效应；根据响应变量的数据分布，指定……分布与……链接函数。”

英文：

"We fitted a generalized linear mixed model (GLMM) with ... as the response variable, ... as fixed effects, and individual ID as a random effect, using a ... family with a ... link."
