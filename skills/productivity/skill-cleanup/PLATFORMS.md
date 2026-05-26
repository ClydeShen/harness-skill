# Platform Path Reference

All paths use `~` as shorthand for the home directory.
- **macOS / Linux**: `~` = `$HOME` (e.g. `/Users/yourname` or `/home/yourname`)
- **Windows**: `~` = `%USERPROFILE%` (e.g. `C:\Users\yourname`)

---

## Central store

| OS | Path |
|---|---|
| macOS / Linux | `~/.agents/skills/` |
| Windows | `~\.agents\skills\` |

All platforms share this store. `npx skills` always installs here first, then links or copies to platform dirs.

---

## Symlink platforms

These platform dirs contain **symlinks** (macOS/Linux) or **junctions** (Windows) pointing into the central store. Removing the entry here does not affect the central store.

| Platform | macOS / Linux | Windows |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `~\.claude\skills\` |
| Kiro CLI | `~/.kiro/skills/` | `~\.kiro\skills\` |
| Pi | `~/.pi/agent/skills/` | `~\.pi\agent\skills\` |
| Kilo Code | `~/.kilocode/skills/` | `~\.kilocode\skills\` |
| Qwen Code | `~/.qwen/skills/` | `~\.qwen\skills\` |

**Detection**: config dir exists → platform is installed. E.g. `~/.claude/` present → Claude Code installed.

---

## Copy platforms

These platform dirs contain **independent full copies**. Each must be removed separately; removing from central store does not remove copies.

| Platform | macOS / Linux | Windows |
|---|---|---|
| Codex | `~/.codex/skills/` | `~\.codex\skills\` |
| Windsurf | `~/.codeium/windsurf/skills/` | `~\.codeium\windsurf\skills\` |
| Gemini CLI | `~/.gemini/config/skills/` | `~\.gemini\config\skills\` |
| Gemini CLI (IDE) | `~/.gemini/antigravity-ide/skills/` | `~\.gemini\antigravity-ide\skills\` |
| Gemini CLI (backup) | `~/.gemini/antigravity-backup/skills/` | `~\.gemini\antigravity-backup\skills\` |
| GitHub Copilot | varies — check `~/.config/github-copilot/` | varies |
| Cursor | varies — check `~/.cursor/` | varies |
| OpenCode | varies — check `~/.opencode/` | varies |

**Note**: Gemini CLI installs into up to three subdirs. Always check all three when removing a Gemini copy.

---

## Removal commands

### macOS / Linux

```bash
# Symlink platform entry
rm ~/.claude/skills/<name>

# Copy platform entry
rm -rf ~/.codex/skills/<name>
rm -rf ~/.codeium/windsurf/skills/<name>
rm -rf ~/.gemini/config/skills/<name>

# Central store (last — after all platform entries removed)
rm -rf ~/.agents/skills/<name>
```

### Windows (PowerShell)

```powershell
# Symlink / junction platform entry
Remove-Item -Force "$env:USERPROFILE\.claude\skills\<name>"

# Copy platform entry
Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\skills\<name>"
Remove-Item -Recurse -Force "$env:USERPROFILE\.codeium\windsurf\skills\<name>"
Remove-Item -Recurse -Force "$env:USERPROFILE\.gemini\config\skills\<name>"

# Central store (last)
Remove-Item -Recurse -Force "$env:USERPROFILE\.agents\skills\<name>"
```

---

## settings.json locations

| Platform | Config file |
|---|---|
| Claude Code | `~/.claude/settings.json` |
| Kiro CLI | `~/.kiro/settings.json` |
| Pi | `~/.pi/settings.json` |

Check the `plugins` array for entries whose repo URL or skill name no longer matches installed skills. Surface for human review — do not auto-remove.
