# Detection Guide

## Stack Detection

| File present | Stack |
|---|---|
| `package.json` with `typescript` dep or `tsconfig.json` | Node/TypeScript |
| `package.json` without TypeScript | Node/JavaScript |
| `pyproject.toml` or `requirements.txt` or `setup.py` | Python |
| `go.mod` | Go |
| None of the above | Unknown — ask |

If frontend: look for `next.config.*`, `vite.config.*`, `react` in deps.
Frontend detected → also check for `DESIGN.md`.

---

## Gap Classification

### Major gaps (each counts toward the Q3 threshold)

| Gap | Detection | Failure mode prevented |
|---|---|---|
| No Stop hook | `.claude/settings.json` missing or lacks `Stop` entry | Claude declares done without verifying — most common failure mode |
| No PostToolUse hook | `.claude/settings.json` missing or lacks `PostToolUse` entry | Lint violations accumulate silently across edits |
| No CLAUDE.md | `CLAUDE.md` absent | No persistent context anchor — every session starts blind |
| CLAUDE.md over budget | `CLAUDE.md` exceeds 200 lines | Instructions degrade uniformly; critical rules get ignored |
| No CI | `.github/workflows/` absent or no lint+build steps | Broken code merges undetected |
| No health check | `init.sh` absent | Sessions start on a broken baseline without warning |

### Minor gaps (do not count toward Q3 threshold)

| Gap | Detection | Failure mode prevented |
|---|---|---|
| No pre-commit hooks | `.husky/` and `.pre-commit-config.yaml` both absent | Style violations reach commit; slow feedback loop |
| No spec workflow | `docs/superpowers/specs/` absent | Work starts without agreed done criteria |
| No DESIGN.md (frontend only) | `DESIGN.md` absent, frontend detected | UI work starts without visual language anchor |
| CLAUDE.md has no `<important if>` tags or `.claude/rules/` | Scan file content and directory | Task-specific rules applied universally; foundational rules crowded out |
| No `.claude/rules/` when CLAUDE.md > 100 lines | `.claude/rules/` absent | Path-specific rules bloat the always-loaded context instead of loading on demand |
| Cross-session memory absent | None of the common memory signals detected (see below) | Preferences and decisions lost between sessions |

---

## Detecting Cross-Session Memory

Count as "memory present" if **any** of these signals exist:

| Signal | Tool |
|---|---|
| `~/.claude/projects/*/memory/MEMORY.md` exists | Claude Code native auto memory |
| `MEMORY.md` in project root | Manual memory file (simple, zero-dep) |
| `.memobank/` directory in project root | memobank |
| `memory/` or `.memory/` directory in project root | Generic memory directory |
| `onecontext` in installed skills or CLAUDE.md reference | OneContext |
| `mem0` package in `package.json` / `pyproject.toml` | mem0 |
| `CLAUDE.md` references a memory file with `@` import | Custom memory via import |

If none found, suggest the simplest option first: a `MEMORY.md` file at project root with a note in `CLAUDE.md` to load it at session start. Only suggest heavier tools if the user asks.

---

## Interpreting CI workflows

A CI workflow counts as covering lint if it runs any of:
`eslint`, `ruff`, `golangci-lint`, `npm run lint`, `make lint`

A CI workflow counts as covering build if it runs any of:
`npm run build`, `next build`, `tsc --noEmit`, `go build`, `python -m build`, `make build`

If CI exists but covers neither, treat as "CI present but incomplete" — list as a gap with lower priority than "no CI".

---

## Interpreting .claude/settings.json

PostToolUse hook is present if `settings.json` contains a `PostToolUse` key
with a matcher covering `Edit` or `Write` and a non-empty `hooks` array.

Stop hook is present if `settings.json` contains a `Stop` key with a non-empty
`hooks` array containing a prompt entry.

If `settings.json` exists but hooks are missing or empty, treat as
"hooks configured but incomplete".
