#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


REQUIRED_AGENT_FIELDS = [
    "chinese_title",
    "chinese_summary",
    "chinese_methods",
    "chinese_findings",
    "chinese_significance",
    "selection_reason",
]

OPTIONAL_AGENT_FIELDS = [
    "chinese_background",
    "chinese_limitations",
]


def parse_index_list(raw_value):
    values = []
    for chunk in (raw_value or "").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            values.append(int(chunk))
        except ValueError as exc:
            raise SystemExit(f"Invalid paper index: {chunk}") from exc
    return values


def join_authors(authors, limit=10):
    if not authors:
        return "Unknown"
    return ", ".join(authors[:limit])


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def paper_guidance(candidate_index, item):
    source = item.get("source_label") or item.get("source", "unknown")
    published = item.get("published", "")[:10] or "unknown"
    return {
        "candidate_index": candidate_index,
        "focus_questions": [
            "这篇文章要解决的核心科学问题是什么？",
            "作者使用了什么实验体系、记录/成像/行为范式或分析方法？",
            "最关键的结果是什么，证据是否足够直接？",
            "这些发现对神经行为学或行为神经科学的意义是什么？",
            "有哪些边界条件、限制或尚未解决的问题？",
        ],
        "writing_requirements": [
            f"先给出准确、自然的中文标题，保留物种、脑区、任务范式等关键信息。",
            f"写 120-220 字中文综合导读，避免空泛评价，优先概括研究问题、方法、主要发现和意义。",
            f"方法速览用 1-2 句，点出样本/物种、主要技术路线、行为任务或数据分析方法。",
            f"核心发现用 2-4 句，写清楚因果链、比较关系或关键定量趋势，不要只重复标题。",
            f"意义部分说明为什么值得读，特别是对 {source} / {published} 这类近期工作有什么启发。",
            "如果摘要本身证据有限，明确写出限制或需要阅读全文确认的地方。",
        ],
    }


def build_agent_packet(merged_payload, selected_indexes):
    items = merged_payload.get("items", [])
    if not items:
        raise SystemExit("Merged input contains no papers.")

    selected_papers = []
    seen = set()
    for slot, candidate_index in enumerate(selected_indexes, start=1):
        if candidate_index in seen:
            raise SystemExit(f"Duplicate candidate index: {candidate_index}")
        seen.add(candidate_index)

        zero_based = candidate_index - 1
        if zero_based < 0 or zero_based >= len(items):
            raise SystemExit(f"Candidate index out of range: {candidate_index}")

        item = items[zero_based]
        selected_papers.append(
            {
                "slot": slot,
                "candidate_index": candidate_index,
                "title": item.get("title", ""),
                "source": item.get("source_label") or item.get("source", "unknown"),
                "authors": item.get("authors", []),
                "published": item.get("published", "")[:10],
                "journal": item.get("journal", ""),
                "url": item.get("url", ""),
                "pdf_url": item.get("pdf_url", ""),
                "abstract": item.get("summary", ""),
                "weighted_score": item.get("weighted_score", item.get("relevance_score", "")),
                "reader_guidance": paper_guidance(candidate_index, item),
                "chinese_title": "",
                "chinese_summary": "",
                "chinese_background": "",
                "chinese_methods": "",
                "chinese_findings": "",
                "chinese_significance": "",
                "chinese_limitations": "",
                "selection_reason": "",
            }
        )

    return {
        "generated_at": merged_payload.get("generated_at", ""),
        "candidate_count": merged_payload.get("count", 0),
        "selected_indexes": selected_indexes,
        "agent_guidance": {
            "goal": "阅读所选摘要，为每篇候选文献产出更详细、可读性高的中文导读。",
            "recommended_process": [
                "优先在独立子会话中完成候选筛选与摘要撰写，主会话只接收最终成稿，减少 token 消耗。",
                "先读完整摘要，再填写结构化字段，最后回头润色 chinese_summary。",
                "如果某条信息无法仅凭摘要确认，写成保守表述，不要脑补。",
            ],
            "minimum_fields": REQUIRED_AGENT_FIELDS + OPTIONAL_AGENT_FIELDS,
            "style_rules": [
                "面向科研读者，避免营销式形容词。",
                "尽量保留物种、脑区、行为范式、记录技术、因果操作等关键实体。",
                "中文导读要比一句话摘要更具体，至少覆盖问题、方法、结果、意义四部分。",
            ],
        },
        "selected_papers": selected_papers,
    }


