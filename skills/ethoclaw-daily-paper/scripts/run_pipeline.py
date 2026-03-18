#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import load_config  # noqa: E402


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
DEFAULT_CONFIG = SKILL_DIR / "assets" / "config.template.yaml"


def coerce_float(value, default):
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def run_command(command, cwd):
    subprocess.run(command, cwd=str(cwd), check=True)


def join_values(values, limit=None):
    if not values:
        return "Unknown"
    selected = values[:limit] if limit else values
    return ", ".join(selected)


def render_candidate_titles(payload):
    lines = [
        "# Candidate Titles Passed to Agent",
        "",
        f"- Generated At: {payload.get('generated_at', '')}",
        f"- Candidate Count: {payload.get('count', 0)}",
        "",
    ]
    for index, item in enumerate(payload.get("items", []), start=1):
        source = item.get("source_label") or item.get("source", "unknown")
        published = item.get("published", "")[:10] or "unknown"
        lines.append(f"{index}. [{source}] {item.get('title', '').strip() or '(untitled)'} ({published})")
    return "\n".join(lines).rstrip() + "\n"


def render_candidate_pool(payload):
    lines = [
        "# Neuroethology Candidate Pool",
        "",
        f"- Generated At: {payload.get('generated_at', '')}",
        f"- Candidate Count: {payload.get('count', 0)}",
        "",
    ]
    for index, item in enumerate(payload.get("items", []), start=1):
        lines.extend(
            [
                f"## {index}. {item.get('title', '').strip() or '(untitled)'}",
                "",
                f"- Source: {item.get('source_label') or item.get('source', 'unknown')}",
                f"- Authors: {join_values(item.get('authors', []), limit=10)}",
                f"- Published: {item.get('published', '')[:10] or 'Unknown'}",
                f"- Journal: {item.get('journal') or 'Unknown'}",
                f"- Article Link: {item.get('url') or 'N/A'}",
                f"- PDF Link: {item.get('pdf_url') or 'N/A'}",
                f"- Weighted Score: {item.get('weighted_score', 'Unknown')}",
                "",
                "### Original Abstract",
                "",
                item.get("summary", "").strip() or "No abstract available",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run the full neuroethology Top 5 literature workflow.")
    parser.add_argument("--query-file", default="", help="Config file path")
    parser.add_argument("--output-dir", required=True, help="Directory for all generated files")
    parser.add_argument("--days", type=int, default=7, help="Recency window in days")
    parser.add_argument("--selected-indexes", default="", help="Comma-separated candidate indexes chosen by the agent")
    args = parser.parse_args()

    config_path = Path(args.query_file).expanduser().resolve() if args.query_file else DEFAULT_CONFIG
    config = load_config(str(config_path))

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    arxiv_output = output_dir / "arxiv.json"
    pubmed_output = output_dir / "pubmed.json"
