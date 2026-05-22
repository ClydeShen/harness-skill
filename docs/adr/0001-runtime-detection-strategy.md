# ADR 0001: Runtime Detection Strategy

**Status:** Accepted

## Context

The skill needs to adapt its output for multiple agent runtimes (Claude Code, Codex, Kiro, Gemini). Three options were considered:

- **A. Default to Claude Code.** No detection. Always output `.claude/settings.json` snippets. Non-Claude users get a best-effort note.
- **B. Always ask.** Consume a Phase 2 question slot unconditionally to ask "which runtime are you on?" Costs an interview slot for the majority case (Claude Code users who already have `.claude/`).
- **C. File-system first, question only when ambiguous.** Detect via directory presence (`.claude/`, `.kiro/`, `.gemini/`). Consume the Q2 slot only when no signal is found. (Chosen)

## Decision

Option C. Phase 1 gains a step 0 that checks for runtime-specific directories. If a runtime is detected, proceed with adapted snippets. If none found, the Phase 2 Q2 slot is replaced with a runtime question; the brownfield sub-question fires only after runtime is confirmed.

## Rationale

The majority of users will have `.claude/` already (they are Claude Code users invoking a Claude Code skill). Paying an interview question for the majority case degrades the experience unnecessarily. File-system detection is free — it runs during the Phase 1 scan that already happens.

## Consequences

- Phase 1 step 0 must check `.claude/`, `.kiro/`, `.gemini/` before any other check.
- Q2 becomes conditional: runtime question fires when step 0 is inconclusive; brownfield question fires when runtime is confirmed.
- Projects with none of these directories (truly new setup) will always consume Q2 for runtime — acceptable because first-time setup is the edge case, not the common path.
