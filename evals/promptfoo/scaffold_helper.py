"""Project scaffolding for harness-engineering promptfoo evals.

Mirrors the scaffold() function in run_evals.py — single source of truth is
run_evals.py; update both if you change scaffolding logic.
"""

import json
import textwrap
from pathlib import Path

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


def scaffold(tmpdir: str, files: list) -> None:
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
        if "lint and build" in desc or "lint + build" in desc:
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
                      - run: npm run lint
                      - run: npm run build
            """))
        else:
            # Intentionally no lint — this is the gap the skill should catch
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
    elif "claude.md" in desc and "90 lines" in desc:
        (root / "CLAUDE.md").write_text(
            "# CLAUDE.md\n\n" + "\n".join(
                f"## Rule {i}\n\nSome guideline about situation {i}.\n"
                for i in range(1, 20)
            )
        )

    if "agents.md" in desc:
        (root / "AGENTS.md").write_text(DUMMY_AGENTS_MD_80)

    if ".kiro" in desc:
        kiro = root / ".kiro"
        kiro.mkdir(exist_ok=True)
        (kiro / ".keep").write_text("")

    if ".gemini" in desc:
        gemini = root / ".gemini"
        gemini.mkdir(exist_ok=True)
        (gemini / ".keep").write_text("")

    if "eslint" in desc:
        (root / ".eslintrc.json").write_text('{"extends":"next/core-web-vitals"}')

    if "requirements.txt" in desc:
        (root / "requirements.txt").write_text("flask\nrequests\npytest\n")

    if "posttooluse hook only" in desc or ("posttooluse" in desc and "no stop" in desc):
        # settings.json with PostToolUse only — Stop hook is deliberately missing
        c = root / ".claude"
        c.mkdir(exist_ok=True)
        (c / "settings.json").write_text(textwrap.dedent("""\
            {
              "hooks": {
                "PostToolUse": [{"matcher": {"type": "Write"}, "hooks": [{"prompt": "Run lint after every write."}]}]
              }
            }
        """))
    elif "stop" in desc or "posttooluse" in desc:
        # Full settings.json with both hooks
        c = root / ".claude"
        c.mkdir(exist_ok=True)
        (c / "settings.json").write_text(textwrap.dedent("""\
            {
              "hooks": {
                "Stop": [{"prompt": "Before declaring done, verify all tasks are truly complete: check git diff, run lint+build, confirm no regressions."}],
                "PostToolUse": [{"matcher": {"type": "Write"}, "hooks": [{"prompt": "After every Write: verify the change is correct, run lint+typecheck, commit in logical chunks."}]}]
              }
            }
        """))

    if "docs/agents" in desc:
        agents_dir = root / "docs" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        for fname in ["issue-tracker.md", "triage-labels.md", "domain.md",
                      "github-project.md", "session-config.md"]:
            (agents_dir / fname).write_text(f"# {fname}\n\nPlaceholder content.\n")
