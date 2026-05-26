---
name: skill-cleanup
description: Scan installed skills across ~/.claude/skills/ and ~/.agents/skills/, detect stale or duplicate entries (renamed originals, broken symlinks, orphaned installs, .zip artifacts), and guide safe removal with confirmation. Use when skills list feels cluttered, after renaming a skill, after uninstalling a plugin, or when user says "clean up skills", "remove old skill", "prune skills", "stale skill", "duplicate skill".
---

# Skill Cleanup

**You are an audit tool. Never delete anything without explicit user confirmation.**

---

## Step 1 — Scan installed locations

Run both:

```bash
ls ~/.claude/skills/
ls ~/.agents/skills/
```

Group findings into two lists: **symlinks** (`~/.claude/skills/`) and **installs** (`~/.agents/skills/`).

---

## Step 2 — Flag stale entries

Mark as stale when ANY signal is true:

| Signal | Type |
|---|---|
| Name matches a known renamed skill and the replacement is also installed | Renamed original |
| Two entries with similar names where one is clearly the successor (e.g. `foo` and `foo-v2`) | Duplicate |
| Symlink in `~/.claude/skills/` whose target path does not exist | Broken symlink |
| `.zip` file or `-workspace` suffix | Install artifact |
| Entry absent from every `plugins` entry in `~/.claude/settings.json` AND not installed via `npx skills` recently | Orphaned |

---

## Step 3 — Check settings.json

Read `~/.claude/settings.json`. For each `plugins` entry with `type: git`:
- If the repo was renamed or a skill within it was renamed, flag the entry as potentially stale.
- Never auto-remove plugin entries — surface them for human review only.

---

## Step 4 — Present findings

Show a confirmation table before touching anything:

```
Stale entries found:

  #  Name                        Location                  Reason
  1  harness-engineering         ~/.claude/skills/         renamed → harness-audit (both present)
  2  harness-engineering         ~/.agents/skills/         renamed → harness-audit (both present)
  3  harness-engineering.zip     ~/.claude/skills/         install artifact

Remove all? Enter numbers to pick (e.g. 1,3), "all", or "none".
```

Wait for the user's answer before proceeding.

---

## Step 5 — Remove confirmed entries

For each confirmed item, use the correct command for its type:

```bash
# Symlink in ~/.claude/skills/
rm ~/.claude/skills/<name>

# Full install directory in ~/.agents/skills/
rm -rf ~/.agents/skills/<name>

# Artifact file (.zip, -workspace dir)
rm -rf ~/.claude/skills/<name>
```

After removal, re-list both directories and confirm the clean state.

---

## Gotchas

- `~/.claude/skills/` entries are symlinks — `rm` (no `-rf`) is sufficient and safe.
- `~/.agents/skills/` entries are full directories — always confirm before `rm -rf`.
- Remove the symlink first, then the install directory.
- Never remove the only installed version of a skill (no replacement present = keep it).
