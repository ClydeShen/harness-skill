#!/usr/bin/env bash
# Links all skills in this collection into ~/.claude/skills/
# Run once per machine after cloning this repo.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="$HOME/.claude/skills"
mkdir -p "$TARGET_DIR"

for skill_dir in "$REPO_ROOT/skills"/*/*; do
  [ -f "$skill_dir/SKILL.md" ] || continue
  skill_name="$(basename "$skill_dir")"
  link="$TARGET_DIR/$skill_name"
  if [ -L "$link" ]; then rm "$link"; fi
  ln -s "$skill_dir" "$link"
  echo "Linked: $skill_name → $link"
done

echo "Done. Run 'claude skills' to verify."
