"""promptfoo provider — calls pi CLI with --skill from a scaffolded project dir.

Pi loads SKILL.md + references natively (equivalent to claude --plugin-dir).
scaffold_files test var creates realistic project context so the skill can
discover files via tools, matching the isolation strategy in run_evals.py.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Ensure scaffold_helper (same dir) is importable regardless of promptfoo's cwd
sys.path.insert(0, str(Path(__file__).parent))
from scaffold_helper import scaffold

SKILL_DIR = (
    Path(__file__).parent.parent.parent
    / "skills" / "engineering" / "harness-engineering"
)
PI_EXE = shutil.which("pi") or shutil.which("pi.cmd") or "pi"
MODEL = "llamacpp/qwen3.6-35b-a3b-ud-q5_k_m"


def call_api(prompt: str, options: dict, context: dict) -> dict:
    scaffold_files = context.get("vars", {}).get("scaffold_files") or []

    with tempfile.TemporaryDirectory(prefix="pf_proj_") as project_dir:
        if scaffold_files:
            scaffold(project_dir, scaffold_files)

        result = subprocess.run(
            [
                PI_EXE, "-p",
                "--model", MODEL,
                "--skill", str(SKILL_DIR),
                "--no-context-files",
                prompt,
            ],
            capture_output=True, text=True, timeout=300,
            encoding="utf-8", errors="replace",
            cwd=project_dir,
        )

    if result.returncode != 0:
        stderr = result.stderr or ""
        if "context size" in stderr.lower() or "context size" in (result.stdout or "").lower():
            return {"error": "pi context size exceeded — eval skipped"}
        return {"error": f"pi exit {result.returncode}: {stderr[:200]}"}

    output = (result.stdout or "").strip()
    if not output:
        return {"error": "pi returned empty response"}
    return {"output": output}
