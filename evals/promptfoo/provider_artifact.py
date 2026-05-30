"""Artifact-aware promptfoo provider for evals that check file writes.

Extends provider.py with:
- Structured fixture format (fixture.files dict with json/text content)
- artifact-json block extraction from model output
- files_before / files_after / changed_files in the returned payload

Model output may contain a fenced artifact-json block:
    ```artifact-json
    {"writes": [{"path": ".harness/state.json", "content": "{...}"}]}
    ```
The provider applies those writes to the temp workspace, then assertions can
inspect files_after with type:python helpers from assertions/__init__.py.

Config (set in promptfoo provider config):
  skill_name: skill to load (same as provider.py)
"""

import json
import os
import re
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
_ARTIFACT_FENCE = re.compile(
    r"```artifact-json\s*\n(.*?)```", re.DOTALL
)


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


def _snapshot_dir(root: Path) -> dict[str, str]:
    """Return {relative_path: content} for all files under root."""
    out: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(root))
            try:
                out[rel] = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                out[rel] = "<binary>"
    return out


def _apply_fixture(root: Path, fixture: dict) -> None:
    """Apply structured fixture dict to temp workspace.

    fixture format:
      {"files": {".harness/state.json": {"json": {...}} | {"text": "..."}}}
    """
    for rel_path, spec in (fixture.get("files") or {}).items():
        dest = root / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if "json" in spec:
            dest.write_text(json.dumps(spec["json"], indent=2), encoding="utf-8")
        elif "text" in spec:
            dest.write_text(spec["text"], encoding="utf-8")


def _apply_artifact_writes(root: Path, artifact_json_str: str) -> list[str]:
    """Parse and apply writes from an artifact-json block. Returns list of changed paths."""
    try:
        artifact = json.loads(artifact_json_str)
    except json.JSONDecodeError:
        return []
    changed: list[str] = []
    for write in artifact.get("writes") or []:
        rel = write.get("path", "")
        content = write.get("content", "")
        if not rel:
            continue
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        changed.append(rel)
    return changed


def _build_file_listing(root: Path) -> str:
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
    vars_ = context.get("vars", {})

    # Support both legacy scaffold_files (list of hint strings) and
    # structured fixture dict (fixture.files format from spec).
    raw_scaffold = vars_.get("scaffold_files") or []
    if isinstance(raw_scaffold, str):
        try:
            raw_scaffold = json.loads(raw_scaffold)
        except (ValueError, json.JSONDecodeError):
            raw_scaffold = [raw_scaffold] if raw_scaffold else []

    raw_fixture = vars_.get("fixture") or {}
    if isinstance(raw_fixture, str):
        try:
            raw_fixture = json.loads(raw_fixture)
        except (ValueError, json.JSONDecodeError):
            raw_fixture = {}

    artifact_instruction = (
        "\n\nIf your response includes file writes, append a fenced artifact-json block "
        "at the end of your response with the files you would write:\n"
        "```artifact-json\n"
        '{"writes": [{"path": "relative/path", "content": "file content"}]}\n'
        "```"
    )

    with tempfile.TemporaryDirectory(prefix="pf_artifact_") as project_dir:
        root = Path(project_dir)

        if raw_scaffold:
            scaffold(project_dir, raw_scaffold)
        if raw_fixture:
            _apply_fixture(root, raw_fixture)

        files_before = _snapshot_dir(root)
        file_listing = _build_file_listing(root)
        user_message = f"Project files present:\n{file_listing}\n\n{prompt}{artifact_instruction}"

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
                    "max_tokens": 1024,
                },
                timeout=300,
            )
            resp.raise_for_status()
            output = resp.json()["choices"][0]["message"]["content"]
        except requests.exceptions.ConnectionError:
            return {"error": f"llamacpp server not reachable at {API_BASE}"}
        except Exception as exc:
            return {"error": str(exc)}

        # Extract and apply artifact-json block if present
        changed_files: list[str] = []
        parse_errors: list[str] = []
        match = _ARTIFACT_FENCE.search(output)
        if match:
            try:
                changed_files = _apply_artifact_writes(root, match.group(1).strip())
            except Exception as exc:
                parse_errors.append(str(exc))

        files_after = _snapshot_dir(root)

        # Strip artifact block from visible output for cleaner rubric grading
        clean_output = _ARTIFACT_FENCE.sub("", output).strip()

        return {
            "output": json.dumps({
                "output": clean_output,
                "files_before": files_before,
                "files_after": files_after,
                "changed_files": changed_files,
                "commands": [],
                "errors": parse_errors,
            })
        }
