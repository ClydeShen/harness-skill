---
name: skill-cleanup
description: Audit and remove stale, renamed, or duplicate skills across all installed agent platforms (Claude Code, Kiro, Codex, Windsurf, Gemini, Pi, and more). Handles symlink and copy installs, detects artifacts, and generates OS-correct removal commands. Use when skills list feels cluttered, after renaming a skill, after uninstalling a plugin, or when user says "clean up skills", "remove old skill", "prune skills", "stale skill", "duplicate skill".
---

# Skill Cleanup

**Audit tool. Never delete anything without explicit user confirmation per item.**

---

## Phase 1 — Detect OS and home directory

Run the appropriate probe:

**macOS / Linux:**
```bash
echo "OS: $(uname -s)"
echo "HOME: $HOME"
```

**Windows (PowerShell):**
```powershell
echo "OS: Windows"
echo "HOME: $env:USERPROFILE"
```

Use the detected home directory for all paths below. On Windows substitute `\` for `/` throughout.

---

## Phase 2 — Scan installed locations

Run each command that applies (skip if directory does not exist):

```bash
# Central store — source of truth
ls ~/.agents/skills/

# Symlink platforms (point into central store)
ls ~/.claude/skills/          # Claude Code
ls ~/.kiro/skills/            # Kiro CLI
ls ~/.pi/agent/skills/        # Pi
ls ~/.kilocode/skills/        # Kilo Code
ls ~/.qwen/skills/            # Qwen Code

# Copy platforms (independent copies — not symlinks)
ls ~/.codex/skills/           # Codex
ls ~/.codeium/windsurf/skills/ # Windsurf
ls ~/.gemini/config/skills/   # Gemini CLI
```

See [PLATFORMS.md](PLATFORMS.md) for exact paths per OS and notes on each platform's install type.

Build two inventories:
- **Central store list** — what `~/.agents/skills/` contains
- **Platform lists** — what each platform dir contains

---

## Phase 3 — Flag stale entries

Compare inventories. Flag an entry as stale when ANY signal is true:

| Signal | Stale type |
|---|---|
| Name matches a known renamed skill AND the replacement is also in central store | Renamed original |
| Two entries where one is clearly the predecessor (e.g. `foo` and `foo-v2`, `bar` and `bar-old`) | Duplicate |
| Entry present in a platform dir but absent from central store | Orphaned platform entry |
| Entry in central store but absent from ALL platform dirs | Orphaned install (no platform linked) |
| `.zip` suffix, `-workspace` suffix, or `-backup` suffix | Install artifact |
| Symlink in a symlink-platform dir whose target path does not resolve | Broken symlink |

Also check `~/.claude/settings.json` (or equivalent) for `plugins` entries whose repo or skill name no longer matches what is installed.

---

## Phase 4 — Present findings

Group by stale type and show a numbered table:

```
Stale entries found:

  #  Name                     Location                        Reason
  1  harness-engineering      ~/.agents/skills/               renamed → harness-audit (both present)
  2  harness-engineering      ~/.claude/skills/               renamed → harness-audit (both present)
  3  harness-engineering      ~/.codex/skills/                renamed → harness-audit (copy)
  4  harness-engineering.zip  ~/.claude/skills/               install artifact
  5  old-skill                ~/.kiro/skills/                 orphaned — absent from central store

Nothing to remove? → state "All installed skills look clean."
```

Wait for user response before any deletion.

User may respond:
- `all` — remove everything listed
- `1,3,5` — remove specific numbers
- `none` / `n` — abort

---

## Phase 5 — Remove confirmed entries

Use OS-correct commands. For each confirmed item:

**macOS / Linux:**
```bash
# Symlink entry (Claude Code, Kiro, Pi, Kilo Code, Qwen Code)
rm ~/.claude/skills/<name>

# Full directory (central store or copy platform)
rm -rf ~/.agents/skills/<name>
rm -rf ~/.codex/skills/<name>
```

**Windows (PowerShell):**
```powershell
# Symlink / junction
Remove-Item -Force "$env:USERPROFILE\.claude\skills\<name>"

# Full directory
Remove-Item -Recurse -Force "$env:USERPROFILE\.agents\skills\<name>"
Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\skills\<name>"
```

Removal order: platform entries first, central store last.

After removal, re-run Phase 2 scans and confirm the entries are gone.

---

## Gotchas

- **Never remove the only installed version** of a skill — if no replacement exists, keep it.
- **Symlink platforms** (`~/.claude/`, `~/.kiro/`, `~/.pi/agent/`, `~/.kilocode/`, `~/.qwen/`): entries are symlinks, `rm` without `-rf` is sufficient on macOS/Linux; `Remove-Item -Force` on Windows.
- **Copy platforms** (`~/.codex/`, `~/.codeium/windsurf/`, `~/.gemini/config/`): entries are full directory copies — remove from each platform dir independently, then from central store.
- **Pi path** is `~/.pi/agent/skills/`, not `~/.pi/skills/` — the extra `agent/` level is intentional.
- **Gemini CLI** may install under multiple subdirs (`antigravity-backup/`, `antigravity-ide/`, `config/`) — check all three.
- **`settings.json` plugin entries**: surface for human review only; do not auto-remove them.
