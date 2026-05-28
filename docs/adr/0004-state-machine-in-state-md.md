# ADR 0004: STATE.md Session State Machine

**Status:** Accepted

## Context

`session-start` previously only *read* `.harness/STATE.md`. The file was written
exclusively by `context-handover` at the end of a clean session. This meant that
if a session was interrupted before context-handover fired, STATE.md was stale —
it reflected the state from the *previous* session's handover, not the interrupted
session's work.

For mid-session interruption recovery (no handover), the only durable signals were:
- GitHub per-AC progress comments (requires GitHub configured)
- `git log` (shows what code changed, not the agent's intent)

The memory system was also stale (only updated at context-handover), leaving a
gap in local recovery without GitHub.

Two options were considered:

**A. Read-only session-start.** Keep session-start as a reader only. Accept that
mid-session recovery depends on GitHub per-AC comments or cold git-log
reconstruction. Simpler, but breaks the "recovery at any interruption point"
requirement for GitHub-free setups.

**B. session-start writes a session-start record to STATE.md.** Session-start
writes `session_status: in_progress` and `session_started: <timestamp>` to the
Session Continuity section at the moment a session begins. context-handover
writes `session_status: idle` on clean exit. An interrupted session is detected
by the next session-start reading `in_progress` with a stale timestamp.

## Decision

Option B. STATE.md is treated as a state machine with two session-level states:

| State | Written by | Meaning |
|---|---|---|
| `in_progress` | `session-start` | Session is live |
| `idle` | `context-handover` | Clean exit; safe to resume |

Interrupted sessions are never explicitly marked — they are *inferred* by
`session-start` reading `in_progress` with a stale `session_started` timestamp.

The session state lives in the **Session Continuity** markdown section — not in
the YAML frontmatter `status` field, which is GSD's project-level status and must
not be overwritten.

When an interrupted session is detected, `session-start` outputs a **Recovery
briefing** that includes `git log --after=<session_started>` as a diff summary of
what changed during the interrupted session.

## Rationale

The `session_started` timestamp written at session-start becomes the git log
cutoff for interrupted recovery — giving the next session precise, scoped evidence
of what the interrupted session actually did. This makes recovery fully local
(no GitHub required), with the memory system as an additional recovery signal
when it has been updated.

Keeping the session state in the Session Continuity markdown section (not YAML
frontmatter) avoids any collision with GSD's project-level `status` field —
GSD reads and validates frontmatter, not markdown sections.

## Consequences

- `session-start` gains a write step: update STATE.md Session Continuity on begin.
- `context-handover` gains one additional write: set `session_status: idle`.
- `session-start` must distinguish clean resume (idle) from interrupted recovery
  (in_progress + stale timestamp) and emit different briefing output for each.
- One cross-skill integration eval added to `session-start.yaml`: scaffolds a
  STATE.md with `session_status: in_progress` + stale timestamp, asserts recovery
  briefing output includes git log diff summary.
- `session-start` evals (scenarios 1, 2, 3) require fixture updates: `state_md`
  replaces `session_json`, new `session_status` field.
