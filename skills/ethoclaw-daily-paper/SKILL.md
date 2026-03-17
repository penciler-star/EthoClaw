---
name: ethoclaw-daily-paper
description: "Search arXiv and PubMed for neuroethology and behavioral neuroscience papers, merge the candidate pool, prepare title-only and abstract review packets for in-agent ranking, and render a final Chinese Markdown digest without using an external summarization API. Use when Codex needs a reusable neuroethology literature-monitoring workflow, especially when it should run retrieval and digest assembly in an automatically spawned sub-session/subagent so the main session reads only the final Markdown deliverable."
---

# Neuroethology Top5 Digest

Use the bundled scripts. Keep the parent conversation lean.

## Default operating mode

Prefer a two-layer workflow:

- **Main session**: define scope, spawn the sub-session/subagent, then read only the final deliverable in `return/`.
- **Sub-session**: run retrieval, inspect candidates, choose Top 5, write the Chinese导读, render the final digest, and finalize the return contract.

Do **not** bounce `candidate_pool.md`, full abstract packets, or large intermediate JSON back to the main session unless the user explicitly asks.

## Main session responsibilities

1. Decide whether the default config is enough or whether query constraints must change.
2. Create a run directory contract:

```bash
python3 scripts/subsession_contract.py init \
  --base-dir ./runs \
  --run-name 20260316-am
```

3. Spawn a dedicated sub-session/subagent and give it the generated `run_contract.json` path.
4. Tell the sub-session to work inside the contract's `work/` and `return/` directories.
5. After completion, read only:
   - `return/final_digest.md`
   - `return/final_summary.json` (optional, small)

If you need a ready-made wording skeleton for the spawned task, adapt `assets/subsession_task_template.md`.

## Sub-session responsibilities

Inside the spawned sub-session:

1. Read `run_contract.json`.
2. Keep all intermediate artifacts in `work/`.
3. Run retrieval and candidate preparation.
4. Rank candidates inside the sub-session.
5. Build / fill the agent packet.
6. Render the final digest.
7. Finalize the contract so the parent session has a stable return location.
8. Return only the final artifact paths and a short methodology note.

## Standard contract layout

`subsession_contract.py init` creates:

- `run_contract.json`
- `work/merged.json`
- `work/candidate_titles.md`
- `work/candidate_pool.md`
- `work/top5_agent_packet.json`
- `work/top5_agent_packet.md`
- `return/final_digest.md`
- `return/final_summary.json`

Interpretation:

- `work/` = sub-session private workspace
- `return/` = parent-readable handoff only

This boundary is intentional. Treat `return/` as the only default interface back to the main session.

## Quick start inside the sub-session

Run retrieval and candidate preparation into the contract work directory:

```bash
python3 scripts/run_pipeline.py --output-dir ./runs/20260316-am/work
```

If you already know the selected indexes, prepare the packet in one step:

```bash
python3 scripts/run_pipeline.py \
  --output-dir ./runs/20260316-am/work \
  --selected-indexes 1,2,3,4,5
```

If indexes are chosen later, generate the review packet manually:

```bash
python3 scripts/build_top5_digest.py \
  --input ./runs/20260316-am/work/merged.json \
  --paper-indexes 1,2,3,4,5 \
  --agent-json-output ./runs/20260316-am/work/top5_agent_packet.json \
  --review-md-output ./runs/20260316-am/work/top5_agent_packet.md
```

After the packet is filled, render the final digest:

```bash
python3 scripts/build_top5_digest.py \
  --from-agent-json ./runs/20260316-am/work/top5_agent_packet.json \
  --output ./runs/20260316-am/work/top5_digest.md \
  --generator-label subsession-agent
```

Finalize the parent-facing handoff:

```bash
python3 scripts/subsession_contract.py finalize \
  --contract ./runs/20260316-am/run_contract.json \
  --digest ./runs/20260316-am/work/top5_digest.md \
  --selected-indexes 1,2,3,4,5 \
  --methodology-note "Retrieved, ranked, and drafted inside the subsession; main session should read only the final markdown."
```

## Recommended end-to-end sub-session workflow

1. Review `assets/config.template.yaml` if the user wants narrower or broader coverage.
2. Run `scripts/run_pipeline.py` into `work/`.
3. Read `work/candidate_titles.md` for quick ranking.
4. Read `work/candidate_pool.md` only inside the sub-session when abstracts are needed.
5. Choose the best papers.
6. Create or complete `work/top5_agent_packet.json`.
7. Render `work/top5_digest.md`.
8. Finalize to `return/final_digest.md` and `return/final_summary.json`.
9. Tell the parent session only that the run is complete and where those two files are.

## Resources

### `scripts/subsession_contract.py`

- Use `init` to create a stable run directory and output contract.
- Use `finalize` to copy the final digest into `return/` and emit a concise parent-facing summary JSON.
- Use when the main session should read only final markdown instead of the candidate pool.

### `assets/subsession_task_template.md`

- Use as a concise template for the main session when spawning a sub-session/subagent.
- Adapt paths and run names; keep the boundary rules intact.

### `scripts/run_pipeline.py`

- Use as the one-shot retrieval entry point.
- Write `arxiv.json`, `pubmed.json`, `merged.json`, `candidate_pool.md`, and `candidate_titles.md` into the chosen output directory.
- Optionally write `top5_agent_packet.json` and `top5_agent_packet.md` when `--selected-indexes` is provided.

### `scripts/search_arxiv.py`, `scripts/search_pubmed.py`, `scripts/merge_results.py`, `scripts/common.py`

- Keep retrieval and merge logic self-contained inside the skill.
- Reuse them directly if you need partial reruns or debugging.

### `scripts/build_top5_digest.py`

- Build the selected-paper packet after choosing candidate indexes.
- Add per-paper guidance prompts so the sub-session can write richer Chinese导读 with less repeated thinking.
- Render the final Markdown with `assets/top5_digest_template.md` after the JSON packet is completed.
- Do not call any external summarization API; the agent/sub-session performs the reading and writing.

### `assets/config.template.yaml`

- Tune search queries, include and exclude keywords, and source weights.

### `assets/top5_digest_template.md`

- Use as the final Markdown wrapper.
- Keep placeholder names unchanged unless the rendering script changes too.

## Writing guidance for Chinese导读

When filling the packet, do not stop at a one-paragraph generic summary.

For each paper:

- explain the core question in plain but precise Chinese
- mention species / brain region / behavioral paradigm / recording or manipulation method when available
- state the main findings concretely, not just “the study found important differences”
- explain why it matters for neuroethology or behavioral neuroscience
- mention uncertainty or limitations when the abstract alone is insufficient

Keep `chinese_summary` as the polished overview, and use the structured fields to preserve detail.

## Notes

- Use `python3` explicitly on this machine.
- Keep PubMed weighting above arXiv when the user wants published papers to outrank preprints.
- Avoid pushing intermediate candidate content back to the parent session by default.
- Do not call an external summarization API; the reading-and-writing step is intentionally performed by the current agent/sub-session.
