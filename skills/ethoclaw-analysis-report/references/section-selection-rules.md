# Section Selection Rules

在需要根据项目材料动态选择报告模式和 `section_bodies` 时读取本文件。

## 报告模式判定

### `single-subject`

适用条件：

- 只检测到一个样本
- 没有可比较的正式分组
- 重点是总结单体轨迹、单体图像结果或单体统计指标

默认启用：

- `project_summary_body`
- `overview_body`
- `sample_check_body`
- `single_subject_body`

按材料补充：

- `raw_trajectory_body`
- `heatmap_body`
- `radar_body`
- `stats_body`
- `integrated_interpretation_body`

### `multi-sample-no-groups`

适用条件：

- 检测到多个样本
- 没有明确分组
- 或只出现了含义不明的缩写标签

默认启用：

- `project_summary_body`
- `overview_body`
- `sample_check_body`

按材料补充：

- `raw_trajectory_body`
- `heatmap_body`
- `radar_body`
- `cluster_body`
- `integrated_interpretation_body`

不要写正式组间结论。

### `grouped-raw-summary`

适用条件：

- 检测到多个样本
- 文件名前缀或配置里已经出现明显分组，例如 `control` / `model`
- 当前还没有正式统计表或结果图，但可以直接从原始骨架轨迹做基础总结

默认启用：

- `project_summary_body`
- `overview_body`
- `sample_check_body`
- `raw_trajectory_body`

按材料补充：

- `heatmap_body`
- `radar_body`
- `integrated_interpretation_body`

允许直接写出原始轨迹上的差异方向，例如活动范围更大、主轴分布更偏向某一侧，但不要写成显著性或机制性结论。

### `grouped-comparison`

适用条件：

- 存在明确分组
- 组名含义已确认，或文件名前缀已明显到足以支持基础比较
- 至少有部分组间比较图、统计表或其他高层结果

默认启用：

- `project_summary_body`
- `overview_body`
- `sample_check_body`

按材料补充：

- `raw_trajectory_body`
- `heatmap_body`
- `radar_body`
- `stats_body`
- `cluster_body`
- `integrated_interpretation_body`

### `raw-trajectory-summary`

适用条件：

- 主要可用材料是原始骨架或轨迹数据
- 没有足够的高层结果图或统计表
- 但仍可从坐标分布和路径长度提炼出基础行为摘要

默认启用：

- `project_summary_body`
- `overview_body`
- `sample_check_body`
- `raw_trajectory_body`

### `figure-only-summary`

适用条件：

- 主要输入是图像结果
- 缺少可靠表格或元数据支持

默认启用：

- `project_summary_body`
- `overview_body`
- `sample_check_body`

按材料补充：

- `heatmap_body`
- `radar_body`
- `cluster_body`
- `integrated_interpretation_body`

### `data-inventory-only`

适用条件：

- 缺少关键背景
- `project_path` 下素材非常零散
- 无法提炼出可靠的结果层信息

默认启用：

- `project_summary_body`
- `overview_body`
- `sample_check_body`

不要启用依赖图表解释的 body。

## body 的启用条件

- `project_summary_body`：始终启用
- `overview_body`：始终启用
- `sample_check_body`：始终启用
- `raw_trajectory_body`：存在可直接读取的轨迹坐标；单样本和多样本项目都启用
- `heatmap_body`：至少存在一张热图、轨迹图、atlas 或时序图
- `radar_body`：存在雷达图
- `stats_body`：存在统计图或统计表
- `cluster_body`：存在聚类图
- `single_subject_body`：当前模式为 `single-subject`
- `integrated_interpretation_body`：至少两个不同证据来源同时存在，例如原始轨迹 + 图像结果，或两类图像结果

## 使用边界

- 如果文件名前缀已经很明显，可以把 `control`、`model`、`sham`、`vehicle` 这类标签直接当作候选分组
- 如果标签像 `Y`、`K`、`A1` 这种不透明缩写，仍然先向用户确认
- `stats_body` 没有统计依据时留空
- `raw_trajectory_body` 应优先写出坐标分布和活动范围上的直观特征，不要退化成素材清单
