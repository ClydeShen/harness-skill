"""promptfoo grader provider — LLM judge via llamacpp HTTP server.

Receives the full grading prompt from promptfoo's llm-rubric assertion and
returns a JSON verdict: {"pass": bool, "score": float, "reason": str}.
"""

import json
import os
import time

import requests

API_BASE = os.getenv("EVAL_API_BASE", "http://localhost:8080/v1")
MODEL = os.getenv("EVAL_GRADER_MODEL", "default-model")

_SYSTEM = (
    "You are a strict pass/fail evaluator for LLM responses. "
    "Read the rubric and the response, then output ONLY valid JSON — nothing else.\n"
    'Format: {"pass": true, "score": 1.0, "reason": "one sentence"}\n'
    'or:     {"pass": false, "score": 0.0, "reason": "one sentence"}'
)


def _extract_verdict(raw: str) -> dict | None:
    """Extract first JSON object containing a 'pass' key using bracket matching.

    Handles nested braces in reason strings and Qwen3 <think>...</think> preamble.
    """
    try:
        obj = json.loads(raw.strip())
        if isinstance(obj, dict) and "pass" in obj:
            return obj
    except json.JSONDecodeError:
        pass

    depth = 0
    start = -1
    for i, c in enumerate(raw):
        if c == "{":
            if depth == 0:
                start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    obj = json.loads(raw[start : i + 1])
                    if isinstance(obj, dict) and "pass" in obj:
                        return obj
                except json.JSONDecodeError:
                    pass
                start = -1
    return None


def _build_messages(prompt: str) -> list[dict]:
    """Convert prompt to chat messages, handling both JSON array and plain text."""
    try:
        parsed = json.loads(prompt)
        if isinstance(parsed, list) and parsed and "role" in parsed[0]:
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    return [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": prompt},
    ]


def call_api(prompt: str, options: dict, context: dict) -> dict:
    messages = _build_messages(prompt)  # handles JSON messages array or plain string

    for attempt in range(3):
        try:
            resp = requests.post(
                f"{API_BASE}/chat/completions",
                json={
                    "model": MODEL,
                    "messages": messages,
                    "temperature": 0,
                    "max_tokens": 512,
                },
                timeout=120,
            )
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.ConnectionError:
            return {"error": f"llamacpp server not reachable at {API_BASE}"}
        except Exception as exc:
            return {"error": str(exc)}

        verdict = _extract_verdict(raw)
        if verdict is not None:
            return {"output": json.dumps(verdict)}

        upper = raw.upper()
        if "PASS" in upper and "FAIL" not in upper:
            return {"output": '{"pass": true, "score": 1.0, "reason": "model said PASS"}'}
        if "FAIL" in upper:
            return {"output": '{"pass": false, "score": 0.0, "reason": "model said FAIL"}'}

        if attempt < 2:
            time.sleep(1)

    return {"output": '{"pass": false, "score": 0.0, "reason": "grader produced no parseable verdict"}'}
