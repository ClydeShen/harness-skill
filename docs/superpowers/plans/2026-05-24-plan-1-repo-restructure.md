# Harness Engineering Skill Collection — Plan 1: Repo Restructure

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the flat single-skill repo into the multi-skill collection directory structure defined in the spec. No new skill content — pure mechanical restructure. All 6 existing `harness-engineering` evals must pass after completion.

**Architecture:** Three operations: (1) git-move the existing skill into its new path under `skills/engineering/`, (2) create new directories and scaffold files (plugin manifest, scripts, READMEs), (3) update and move `run_evals.py` to `evals/` with multi-skill discovery. CLAUDE.md updated to match.

**Tech Stack:** Python 3.11 (run_evals.py), Bash (shell scripts), JSON (plugin manifest), git.

---

## Chunk 1: Move skill and create skeleton

### Task 1: Create new directory skeleton

**Files:**
- Create dir: `skills/engineering/`
- Create dir: `skills/productivity/`
- Create dir: `.claude-plugin/`
- Create dir: `scripts/`
- Create dir: `evals/`

- [ ] **Step 1: Create directories**

```bash
mkdir -p skills/engineering skills/productivity .claude-plugin scripts evals
```

- [ ] **Step 2: Verify all five directories exist**

```bash
ls -d skills/engineering skills/productivity .claude-plugin scripts evals
```
Expected: five directory names listed with no errors.

---

### Task 2: Move harness-engineering into new path

**Files:**
- Move: `skills/harness-engineering/` → `skills/engineering/harness-engineering/`

- [ ] **Step 1: git mv the skill directory**

```bash
git mv skills/harness-engineering skills/engineering/harness-engineering
```

- [ ] **Step 2: Verify move — new path exists**

```bash
ls skills/engineering/harness-engineering/SKILL.md skills/engineering/harness-engineering/evals/evals.json
```
Expected: both files listed without error.

- [ ] **Step 3: Verify old path is gone**

```bash
ls skills/harness-engineering 2>/dev/null && echo "ERROR: old path still exists" || echo "OK: old path removed"
```
Expected: `OK: old path removed`

- [ ] **Step 4: Commit the move**

```bash
git add skills/
git commit -m "refactor: move harness-engineering into skills/engineering/"
```

---

## Chunk 2: Plugin manifest and scripts

### Task 3: Create .claude-plugin/plugin.json

**Files:**
- Create: `.claude-plugin/plugin.json`

- [ ] **Step 1: Write plugin.json**

Create `.claude-plugin/plugin.json` with this exact content:
```json
{
  "name": "harness-engineering-skills",
  "version": "1.0.0",
  "description": "Harness engineering skill collection — setup, context handover, session management, and adapted mattpocock/skills for compound engineering workflows.",
  "skills": [
    "skills/engineering/harness-engineering"
  ]
}
```

Note: additional skill paths are appended here as Plans 2–4 implement them.

- [ ] **Step 2: Verify plugin.json is valid JSON**

```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json'))" && echo "OK: plugin.json is valid JSON"
```
Expected: `OK: plugin.json is valid JSON`

---

### Task 4: Create .claude-plugin/link-skills.sh

**Files:**
- Create: `.claude-plugin/link-skills.sh`

- [ ] **Step 1: Write link-skills.sh**

Create `.claude-plugin/link-skills.sh`:
```bash
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
```

- [ ] **Step 2: Make executable**

```bash
chmod +x .claude-plugin/link-skills.sh
```

- [ ] **Step 3: Verify syntax is valid**

```bash
bash -n .claude-plugin/link-skills.sh && echo "OK: link-skills.sh syntax valid"
```
Expected: `OK: link-skills.sh syntax valid`

---

### Task 5: Create scripts/link-skills.sh and scripts/list-skills.sh

**Files:**
- Create: `scripts/link-skills.sh`
- Create: `scripts/list-skills.sh`

- [ ] **Step 1: Write scripts/link-skills.sh** (mirrors `.claude-plugin/link-skills.sh`)

Create `scripts/link-skills.sh`:
```bash
#!/usr/bin/env bash
# Links all skills in this collection into ~/.claude/skills/
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
```

