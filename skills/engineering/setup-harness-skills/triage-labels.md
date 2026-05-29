# Triage Labels

## Status labels

| Label | Meaning |
|---|---|
| `status:triage` | New issue — not yet assessed |
| `status:needs-prd` | Needs a PRD before stories can be written |
| `status:needs-review` | HITL: written but agent lacks confidence in ≥1 AC item — human must validate before execution |
| `status:needs-info` | Blocked on missing information from stakeholder |
| `status:ready-for-agent` | AFK: all AC traceable to cited sources, chain complete — agent can execute |
| `status:in-progress` | Agent is actively working on this issue |
| `status:done` | All AC pass, PR merged |
| `status:wontfix` | Closed without implementation |
| `status:ready-for-human` | Needs human action (code review, design decision) |

## Phase labels

| Label | Meaning |
|---|---|
| `phase:discuss` | discuss phase work (spec, ADR, discovery) |
| `phase:plan` | plan phase work (PRD, story breakdown) |
| `phase:execute` | execute phase work (implementation) |
| `phase:verify` | verify phase work (QA, issue filing) |

## Type labels

| Label | Meaning |
|---|---|
| `type:feature` | New user-facing capability |
| `type:bug` | Defect in existing functionality |
| `type:chore` | Non-functional maintenance (deps, config, cleanup) |
| `type:task` | Internal task with no direct user impact |
| `type:spike` | Throwaway investigation — 1–2 context windows (~150K–400K tokens), AFK, discarded after decision is made |

## Priority labels

| Label | Meaning |
|---|---|
| `priority:p1` | Must fix before release |
| `priority:p2` | Important but not blocking |
| `priority:p3` | Nice to have |

## Status flow

```
triage → needs-prd → [needs-review | ready-for-agent] → in-progress → done
```

- `needs-review`: HITL. Human validates AC sources, then relabels to `ready-for-agent`.
- `ready-for-agent`: AFK (agent confident) or human-approved from `needs-review`.
