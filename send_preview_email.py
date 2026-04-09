"""
send_preview_email.py — Sends a weekly preview of upcoming blog posts to editors.

Runs every Sunday at 07:00 UTC via GitHub Actions.
Shows the next 7 scheduled topics from queue.json with approve/edit/skip options.
Recipients reply to the email with instructions — processed by process_feedback.py.
"""

import json
import os
from datetime import date, timedelta
from pathlib import Path

import anthropic
import urllib.request
import urllib.parse

BASE_DIR = Path(__file__).parent
QUEUE_PATH = BASE_DIR / "queue.json"
MANIFEST_PATH = BASE_DIR / "posts_manifest.json"

RESEND_API_KEY = os.environ["RESEND_API_KEY"]
FROM_EMAIL = "info@benchmarkps.org"
FROM_NAME = "Benchmark PS Blog"
TO_EMAILS = ["mike@benchmarkps.org", "gus@benchmarkps.org"]
REPLY_TO = "blog-feedback@benchmarkps.org"

SITE_URL = "https://benchmarkps.org/blog"


def load_json(path):
    with open(path) as f:
        return json.load(f)


def get_upcoming_dates(count: int = 7) -> list[str]:
    """Get the next N weekdays starting from tomorrow."""
    dates = []
    current = date.today() + timedelta(days=1)
    while len(dates) < count:
        dates.append(current.strftime("%A %d %B"))
        current += timedelta(days=1)
    return dates


def generate_preview_summaries(topics: list[str], existing_titles: list[str]) -> list[dict]:
    """Use Claude to generate a one-line summary for each upcoming topic."""
    client = anthropic.Anthropic()

    prompt = f"""For each of the following blog article topics planned for the Benchmark PS blog,
write a single sentence (max 20 words) describing what the article will cover and why it matters
to physiotherapy clinic owners and clinicians.

Topics:
{chr(10).join(f"{i+1}. {t}" for i, t in enumerate(topics))}

Return ONLY a JSON array of objects with "topic" and "summary" keys. No preamble.
[{{"topic": "...", "summary": "..."}}, ...]"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


def build_email_html(topics: list[str], summaries: list[dict], dates: list[str]) -> str:
    """Build the HTML preview email."""

    rows = ""
    for i, (topic, scheduled_date) in enumerate(zip(topics, dates)):
        summary = summaries[i]["summary"] if i < len(summaries) else ""
        row_bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
        rows += f"""
        <tr style="background: {row_bg};">
          <td style="padding: 16px 20px; border-bottom: 1px solid #e8edf2; width: 120px;">
            <span style="font-size: 12px; color: #64748b; font-weight: 500;">{scheduled_date}</span>
          </td>
          <td style="padding: 16px 20px; border-bottom: 1px solid #e8edf2;">
            <div style="font-size: 14px; font-weight: 600; color: #1e3a5f; margin-bottom: 4px;">{topic}</div>
            <div style="font-size: 13px; color: #64748b; line-height: 1.5;">{summary}</div>
          </td>
          <td style="padding: 16px 20px; border-bottom: 1px solid #e8edf2; width: 80px; text-align: center;">
            <span style="font-size: 11px; color: #22c55e; font-weight: 600; background: #f0fdf4; padding: 3px 8px; border-radius: 4px;">#{i+1}</span>
          </td>
        </tr>"""

    week_start = date.today() + timedelta(days=1)
    week_end = week_start + timedelta(days=6)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Benchmark PS Blog — Weekly Preview</title>
</head>
<body style="margin: 0; padding: 0; background: #f1f5f9; font-family: 'Segoe UI', Arial, sans-serif;">

  <div style="max-width: 680px; margin: 40px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08);">

    <!-- Header -->
    <div style="background: hsl(213, 66%, 16%); padding: 32px 40px;">
      <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; color: hsl(199, 68%, 51%); margin-bottom: 8px;">Benchmark PS Blog</div>
      <h1 style="margin: 0; font-size: 22px; font-weight: 700; color: white; line-height: 1.3;">
        Weekly Content Preview
      </h1>
      <p style="margin: 8px 0 0; font-size: 14px; color: rgba(255,255,255,0.65);">
        {week_start.strftime("%d %B")} — {week_end.strftime("%d %B %Y")} &middot; {len(topics)} posts scheduled
      </p>
    </div>

    <!-- Intro -->
    <div style="padding: 28px 40px 20px; border-bottom: 1px solid #e8edf2;">
      <p style="margin: 0; font-size: 14px; color: #475569; line-height: 1.7;">
        Here are the articles scheduled to publish this week. Each post generates automatically at <strong>07:00 UTC</strong> daily.
        To make changes before a post publishes, reply to this email with the post number and your instruction:
      </p>
      <div style="margin: 16px 0 0; background: #f8fafc; border-radius: 8px; padding: 16px 20px;">
        <div style="font-size: 13px; color: #334155; line-height: 1.8;">
          <strong style="color: #1e3a5f;">APPROVE #3</strong> — publish as planned<br>
          <strong style="color: #1e3a5f;">SKIP #2</strong> — remove from queue<br>
          <strong style="color: #1e3a5f;">EDIT #1: New title here</strong> — replace with your title<br>
          <strong style="color: #1e3a5f;">DELAY #4</strong> — move to end of queue
        </div>
      </div>
      <p style="margin: 12px 0 0; font-size: 12px; color: #94a3b8;">
        All posts are approved by default unless you reply. Replies are processed every Wednesday at 07:00 UTC.
      </p>
    </div>

    <!-- Post table -->
    <table style="width: 100%; border-collapse: collapse;">
      <thead>
        <tr style="background: #f8fafc;">
          <th style="padding: 12px 20px; text-align: left; font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; border-bottom: 2px solid #e8edf2;">Date</th>
          <th style="padding: 12px 20px; text-align: left; font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; border-bottom: 2px solid #e8edf2;">Article</th>
          <th style="padding: 12px 20px; text-align: center; font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; border-bottom: 2px solid #e8edf2;">#</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>

    <!-- Queue status -->
    <div style="padding: 20px 40px; background: #f8fafc; border-top: 1px solid #e8edf2;">
      <p style="margin: 0; font-size: 13px; color: #64748b;">
        <strong style="color: #1e3a5f;">Queue status:</strong> {len(topics)} posts scheduled.
        The queue auto-refills daily from Reddit, PubMed, BJSM, NICE guidelines, and podcast feeds.
      </p>
    </div>

    <!-- Footer -->
    <div style="padding: 24px 40px; border-top: 1px solid #e8edf2; text-align: center;">
      <a href="{SITE_URL}" style="font-size: 13px; color: hsl(207, 75%, 40%); text-decoration: none; font-weight: 600;">View live blog</a>
      <span style="color: #cbd5e1; margin: 0 12px;">&middot;</span>
      <a href="https://github.com/maunger-art/bench-form-clinician" style="font-size: 13px; color: hsl(207, 75%, 40%); text-decoration: none; font-weight: 600;">View queue on GitHub</a>
      <p style="margin: 12px 0 0; font-size: 12px; color: #94a3b8;">
        Benchmark Performance Systems &middot; benchmarkps.org
      </p>
    </div>

  </div>
</body>
</html>"""