- [ ] **Step 2: Write scripts/list-skills.sh**

Create `scripts/list-skills.sh`:
```bash
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
```

- [ ] **Step 3: Make both executable**

```bash
chmod +x scripts/link-skills.sh scripts/list-skills.sh
```

- [ ] **Step 3.5: Verify link-skills.sh syntax**

```bash
bash -n scripts/link-skills.sh && echo "OK: scripts/link-skills.sh syntax valid"
```
Expected: `OK: scripts/link-skills.sh syntax valid`

- [ ] **Step 4: Verify list-skills runs and lists harness-engineering**

```bash
bash scripts/list-skills.sh
```
Expected output:
```
SKILL                          PATH
-----                          ----
harness-engineering            skills/engineering/harness-engineering
```

---

### Task 6: Create skills/engineering/README.md and skills/productivity/README.md

**Files:**
- Create: `skills/engineering/README.md`
- Create: `skills/productivity/README.md`

- [ ] **Step 1: Write skills/engineering/README.md**

```markdown
# Engineering Skills

Skills in this directory support the full compound engineering lifecycle:
project setup, phase management, context handover, issue lifecycle, and harness health.

| Skill | Purpose | Status |
|---|---|---|
| `harness-engineering` | Detect harness gaps and output paste-ready fix snippets | Implemented |
| `setup-harness-skills` | One-time gateway: configure GitHub, labels, session state | Plan 2 |
| `context-handover` | End-of-context-window session transition | Plan 3 |
| `session-start` | Phase detection and session briefing | Plan 3 |
| `triage` | Issue triage state machine | Plan 4 |
| `to-prd` | Convert conversation to PRD with Technical Constraints | Plan 4 |
| `to-issues` | Break PRD into vertical-slice user stories | Plan 4 |
| `zoom-out` | Gain high-level architectural perspective | Plan 4 |

Skills marked "Plan 4" are adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT License, copyright Matt Pocock 2026). `harness-engineering` is an original skill.
```

- [ ] **Step 2: Write skills/productivity/README.md**

```markdown
# Productivity Skills

Skills in this directory support day-to-day AI agent workflow and skill authoring.

| Skill | Purpose | Status |
|---|---|---|
| `caveman` | Debug by explaining code in the simplest possible terms | Plan 4 |
| `grill-me` | Stress-test ideas and designs through relentless questioning | Plan 4 |
| `handoff` | Lightweight intra-session summary for briefing subagents | Plan 4 |
| `write-a-skill` | Guided process for authoring new skills in this collection | Plan 4 |

Copied verbatim from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT License, copyright Matt Pocock 2026)
with harness-specific checklist additions applied to `write-a-skill`.
```

- [ ] **Step 3: Commit all of chunk 2**

```bash
git add .claude-plugin/ scripts/ skills/engineering/README.md skills/productivity/README.md
git commit -m "feat: add plugin manifest, link/list scripts, and skill category READMEs"
```

---

## Chunk 3: run_evals.py — move and enhance

### Task 7: Move run_evals.py to evals/ and fix path constants

**Files:**
- Move: `run_evals.py` → `evals/run_evals.py`
- Modify: `evals/run_evals.py:22-24` — update REPO_ROOT and SKILL_DIR

- [ ] **Step 1: git mv the file**

```bash
git mv run_evals.py evals/run_evals.py
```

- [ ] **Step 2: Update REPO_ROOT constant**

In `evals/run_evals.py` line 22, change:
```python
REPO_ROOT  = Path(__file__).parent
```
to:
```python
REPO_ROOT  = Path(__file__).parent.parent
```

- [ ] **Step 3: Update SKILL_DIR constant**

In `evals/run_evals.py` line 23, change:
```python
SKILL_DIR  = REPO_ROOT / "skills" / "harness-engineering"
```
to:
```python
SKILL_DIR  = REPO_ROOT / "skills" / "engineering" / "harness-engineering"
```

- [ ] **Step 4: Run evals to verify nothing broke**

```bash
python evals/run_evals.py
```
Expected: same 6-eval result as before the move. All that currently pass should still pass.
If any fail, check that REPO_ROOT and SKILL_DIR are correct before continuing.

