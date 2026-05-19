# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repo maintains the `harness-engineering` skill — an interactive diagnostic tool that detects harness gaps in a project and produces paste-ready config snippets to close them. It is packaged as a Claude Code marketplace plugin.

## Skill Structure

```
skills/harness-engineering/
  SKILL.md                   ← main skill: detect → interview → output flow
  helpers/
    detect.md                ← gap classification and detection interpretation
    universal-snippets.md    ← .claude/settings.json, init.sh, CI, CLAUDE.md template
    node-snippets.md         ← Node/TS paste-ready configs
    python-snippets.md       ← Python paste-ready configs
```

Root `SKILL.md` stays empty (per README). Evals live in `evals/evals.json`.

## Evals

`evals/evals.json` defines the acceptance criteria for this skill. When modifying any skill file, verify the updated skill would still produce passing responses for all eval prompts before committing.

## Engineering Standards

`2026-05-18-m1-engineering-standards.md` is the canonical Node/TS use case example. It represents the "full harness" output for a Next.js + TypeScript project and is the reference for what the skill should recommend at maximum depth.

## Global Constraints

- **KISS** — prefer the simplest solution. If a simpler path exists, say so before implementing.
- **YAGNI** — no features, abstractions, or flexibility beyond what was asked.
- **DRY** — shared logic in one place. Snippets don't duplicate content across helper files.
- **First Principles** — every gate must justify itself with a failure mode in one sentence.
- **Occam's Razor** — when two solutions close the same gap, prefer fewer moving parts.
