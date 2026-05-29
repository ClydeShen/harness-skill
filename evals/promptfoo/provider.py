"""promptfoo provider — calls llamacpp server at localhost:8080.

Injects SKILL.md + all reference files as the system prompt, scaffolds a
temporary project directory from scaffold_files test vars, and sends a file
listing + eval prompt as the user message so the model sees realistic context.

Config (set in promptfooconfig per provider):
  skill_name: name of skill to load, e.g. "harness-audit".
              Resolved to skills/<category>/<skill_name>/ under the repo root.
"""

import os
import sys
import tempfile
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from scaffold_helper import scaffold

REPO_ROOT = Path(__file__).parent.parent.parent
API_BASE = os.getenv("EVAL_API_BASE", "http://localhost:8080/v1")
MODEL = os.getenv("EVAL_PROVIDER_MODEL", "default-model")

_SYSTEM_CACHE: dict[str, str] = {}


def _resolve_skill_dir(skill_name: str) -> Path:
    matches = list(REPO_ROOT.glob(f"skills/*/{skill_name}"))
    if not matches:
        raise FileNotFoundError(f"skill '{skill_name}' not found under skills/*/")
    return matches[0]


def _load_system_prompt(skill_dir: Path) -> str:
    parts: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        if text.startswith("---"):
            end = text.index("---", 3)
            text = text[end + 3:].lstrip()
        parts.append(text)
    refs = skill_dir / "references"
    if refs.exists():
        for ref in sorted(refs.glob("*.md")):
            parts.append(f"---\n# {ref.name}\n\n{ref.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def _build_file_listing(project_dir: str) -> str:
    root = Path(project_dir)
    lines = [f"  {p.relative_to(root)}" for p in sorted(root.rglob("*")) if p.is_file()]
    return "\n".join(lines) if lines else "(no project files — fresh empty directory)"


def call_api(prompt: str, options: dict, context: dict) -> dict:
    skill_name = (options.get("config") or {}).get("skill_name", "harness-audit")

    if skill_name not in _SYSTEM_CACHE:
        try:
            skill_dir = _resolve_skill_dir(skill_name)
        except FileNotFoundError as exc:
            return {"error": str(exc)}
        _SYSTEM_CACHE[skill_name] = _load_system_prompt(skill_dir)

    system_prompt = _SYSTEM_CACHE[skill_name]
    scaffold_files = context.get("vars", {}).get("scaffold_files") or []

    with tempfile.TemporaryDirectory(prefix="pf_proj_") as project_dir:
        if scaffold_files:
            scaffold(project_dir, scaffold_files)
        file_listing = _build_file_listing(project_dir)
        user_message = f"Project files present:\n{file_listing}\n\n{prompt}"

        try:
            resp = requests.post(
                f"{API_BASE}/chat/completions",
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2048,
                    "chat_template_kwargs": {"enable_thinking": False},
                },
                timeout=300,
            )
            resp.raise_for_status()
            output = resp.json()["choices"][0]["message"]["content"]
            return {"output": output}
        except requests.exceptions.ConnectionError:
            return {"error": f"llamacpp server not reachable at {API_BASE}"}
        except Exception as exc:
            return {"error": str(exc)}
