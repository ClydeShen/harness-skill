# harness-skill

This repository is a harness for agent skills.

## Important

- The root `SKILL.md` is intentionally left empty for user-managed content.

## Best-practice structure (Claude Code SKILL + OpenAI SKILL)

Use one folder per skill and keep each skill self-contained:

```text
skills/
  <skill-name>/
    SKILL.md
    README.md (optional)
    helpers/ (optional)
```

Recommended `skills/<skill-name>/SKILL.md` conventions:

- Include YAML frontmatter (`name`, `description`).
- Define clear purpose, prerequisites, and step-by-step actions.
- Document failure modes and recovery actions.
- Keep helper/script paths relative to the skill folder.
- Keep instructions deterministic and tool-friendly.
