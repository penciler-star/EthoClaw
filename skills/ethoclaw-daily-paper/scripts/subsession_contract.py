#!/usr/bin/env python3
import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def init_contract(base_dir: Path, run_name: str):
    run_dir = (base_dir / run_name).resolve()
    work_dir = run_dir / "work"
    return_dir = run_dir / "return"
    contract_path = run_dir / "run_contract.json"
    final_markdown_path = return_dir / "final_digest.md"
    final_summary_path = return_dir / "final_summary.json"

    work_dir.mkdir(parents=True, exist_ok=True)
    return_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": 1,
        "skill": "ethoclaw-daily-paper",
        "created_at": now_iso(),
        "run_name": run_name,
        "status": "initialized",
        "paths": {
            "run_dir": str(run_dir),
            "work_dir": str(work_dir),
            "return_dir": str(return_dir),
            "contract": str(contract_path),
            "final_markdown": str(final_markdown_path),
            "final_summary": str(final_summary_path),
            "merged_json": str(work_dir / "merged.json"),
            "candidate_titles": str(work_dir / "candidate_titles.md"),
            "candidate_pool": str(work_dir / "candidate_pool.md"),
            "agent_packet_json": str(work_dir / "top5_agent_packet.json"),
            "agent_packet_md": str(work_dir / "top5_agent_packet.md"),
        },
        "parent_session_contract": {
            "read_only": [
                str(final_markdown_path),
                str(final_summary_path),
            ],
            "do_not_read_by_default": [
                str(work_dir / "candidate_titles.md"),
                str(work_dir / "candidate_pool.md"),
                str(work_dir / "top5_agent_packet.md"),
                str(work_dir / "top5_agent_packet.json"),
                str(work_dir / "merged.json"),
            ],
            "return_message": "Subsession complete. Read return/final_digest.md and return/final_summary.json only.",
        },
        "notes": [
            "Run retrieval, ranking, and drafting inside the subsession.",
            "Keep intermediate candidate artifacts under work/.",
            "Copy only the final markdown and concise summary into return/.",
        ],
    }
    write_json(contract_path, payload)
    return payload


def finalize_contract(contract_path: Path, digest_path: Path, selected_indexes: str, methodology_note: str, generator_label: str):
    contract = load_json(contract_path)
    final_markdown_path = Path(contract["paths"]["final_markdown"]).expanduser().resolve()
    final_summary_path = Path(contract["paths"]["final_summary"]).expanduser().resolve()

    source_digest = digest_path.expanduser().resolve()
    if not source_digest.exists():
        raise SystemExit(f"Digest file not found: {source_digest}")

    final_markdown_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_digest, final_markdown_path)

    summary = {
        "schema_version": 1,
        "skill": contract.get("skill", "ethoclaw-daily-paper"),
        "status": "completed",
        "completed_at": now_iso(),
        "generator_label": generator_label,
        "selected_indexes": [int(part.strip()) for part in selected_indexes.split(",") if part.strip()] if selected_indexes else [],
        "final_markdown": str(final_markdown_path),
        "methodology_note": methodology_note.strip(),
        "recommended_parent_reply": "Read final_digest.md only unless the user explicitly asks for candidate details.",
    }
    write_json(final_summary_path, summary)

    contract["status"] = "completed"
    contract["completed_at"] = summary["completed_at"]
    contract["finalized"] = {
        "final_markdown": str(final_markdown_path),
        "final_summary": str(final_summary_path),
        "selected_indexes": summary["selected_indexes"],
        "generator_label": generator_label,
    }
    write_json(contract_path, contract)
    return {"contract": contract, "summary": summary}


def main():
    parser = argparse.ArgumentParser(description="Create or finalize the standard subsession output contract.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a standard subsession run directory")
    init_parser.add_argument("--base-dir", required=True, help="Base directory under which the run directory will be created")
    init_parser.add_argument("--run-name", required=True, help="Run directory name, e.g. 20260316-am")

    finalize_parser = subparsers.add_parser("finalize", help="Copy final digest into return/ and write summary JSON")
    finalize_parser.add_argument("--contract", required=True, help="Path to run_contract.json")
    finalize_parser.add_argument("--digest", required=True, help="Rendered final markdown to copy into return/final_digest.md")
    finalize_parser.add_argument("--selected-indexes", default="", help="Comma-separated selected indexes")
    finalize_parser.add_argument("--methodology-note", default="Retrieved, ranked, and drafted within the subsession.", help="Short note for the parent session")
    finalize_parser.add_argument("--generator-label", default="subsession-agent", help="Short provenance label for the summary")

    args = parser.parse_args()

    if args.command == "init":
        payload = init_contract(Path(args.base_dir).expanduser().resolve(), args.run_name)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if args.command == "finalize":
        payload = finalize_contract(
            Path(args.contract).expanduser().resolve(),
            Path(args.digest),
            args.selected_indexes,
            args.methodology_note,
            args.generator_label,
        )
        print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
