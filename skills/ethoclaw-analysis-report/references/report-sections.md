# Report Sections

在需要组织报告结构或理解 `manifest["section_bodies"]` 时读取本文件。

## 正文回填合同

所有正文都直接写回：

- `manifest["section_bodies"][body_key]["body"]`

不要创建 `sections.json`。不要把正文写进别的中间文件。

## 可用 body 列表

### `project_summary_body`

- 对应章节：Project Summary
- 用途：把路径范围、核心素材、当前报告模式和关键缺口压缩成一个短节
- 留空条件：不留空，始终应填写

### `overview_body`

- 对应章节：Overview
- 用途：给出项目层面的高层概述，并补一句实验目的与基础流程
- 留空条件：只有在项目用途和核心背景完全无法确认时才可极简地按结果整理来写

### `sample_check_body`

- 对应章节：Sample and Group Verification
- 用途：核对样本数、样本标识、候选组别、组别映射和对照组
- 留空条件：不留空，始终应填写

### `raw_trajectory_body`

- 对应章节：Raw Trajectory Summary
- 用途：在只有原始骨架或轨迹数据时，直接总结行动区域、主轴分布、路径长度和样本间差异
- 留空条件：没有可直接读取的轨迹坐标时留空；单样本和多样本项目都适用

### `heatmap_body`

- 对应章节：Heatmap Findings
- 用途：描述热图、轨迹图、atlas、时序图体现的空间分布或运动模式
- 留空条件：当前目录没有热图类素材时留空

### `radar_body`

- 对应章节：Radar Profile Findings
- 用途：描述雷达图中的多指标轮廓
- 留空条件：当前目录没有雷达图时留空

### `stats_body`

- 对应章节：Statistical Comparison Findings
- 用途：总结有统计表或明确统计图支持的比较结果
- 留空条件：没有统计依据，或分组信息不足以支撑比较时留空

### `cluster_body`

- 对应章节：Clustering Findings
- 用途：描述聚类图中的模式结构
- 留空条件：当前目录没有聚类图时留空

### `single_subject_body`

- 对应章节：Single-Subject Profile
- 用途：单样本模式下总结单体核心指标与图像观察
- 留空条件：非 `single-subject` 模式时留空

### `integrated_interpretation_body`

- 对应章节：Integrated Interpretation
- 用途：跨图类整合多个结果来源，形成简洁直接的综合总结
- 留空条件：图类不足，或元数据不足以支持综合整理时留空

## 使用原则

- 并非每次都要填写全部 body
- 图类相关 body 没有证据时应留空
- 留空的 body 不会被渲染
- `section_bodies` 内的 `purpose`、`write_when`、`source_fields`、`rules` 是给 agent 的写作约束，不应原样渲染到最终报告
- body 的语言默认跟随当前用户对话语言；术语首次出现时优先写成“中文（English）”
- 回填 body 时直接编辑 `manifest.json`，不要通过 shell 管道或内联命令注入大段正文，避免编码污染
- 每个 body 都应优先总结当前数据最明显的结果，不要把整节写成“不能下结论”的说明
- 如果需要交代限制，优先集中放在 `project_summary_body`、`overview_body` 或 `integrated_interpretation_body`
- 对于 `control`、`model`、`sham`、`vehicle` 这类明显文件名前缀，可以直接当作候选分组使用
- 对于只有骨架数据的项目，优先写出最明显的行动区域、主轴分布或运动范围差异，而不是只做素材盘点
