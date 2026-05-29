---
name: Harness Issue
about: Feature, task, chore, or spike — follows the harness AC template
title: '[type]: '
labels: 'status:triage'
---
## Story
As a [role], I want [capability], so that [benefit].

## Confidence: AFK ✓ / HITL ⚠
> Agent confidence: **AFK** — all sources cited below.
> (or: **HITL** — missing: [specific gap description])

## Acceptance Criteria
| # | Criterion | Type | Source |
|---|---|---|---|
| 1 | Given X, when Y, then Z | happy path | Spec §N.N |
| 2 | Given X, when error, then W | sad path | User statement YYYY-MM-DD |

## Definition of Done
- [ ] All AC pass (verified by agent or CI)
- [ ] PR merged to main
- [ ] No regressions in related tests
- [ ] Implementation notes written if agent deviated from spec

## Effort
Estimate: **N context window(s)**

## Dependencies
Blocked by: #NNN / None
