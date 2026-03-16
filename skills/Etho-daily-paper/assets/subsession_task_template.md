在独立子会话中运行 `skills/Etho-daily-paper`，目标是只把最终成稿返回主会话，不回传候选池细节。

约束：
1. 先执行 `python3 scripts/subsession_contract.py init --base-dir <runs-dir> --run-name <run-name>`，使用生成的 `work/` 与 `return/` 目录。
2. 所有检索、中间候选列表、agent packet 一律写入 `work/`。
3. 子会话内部完成筛选、中文导读撰写和最终 markdown 渲染。
4. 完成后执行 `python3 scripts/subsession_contract.py finalize --contract <run_contract.json> --digest <top5_digest.md> --selected-indexes <idxs> --methodology-note <short-note>`。
5. 回给主会话时，只报告：
   - `return/final_digest.md`
   - `return/final_summary.json`
6. 除非主会话明确追问，不要粘贴 `candidate_pool.md`、`top5_agent_packet.md/json` 或完整候选标题列表内容。

建议主会话读取方式：只读 `final_digest.md`，必要时再读 `final_summary.json` 了解 provenance / selected indexes / methodology note。