---

### Task 8: Add discover_skills() and --skill flag

**Files:**
- Modify: `evals/run_evals.py` — add helper function and rewrite main()

The enhanced runner supports:
- `python evals/run_evals.py` — discovers and runs all `skills/*/*/evals/evals.json`
- `python evals/run_evals.py --skill harness-engineering` — runs only that skill
- `--evals N[,N]` remains scoped to the selected skill's eval IDs

- [ ] **Step 1: Add discover_skills() helper after the constants block (after line ~27)**

Insert this function before the `# Project scaffolding` comment:
```python
def discover_skills(skill_name: str | None = None) -> list[tuple[str, Path]]:
    """
    Returns list of (skill_name, evals_json_path) tuples.
    If skill_name given, returns only that skill. Otherwise discovers all
    skills/*/*/evals/evals.json files.
    """
    if skill_name:
        matches = list(REPO_ROOT.glob(f"skills/*/{skill_name}/evals/evals.json"))
        if not matches:
            print(f"ERROR: No evals found for skill '{skill_name}'", file=sys.stderr)
            sys.exit(1)
        return [(skill_name, matches[0])]

    found = []
    for path in sorted(REPO_ROOT.glob("skills/*/*/evals/evals.json")):
        # path = skills/<category>/<skill_name>/evals/evals.json
        name = path.parent.parent.name
        found.append((name, path))

    if not found:
        print("ERROR: No evals/evals.json files found under skills/*/*/", file=sys.stderr)
        sys.exit(1)
    return found
```

- [ ] **Step 2: Replace the main() function entirely**

Replace the entire `def main():` function with:
```python
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run skill evals")
    parser.add_argument("--skill", metavar="NAME",
                        help="Run evals for one skill only (e.g. harness-engineering)")
    parser.add_argument("--evals", metavar="N[,N]",
                        help="Comma-separated eval IDs within the selected skill")
    args = parser.parse_args()

    only_ids: set[int] | None = None
    if args.evals:
        only_ids = {int(x.strip()) for x in args.evals.split(",")}

    skills_to_run = discover_skills(args.skill)

    grand_pass = grand_fail = 0
    all_summaries: list[tuple[str, int, bool]] = []

    for skill_name, evals_file in skills_to_run:
        skill_dir = evals_file.parent.parent   # skills/<cat>/<name>/
        print(f"\n{'#'*70}")
        print(f"# Skill: {skill_name}")
        print(f"# Evals: {evals_file.relative_to(REPO_ROOT)}")
        print(f"{'#'*70}")

        data  = json.loads(evals_file.read_text(encoding="utf-8"))
        evals = data["evals"]
        if only_ids:
            evals = [e for e in evals if e["id"] in only_ids]

        with tempfile.TemporaryDirectory(prefix="harness_skill_") as skill_tmp:
            isolated_skill = str(Path(skill_tmp) / "skill")
            shutil.copytree(str(skill_dir), isolated_skill)
            print(f"Skill isolated at: {isolated_skill}\n")

            total_pass = total_fail = 0
            summary: list[tuple[int, bool]] = []

            for ev in evals:
                eid, prompt = ev["id"], ev["prompt"]
                expectations = ev["expectations"]
                file_list    = ev.get("files", [])

                print(f"\n{'='*70}")
                print(f"Eval {eid}: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
                print(f"{'='*70}")

                with tempfile.TemporaryDirectory(prefix="harness_proj_") as project_dir:
                    if file_list:
                        scaffold(project_dir, file_list)
                        created = [
                            str(f.relative_to(project_dir))
                            for f in Path(project_dir).rglob("*") if f.is_file()
                        ]
                        print(f"  Files: {created}")

                    print("  Running skill... ", end="", flush=True)
                    response = run_skill(prompt, project_dir, isolated_skill)
                    print(f"({len(response)} chars)")

                if not response:
                    print("  [SKIP] No response or rate limited.")
                    continue

                print(f"  Preview: {response[:200].replace(chr(10), ' ')[:200]}...\n")

                all_passed = True
                for exp in expectations:
                    passed = judge_one(response, exp)
                    status = "PASS" if passed else "FAIL"
                    if passed:
                        total_pass += 1; grand_pass += 1
                    else:
                        total_fail += 1; grand_fail += 1
                        all_passed = False
                    print(f"  [{status}] {exp}")

                print(f"\n  Eval {eid}: {'ALL PASS' if all_passed else 'HAS FAILURES'}")
                summary.append((eid, all_passed))
                all_summaries.append((skill_name, eid, all_passed))

        total = total_pass + total_fail
        pct = (100 * total_pass // total) if total else 0
        print(f"\n--- {skill_name}: {total_pass}/{total} ({pct}%) ---")
        for eid, passed in summary:
            print(f"  Eval {eid}: {'PASS' if passed else 'FAIL'}")

    print(f"\n{'='*70}")
    grand_total = grand_pass + grand_fail
    grand_pct   = (100 * grand_pass // grand_total) if grand_total else 0
    print(f"GRAND TOTAL: {grand_pass}/{grand_total} expectations passed ({grand_pct}%)\n")
    for skill_name, eid, passed in all_summaries:
        print(f"  {skill_name} / Eval {eid}: {'PASS' if passed else 'FAIL'}")
```

