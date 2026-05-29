---
name: write-harness-skill
description: Create new harness-compatible agent skills with proper structure, progressive disclosure, and bundled resources — includes harness-specific checklist (token budget, setup-harness-skills reference, AI footer, creation gates). Use when user wants to create, write, or build a new skill.
---

# Writing Skills

## Gotchas

- **Generic description** — "Helps with X" gives the agent no way to distinguish this skill. Always include a concrete `Use when [specific triggers]` clause with keywords the agent will see in real requests.
- **Missing trigger keywords** — if the description omits the words users naturally say ("triage", "handover", "cleanup"), the skill never loads. Test: would the description match the user's message verbatim?
- **Over-stuffed SKILL.md** — dumping all edge cases into SKILL.md causes the agent to pursue unproductive paths. Move rarely-needed content to `references/` and add a conditional load instruction ("read `references/X.md` if Y").
- **No working example** — a template or inline snippet is more reliable than prose description. If the output has a fixed structure, show it.
- **Stale harness references** — skills that read setup config (issue tracker, labels, board) must include "run `/setup-harness-skills` if missing context" or they silently fail on unconfigured projects.

---

## Process

1. **Gather requirements** - ask user about:
   - What task/domain does the skill cover?
   - What specific use cases should it handle?
   - Does it need executable scripts or just instructions?
   - Any reference materials to include?

2. **Draft the skill** - create:
   - SKILL.md with concise instructions
   - Additional reference files if content exceeds 500 lines
   - Utility scripts if deterministic operations needed

3. **Review with user** - work through the Review Checklist below against the draft, then ask:
   - Does this cover your use cases?
   - Anything missing or unclear?
   - Should any section be more/less detailed?

## Skill Structure

```
skill-name/
├── SKILL.md           # Main instructions (required)
├── REFERENCE.md       # Detailed docs (if needed)
├── EXAMPLES.md        # Usage examples (if needed)
└── scripts/           # Utility scripts (if needed)
    └── helper.js
```

## SKILL.md Template

```md
---
name: skill-name
description: Brief description of capability. Use when [specific triggers].
---

# Skill Name

## Quick start

[Minimal working example]

## Workflows

[Step-by-step processes with checklists for complex tasks]

## Advanced features

[Link to separate files: See [REFERENCE.md](REFERENCE.md)]
```

## Description Requirements

The description is **the only thing your agent sees** when deciding which skill to load. It's surfaced in the system prompt alongside all other installed skills. Your agent reads these descriptions and picks the relevant skill based on the user's request.

**Goal**: Give your agent just enough info to know:

1. What capability this skill provides
2. When/why to trigger it (specific keywords, contexts, file types)

**Format**:

- Max 1024 chars
- Write in third person
- First sentence: what it does
- Second sentence: "Use when [specific triggers]"

**Good example**:

```
Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
```

**Bad example**:

```
Helps with documents.
```

The bad example gives your agent no way to distinguish this from other document skills.

## When to Add Scripts

Add utility scripts when:

- Operation is deterministic (validation, formatting)
- Same code would be generated repeatedly
- Errors need explicit handling

Scripts save tokens and improve reliability vs generated code.

## When to Split Files

Split into separate files when:

- SKILL.md exceeds 500 lines
- Content has distinct domains (finance vs sales schemas)
- Advanced features are rarely needed

If the user requests "thorough", "comprehensive", or "detailed" content, or explicitly lists many topics (5+), plan to use reference files from the start — do not try to fit all content into SKILL.md.

## Review Checklist

After drafting, verify:

- [ ] Description includes triggers ("Use when...")
- [ ] SKILL.md under 500 lines
- [ ] No time-sensitive info
- [ ] Consistent terminology
- [ ] Concrete examples included
- [ ] References one level deep
- [ ] Does the skill's description mention its typical token budget? (e.g. "typically consumes ~5K–10K tokens / <5% of a context window")
- [ ] If the skill reads setup config (issue tracker, labels, GitHub board), does it include "run `/setup-harness-skills` if missing context"?
- [ ] If the skill posts any comment or body to the issue tracker, does every post end with the AI-generated footer (`🤖 Posted by /[skill-name] (AI-generated)`)?
- [ ] If the skill creates issues, does it enforce all three creation gates: (1) Estimable, (2) ≤8 context windows (8 sessions of focused work — beyond this, handoff drift compounds), (3) demoable user-facing outcome?
