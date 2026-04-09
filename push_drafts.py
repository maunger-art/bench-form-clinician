"""
push_drafts.py — Pushes draft files directly to GitHub via API.
Bypasses git push entirely, avoiding all merge conflicts.
"""

import json
import os
import base64
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).parent
DRAFTS_DIR = BASE_DIR / "drafts"
PREVIEW_PATH = BASE_DIR / "output" / "preview" / "index.html"
QUEUE_PATH = BASE_DIR / "queue.json"

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = "maunger-art/bench-form-clinician"
BRANCH = "main"
API = f"https://api.github.com/repos/{REPO}/contents"


def api_request(url, method="GET", data=None):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 404:
            return None
        raise Exception(f"API error {e.code}: {body}")


def get_file_sha(path):
    result = api_request(f"{API}/{path}?ref={BRANCH}")
    return result["sha"] if result else None


def push_file(repo_path, content_str, message):
    sha = get_file_sha(repo_path)
    content_b64 = base64.b64encode(content_str.encode()).decode()
    data = {
        "message": message,
        "content": content_b64,
        "branch": BRANCH,
    }
    if sha:
        data["sha"] = sha
    result = api_request(f"{API}/{repo_path}", method="PUT", data=data)
    print(f"  Pushed: {repo_path}")
    return result


def main():
    from datetime import date
    today = date.today().isoformat()

    # Push all draft files
    if DRAFTS_DIR.exists():
        for draft_file in DRAFTS_DIR.glob("*.json"):
            content = draft_file.read_text(encoding="utf-8")
            push_file(f"drafts/{draft_file.name}", content, f"Draft: {draft_file.stem}")

    # Push preview page
    if PREVIEW_PATH.exists():
        content = PREVIEW_PATH.read_text(encoding="utf-8")
        push_file("output/preview/index.html", content, f"Preview page: {today}")

    # Push queue
    if QUEUE_PATH.exists():
        content = QUEUE_PATH.read_text(encoding="utf-8")
        push_file("queue.json", content, f"Queue update: {today}")

    print("All files pushed via GitHub API.")


if __name__ == "__main__":
    main()