- [ ] **Step 2.5: Remove dead constants**

After replacing `main()`, the module-level `SKILL_DIR` and `EVALS_FILE` constants are no longer referenced by any code. Remove both lines:
```python
SKILL_DIR  = REPO_ROOT / "skills" / "engineering" / "harness-engineering"
EVALS_FILE = SKILL_DIR / "evals" / "evals.json"
```
Retain `REPO_ROOT`, `RESPONSE_MODEL`, and `JUDGE_MODEL` — these are still used.

- [ ] **Step 3: Verify --skill flag works**

```bash
python evals/run_evals.py --skill harness-engineering
```
Expected: `# Skill: harness-engineering` header, then all 6 evals run.

- [ ] **Step 3.5: Verify error path for unknown skill**

```bash
python evals/run_evals.py --skill nonexistent-skill; echo "Exit code: $?"
```
Expected: `ERROR: No evals found for skill 'nonexistent-skill'` on stderr, exit code `1`.

- [ ] **Step 4: Verify default (no --skill) also works**

```bash
python evals/run_evals.py
```
Expected: discovers `harness-engineering`, same results as Step 3, GRAND TOTAL line at end.

- [ ] **Step 5: Verify --evals flag still scopes correctly**

```bash
python evals/run_evals.py --skill harness-engineering --evals 1
```
Expected: only eval ID 1 runs.

- [ ] **Step 6: Commit**

```bash
git add evals/run_evals.py
git commit -m "feat: move run_evals.py to evals/, add --skill flag and multi-skill discovery"
```

---

## Chunk 4: CLAUDE.md update

### Task 9: Update CLAUDE.md for new structure

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Replace Purpose section**

Replace the entire `## Purpose` block (current text: "This repo maintains the `harness-engineering` skill…") with:
```markdown
## Purpose

This repo is a curated skill collection for compound engineering workflows, packaged as a Claude Code / Codex plugin.

Currently implemented: `harness-engineering` — detects agent-harness gaps and outputs paste-ready config snippets.
Planned (subsequent plans): `setup-harness-skills`, `context-handover`, `session-start` (Plans 2–3); adapted skills from [mattpocock/skills](https://github.com/mattpocock/skills) MIT License (Plans 4+).

Install via `bash scripts/link-skills.sh`. Skills live in `skills/engineering/` or `skills/productivity/`.
```

- [ ] **Step 2: Replace Skill Structure section**

Replace the entire `## Skill Structure` block (current text starts with the ` ```  ` fence containing `skills/harness-engineering/`).

**IMPORTANT — nested fencing:** The replacement content below contains a triple-backtick code block inside the markdown block. Copy only the inner content (from `skills/` through the closing ` ``` `) into CLAUDE.md. Do not include the outer plan-document fencing.

Replace with:
````markdown
## Skill Structure

