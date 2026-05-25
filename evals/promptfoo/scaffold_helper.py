"""Project scaffolding for promptfoo evals.

Produces realistic project file trees in a temp directory so the model sees
accurate filesystem context during eval runs. Each scaffold_files entry is a
plain-English hint; scaffold() interprets them case-insensitively.
"""

import json
import textwrap
from pathlib import Path

DUMMY_CLAUDE_MD_250 = "# CLAUDE.md\n\n" + "\n".join(
    f"## Rule {i}\n\nSome rule about handling situation {i}.\n"
    for i in range(1, 42)
)  # ~252 lines

DUMMY_CLAUDE_MD_90 = "# CLAUDE.md\n\n" + "\n".join(
    f"## Rule {i}\n\nSome guideline about situation {i}.\n"
    for i in range(1, 20)
)  # ~94 lines

DUMMY_CLAUDE_MD_BASIC = textwrap.dedent("""\
    # CLAUDE.md

    ## Stack
    This project.

    ## Key Commands
    ```bash
    npm run dev
    npm run build
    npm run lint
    npm run test
    ```
""")

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
    desc = " ".join(str(f) for f in files).lower()

    # package.json
    if "package.json" in desc or "next.js" in desc or "next js" in desc:
        pkg: dict = {
            "name": "my-app",
            "version": "1.0.0",
            "scripts": {
                "build": "next build",
                "lint": "next lint",
                "typecheck": "tsc --noEmit",
                "test": "jest",
                "dev": "next dev",
            },
        }
        if "typescript" in desc:
            pkg["devDependencies"] = {"typescript": "^5.0.0", "eslint": "^8.0.0"}
        if "next" in desc:
            pkg.setdefault("dependencies", {})["next"] = "^14.0.0"
        if "supabase" in desc:
            pkg.setdefault("dependencies", {})["@supabase/supabase-js"] = "^2.0.0"
        if "stripe" in desc:
            pkg.setdefault("dependencies", {})["stripe"] = "^14.0.0"
        (root / "package.json").write_text(json.dumps(pkg, indent=2))

    # tsconfig.json
    if "typescript" in desc or "tsconfig" in desc:
        (root / "tsconfig.json").write_text('{"compilerOptions":{"strict":true}}')

    # .github/workflows/ci.yml
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

    # CLAUDE.md
    if "claude.md" in desc and "250 lines" in desc:
        (root / "CLAUDE.md").write_text(DUMMY_CLAUDE_MD_250)
    elif "claude.md" in desc and "90 lines" in desc:
        (root / "CLAUDE.md").write_text(DUMMY_CLAUDE_MD_90)
    elif "claude.md" in desc:
        (root / "CLAUDE.md").write_text(DUMMY_CLAUDE_MD_BASIC)

    # AGENTS.md
    if "agents.md" in desc:
        (root / "AGENTS.md").write_text(DUMMY_AGENTS_MD_80)

    # CONTEXT.md
    if "context.md" in desc:
        (root / "CONTEXT.md").write_text(textwrap.dedent("""\
            # CONTEXT.md

            ## Glossary
            user: A registered account holder.
            session: An authenticated browser or API session.
            workspace: A top-level tenant container.
        """))

    # MEMORY.md
    if "memory.md" in desc:
        (root / "MEMORY.md").write_text(textwrap.dedent("""\
            # Memory

            ## Session notes
            - No active memories recorded.
        """))

    # requirements.txt
    if "requirements.txt" in desc:
        (root / "requirements.txt").write_text("flask\nrequests\npytest\n")

    # .eslintrc.json
    if "eslint" in desc:
        (root / ".eslintrc.json").write_text('{"extends":"next/core-web-vitals"}')

    # src/ files
    if "src/index.ts" in desc or "src/index" in desc:
        src = root / "src"
        src.mkdir(exist_ok=True)
        (src / "index.ts").write_text(textwrap.dedent("""\
            // Main entry point
            export function main() {
              console.log("app started");
            }
        """))

    if "src/lib/parser" in desc:
        lib = root / "src" / "lib"
        lib.mkdir(parents=True, exist_ok=True)
        (lib / "parser.ts").write_text(textwrap.dedent("""\
            // Parser module
            export function parse(input: string): unknown {
              return JSON.parse(input);
            }
        """))

    if "src/auth" in desc:
        auth = root / "src" / "auth"
        auth.mkdir(parents=True, exist_ok=True)
        (auth / "index.ts").write_text(textwrap.dedent("""\
            // Auth module
            export async function verifyToken(token: string): Promise<boolean> {
              // JWT verification placeholder
              return token.length > 0;
            }

            export async function createSession(userId: string): Promise<string> {
              return `session-${userId}-${Date.now()}`;
            }
        """))

    # docs/prd.md
    if "docs/prd" in desc or "prd.md" in desc:
        docs = root / "docs"
        docs.mkdir(exist_ok=True)
        (docs / "prd.md").write_text(textwrap.dedent("""\
            # PRD — Payment Integration

            ## Problem Statement
            Users cannot pay for subscriptions inside the app.

            ## Solution
            Integrate Stripe Checkout for subscription management.

            ## User Stories
            - As a user, I can subscribe to a plan
            - As a user, I can manage my billing

            ## Out of Scope
            - Refunds (handled via Stripe dashboard)
            - Tax calculation
        """))

    # docs/agents/
    if "docs/agents" in desc:
        agents_dir = root / "docs" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        for fname in ["issue-tracker.md", "triage-labels.md", "domain.md",
                      "github-project.md", "session-config.md"]:
            if fname.replace(".md", "") in desc or "docs/agents" in desc:
                (agents_dir / fname).write_text(f"# {fname}\n\nPlaceholder content.\n")

    # .kiro directory
    if ".kiro" in desc:
        kiro = root / ".kiro"
        kiro.mkdir(exist_ok=True)
        (kiro / ".keep").write_text("")

    # .gemini directory
    if ".gemini" in desc:
        gemini = root / ".gemini"
        gemini.mkdir(exist_ok=True)
        (gemini / ".keep").write_text("")

    # .claude/settings.json
    if "posttooluse hook only" in desc or ("posttooluse" in desc and "no stop" in desc):
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

    # .claude/session.json
    if "session.json" in desc:
        c = root / ".claude"
        c.mkdir(exist_ok=True)
        # Parse issue number and effort from desc
        import re
        issue_match = re.search(r"issue (\d+)", desc)
        effort_match = re.search(r"effort (\d+)", desc)
        issue_num = int(issue_match.group(1)) if issue_match else 42
        effort = int(effort_match.group(1)) if effort_match else 2
        (c / "session.json").write_text(json.dumps({
            "phase": "execution",
            "active_issue": issue_num,
            "effort": effort,
            "task": f"Implement feature for issue #{issue_num}",
            "pick_up_point": "Finished auth middleware, starting route handlers next.",
        }, indent=2))

    # .claude/handoff.md
    if "handoff.md" in desc:
        c = root / ".claude"
        c.mkdir(exist_ok=True)
        (c / "handoff.md").write_text(textwrap.dedent("""\
            # Session Handoff
            Last updated: 2026-01-01T12:00:00Z

            ## Phase
            execute

            ## Active task
            Issue #42 — Add auth middleware

            ## Pick-up point
            Finished writing the middleware stub. Next: wire it into Express routes.

            ## Next session hint
            Continue execute phase. Run tests before writing new code.
        """))

    # .planning/STATE.md — idle state (clean prior session)
    if "state.md" in desc and "idle" in desc:
        planning = root / ".planning"
        planning.mkdir(exist_ok=True)
        import re
        phase_match = re.search(r"current[_ ]focus[:\s]+(\S+)", desc)
        phase = phase_match.group(1) if phase_match else "02-plan"
        task_match = re.search(r"issue (\d+)", desc)
        task_num = task_match.group(1) if task_match else "42"
        (planning / "STATE.md").write_text(textwrap.dedent(f"""\
            ---
            gsd_state_version: '1.0'
            status: in_progress
            progress:
              total_phases: 4
              completed_phases: 1
              total_plans: 0
              completed_plans: 0
              percent: 25
            ---

            # Project State

            ## Project Reference

            See: .planning/PROJECT.md (updated 2026-05-26)

            **Core value:** Harness engineering skill collection
            **Current focus:** {phase}

            ## Current Position

            Phase: 2 of 4 ({phase})
            Status: In progress
            Last activity: 2026-05-26 — context handover

            ## Session Continuity

            session_status: idle
            session_started:
            last_session: 2026-05-26 14:30
            Stopped at: Finished auth middleware, starting route handlers next.
            Resume file: .planning/phases/{phase}/.continue-here.md
        """))

    # .planning/STATE.md — in_progress with stale timestamp (interrupted session)
    if "state.md" in desc and "interrupted" in desc:
        planning = root / ".planning"
        planning.mkdir(exist_ok=True)
        import re
        task_match = re.search(r"issue (\d+)", desc)
        task_num = task_match.group(1) if task_match else "42"
        (planning / "STATE.md").write_text(textwrap.dedent(f"""\
            ---
            gsd_state_version: '1.0'
            status: in_progress
            progress:
              total_phases: 4
              completed_phases: 1
              total_plans: 0
              completed_plans: 0
              percent: 25
            ---

            # Project State

            ## Project Reference

            See: .planning/PROJECT.md (updated 2026-05-26)

            **Core value:** Harness engineering skill collection
            **Current focus:** 03-execute

            ## Current Position

            Phase: 3 of 4 (03-execute)
            Active task: #{task_num}
            Status: In progress
            Last activity: 2026-05-25 — session started

            ## Session Continuity

            session_status: in_progress
            session_started: 2026-05-25T10:15:00Z
            last_session: 2026-05-24 18:00
            Stopped at: Writing auth middleware tests.
            Resume file: .planning/phases/03-execute/.continue-here.md
        """))

    # .planning/phases/XX/.continue-here.md
    if ".continue-here.md" in desc or "continue-here" in desc:
        import re
        phase_match = re.search(r"phase[:\s]+(\S+)", desc)
        phase = phase_match.group(1) if phase_match else "03-execute"
        phase_dir = root / ".planning" / "phases" / phase
        phase_dir.mkdir(parents=True, exist_ok=True)
        (root / ".planning").mkdir(exist_ok=True)
        task_match = re.search(r"task (\d+)", desc)
        total_match = re.search(r"total[_ ]tasks (\d+)", desc)
        task_num = task_match.group(1) if task_match else "2"
        total = total_match.group(1) if total_match else "5"
        (phase_dir / ".continue-here.md").write_text(textwrap.dedent(f"""\
            ---
            phase: {phase}
            task: {task_num}
            total_tasks: {total}
            status: in_progress
            last_updated: 2026-05-26T14:30:00Z
            ---

            <current_state>
            Implementing auth middleware for issue #42.
            </current_state>

            <completed_work>
            - Task 1: Schema migration — Done
            - Task 2: Auth middleware stub — Done
            </completed_work>

            <remaining_work>
            - Task 2: Wire middleware into Express routes
            - Task 3: Write integration tests
            </remaining_work>

            <decisions_made>
            - Used JWT over session cookies for stateless auth
            </decisions_made>

            <blockers>
            None
            </blockers>

            <context>
            Middleware stub is in src/auth/middleware.ts. Routes in src/routes/.
            </context>

            <next_action>
            Start with: Wire auth middleware into src/routes/index.ts
            </next_action>
        """))

    # .planning/config.json
    if "planning config" in desc or "planning/config" in desc:
        planning = root / ".planning"
        planning.mkdir(exist_ok=True)
        has_harness = "harness key" in desc or "with harness" in desc
        config: dict = {
            "model_profile": "balanced",
            "commit_docs": True,
        }
        if has_harness:
            config["harness"] = {
                "schema_version": 1,
                "github": {
                    "owner": "org",
                    "repo": "my-project",
                    "default_branch": "main",
                },
                "docs_agents_dir": "docs/agents",
                "issue_tracker": "github",
            }
        (planning / "config.json").write_text(json.dumps(config, indent=2))
