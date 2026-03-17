# Metadata Schema

需要判断“哪些信息必须向用户确认”时读取本文件。

## 关键元数据

以下信息如果无法从项目目录、文件名、图表标题或用户对话中确认，就应先向用户提问：

- `project_name`：项目名或报告标题
- `report_goal`：报告用途，例如结果整理、内部汇报、论文草稿
- `experiment_type`：实验范式或任务类型
- `has_groups`：是否存在分组
- `group_mapping`：组标签分别代表什么
- `control_group`：如果存在对照组，哪一组是对照组
- `allow_interpretive_conclusion`：是否允许写解释性结论

## 建议补充的信息

- `species`
- `sample_definition`：一条记录对应个体、session、trial 还是其他单位
- `preferred_language`
- `priority_figures`
- `main_result_dirs`
- `notes`

## 这些信息从哪里来

元数据来源只有三类：

- 项目目录内已有的说明文本、结果文件和图表标题
- 文件名、目录名和样本命名方式中可以直接推断的信息
- 用户在对话中补充的实验背景和写作要求

## 提问规则

- 缺少 `project_path`：先问路径，不做其他工作
- 组名是 `control`、`model`、`sham`、`vehicle` 这类明显标签时，可先作为候选分组使用
- 组名是 `Y`、`con`、`k` 这类含义不透明的缩写时，先问组别含义
- 需要写正式组间比较，但没有 `control_group`：先问对照组
- 用户要求写解释性结论，但 `allow_interpretive_conclusion` 不明确：先问是否允许

## 未确认时允许写什么

即使元数据不完整，也允许先输出：

- 项目与素材概况
- 样本和候选分组核对
- 原始轨迹摘要
- 图像和统计结果的直接总结

不要因为少量背景缺失就回避明显的数据特征；只是在确实缺少关键信息时，不把不透明缩写硬解释成正式实验组定义。

## 与 manifest 的关系

- `build_report_manifest.py` 会把未确认项汇总到 `facts.unconfirmed_items`
- agent 在填写 `project_summary_body`、`overview_body`、`sample_check_body` 时，可简短带出仍待确认的关键点
- 所有正文都直接回填到 `manifest.json`，不再创建额外的配置或 section 文件