def build_email_text(topics: list[str], summaries: list[dict], dates: list[str]) -> str:
    """Plain text version of the email."""
    lines = [
        "BENCHMARK PS BLOG — WEEKLY PREVIEW",
        "=" * 40,
        "",
        "Posts scheduled for this week:",
        "",
    ]
    for i, (topic, scheduled_date) in enumerate(zip(topics, dates)):
        summary = summaries[i]["summary"] if i < len(summaries) else ""
        lines.append(f"#{i+1} — {scheduled_date}")
        lines.append(f"   {topic}")
        lines.append(f"   {summary}")
        lines.append("")

    lines += [
        "-" * 40,
        "To make changes, reply with:",
        "  APPROVE #3 — publish as planned",
        "  SKIP #2    — remove from queue",
        "  EDIT #1: New title here",
        "  DELAY #4   — move to end of queue",
        "",
        "Replies processed every Wednesday at 07:00 UTC.",
        "All posts publish by default unless you reply.",
        "",
        f"View live blog: {SITE_URL}",
    ]
    return "\n".join(lines)


def send_email(subject: str, html: str, text: str):
    """Send email via Resend API."""
    payload = {
        "from": f"{FROM_NAME} <{FROM_EMAIL}>",
        "to": TO_EMAILS,
        "reply_to": REPLY_TO,
        "subject": subject,
        "html": html,
        "text": text,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=data,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read())
            print(f"Email sent successfully. ID: {result.get('id')}")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Email send failed: {e.code} — {error_body}")
        return False


def main():
    queue = load_json(QUEUE_PATH)
    manifest = load_json(MANIFEST_PATH)

    if not queue:
        print("Queue is empty — nothing to preview.")
        return

    # Preview next 7 topics
    upcoming = queue[:7]
    dates = get_upcoming_dates(len(upcoming))
    existing_titles = [p["title"] for p in manifest]

    print(f"Generating preview for {len(upcoming)} upcoming posts...")

    # Generate summaries with Claude
    try:
        summaries = generate_preview_summaries(upcoming, existing_titles)
    except Exception as e:
        print(f"Summary generation failed: {e} — sending without summaries")
        summaries = [{"topic": t, "summary": ""} for t in upcoming]

    # Build email
    week_start = date.today() + timedelta(days=1)
    subject = f"Benchmark PS Blog — {len(upcoming)} posts scheduled w/c {week_start.strftime('%d %b')}"
    html = build_email_html(upcoming, summaries, dates)
    text = build_email_text(upcoming, summaries, dates)

    # Send
    print(f"Sending preview to: {', '.join(TO_EMAILS)}")
    success = send_email(subject, html, text)

    if success:
        print("Weekly preview sent successfully.")
    else:
        print("Failed to send preview email.")
        exit(1)


if __name__ == "__main__":
    main()
