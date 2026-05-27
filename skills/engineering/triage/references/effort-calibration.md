# Effort Calibration

Effort unit = token budget consumed in one execution session.

| Effort | Token budget | What fits |
|---|---|---|
| 1 | 30K–60K | Single vertical slice: 1 file change + test cycle |
| 2 | 80K–150K | 1 GSD phase (discuss+plan OR execute+verify) |
| 3 | 200K–300K | 2–3 GSD phases: full feature end-to-end |
| 4+ | 300K–600K | Epic — requires multi-window handoff |

Adjustment factors:
- Tool-heavy (bash/grep outputs): ×1.3–1.5
- Code-read-heavy (large file traversal): ×1.2–1.5
- Pure reasoning/planning: ×0.9

Practical limit: Sonnet 4.6 working window ≈ 150K–180K tokens before context rot.
Compaction at ~90% usage. Run /context-handover before 80%.
