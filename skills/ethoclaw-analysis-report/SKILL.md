---
name: ethoclaw-analysis-report
description: 用于基于单个项目路径（project_path）下已有的骨架数据、行为数据、统计表和结果图，先生成 manifest.json，再由 agent 直接回填 manifest 内的 section bodies，最后渲染结构化分析报告。适用于热图、轨迹图、雷达图、小提琴图、聚类图、统计结果汇总等场景。默认输出单文件 HTML 报告。用户可能会用“根据这个项目文件夹生成报告”“把这些结果整理成 HTML 报告”“基于现有图表生成分析总结”“帮我核对分组并出一份报告”这类中文请求触发。
---

# Ethoclaw Analysis Report

基于单个 `project_path` 下的现有数据和图表生成结构化分析报告。主流程固定为：

1. 用 `build_report_manifest.py` 生成 `manifest.json`
2. agent 只读取 `manifest.json`，并直接回填 `manifest["section_bodies"][...]["body"]`
3. 用 `render_report.py --manifest manifest.json` 渲染 `report.md` 和单文件 `report.html`

不要创建 `sections.json`。不要把正文写到其他中间文件。`manifest.json` 是唯一的中间产物。

## 环境要求

- Python `>=3.10`
  - 当前脚本使用了 `str | None`、`list[...]` 等现代类型注解语法，低于 3.10 的解释器无法直接运行
- 必需依赖：`Pillow`
  - `report_utils.py` 顶层直接依赖 `PIL.Image`
  - 用于在渲染 HTML 时压缩并内嵌 `.png` / `.jpg` / `.jpeg` 图片
- 文件编码：必须按 `UTF-8` 读写 `manifest.json`、`report.md`、`report.html`
- shell / 平台注意事项：
  - 在 Windows PowerShell 下，长段中文正文经命令行参数、管道、here-string、环境变量或 `python -c` / `python -` 注入后，容易被替换成 `?` 或产生乱码
  - 因此正文回填必须直接编辑 `manifest.json` 文件本身，不要通过 shell 文本通道回写

## 核心范围

仅处理一个项目目录。用户必须提供 `project_path`，且只允许读取该路径下的文件。

允许的输入包括但不限于：

- 骨架或轨迹数据：`.h5`、`.csv`、关键点坐标表
- 行为或统计数据：summary 表、事件表、显著性检验表、参数表、单样本统计 JSON
- 图像结果：热图、轨迹图、雷达图、小提琴图、聚类图、atlas、时序图
- 项目元数据：说明文本、同目录备注文件、用户在对话中补充的实验信息

不要默认项目一定包含分组，也不要默认所有图表都齐全。

## 脚本职责

- `scripts/build_report_manifest.py`
  - 输入：`project_path`
  - 输出：`manifest.json`
  - 负责扫描项目、汇总事实、判定报告模式、生成可填写的 `section_bodies`

- agent
  - 输入：`manifest.json`
  - 负责阅读 `facts`、`galleries` 和 `section_bodies` 中的写作说明
  - 直接回填 `manifest["section_bodies"][body_key]["body"]`

- `scripts/render_report.py`
  - 输入：已经回填正文的 `manifest.json`
  - 输出：`report.md`、单文件 `report.html`
  - HTML 默认把图片压缩后内嵌为 data URI，不依赖外部图片文件
  - 只负责渲染，不负责自动补写正文

## 标准工作流

按下面顺序执行：

1. 确认用户提供了 `project_path`
2. 运行 `build_report_manifest.py --project-path <project_path> --output <manifest.json>`
3. 读取 `manifest.json`
4. 检查 `facts.unconfirmed_items` 和 `facts.sample_check`
5. 如有关键元数据缺失，先向用户提问
6. 逐个填写 `manifest["section_bodies"][body_key]["body"]`
7. 保存回同一个 `manifest.json`
8. 用 UTF-8 重新读取刚写回的 `manifest.json`，逐项检查已填写的 `body` 是否仍为正常正文，而不是 `?`、`\uFFFD`、乱码或被截断的文本
9. 仅在第 8 步确认无误后，运行 `render_report.py --manifest <manifest.json> --output-dir <report_output>`
不要先渲染一个空报告再回填。
回填正文时，直接编辑现有 `manifest.json` 文件，不要通过 shell 内联文本、命令参数、重定向或管道把大段正文写入 JSON。
也不要把正文先拼进 `python -c`、`python -`、`node -e`、PowerShell here-string、`jq` 过滤器、环境变量或任何命令行字符串里，再由脚本回写到 `manifest.json`；这些都属于正文注入，不属于“直接编辑文件”。
这样做是为了避免不同系统和 shell 的默认编码差异，尤其是在 Windows PowerShell 下，大段中文正文经过命令行通道时容易被替换成 `?`。
如果第 8 步发现正文已经变成 `?`、乱码或异常转义，停止渲染，直接重新编辑 `manifest.json` 文件本身并再次校验，不要带着损坏内容继续生成报告。

