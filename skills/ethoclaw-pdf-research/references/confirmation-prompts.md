# Confirmation Prompts

When a PDF arrives, do not start parsing immediately unless the user explicitly asked for immediate analysis.

Use a short confirmation message like this:

## Default confirmation

我收到了这份 PDF。你想让我怎么处理？
- 简版摘要
- 详细分析
- 研究日志（直接回复给你）
- 重点看某几页 / 某个章节 / 图表
- 如果你要，我也可以额外整理成 markdown 文件

你确认后我再开始解析。

## If the file looks like a manual / SOP / guide

我收到了这份 PDF，看起来像操作手册/说明文档。你想要我怎么输出？
- 快速总结
- 按“用途-流程-输出-注意事项”整理
- 直接回复研究日志
- 面向新人整理成操作说明
- 如果你要，我也可以额外生成 markdown 文件

你确认后我再解析。

## If the user already gave a goal

If the user says things like “帮我总结一下”“做个研究日志”“重点看方法部分”, that counts as confirmation. Start parsing directly and produce the requested output without asking again.
