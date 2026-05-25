"""promptfoo provider — calls llamacpp server at localhost:8080.

Injects SKILL.md + all reference files as the system prompt, scaffolds a
temporary project directory from scaffold_files test vars, and sends a file
listing + eval prompt as the user message so the model sees realistic context.

The llamacpp server exposes a standard OpenAI-compatible API.
"""

import sys
import tempfile
from pathlib import Path

import requests

# Ensure scaffold_helper (same dir) is importable regardless of promptfoo's cwd
sys.path.insert(0, str(Path(__file__).parent))
from scaffold_helper import scaffold

SKILL_DIR = (
    Path(__file__).parent.parent.parent
    / "skills" / "engineering" / "harness-engineering"
)
API_BASE = "http://localhost:8080/v1"
MODEL = "Qwen3.6-35B-A3B-UD-Q5_K_M.gguf"


def _load_system_prompt() -> str:
    """Read SKILL.md + all reference/*.md files into a single system prompt."""
    parts: list[str] = []

    skill_md = SKILL_DIR / "SKILL.md"
    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        if text.startswith("---"):
            end = text.index("---", 3)
            text = text[end + 3:].lstrip()
        parts.append(text)

    refs = SKILL_DIR / "references"
    if refs.exists():
        for ref in sorted(refs.glob("*.md")):
            parts.append(f"---\n# {ref.name}\n\n{ref.read_text(encoding='utf-8')}")

    return "\n\n".join(parts)


def _build_file_listing(project_dir: str) -> str:
    """Walk scaffolded directory and return a file tree for the model."""
    root = Path(project_dir)
    lines: list[str] = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            rel = p.relative_to(root)
            lines.append(f"  {rel}")
    if not lines:
        return "(no project files — fresh empty directory)"
    return "\n".join(lines)


# Cache system prompt across calls within one eval run
_SYSTEM_PROMPT: str | None = None


def call_api(prompt: str, options: dict, context: dict) -> dict:
    global _SYSTEM_PROMPT
    if _SYSTEM_PROMPT is None:
        _SYSTEM_PROMPT = _load_system_prompt()

    scaffold_files = context.get("vars", {}).get("scaffold_files") or []

    with tempfile.TemporaryDirectory(prefix="pf_proj_") as project_dir:
        if scaffold_files:
            scaffold(project_dir, scaffold_files)

        file_listing = _build_file_listing(project_dir)
        user_message = (
            f"Project files present:\n{file_listing}\n\n"
            f"{prompt}"
        )

        try:
            resp = requests.post(
                f"{API_BASE}/chat/completions",
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": _SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2048,
                    "chat_template_kwargs": {"enable_thinking": False},
                },
                timeout=300,
            )
            resp.raise_for_status()
            data = resp.json()
            output = data["choices"][0]["message"]["content"]
            return {"output": output}

        except requests.exceptions.ConnectionError:
            return {"error": "llamacpp server not reachable at localhost:8080"}
        except Exception as exc:
            return {"error": str(exc)}
