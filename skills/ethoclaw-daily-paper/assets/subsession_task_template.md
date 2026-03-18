Run `skills/ethoclaw-daily-paper` in an independent sub-session, with the goal of only returning the final draft to the main session, not sending candidate pool details back.

Constraints:
1. First execute `python3 scripts/subsession_contract.py init --base-dir <runs-dir> --run-name <run-name>`, use the generated `work/` and `return/` directories.
2. All retrieval, intermediate candidate lists, and agent packets must be written to `work/`.
3. Complete screening, English summary writing, and final markdown rendering within the sub-session.
4. After completion, execute `python3 scripts/subsession_contract.py finalize --contract <run_contract.json> --digest <top5_digest.md> --selected-indexes <idxs> --methodology-note <short-note>`.
5. When returning to the main session, only report:
   - `return/final_digest.md`
   - `return/final_summary.json`
6. Unless the main session explicitly asks, do not paste `candidate_pool.md`, `top5_agent_packet.md/json`, or full candidate title list content.

Suggested main session reading method: only read `final_digest.md`, if necessary read `final_summary.json` to understand provenance / selected indexes / methodology note.
