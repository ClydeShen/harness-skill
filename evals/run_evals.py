#!/usr/bin/env python3
"""
Eval runner for harness-engineering skill.

Isolation strategy:
  - Copy skill to a non-git temp location so --plugin-dir doesn't inherit
    the parent git repo as the workspace (which caused eval 6 to see the
    wrong files in earlier runs).
  - Scaffold minimal project files per eval in a separate temp dir.
  - Use individual haiku calls for judging (reliable, no parsing ambiguity).

Backends:
  --backend claude    (default) uses `claude -p --plugin-dir`
  --backend opencode  uses `opencode run --model`; injects skill content
                      directly into the prompt since opencode has no --plugin-dir
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

REPO_ROOT  = Path(__file__).parent.parent

# Claude backend models
RESPONSE_MODEL = "sonnet"
JUDGE_MODEL    = "haiku"

# Opencode backend models
OPENCODE_RESPONSE_MODEL = "llama-cpp/Qwen3.6-35B-A3B-UD-Q5_K_M.gguf"
OPENCODE_JUDGE_MODEL    = "llama-cpp/Qwen3.6-35B-A3B-UD-Q5_K_M.gguf"

# Pi backend models (pi uses llamacpp/<model-name> format)
PI_RESPONSE_MODEL = "llamacpp/qwen3.6-35b-a3b-ud-q5_k_m"
PI_JUDGE_MODEL    = "llamacpp/qwen3.6-35b-a3b-ud-q5_k_m"

# Resolve pi executable (on Windows pi ships as pi.cmd — shutil.which handles this)
_PI_EXE: str = shutil.which("pi") or shutil.which("pi.cmd") or "pi"

_ANSI_RE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


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
        kiro = root / ".kiro"
        kiro.mkdir(exist_ok=True)
        # Sentinel file so the skill can detect the directory during Phase 1 scan
        (kiro / ".keep").write_text("")

    if ".gemini" in desc:
        gemini = root / ".gemini"
        gemini.mkdir(exist_ok=True)
        # Sentinel file so the skill can detect the directory during Phase 1 scan
        (gemini / ".keep").write_text("")

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
# Opencode backend
# ---------------------------------------------------------------------------

def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def _strip_opencode_header(text: str) -> str:
    """Remove the '> build · model-name' header line opencode prepends."""
    lines = text.split("\n")
    lines = [l for l in lines if not (l.startswith(">") and "build" in l)]
    return "\n".join(lines)


def _load_skill_content(skill_dir: str) -> str:
    """Load SKILL.md + all reference *.md files for prompt injection."""
    root = Path(skill_dir)
    parts: list[str] = []
    skill_md = root / "SKILL.md"
    if skill_md.exists():
        parts.append(f"# SKILL.md\n\n{skill_md.read_text(encoding='utf-8')}")
    refs = root / "references"
    if refs.exists():
        for f in sorted(refs.glob("*.md")):
            parts.append(f"# references/{f.name}\n\n{f.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(parts)


def run_skill_opencode(prompt: str, project_dir: str, isolated_skill_dir: str) -> str:
    # Windows has a ~32KB command-line limit, so write skill content to a temp
    # file inside project_dir and send a short prompt referencing it.
    skill_content = _load_skill_content(isolated_skill_dir)
    skill_file = Path(project_dir) / "__skill_context__.md"
    skill_file.write_text(
        "You are executing the following agent skill. Follow its instructions exactly.\n\n"
        + skill_content,
        encoding="utf-8",
    )
    short_prompt = (
        f"Read the file __skill_context__.md — it contains your skill instructions. "
        f"Follow those instructions exactly for this user request: {prompt}"
    )
    try:
        result = subprocess.run(
            ["opencode", "run", "--model", OPENCODE_RESPONSE_MODEL, short_prompt],
            capture_output=True, text=True, timeout=300,
            encoding="utf-8", errors="replace",
            cwd=project_dir,
        )
    finally:
        skill_file.unlink(missing_ok=True)
    if result.returncode != 0:
        print(f"  [WARN] opencode exit {result.returncode}: {result.stderr[:200]}", file=sys.stderr)
    raw = _strip_ansi(result.stdout or "").strip()
    return _strip_opencode_header(raw).strip()


def judge_one_opencode(response: str, expectation: str, retries: int = 2) -> bool:
    # Write judge prompt to a temp file to avoid Windows CLI length limit.
    judge_content = (
        "You are a strict evaluator. Respond with exactly PASS or FAIL — no other text.\n\n"
        f"EXPECTATION: {expectation}\n\n"
        f"RESPONSE:\n{response[:4000]}\n\n"
        "Verdict (PASS or FAIL):"
    )
    judge_file = REPO_ROOT / "__judge_prompt__.md"
    judge_file.write_text(judge_content, encoding="utf-8")
    short_prompt = "Read __judge_prompt__.md and output exactly PASS or FAIL based on its instructions."
    try:
        for attempt in range(retries + 1):
            result = subprocess.run(
                ["opencode", "run", "--model", OPENCODE_JUDGE_MODEL, short_prompt],
                capture_output=True, text=True, timeout=120,
                encoding="utf-8", errors="replace",
                cwd=REPO_ROOT,
            )
            raw = _strip_ansi(result.stdout or "").strip()
            raw = _strip_opencode_header(raw).strip()
            for line in raw.split("\n"):
                line = line.strip().upper()
                if line.startswith("PASS"):
                    return True
                if line.startswith("FAIL"):
                    return False
            if attempt < retries:
                time.sleep(2)
    finally:
        judge_file.unlink(missing_ok=True)
    return False


# ---------------------------------------------------------------------------
# Pi backend  (pi -p --skill <dir> — closest to claude --plugin-dir)
# ---------------------------------------------------------------------------

def run_skill_pi(prompt: str, project_dir: str, isolated_skill_dir: str) -> str:
    """Run skill via pi -p --skill <dir>. Output is plain text, no stripping needed."""
    result = subprocess.run(
        [
            _PI_EXE, "-p",
            "--model", PI_RESPONSE_MODEL,
            "--skill", isolated_skill_dir,
            "--no-context-files",
            prompt,
        ],
        capture_output=True, text=True, timeout=300,
        encoding="utf-8", errors="replace",
        cwd=project_dir,
    )
    if result.returncode != 0:
        print(f"  [WARN] pi exit {result.returncode}: {result.stderr[:200]}", file=sys.stderr)
    return (result.stdout or "").strip()


def judge_one_pi(response: str, expectation: str, retries: int = 2) -> bool:
    judge_prompt = (
        "You are a strict evaluator. Respond with exactly PASS or FAIL — no other text.\n\n"
        f"EXPECTATION: {expectation}\n\n"
        f"RESPONSE:\n{response[:4000]}\n\n"
        "Verdict (PASS or FAIL):"
    )
    for attempt in range(retries + 1):
        result = subprocess.run(
            [_PI_EXE, "-p", "--model", PI_JUDGE_MODEL, "--no-context-files", judge_prompt],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
            cwd=REPO_ROOT,
        )
        verdict = (result.stdout or "").strip().upper()
        if verdict.startswith("PASS"):
            return True
        if verdict.startswith("FAIL"):
            return False
        if attempt < retries:
            time.sleep(2)
    return False


# ---------------------------------------------------------------------------
# Skill discovery
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run skill evals")
    parser.add_argument("--skill", metavar="NAME",
                        help="Run evals for one skill only (e.g. harness-engineering)")
    parser.add_argument("--evals", metavar="N[,N]",
                        help="Comma-separated eval IDs within the selected skill")
    parser.add_argument("--backend", choices=["claude", "opencode", "pi"], default="claude",
                        help="Model backend: claude (default), opencode, or pi (local model)")
    args = parser.parse_args()

    use_opencode = args.backend == "opencode"
    use_pi       = args.backend == "pi"
    if use_opencode:
        print(f"Backend: opencode  response={OPENCODE_RESPONSE_MODEL}  judge={OPENCODE_JUDGE_MODEL}")
    elif use_pi:
        print(f"Backend: pi  response={PI_RESPONSE_MODEL}  judge={PI_JUDGE_MODEL}")
    else:
        print(f"Backend: claude  response={RESPONSE_MODEL}  judge={JUDGE_MODEL}")

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
                    if use_opencode:
                        response = run_skill_opencode(prompt, project_dir, isolated_skill)
                    elif use_pi:
                        response = run_skill_pi(prompt, project_dir, isolated_skill)
                    else:
                        response = run_skill(prompt, project_dir, isolated_skill)
                    print(f"({len(response)} chars)")

                if not response:
                    print("  [SKIP] No response or rate limited.")
                    continue

                print(f"  Preview: {response[:200].replace(chr(10), ' ')[:200]}...\n")

                all_passed = True
                for exp in expectations:
                    if use_opencode:
                        passed = judge_one_opencode(response, exp)
                    elif use_pi:
                        passed = judge_one_pi(response, exp)
                    else:
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


if __name__ == "__main__":
    main()
