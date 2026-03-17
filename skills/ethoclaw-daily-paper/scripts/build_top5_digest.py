#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


REQUIRED_AGENT_FIELDS = [
    "title",
    "summary",
    "methods",
    "findings",
    "significance",
    "selection_reason",
]

OPTIONAL_AGENT_FIELDS = [
    "background",
    "limitations",
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
            "What is the core scientific question this article aims to address?",
            "What experimental paradigm, recording/imaging/behavior paradigm, or analytical methods did the authors use?",
            "What are the most critical results, and is the evidence sufficiently direct?",
            "What is the significance of these findings for neuroethology or behavioral neuroscience?",
            "What are the boundary conditions, limitations, or unresolved issues?",
        ],
        "writing_requirements": [
            f"First provide an accurate, natural title, retaining key information such as species, brain region, task paradigm, etc.",
            f"Write a 120-220 word comprehensive summary, avoid empty evaluations, prioritize summarizing research question, methods, main findings, and significance.",
            f"Methods overview in 1-2 sentences, highlighting sample/species, main technical approach, behavioral task or data analysis methods.",
            f"Core findings in 2-4 sentences, clearly describing causal chains, comparative relationships, or key quantitative trends, not just repeating the title.",
            f"Significance section explains why it's worth reading, especially what insights it offers for recent work like {source} / {published}.",
            "If the abstract itself has limited evidence, clearly state limitations or places that need reading the full article to confirm.",
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
                "title": "",
                "summary": "",
                "background": "",
                "methods": "",
                "findings": "",
                "significance": "",
                "limitations": "",
                "selection_reason": "",
            }
        )

    return {
        "generated_at": merged_payload.get("generated_at", ""),
        "candidate_count": merged_payload.get("count", 0),
        "selected_indexes": selected_indexes,
        "agent_guidance": {
            "goal": "Read the selected abstracts and produce detailed, readable summaries for each candidate paper.",
            "recommended_process": [
                "Preferably complete candidate screening and abstract writing in independent sub-sessions, with the main session only receiving final drafts to reduce token consumption.",
                "First read the complete abstract, then fill in structured fields, finally polish the summary.",
                "If certain information cannot be confirmed from the abstract alone, write conservative statements, do not speculate.",
            ],
            "minimum_fields": REQUIRED_AGENT_FIELDS + OPTIONAL_AGENT_FIELDS,
            "style_rules": [
                "Target scientific readers, avoid marketing-style adjectives.",
                "Try to retain key entities such as species, brain region, behavioral paradigm, recording techniques, causal manipulations, etc.",
                "Summary should be more specific than one-sentence abstracts, covering at least question, methods, results, and significance.",
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
        "> First read each abstract, then fill in the structured JSON fields; finally polish the `summary`, do not skip `methods` / `findings` / `significance`.",
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
                "- title:",
                "- summary:",
                "- background:",
                "- methods:",
                "- findings:",
                "- significance:",
                "- limitations:",
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
                f"- Title: {paper.get('title', '').strip() or 'To be added'}",
                f"- Source: {paper.get('source', 'unknown')}",
                f"- Authors: {join_authors(paper.get('authors', []))}",
                f"- Published: {paper.get('published', '') or 'Unknown'}",
                f"- Selection Reason: {paper.get('selection_reason', '').strip() or 'To be added'}",
                f"- Article Link: {paper.get('url') or 'N/A'}",
                f"- PDF Link: {paper.get('pdf_url') or 'N/A'}",
                "",
                "### Summary",
                "",
                paper.get("summary", "").strip() or "To be added",
                "",
                "### Research Background / Core Question",
                "",
                paper.get("background", "").strip() or "To be added",
                "",
                "### Methods Overview",
                "",
                paper.get("methods", "").strip() or "To be added",
                "",
                "### Key Findings",
                "",
                paper.get("findings", "").strip() or "To be added",
                "",
                "### Significance & Insights",
                "",
                paper.get("significance", "").strip() or "To be added",
                "",
                "### Limitations & Notes",
                "",
                paper.get("limitations", "").strip() or "To be added",
                "",
                "### Original Abstract",
                "",
                paper.get("abstract", "").strip() or "No abstract available",
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