## 先确认 project_path

开始工作前必须先确认用户提供了 `project_path`。

如果没有提供：

- 先向用户提问索取 `project_path`
- 在拿到路径前，不要假设默认目录，不要跨目录搜索素材

如果用户给了路径：

- 只读取该路径下的文件
- 不从兄弟目录、父目录或其他项目目录补抓图片和数据
- 如果发现路径内素材不足，只能报告不足并提问，不得改为读取其他目录

## 什么时候必须提问

以下信息如果项目路径内无法确认，必须先向用户提问，再继续生成完整报告：

- 是否存在分组；如果文件名前缀已经明显出现 `control`、`model`、`sham`、`vehicle` 这类标签，可以先按候选分组处理
- 各组标签的含义，例如 `Y`、`con`、`k` 这类不透明缩写分别代表什么
- 哪个组是对照组，或者是否根本没有对照组
- 实验范式、实验场景或任务类型
- 报告用途：内部汇报、实验记录、论文草稿、图表整理等
- 是否允许做解释性结论，还是只做结果整理
- 如果有多个结果目录，哪个是这次报告的主结果

在未确认这些关键项前：

- 可以完成材料盘点和基于当前证据的结果描述
- 可以填写不依赖背景解释的 section body
- 不要输出带强结论的完整报告
- 不要把含义不明的缩写自动解释成实验组含义；仅对 `control`、`model` 等明显标签做候选分组判断

## manifest.json 合同

`manifest.json` 至少包含这些顶层字段：

- `project_path`
- `project_name`
- `report_title`
- `report_goal`
- `scan`
- `report_mode`
- `report_mode_reason`
- `facts`
- `galleries`
- `section_bodies`

其中 `section_bodies` 是唯一的正文回填位置。结构如下：

```json
{
  "overview_body": {
    "section_id": "overview",
    "title": "项目概述",
    "purpose": "给出项目层面的简短概览。",
    "write_when": "通常填写；若连项目基本用途都无法确认，就按结果整理来概述。",
    "source_fields": ["facts.overview", "report_mode", "facts.unconfirmed_items"],
    "rules": [
      "说明项目名、报告用途、实验范式或其缺失状态。",
      "概述可以覆盖的核心图类或分析范围。"
    ],
    "body": ""
  }
}
```

agent 只需要改 `body`。不要改 `section_id`、`title`、`purpose`、`write_when`、`source_fields`、`rules` 的含义。
如果需要批量修改多个 body，也应直接编辑这个 UTF-8 `manifest.json` 文件本身，而不是拼装一个包含正文的 shell 命令去覆写它。
写完后必须再次从磁盘读取这个 `manifest.json`，确认每个已填写的 `body` 都能以正常 UTF-8 文本显示；只有确认文件内正文正确，才能进入渲染步骤。

## 每个 body 要写什么

### `project_summary_body`

- 作用：把项目路径、素材范围、当前模式和关键缺口压缩成一个短节
- 必写内容：扫描范围、核心素材、当前最适合的写法、最关键的缺口
- 不该写：文件逐条清单、路径外素材、长篇免责声明

### `overview_body`

- 作用：给出项目层面的高层概述，并先点出当前最明显的结果特征
- 必写内容：项目名、实验范式、当前报告用途、该实验通常评估什么和基础流程、当前数据最值得注意的 1 到 2 个结论
- 不该写：把整节写成方法说明

### `sample_check_body`

- 作用：核对样本和分组
- 必写内容：样本数量、样本 ID、候选组标签、组名是否已确认、对照组状态、待确认项
- 不该写：对含义不明的缩写强行解释
- 额外要求：如果文件名前缀已经明显出现 `control`、`model`、`sham`、`vehicle` 这类标签，可以直接当作候选分组写出

### `raw_trajectory_body`

- 作用：在只有原始骨架或轨迹数据时，基于坐标分布和路径长度做简单结果总结
- 必写内容：用了哪些原始轨迹文件、最明显的行动区域或主轴分布、运动范围或路径长度上的直观差异
- 不该写：没有装置映射时硬把纵横主轴写成已确认的开放臂/闭合臂
- 启用习惯：只要项目里能直接提炼出原始轨迹摘要，不管是单样本还是多样本，都应填写

### `heatmap_body`

- 作用：总结热图、轨迹图、atlas、时序图展示的空间分布或运动模式
- 必写内容：引用了哪些图、图上观察到的主要现象
- 不该写：统计显著性或机制性结论

