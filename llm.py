"""
llm.py — Max-plan LLM shim for the Benchmark PS blog engine.

Drop-in replacement for the small slice of the `anthropic` SDK this engine uses:

    client = anthropic.Anthropic()
    msg = client.messages.create(model=..., max_tokens=..., system=..., messages=[...])
    text = msg.content[0].text

Instead of calling api.anthropic.com (which needs a funded ANTHROPIC_API_KEY and was
failing with 401 "API key is invalid"), it shells out to Claude Code headless
(`claude -p`), which authenticates via a Claude Max subscription:

  - Locally:  uses your interactive `claude login` session (no key needed).
  - In CI:    set CLAUDE_CODE_OAUTH_TOKEN (generated once via `claude setup-token`).

To adopt it, change ONE line at the top of each generation script:

    import anthropic          ->    import llm as anthropic

Everything else in those scripts stays the same.

Env overrides:
  LLM_MODEL     model alias/id passed to `claude --model` (default: "sonnet" = latest Sonnet)
  CLAUDE_BIN    path to the claude binary (default: "claude")
  LLM_TIMEOUT   per-call timeout in seconds (default: 300)
"""

import json
import os
import shutil
import subprocess

DEFAULT_MODEL = os.environ.get("LLM_MODEL", "sonnet")
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "claude")
TIMEOUT = int(os.environ.get("LLM_TIMEOUT", "300"))


class _Block:
    __slots__ = ("text", "type")

    def __init__(self, text: str):
        self.text = text
        self.type = "text"


class _Message:
    """Mimics the shape of anthropic's response object: .content[0].text"""

    def __init__(self, text: str):
        self.content = [_Block(text)]


def _build_prompt(system, messages) -> str:
    parts = []
    if system:
        parts.append(str(system).strip())
    for m in messages or []:
        content = m.get("content", "")
        if isinstance(content, list):
            content = "".join(
                b.get("text", "") if isinstance(b, dict) else str(b) for b in content
            )
        if content:
            parts.append(str(content))
    return "\n\n".join(parts)


class _Messages:
    def create(self, *, messages, model=None, system=None, max_tokens=None, **_ignored):
        prompt = _build_prompt(system, messages)

        if shutil.which(CLAUDE_BIN) is None:
            raise RuntimeError(
                f"'{CLAUDE_BIN}' not found on PATH. Install Claude Code "
                f"(`npm i -g @anthropic-ai/claude-code`) and either run `claude login` "
                f"(local) or set CLAUDE_CODE_OAUTH_TOKEN (CI, from `claude setup-token`)."
            )

        # The caller's hard-coded model id (e.g. an old sonnet-4) is intentionally
        # ignored in favour of LLM_MODEL/DEFAULT_MODEL so the engine tracks a current model.
        cmd = [
            CLAUDE_BIN,
            "-p",
            prompt,
            "--output-format",
            "json",
            "--model",
            os.environ.get("LLM_MODEL", DEFAULT_MODEL),
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        if proc.returncode != 0:
            raise RuntimeError(
                f"`claude -p` failed (exit {proc.returncode}). "
                f"stderr: {proc.stderr.strip()[:800] or '(empty)'}"
            )

        out = proc.stdout.strip()
        try:
            envelope = json.loads(out)
        except json.JSONDecodeError:
            # Not JSON-wrapped for some reason — treat stdout as the raw completion.
            return _Message(out)

        if isinstance(envelope, dict):
            if envelope.get("is_error"):
                raise RuntimeError(
                    f"`claude -p` returned an error: {envelope.get('result', out)[:800]}"
                )
            return _Message(envelope.get("result", ""))
        return _Message(out)


class Anthropic:
    """Stand-in for anthropic.Anthropic(); accepts and ignores any init args."""

    def __init__(self, *args, **kwargs):
        self.messages = _Messages()
