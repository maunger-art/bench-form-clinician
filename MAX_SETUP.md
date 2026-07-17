# Blog engine on the Claude Max plan

This engine used to call `api.anthropic.com` with an `ANTHROPIC_API_KEY` secret.
That key went invalid and **every "Daily Post" run failed with `401 API key is invalid`**.

It now runs on a **Claude Max subscription** via Claude Code headless (`claude -p`),
so there is no metered API bill. The swap is isolated to one shim file, `llm.py`.

## What changed
- **`llm.py`** — new. A drop-in stand-in for the slice of the `anthropic` SDK the
  engine used (`Anthropic().messages.create(...) -> .content[0].text`). It shells out
  to `claude -p --output-format json` instead of the HTTP API.
- **6 generation scripts** — one line each: `import anthropic` → `import llm as anthropic`.
  (`generate_post.py`, `generate_drafts.py`, `scrape_topics.py`,
  `rewrite_pillar_posts.py`, `social_snippets.py`, `send_preview_email.py`)
- **3 workflows** — `weekly_post.yml`, `monday_drafts.yml`, `preview_email.yml` now
  install Claude Code and pass `CLAUDE_CODE_OAUTH_TOKEN` instead of `ANTHROPIC_API_KEY`.

## One-time setup (required before the crons go green)
1. **Generate a token** on a machine logged into your Max plan:
   ```bash
   claude setup-token          # prints a 1-year CLAUDE_CODE_OAUTH_TOKEN
   ```
2. **Add the GitHub secret**: repo → Settings → Secrets and variables → Actions →
   New secret → name `CLAUDE_CODE_OAUTH_TOKEN`, paste the token.
3. (Optional) delete the old `ANTHROPIC_API_KEY` secret — it's no longer used.

## Test it locally first
On your Mac (already `claude login`-ed to Max), no token needed:
```bash
python generate_post.py          # uses your interactive Max session via `claude -p`
```
Override the model with `LLM_MODEL` (default `sonnet` = latest Sonnet):
```bash
LLM_MODEL=opus python generate_post.py
```

## Notes / caveats
- **Renew** the token roughly yearly (`claude setup-token` again) — you get a ~5-day expiry warning.
- Keep volume modest (Daily + 7 Monday drafts ≈ a dozen generations/week) and confirm
  Anthropic's ToS treats scheduled generation as acceptable subscription use before scaling.
- In CI use plain `claude -p` (the shim does) — **not** `--bare`, which ignores the token.
- `requirements.txt` still lists `anthropic`; it's now unused but harmless to keep.
