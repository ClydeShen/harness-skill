# ADR 0003: GSD File Structure Adoption

**Status:** Accepted

## Context

This collection used its own artifact locations (.claude/session.json, .claude/handoff.md,
.claude/harness.json) and its own phase vocabulary (Design/Product/Execution/Testing).
GSD Redux (open-gsd/get-shit-done-redux) uses .harness/STATE.md, .harness/phases/XX/,
and the verbs discuss/plan/execute/verify.

Users who adopt this collection and later install GSD face a migration. Users running both
simultaneously have two parallel session-state stores.

## Decision

This collection writes GSD-compatible artifacts from day one:
- .harness/STATE.md replaces .claude/session.json
- .harness/phases/XX/.continue-here.md replaces .claude/handoff.md
- .harness/config.json (harness namespace) replaces .claude/harness.json
- Phase vocabulary: discuss / plan / execute / verify

GSD ignores the `harness` namespace in config.json (unknown keys pass through).
When GSD is installed later, it reads the existing .harness/ artifacts directly.

## Consequences

- setup-harness-skills writes .harness/ in GSD format
- session-start reads STATE.md as the primary source and writes session_status on begin
- context-handover writes .continue-here.md in GSD format and session_status: idle on exit
- to-prd creates .harness/phases/01-discuss/CONTEXT.md
- to-issues creates .harness/phases/02-plan/PLAN.md + GitHub Issues
- harness-engineering extends gap detection for .harness/ and memory systems
- All skill evals updated: fixture scaffolds use .harness/ paths
- Old .claude/ artifacts (session.json, handoff.md, harness.json) are deprecated;
  setup-harness-skills migrates existing values on re-run
