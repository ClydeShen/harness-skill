#!/usr/bin/env bash
# Lists all skills in this collection with their names and paths.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
printf "%-30s %s\n" "SKILL" "PATH"
printf "%-30s %s\n" "-----" "----"

for skill_dir in "$REPO_ROOT/skills"/*/*; do
  [ -f "$skill_dir/SKILL.md" ] || continue
  skill_name="$(basename "$skill_dir")"
  rel_path="${skill_dir#$REPO_ROOT/}"
  printf "%-30s %s\n" "$skill_name" "$rel_path"
done
