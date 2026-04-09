"""
generate_preview_page.py — Generates a weekly preview page showing upcoming posts.

Outputs output/preview/index.html — a branded page showing the next 7 queued
articles with approve/skip/edit buttons linking to the approval flow.

Run every Monday at 07:00 UTC via GitHub Actions (before daily post generation).
"""

import json
from datetime import date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
QUEUE_PATH = BASE_DIR / "queue.json"
OUTPUT_PATH = BASE_DIR / "output" / "preview" / "index.html"

SITE_URL = "https://benchmarkps.org/blog"
APPROVAL_BASE_URL = "https://benchmarkps.org/blog/approve"
FEEDBACK_TOKEN = "BPSfeedback2026"
LOGO_URL = "/assets/benchmark-icon-nav-BhAe3FNc.png"


def load_json(path):
    with open(path) as f:
        return json.load(f)


def get_upcoming_dates(count: int = 7) -> list[str]:
    dates = []
    current = date.today() + timedelta(days=1)
    while len(dates) < count:
        dates.append(current.strftime("%A %d %B"))
        current += timedelta(days=1)
    return dates


def build_preview_page(topics: list[str], dates: list[str]) -> str:
    import urllib.parse

    week_start = date.today() + timedelta(days=1)
    week_end = week_start + timedelta(days=6)
    generated = date.today().strftime("%d %B %Y")

    cards = ""
    for i, (topic, scheduled_date) in enumerate(zip(topics, dates)):
        t_encoded = urllib.parse.quote(topic)
        approve_url = f"{APPROVAL_BASE_URL}/?token={FEEDBACK_TOKEN}&n={i+1}&t={t_encoded}&a=approve"
        skip_url = f"{APPROVAL_BASE_URL}/?token={FEEDBACK_TOKEN}&n={i+1}&t={t_encoded}&a=skip"
        edit_url = f"{APPROVAL_BASE_URL}/?token={FEEDBACK_TOKEN}&n={i+1}&t={t_encoded}&a=edit"
        delay_url = f"{APPROVAL_BASE_URL}/?token={FEEDBACK_TOKEN}&n={i+1}&t={t_encoded}&a=delay"

        cards += f"""
<div class="post-card">
  <div class="post-header">
    <span class="post-number">#{i+1}</span>
    <span class="post-date">{scheduled_date}</span>
  </div>
  <h2 class="post-title">{topic}</h2>
  <div class="post-actions">
    <a href="{approve_url}" class="btn btn-approve">✓ Approve</a>
    <a href="{skip_url}" class="btn btn-skip">✗ Skip</a>
    <a href="{edit_url}" class="btn btn-edit">✎ Edit</a>
    <a href="{delay_url}" class="btn btn-delay">⏱ Delay</a>
  </div>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Weekly Preview — Benchmark PS Blog</title>
  <meta name="robots" content="noindex, nofollow">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Lora:wght@400;600&display=swap');

    :root {{
      --navy: hsl(213, 66%, 16%);
      --navy-soft: hsl(211, 53%, 23%);
      --blue: hsl(207, 75%, 40%);
      --blue-mid: hsl(199, 68%, 51%);
      --blue-pale: hsl(202, 78%, 91%);
      --teal: hsl(172, 82%, 30%);
      --warm: hsl(213, 33%, 97%);
      --warm-mid: hsl(212, 26%, 90%);
      --mid: hsl(211, 27%, 39%);
      --green: hsl(152, 69%, 32%);
      --red: hsl(0, 72%, 45%);
      --amber: hsl(35, 88%, 43%);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: var(--warm);
      color: var(--navy);
      min-height: 100vh;
    }}

    /* Nav */
    .site-nav {{
      background: var(--navy);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 3rem;
      height: 66px;
    }}
    .nav-brand {{ display: flex; align-items: center; gap: 12px; text-decoration: none; }}
    .nav-brand img {{ height: 44px; width: auto; }}
    .nav-wordmark-main {{ font-size: 18px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: white; line-height: 1; }}
    .nav-wordmark-sub {{ font-size: 8px; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase; color: var(--blue-mid); margin-top: 4px; line-height: 1; }}
    .nav-back {{ color: rgba(255,255,255,0.6); font-size: 13px; text-decoration: none; }}
    .nav-back:hover {{ color: white; }}

    /* Header */
    .page-header {{
      background: var(--navy);
      padding: 3rem 2rem;
      text-align: center;
      border-top: 1px solid rgba(255,255,255,0.1);
    }}
    .page-header h1 {{
      font-family: 'Lora', serif;
      color: white;
      font-size: 2rem;
      margin-bottom: 0.5rem;
    }}
    .page-header p {{
      color: rgba(255,255,255,0.65);
      font-size: 0.95rem;
    }}
    .page-header .generated {{
      color: rgba(255,255,255,0.4);
      font-size: 0.78rem;
      margin-top: 0.5rem;
    }}

    /* Instructions */
    .instructions {{
      max-width: 760px;
      margin: 2rem auto;
      padding: 1.25rem 1.75rem;
      background: white;
      border-radius: 10px;
      border-left: 4px solid var(--blue-mid);
      font-size: 0.875rem;
      color: var(--mid);
      line-height: 1.7;
    }}
    .instructions strong {{ color: var(--navy); }}

    /* Post cards */
    .posts-container {{
      max-width: 760px;
      margin: 0 auto 4rem;
      padding: 0 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    .post-card {{
      background: white;
      border: 1px solid var(--warm-mid);
      border-radius: 12px;
      padding: 1.5rem;
      transition: box-shadow 0.2s;
    }}
    .post-card:hover {{ box-shadow: 0 4px 20px rgba(30, 58, 92, 0.08); }}

    .post-header {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 0.75rem;
    }}
    .post-number {{
      background: var(--blue-pale);
      color: var(--navy);
      font-size: 0.75rem;
      font-weight: 700;
      padding: 0.2rem 0.6rem;
      border-radius: 4px;
    }}
    .post-date {{
      font-size: 0.8rem;
      color: var(--mid);
      font-weight: 500;
    }}

    .post-title {{
      font-size: 1rem;
      font-weight: 700;
      color: var(--navy);
      line-height: 1.4;
      margin-bottom: 1rem;
    }}

    .post-actions {{
      display: flex;
      gap: 0.6rem;
      flex-wrap: wrap;
    }}

    .btn {{
      display: inline-block;
      padding: 0.45rem 1rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 700;
      text-decoration: none;
      transition: opacity 0.15s;
      white-space: nowrap;
    }}
    .btn:hover {{ opacity: 0.8; text-decoration: none; }}
    .btn-approve {{ background: hsl(152, 52%, 93%); color: var(--green); border: 1px solid hsl(152, 52%, 80%); }}
    .btn-skip {{ background: hsl(0, 72%, 95%); color: var(--red); border: 1px solid hsl(0, 72%, 85%); }}
    .btn-edit {{ background: var(--blue-pale); color: var(--blue); border: 1px solid var(--blue-light); }}
    .btn-delay {{ background: hsl(39, 92%, 94%); color: var(--amber); border: 1px solid hsl(39, 92%, 80%); }}

    /* Empty state */
    .empty-state {{
      text-align: center;
      padding: 4rem 2rem;
      color: var(--mid);
    }}
    .empty-state h2 {{ color: var(--navy); margin-bottom: 0.5rem; }}

    /* Footer */
    .site-footer {{
      background: var(--navy);
      padding: 2rem;
      text-align: center;
      color: rgba(255,255,255,0.4);
      font-size: 0.8rem;
    }}
    .site-footer a {{ color: rgba(255,255,255,0.5); text-decoration: none; }}
    .site-footer a:hover {{ color: white; }}

    @media (max-width: 640px) {{
      .site-nav {{ padding: 0 1.25rem; }}
      .page-header h1 {{ font-size: 1.5rem; }}
      .post-actions {{ gap: 0.4rem; }}
      .btn {{ font-size: 0.75rem; padding: 0.4rem 0.75rem; }}
    }}
  </style>
</head>
<body>

  <nav class="site-nav">
    <a href="https://benchmarkps.org" class="nav-brand">
      <img src="{LOGO_URL}" alt="Benchmark PS" onerror="this.style.display='none'">
      <span>
        <div class="nav-wordmark-main">Benchmark</div>
        <div class="nav-wordmark-sub">Performance Systems</div>
      </span>
    </a>
    <a href="{SITE_URL}" class="nav-back">← Back to blog</a>
  </nav>

  <div class="page-header">
    <h1>Weekly Content Preview</h1>
    <p>{week_start.strftime("%d %B")} — {week_end.strftime("%d %B %Y")} &middot; {len(topics)} posts scheduled</p>
    <div class="generated">Last updated: {generated}</div>
  </div>

  <div class="posts-container">

    <div class="instructions">
      <strong>How to give feedback:</strong> Click any button below to approve, skip, edit, or delay a post.
      All posts publish automatically at 07:00 UTC each day unless you take action.
      Changes are processed immediately when you click.
    </div>

    {"".join([f'<div>{cards}</div>']) if topics else ""}

    {cards if topics else '''
    <div class="empty-state">
      <h2>No posts scheduled</h2>
      <p>The queue is empty. New topics will be scraped and added automatically.</p>
    </div>'''}

  </div>

  <footer class="site-footer">
    <a href="{SITE_URL}">Benchmark PS Blog</a> &middot;
    <a href="https://benchmarkps.org">benchmarkps.org</a>
  </footer>

</body>
</html>"""


def main():
    queue = load_json(QUEUE_PATH)

    if not queue:
        print("Queue is empty — generating empty preview page.")
        topics = []
        dates = []
    else:
        topics = queue[:7]
        dates = get_upcoming_dates(len(topics))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    html = build_preview_page(topics, dates)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Preview page generated: {OUTPUT_PATH}")
    print(f"Live at: {SITE_URL}/preview/")


if __name__ == "__main__":
    main()
