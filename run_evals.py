#!/usr/bin/env python3
"""
Eval runner for harness-engineering skill.

Isolation strategy:
  - Copy skill to a non-git temp location so --plugin-dir doesn't inherit
    the parent git repo as the workspace (which caused eval 6 to see the
    wrong files in earlier runs).
  - Scaffold minimal project files per eval in a separate temp dir.
  - Use individual haiku calls for judging (reliable, no parsing ambiguity).
"""

import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

REPO_ROOT  = Path(__file__).parent
SKILL_DIR  = REPO_ROOT / "skills" / "harness-engineering"
EVALS_FILE = SKILL_DIR / "evals" / "evals.json"
RESPONSE_MODEL = "sonnet"
JUDGE_MODEL    = "haiku"


# ---------------------------------------------------------------------------
# Project scaffolding
# ---------------------------------------------------------------------------

DUMMY_CLAUDE_MD_250 = "# CLAUDE.md\n\n" + "\n".join(
    f"## Rule {i}\n\nSome rule about handling situation {i}.\n"
    for i in range(1, 42)
)  # ~252 lines

DUMMY_AGENTS_MD_80 = textwrap.dedent("""\
    # AGENTS.md

    ## Stack
    Next.js 14 · TypeScript · Supabase · Stripe · Tailwind

    ## Key Commands
    ```bash
    npm run dev      # Start dev server
    npm run build    # Build for production
    npm run lint     # Run ESLint
    npm run test     # Run tests
    ```

    ## Architecture
    Pages in `app/`, shared components in `components/`, API routes in `app/api/`.
    Supabase client is initialised in `lib/supabase.ts`. Stripe webhook handler
    lives in `app/api/webhooks/stripe/route.ts`.

    ## Gotchas
    - Never import `@/lib/supabase-admin` in client components (service key exposure)
    - Stripe webhook must verify signature before processing
    - Run `supabase db push` after schema changes, not `db reset` in prod
    - Auth check must be first in every API route

    ## Coding Conventions
    - Use `async/await`, never `.then()` chains
    - All API routes must check auth before any DB access
    - Components must be under 200 lines; extract hooks if larger
""")


def scaffold(tmpdir: str, files: list[str]) -> None:
    root = Path(tmpdir)
    desc = " ".join(files).lower()

    if "package.json" in desc or "next.js" in desc or "next js" in desc:
        pkg: dict = {
            "name": "my-app",
            "version": "1.0.0",
            "scripts": {
                "build": "next build",
                "lint": "next lint",
                "typecheck": "tsc --noEmit",
            },
        }
        if "typescript" in desc:
            pkg["devDependencies"] = {"typescript": "^5.0.0", "eslint": "^8.0.0"}
        if "next" in desc:
            pkg.setdefault("dependencies", {})["next"] = "^14.0.0"
        (root / "package.json").write_text(json.dumps(pkg, indent=2))

    if "typescript" in desc or "tsconfig" in desc:
        (root / "tsconfig.json").write_text('{"compilerOptions":{"strict":true}}')

    if "ci.yml" in desc or ("github" in desc and "workflow" in desc):
        gha = root / ".github" / "workflows"
        gha.mkdir(parents=True, exist_ok=True)
        # Intentionally no lint step — this is the gap the skill should catch
        (gha / "ci.yml").write_text(textwrap.dedent("""\
            name: CI
            on:
              push:
                branches: [main]
            jobs:
              build:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - uses: actions/setup-node@v4
                    with:
                      node-version: '20'
                  - run: npm ci
                  - run: npm run build
        """))

    if "claude.md" in desc and "250 lines" in desc:
        (root / "CLAUDE.md").write_text(DUMMY_CLAUDE_MD_250)

    if "agents.md" in desc:
        (root / "AGENTS.md").write_text(DUMMY_AGENTS_MD_80)

    if ".kiro" in desc:
        (root / ".kiro").mkdir(exist_ok=True)

    if ".gemini" in desc:
        (root / ".gemini").mkdir(exist_ok=True)

    if "eslint" in desc:
        (root / ".eslintrc.json").write_text('{"extends":"next/core-web-vitals"}')


# ---------------------------------------------------------------------------
# Skill runner
# ---------------------------------------------------------------------------

def run_skill(prompt: str, project_dir: str, isolated_skill_dir: str) -> str:
    """Run the skill from a clean project dir, with skill copy in non-git temp location."""
    result = subprocess.run(
        [
            "claude", "-p",
            "--plugin-dir", isolated_skill_dir,
            "--model", RESPONSE_MODEL,
            "--dangerously-skip-permissions",
            prompt,
        ],
        capture_output=True, text=True, timeout=240, encoding='utf-8', errors='replace',
        cwd=project_dir,
    )
    if result.returncode != 0 and "session limit" in (result.stdout or "").lower():
        print(f"  [RATE LIMIT] {(result.stdout or '').strip()[:120]}", file=sys.stderr)
        return ""
    if result.returncode != 0:
        print(f"  [WARN] exit {result.returncode}: {result.stderr[:200]}", file=sys.stderr)
    return (result.stdout or "").strip()


# ---------------------------------------------------------------------------
# Judge
# ---------------------------------------------------------------------------

def judge_one(response: str, expectation: str, retries: int = 2) -> bool:
    judge_prompt = (
        "You are a strict evaluator. Respond with exactly PASS or FAIL — no other text.\n\n"
        f"EXPECTATION: {expectation}\n\n"
        f"RESPONSE:\n{response[:4000]}\n\n"
        "Verdict (PASS or FAIL):"
    )
    for attempt in range(retries + 1):
        result = subprocess.run(
            ["claude", "-p", "--model", JUDGE_MODEL,
             "--dangerously-skip-permissions", judge_prompt],
            capture_output=True, text=True, timeout=240,
            cwd=REPO_ROOT,
        )
        verdict = (result.stdout or "").strip().upper()
        if verdict.startswith("PASS"):
            return True
        if verdict.startswith("FAIL"):
            return False
        # Unexpected output — retry after a short wait
        if attempt < retries:
            time.sleep(2)
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    data  = json.loads(EVALS_FILE.read_text(encoding="utf-8"))
    evals = data["evals"]

    # Copy skill to an isolated temp directory (no git parent = no repo leakage)
    with tempfile.TemporaryDirectory(prefix="harness_skill_") as skill_tmp:
        isolated_skill = str(Path(skill_tmp) / "skill")
        shutil.copytree(str(SKILL_DIR), isolated_skill)
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
                    total_pass += 1
                else:
                    total_fail += 1
                    all_passed = False
                print(f"  [{status}] {exp}")

            print(f"\n  Eval {eid}: {'ALL PASS' if all_passed else 'HAS FAILURES'}")
            summary.append((eid, all_passed))

    print(f"\n{'='*70}")
    total = total_pass + total_fail
    pct = (100 * total_pass // total) if total else 0
    print(f"FINAL: {total_pass}/{total} expectations passed ({pct}%)")
    print()
    for eid, passed in summary:
        print(f"  Eval {eid}: {'PASS' if passed else 'FAIL'}")


if __name__ == "__main__":
    main()
