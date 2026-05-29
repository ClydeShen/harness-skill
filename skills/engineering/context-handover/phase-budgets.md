# Phase Budgets

Used by both `/context-handover` (handoff content) and `/session-start` (session briefing).

---

## discuss

### Session budget
| Activity | Budget |
|---|---|
| Reading prior context | <10% |
| User/agent dialogue | <20% |
| Main output (spec, ADR, decisions) | <40% |
| Review | <10% |
| Memory update | <5% |
| Handover | <5% |

### Handoff focuses on
- Decisions made this session (cite spec section or user statement)
- Open questions that remain unresolved
- Next document to write (path)
- Suggested skills: `grill-with-docs`, `brainstorming`, `writing-plans`

---

## plan

### Session budget
| Activity | Budget |
|---|---|
| Reading prior context | <20% |
| Main output (PRD, story breakdown) | <40% |
| Review | <10% |
| Memory update | <5% |
| Handover | <5% |

### Handoff focuses on
- Stories broken down so far (issue numbers)
- Next story to write or refine
- Effort remaining (context windows; 1 = ~150K–200K tokens)
- Any HITL stories pending human review (`status:needs-review`)
- Suggested skills: `to-prd`, `to-issues`

---

## execute

### Session budget
| Activity | Budget |
|---|---|
| Reading prior context | <20% |
| Main output (code, tests) | <40% |
| Review | <10% |
| Memory update | <5% |
| Handover | <5% |

### Handoff focuses on
- Code written this session (file paths, not content)
- Test status (passing / failing / not yet written)
- Next file or function to implement
- AC items completed vs remaining (reference GitHub issue #N)
- Suggested skills: `systematic-debugging`, `zoom-out`

---

## verify

### Session budget
| Activity | Budget |
|---|---|
| Reading prior context | <20% |
| Main output (test execution, issue filing) | <40% |
| Review | <20% |
| Memory update | <5% |
| Handover | <5% |

### Handoff focuses on
- Issues found this session (GitHub issue numbers)
- Root causes identified
- Next test case to run
- Open `priority:p1` bugs remaining
- Suggested skills: `systematic-debugging`

---

## Handoff doc format

```markdown
Last updated: YYYY-MM-DD HH:mm

## Phase
[discuss / plan / execute / verify]

## Active task
Issue: #N — [title]
Effort remaining: ~N context window(s) (token budget: 1 = ~150K–200K)

## This session
[1–3 sentences: what was done]

## Next step
[Specific pick-up point — concrete enough for a fresh agent]

## Open questions
- [any unresolved decisions]

## Suggested skills
- [skill names relevant to next session]

## Key decisions
[Only present when no memory system is active — move to memory system otherwise]
```