### `radar_body`

- 作用：总结雷达图中的多指标轮廓
- 必写内容：图的对象、轮廓相对高低、主要差异点
- 不该写：未经确认的指标含义、未经确认的组间比较

### `stats_body`

- 作用：总结统计表或统计图支持的比较结果
- 必写内容：依据了哪些统计表/图，以及可被这些材料支持的比较结果
- 不该写：没有统计表时的显著性结论
- 额外要求：即使正式分组定义不完整，只要组名非常明显，也可以总结原始差异方向，但不要写成机制性结论

### `cluster_body`

- 作用：描述聚类图呈现的模式结构
- 必写内容：聚类对象、相对接近或分离的趋势
- 不该写：把视觉分离写成统计显著

### `single_subject_body`

- 作用：单样本模式下总结单个个体或单条记录的核心结果
- 必写内容：总时长、有效检测时长、距离、区域停留/进入等核心指标；如果只有原始骨架数据，也要结合轨迹分布写出主要行动区域
- 不该写：群体规律

### `integrated_interpretation_body`

- 作用：跨图类整合多个结果来源
- 必写内容：整合了哪些图类或统计来源，哪些是事实、哪些是结合当前实验范式做出的解释
- 不该写：未获允许的机制性、因果性总结

## 报告模式

优先在以下模式中选择最贴近的一种：

- `single-subject`
- `multi-sample-no-groups`
- `grouped-raw-summary`
- `grouped-comparison`
- `raw-trajectory-summary`
- `figure-only-summary`
- `data-inventory-only`

如果多个模式都可能成立，优先选与现有证据最匹配的模式；若仍有关键歧义，再向用户确认。

## 参考资料导航

根据任务阶段按需读取以下文件，不要一次性加载全部：

- 需要判断当前目录包含哪些材料类型时：读取 `references/input-types.md`
- 需要判断哪些项必须向用户确认时：读取 `references/metadata-schema.md`
- 需要确定本次有哪些章节以及 body 的职责时：读取 `references/report-sections.md`
- 需要根据材料选择报告模式和章节时：读取 `references/section-selection-rules.md`
- 需要约束解释口径、避免越界结论时：读取 `references/interpretation-guardrails.md`
- 如果 `facts.overview.experiment_type` 或其他项目材料明确指向特定动物行为学范式，在写 `overview_body`、`raw_trajectory_body`、`heatmap_body`、`stats_body`、`single_subject_body`、`integrated_interpretation_body` 前读取对应文件：
  - `TCST`：`references/experiment-types/tcst.md`
  - `OFT`：`references/experiment-types/oft.md`
  - `TST`：`references/experiment-types/tst.md`
  - `EPM`：`references/experiment-types/epm.md`
  - `FST`：`references/experiment-types/fst.md`
  - `NOR`：`references/experiment-types/nor.md`
- 需要查看展示模板时：读取 `assets/report_template_cn.md` 和相关 `assets/section_templates/*.md`

## 表达要求

- body 的默认语言应与当前用户对话语言一致；用户用中文交流就用中文写，用户用英文交流就用英文写；如果用户明确指定报告语言，优先服从用户指定。
- 术语首次出现时，优先使用“中文（English）”格式，尤其是统计方法、图类名称、行为学指标和实验范式名称；后文可在不引起歧义的前提下保持一种写法。
- 文件名、组标签、列名、原始指标名如果本身来自项目文件，可保留原始英文，不要强行翻译后再改写原值。
- 优先给出基于当前数据最直接、最有信息量的总结，不要因为缺少完整背景就回避明显的结果特征。
- 如果需要交代限制，把限制集中放在 `project_summary_body`、`overview_body` 或 `integrated_interpretation_body` 里简短提一次，不要在每一节重复写免责声明。
- 当实验范式已经明确时，可以结合对应范式的 readout 含义，对区域偏好、探索方向、活动模式或应对方式做简洁结论。
- 先说明依据了哪些文件和图，再写解释
- 把“观察到的事实”和“基于上下文的推断”分开写
- 缺失图或表时，跳过对应 body，保留空字符串即可
- 没有分组时，不得写组间比较
- 没有统计表时，不得写显著性结论
- 只有图、没有可靠表格支撑时，也要把最明显的图像模式总结出来，但不要写成统计显著或机制性结论
- 不把提示性文字、写作说明、推理规则渲染进最终 HTML

## 质量约束

- 不要跨出 `project_path` 读取素材
- 不要编造组别含义、样本量、实验背景、统计方法或结果结论
- 不要把聚类、热图或可视化分离直接写成显著差异
- 不要把单样本现象夸大为组间规律
- 如果用户没有给出报告用途，先询问；若暂时拿不到答案，就先按“结果整理”来写