```
skills/
  engineering/
    harness-engineering/      ← detect harness gaps, output snippets
      SKILL.md
      skill.json
      evals/evals.json
      references/
    (setup-harness-skills/ context-handover/ session-start/ — Plan 2–3, not yet created)
    (triage/ to-prd/ to-issues/ zoom-out/ — Plan 4, not yet created)
  productivity/
    (caveman/ grill-me/ handoff/ write-a-skill/ — Plan 4, not yet created)
evals/
  run_evals.py               ← discovers and runs all skill evals
.claude-plugin/
  plugin.json                ← registered skill list
  link-skills.sh             ← symlinks skills/ into ~/.claude/skills/
scripts/
  link-skills.sh             ← same as .claude-plugin/link-skills.sh
  list-skills.sh             ← lists all skills in collection
```

Root `SKILL.md` stays intentionally empty (see README).
````

- [ ] **Step 3: Update Running Evals section**

Replace the entire `## Running Evals` block — from `## Running Evals` through the closing line `Models: \`RESPONSE_MODEL = "sonnet"\`, \`JUDGE_MODEL = "haiku"\` — change at the top of \`run_evals.py\`.` — with:
````markdown
## Running Evals

```bash
# All skills:
python evals/run_evals.py

# One skill only:
python evals/run_evals.py --skill harness-engineering

# Specific eval IDs within a skill:
python evals/run_evals.py --skill harness-engineering --evals 1,2
```

Requires `claude` CLI on PATH with an active session. The runner:
1. Copies the skill to an isolated temp dir (avoids git repo leakage into eval workspace)
2. Scaffolds a minimal project per eval (package.json, ci.yml, CLAUDE.md stubs, etc.)
3. Runs each eval prompt via `claude -p --plugin-dir <isolated> --model sonnet`
4. Judges each expectation via a separate `claude -p --model haiku` call (PASS/FAIL)

Models: `RESPONSE_MODEL = "sonnet"`, `JUDGE_MODEL = "haiku"` — change at the top of `evals/run_evals.py`.
````

- [ ] **Step 4: Update the commit-gate line**

Change:
```
**Before committing any change to a skill file, run evals and confirm all 6 pass.**
```
To:
```
**Before committing any change to a skill file, run `python evals/run_evals.py --skill <name>` and confirm all evals pass.**
```

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for multi-skill collection structure and new eval path"
```

---

## Chunk 5: Final verification

### Task 10: Full verification pass

- [ ] **Step 1: Run all evals — must all pass**

```bash
python evals/run_evals.py
```
Expected: `GRAND TOTAL: X/Y expectations passed` where X = Y (100%).
If any fail — stop, investigate, fix before moving on. Do not proceed to Plan 2 with failing evals.

- [ ] **Step 2: Verify list-skills shows harness-engineering**

```bash
bash scripts/list-skills.sh
```
Expected:
```
SKILL                          PATH
-----                          ----
harness-engineering            skills/engineering/harness-engineering
```

- [ ] **Step 2.5: Verify root run_evals.py is gone**

```bash
test ! -f run_evals.py && echo "OK: root run_evals.py absent" || echo "ERROR: root run_evals.py still present"
```
Expected: `OK: root run_evals.py absent`

- [ ] **Step 3: Verify git log shows all four commits from this plan**

```bash
git log --oneline -10
```
Expected (newest first):
```
<hash> docs: update CLAUDE.md for multi-skill collection structure and new eval path
<hash> feat: move run_evals.py to evals/, add --skill flag and multi-skill discovery
<hash> feat: add plugin manifest, link/list scripts, and skill category READMEs
<hash> refactor: move harness-engineering into skills/engineering/
```

- [ ] **Step 4: Verify git status is clean**

```bash
git status
```
Expected: `nothing to commit, working tree clean`

---

**Plan 1 complete.** The repo now has the multi-skill collection skeleton in place.

**Next:** Plan 2 — `setup-harness-skills` (gateway skill). Write Plan 2 at the start of the next execution session by reading the spec section 5.1 and the `docs/agents/` seed template format.

**Spec reference:** `docs/superpowers/specs/2026-05-24-harness-skill-collection-design.md` — Section 5.1 and Section 9 (implementation order).
