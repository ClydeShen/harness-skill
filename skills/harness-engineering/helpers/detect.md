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
| CLAUDE.md has no `<important if>` tags | Scan file content | Task-specific rules applied universally; foundational rules crowded out |
| Cross-session memory absent | No `MEMORY.md` or `.memobank/` | Preferences and decisions lost between sessions |

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
