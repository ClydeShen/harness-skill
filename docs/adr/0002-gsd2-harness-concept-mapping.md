# ADR 0002: gsd-2 Harness-Concept Mapping

**Status:** Accepted

## Context

gsd-2 exposes commands that overlap with existing harness gaps the skill detects:

- `/gsd doctor` — runtime health checks (same failure mode as `init.sh`)
- `/gsd verdict` — milestone validation (same failure mode as the Judge audit pattern)
- `/gsd status` — progress dashboard (session tracking)

Two integration depths were considered:

- **A. Substitution table fix only.** Update deprecated skill names in the CLAUDE.md substitution table. Gap list is unchanged regardless of whether gsd-2 is installed.
- **B. Substitution fix + harness-concept mapping.** When gsd-2 is detected, commands that cover existing gaps conditionally close those gaps — the gap list gets shorter for gsd-2 users. (Chosen)

## Decision

Option B. When gsd-2 is detected in Phase 1 step 10, the following gaps are treated as conditionally closed:

| Gap | Closed by |
|---|---|
| `init.sh` absent | `/gsd doctor` |
| Judge audit (long-task exit criterion) | `/gsd verdict` |

Phase 3 output notes the closure explicitly ("init.sh gap closed — `/gsd doctor` covers this") rather than silently omitting the gap.

## Rationale

`/gsd doctor` and `/gsd verdict` cover the same failure modes as `init.sh` and the Judge audit with fewer moving parts — Occam's Razor. Pretending the gap is open when gsd-2 already closes it produces misleading output and encourages duplication.

Stating the closure explicitly (rather than silently dropping the gap) preserves transparency: users who later remove gsd-2 understand why the gap reappears.

## Consequences

- Phase 3 output logic must check for gsd-2 detection before rendering the `init.sh` and Judge audit gaps.
- The "Already in place" section gains entries for gsd-2 users: "init.sh: covered by `/gsd doctor`" and "Judge audit: covered by `/gsd verdict`".
- Future gsd-2 commands that cover other gaps (e.g., `/gsd forensics` for session recovery) can be added to this mapping without structural changes.
