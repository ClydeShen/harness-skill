# Effort Calibration

Effort unit = effective token budget consumed per execution session.

Context window sizes (Claude Code, as of 2026): Opus 4.x / Sonnet 4.6 = 1M tokens technical limit.
Effective working limit before context rot ≈ 150K–180K tokens of active tool use.
Source: https://support.claude.com/en/articles/8606394-how-large-is-the-context-window-on-paid-claude-plans

| Effort | Effective token budget | What fits |
|---|---|---|
| 1 | ~150K–200K | Single vertical slice: 1 file change + test cycle |
| 2 | ~300K–400K | 1 GSD phase (discuss+plan OR execute+verify) |
| 3 | ~500K–700K | 2–3 GSD phases: full feature end-to-end |
| 4+ | >700K | Epic — requires multi-window handoff |

Adjustment factors:
- Tool-heavy (bash/grep outputs): ×1.3–1.5
- Code-read-heavy (large file traversal): ×1.2–1.5
- Pure reasoning/planning: ×0.9

Maximum: 8 effort windows per issue (≈ 8 sessions). Above this, handoff drift compounds and original intent becomes unrecoverable.
Run /context-handover before 80% usage.
