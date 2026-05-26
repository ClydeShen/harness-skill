# Recommended Skill Collections

These are companion skill collections that significantly extend the compound engineering capability of a harness. Neither is required, but both are strongly recommended for long-running or autonomous work.

## GSD Redux

**Repo:** https://github.com/open-gsd/get-shit-done-redux
**What it provides:** A full compound engineering workflow — `/gsd`, `/gsd-plan`, `/gsd-execute`, `/gsd-verify`, `/gsd-doctor`, `/gsd-verdict`, and related skills for structured multi-day autonomous work.
**Detect:** Any `gsd-*` skill present in `~/.claude/skills/`
**Why it matters:** Without GSD Redux, long-running agents have no structured task tracking, no per-AC progress comments, and no built-in phase transitions. Sessions go off-rails faster.

## Superpowers

**Repo:** https://github.com/obra/superpowers
**What it provides:** Curated advanced skills: `brainstorming`, `systematic-debugging`, `writing-plans`, `subagent-driven-development`, `dispatching-parallel-agents`, and more.
**Detect:** Any of `brainstorming`, `systematic-debugging`, `writing-plans`, `subagent-driven-development` present in `~/.claude/skills/`
**Why it matters:** Without Superpowers, agents lack structured debugging protocols and parallel task dispatch, leading to linear, slower execution on complex problems.

## Detection logic

```
gsd_present = any skill matching gsd-* in ~/.claude/skills/
superpowers_present = any of [brainstorming, systematic-debugging, writing-plans, subagent-driven-development] in ~/.claude/skills/
```

Only surface the suggestion for absent collections. If both are installed, omit the section entirely from output.
