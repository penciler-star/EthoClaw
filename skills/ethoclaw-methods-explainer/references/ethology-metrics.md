# Ethology Metrics Reference

在用户询问行为学指标“怎么定义、怎么计算、怎么解释”时读取本文件。

## 适用范围

优先用于解释以下常见行为学指标：

- Frequency / rate
- Duration
- Latency
- Proportion / time budget
- Transition count / transition probability
- Bout length / bout count
- Inter-event interval
- Individual-level summary 与 group-level summary 的区别

## 解释顺序

解释任何指标时，优先按这个顺序输出：

1. 原始输入是什么。
2. 一条记录代表什么。
3. 预处理做了什么。
4. 指标如何计算。
5. 结果单位是什么。
6. 生物学上如何解释。
7. 有哪些常见误解或限制。

## 常见指标定义

### Frequency

- 含义：在给定观察窗口内，某行为开始发生的次数。
- 常见输入：行为事件表，至少包含个体 ID、行为标签、开始时间。
- 公式：Frequency = event onset count within window
- 单位：次 / 窗口，或次 / 分钟、次 / 小时。
- 注意：必须说明是按 onset 计数，还是按任意被标记帧计数。

### Duration

- 含义：某行为在观察窗口内累计持续的总时间。
- 常见输入：包含开始时间和结束时间的行为片段表。
- 公式：Duration = sum(end_time - start_time)
- 单位：秒、分钟，或占窗口的比例。
- 注意：说明是否剔除了不可见时段和中断片段。

### Latency

- 含义：从一个参考时点到目标行为首次出现的等待时间。
- 常见输入：参考事件时间、目标行为首次 onset 时间。
- 公式：Latency = first_target_onset - reference_time
- 单位：秒、分钟。
- 注意：如果目标行为未出现，说明是否记为缺失、删失（censored）或赋最大观察时长。

### Proportion / Time Budget

- 含义：某行为持续时间占总可观察时间的比例。
- 公式：Proportion = behavior_duration / observable_time
- 单位：0 到 1，或百分比。
- 注意：observable time 不一定等于 session 总时长，可能需要扣除遮挡、离屏、无法编码时间。

### Transition Probability

- 含义：从行为 A 转换到行为 B 的条件概率。
- 常见输入：按时间排序的行为序列。
- 公式：P(A -> B) = count(A -> B) / total outgoing transitions from A
- 注意：要说明是否允许 self-transition、是否按个体分别算后再汇总。

### Bout Length

- 含义：某行为一次连续发生、直到切换为其他行为前的持续时间。
- 公式：Bout length = end_of_continuous_run - start_of_continuous_run
- 注意：必须定义“连续”的判据，例如是否允许短暂中断合并。

### Inter-event Interval

- 含义：两次相邻目标事件之间的时间间隔。
- 公式：IEI = onset(i+1) - onset(i)
- 注意：只有在事件定义清晰且时间排序可靠时才有意义。

## 常见预处理

在解释指标时，优先检查是否涉及：

- 行为标签合并或重编码。
- 时间窗切分（binning）。
- 平滑或滚动窗口。
- 缺失值或不可见时段剔除。
- 按个体、session、trial 先聚合再做组间分析。
- 标准化为每分钟、每小时或每次试验。

## 常见坑

- 把 frequency 和 duration 混为一谈。
- 不说明 denominator，导致 proportion 无法复现。
- 用 group mean 掩盖 individual variation。
- 把原始事件层级的数据和聚合后的 summary 层级混用。
- 不交代未观察到目标行为时 latency 怎么处理。

## 建议输出句式

### 参数卡最小模板

- 名称：
- 输入：
- 公式：
- 单位：
- 预处理：
- 解释：
- 限制：

### Methods 写法提示

优先使用这种句式：

"For each individual / trial / session, we calculated ... as ..."

中文可写成：

“对每个个体 / trial / session，计算……，其定义为……。”