def render_agent_review_markdown(packet):
    lines = [
        "# Top 5 Review Packet",
        "",
        f"- Generated At: {packet.get('generated_at', '')}",
        f"- Candidate Count: {packet.get('candidate_count', 0)}",
        f"- Selected Indexes: {', '.join(str(value) for value in packet.get('selected_indexes', []))}",
        "",
        "> 先逐篇读摘要，再填写 JSON 中的结构化中文字段；最后再润色 `chinese_summary`，不要跳过 `chinese_methods` / `chinese_findings` / `chinese_significance`。",
        "",
    ]
    guidance = packet.get("agent_guidance", {})
    if guidance:
        lines.extend([
            "## Packet Guidance",
            "",
            f"- Goal: {guidance.get('goal', '')}",
            "- Recommended Process:",
        ])
        for step in guidance.get("recommended_process", []):
            lines.append(f"  - {step}")
        lines.append("- Style Rules:")
        for rule in guidance.get("style_rules", []):
            lines.append(f"  - {rule}")
        lines.extend(["", "## Required JSON Fields", ""])
        for field in guidance.get("minimum_fields", []):
            lines.append(f"- {field}")
        lines.append("")

    for paper in packet.get("selected_papers", []):
        lines.extend(
            [
                f"## Slot {paper['slot']}: {paper.get('title', '').strip() or '(untitled)'}",
                "",
                f"- Candidate Index: {paper['candidate_index']}",
                f"- Source: {paper.get('source', 'unknown')}",
                f"- Authors: {join_authors(paper.get('authors', []))}",
                f"- Published: {paper.get('published', '') or 'Unknown'}",
                f"- Journal: {paper.get('journal') or 'Unknown'}",
                f"- URL: {paper.get('url') or 'N/A'}",
                f"- PDF URL: {paper.get('pdf_url') or 'N/A'}",
                f"- Weighted Score: {paper.get('weighted_score', 'N/A')}",
                "",
                "### Focus Questions",
                "",
            ]
        )
        for question in paper.get("reader_guidance", {}).get("focus_questions", []):
            lines.append(f"- {question}")
        lines.extend(["", "### Writing Requirements", ""])
        for requirement in paper.get("reader_guidance", {}).get("writing_requirements", []):
            lines.append(f"- {requirement}")
        lines.extend(
            [
                "",
                "### Abstract",
                "",
                paper.get("abstract", "").strip() or "No abstract available.",
                "",
                "### JSON Fields To Fill",
                "",
                "- chinese_title:",
                "- chinese_summary:",
                "- chinese_background:",
                "- chinese_methods:",
                "- chinese_findings:",
                "- chinese_significance:",
                "- chinese_limitations:",
                "- selection_reason:",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_final_markdown(template_text, packet, generator_label):
    papers_blocks = []
    for paper in packet.get("selected_papers", []):
        papers_blocks.extend(
            [
                f"## {paper['slot']}. {paper.get('title', '').strip() or '(untitled)'}",
                "",
                f"- 中文标题：{paper.get('chinese_title', '').strip() or '待补充'}",
                f"- 来源：{paper.get('source', 'unknown')}",
                f"- 作者：{join_authors(paper.get('authors', []))}",
                f"- 发表时间：{paper.get('published', '') or '未知'}",
                f"- 入选理由：{paper.get('selection_reason', '').strip() or '待补充'}",
                f"- 文献链接：{paper.get('url') or '暂无'}",
                f"- PDF 链接：{paper.get('pdf_url') or '暂无'}",
                "",
                "### 中文导读",
                "",
                paper.get("chinese_summary", "").strip() or "待补充",
                "",
                "### 研究背景 / 核心问题",
                "",
                paper.get("chinese_background", "").strip() or "待补充",
                "",
                "### 方法速览",
                "",
                paper.get("chinese_methods", "").strip() or "待补充",
                "",
                "### 核心发现",
                "",
                paper.get("chinese_findings", "").strip() or "待补充",
                "",
                "### 意义与启发",
                "",
                paper.get("chinese_significance", "").strip() or "待补充",
                "",
                "### 局限与备注",
                "",
                paper.get("chinese_limitations", "").strip() or "待补充",
                "",
                "### 原始摘要",
                "",
                paper.get("abstract", "").strip() or "暂无摘要",
                "",
            ]
        )

    return (
        template_text.replace("{{generated_at}}", packet.get("generated_at", ""))
        .replace("{{candidate_count}}", str(packet.get("candidate_count", 0)))
        .replace("{{generator_label}}", generator_label)
        .replace("{{papers}}", "\n".join(papers_blocks).strip())
        .rstrip()
        + "\n"
    )


def ensure_agent_fields(packet):
    papers = packet.get("selected_papers", [])
    if not papers:
        raise SystemExit("Agent packet contains no selected papers.")
    for paper in papers:
        for field in REQUIRED_AGENT_FIELDS:
            if not str(paper.get(field, "")).strip():
                raise SystemExit(f"Missing `{field}` for slot {paper.get('slot', '?')}.")


def main():
    parser = argparse.ArgumentParser(description="Prepare or render a Top 5 neuroethology digest without calling an API.")
    parser.add_argument("--input", default="", help="Merged JSON generated by merge_results.py")
    parser.add_argument("--paper-indexes", default="", help="Comma-separated candidate indexes chosen by the agent")
    parser.add_argument("--agent-json-output", default="", help="Write the agent packet JSON here")
    parser.add_argument("--review-md-output", default="", help="Write the review packet Markdown here")
    parser.add_argument("--from-agent-json", default="", help="Render final digest from a completed agent packet JSON")
    parser.add_argument("--output", default="", help="Final Markdown output path")
    parser.add_argument("--template", default="", help="Markdown template path")
    parser.add_argument("--generator-label", default="same-agent", help="Label recorded in the final Markdown")
    args = parser.parse_args()

    if args.from_agent_json:
        if not args.output:
            raise SystemExit("`--output` is required when using `--from-agent-json`.")
        packet = load_json(args.from_agent_json)
        ensure_agent_fields(packet)
        template_path = Path(args.template) if args.template else Path(__file__).resolve().parents[1] / "assets" / "top5_digest_template.md"
        template_text = template_path.read_text(encoding="utf-8")
        markdown = render_final_markdown(template_text, packet, args.generator_label)
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        print(output_path)
        return

    if not args.input:
        raise SystemExit("`--input` is required when preparing an agent packet.")
    if not args.paper_indexes:
        raise SystemExit("`--paper-indexes` is required when preparing an agent packet.")
    if not args.agent_json_output and not args.review_md_output:
        raise SystemExit("Provide at least one of `--agent-json-output` or `--review-md-output`.")

    merged_payload = load_json(args.input)
    selected_indexes = parse_index_list(args.paper_indexes)
    packet = build_agent_packet(merged_payload, selected_indexes)

    if args.agent_json_output:
        json_output_path = Path(args.agent_json_output).expanduser().resolve()
        json_output_path.parent.mkdir(parents=True, exist_ok=True)
        json_output_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json_output_path)

    if args.review_md_output:
        review_output_path = Path(args.review_md_output).expanduser().resolve()
        review_output_path.parent.mkdir(parents=True, exist_ok=True)
        review_output_path.write_text(render_agent_review_markdown(packet), encoding="utf-8")
        print(review_output_path)


if __name__ == "__main__":
    main()
