"""
generate_preview_page.py — Generates the weekly preview page showing full draft articles.

Reads from drafts/*.json and renders each article in full so editors can
review content quality before approving for publication.

Output: output/preview/index.html
"""

import json
import re
from datetime import date, timedelta
from pathlib import Path
import urllib.parse

BASE_DIR = Path(__file__).parent
QUEUE_PATH = BASE_DIR / "queue.json"
DRAFTS_DIR = BASE_DIR / "drafts"
OUTPUT_PATH = BASE_DIR / "output" / "preview" / "index.html"

SITE_URL = "https://benchmarkps.org/blog"
APPROVAL_BASE_URL = "https://benchmarkps.org/blog/approve"
FEEDBACK_TOKEN = "BPSfeedback2026"
LOGO_URL = "/assets/benchmark-icon-nav-BhAe3FNc.png"


def load_json(path):
    with open(path) as f:
        return json.load(f)


def load_drafts() -> list[dict]:
    drafts = []
    if not DRAFTS_DIR.exists():
        return drafts
    for draft_file in sorted(DRAFTS_DIR.glob("*.json")):
        try:
            draft = load_json(draft_file)
            if draft.get("status") != "skipped":
                draft["_file"] = draft_file.name
                drafts.append(draft)
        except Exception:
            pass
    drafts.sort(key=lambda d: d.get("queue_position", 99))
    return drafts[:7]


def get_upcoming_dates(count: int) -> list[str]:
    dates = []
    current = date.today() + timedelta(days=1)
    while len(dates) < count:
        dates.append(current.strftime("%A %d %B"))
        current += timedelta(days=1)
    return dates


def build_faq_html(faq: list) -> str:
    if not faq:
        return ""
    items = ""
    for item in faq:
        items += f"""
<div class="faq-item">
  <h4>{item['q']}</h4>
  <p>{item['a']}</p>
</div>"""
    return f'<div class="faq-section"><h3>Frequently Asked Questions</h3>{items}</div>'


def build_preview_page(drafts: list[dict]) -> str:
    week_start = date.today() + timedelta(days=1)
    week_end = week_start + timedelta(days=6)
    generated = date.today().strftime("%d %B %Y")
    dates = get_upcoming_dates(len(drafts))

    draft_sections = ""
    toc_items = ""

    for i, draft in enumerate(drafts):
        title = draft.get("title", draft.get("original_topic", "Untitled"))
        meta = draft.get("meta_description", "")
        cluster = draft.get("cluster", "")
        tags = draft.get("tags", [])
        html_content = draft.get("html_content", "<p>Content not available.</p>")
        faq = draft.get("faq", [])
        status = draft.get("status", "pending")
        scheduled_date = dates[i] if i < len(dates) else ""

        tags_html = " ".join(f'<span class="tag">{t}</span>' for t in tags[:4])
        faq_html = build_faq_html(faq)

        t_encoded = urllib.parse.quote(title)
        approve_url = f"{APPROVAL_BASE_URL}/?token={FEEDBACK_TOKEN}&n={i+1}&t={t_encoded}&a=approve"
        skip_url = f"{APPROVAL_BASE_URL}/?token={FEEDBACK_TOKEN}&n={i+1}&t={t_encoded}&a=skip"
        edit_url = f"{APPROVAL_BASE_URL}/?token={FEEDBACK_TOKEN}&n={i+1}&t={t_encoded}&a=edit"
        delay_url = f"{APPROVAL_BASE_URL}/?token={FEEDBACK_TOKEN}&n={i+1}&t={t_encoded}&a=delay"

        status_badge = ""
        if status == "approved":
            status_badge = '<span class="status-badge status-approved">&#10003; Approved</span>'
        elif status == "skipped":
            status_badge = '<span class="status-badge status-skipped">&#10007; Skipped</span>'

        toc_items += f'<div class="toc-item"><span class="toc-num">#{i+1}</span><a href="#draft-{i+1}">{title[:75]}</a><span class="toc-date">{scheduled_date}</span></div>'

        draft_sections += f"""
<div class="draft-article" id="draft-{i+1}">
  <div class="draft-header">
    <div class="draft-meta-top">
      <span class="draft-number">Draft #{i+1}</span>
      <span class="draft-date">Scheduled: {scheduled_date}</span>
      {status_badge}
    </div>
    <h2 class="draft-title">{title}</h2>
    <div class="draft-meta">
      {f'<span class="cluster-badge">{cluster}</span>' if cluster else ''}
      {tags_html}
    </div>
    <p class="draft-description">{meta}</p>
    <div class="draft-actions">
      <a href="{approve_url}" class="btn btn-approve">&#10003; Approve</a>
      <a href="{skip_url}" class="btn btn-skip">&#10007; Skip</a>
      <a href="{edit_url}" class="btn btn-edit">&#9998; Edit title</a>
      <a href="{delay_url}" class="btn btn-delay">&#9201; Delay</a>
    </div>
  </div>
  <div class="draft-content">
    <div class="article-body">
      {html_content}
      {faq_html}
    </div>
  </div>
  <div class="draft-footer-actions">
    <a href="{approve_url}" class="btn btn-approve">&#10003; Approve for publication</a>
    <a href="{skip_url}" class="btn btn-skip">&#10007; Skip this post</a>
  </div>
</div>"""

    toc_html = f"""<div class="toc">
  <h3>This week</h3>
  <div class="toc-list">{toc_items}</div>
</div>""" if drafts else ""

    empty_html = """<div class="empty-state">
  <h2>No drafts available</h2>
  <p>Drafts are generated every Monday. Trigger the Generate Drafts workflow in GitHub Actions to create this week's drafts.</p>
</div>""" if not drafts else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Weekly Draft Review — Benchmark PS Blog</title>
  <meta name="robots" content="noindex, nofollow">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Lora:ital,wght@0,400;0,500;0,600;1,400&display=swap');
    :root {{
      --navy: hsl(213,66%,16%); --navy-soft: hsl(211,53%,23%);
      --blue: hsl(207,75%,40%); --blue-mid: hsl(199,68%,51%);
      --blue-pale: hsl(202,78%,91%); --blue-light: hsl(206,64%,83%);
      --teal: hsl(172,82%,30%); --warm: hsl(213,33%,97%);
      --warm-mid: hsl(212,26%,90%); --mid: hsl(211,27%,39%);
      --green: hsl(152,69%,32%); --red: hsl(0,72%,45%); --amber: hsl(35,88%,43%);
    }}
    * {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ font-family:'Plus Jakarta Sans',sans-serif; background:var(--warm); color:var(--navy); }}
    .site-nav {{ background:var(--navy); display:flex; align-items:center; justify-content:space-between; padding:0 3rem; height:66px; position:sticky; top:0; z-index:100; }}
    .nav-brand {{ display:flex; align-items:center; gap:12px; text-decoration:none; }}
    .nav-brand img {{ height:44px; width:auto; }}
    .nav-wordmark-main {{ font-size:18px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:white; line-height:1; }}
    .nav-wordmark-sub {{ font-size:8px; font-weight:600; letter-spacing:0.22em; text-transform:uppercase; color:var(--blue-mid); margin-top:4px; line-height:1; }}
    .nav-right {{ display:flex; align-items:center; gap:1.5rem; }}
    .nav-back {{ color:rgba(255,255,255,0.6); font-size:13px; text-decoration:none; }}
    .nav-back:hover {{ color:white; }}
    .draft-count {{ background:var(--blue-mid); color:white; font-size:11px; font-weight:700; padding:0.25rem 0.6rem; border-radius:10px; }}
    .page-header {{ background:var(--navy); padding:2.5rem 2rem; text-align:center; border-top:1px solid rgba(255,255,255,0.08); }}
    .page-header h1 {{ font-family:'Lora',serif; color:white; font-size:1.85rem; margin-bottom:0.4rem; }}
    .page-header p {{ color:rgba(255,255,255,0.65); font-size:0.9rem; }}
    .page-header .generated {{ color:rgba(255,255,255,0.35); font-size:0.75rem; margin-top:0.4rem; }}
    .drafts-container {{ max-width:860px; margin:0 auto 4rem; padding:1.5rem 1.5rem 0; display:flex; flex-direction:column; gap:1.5rem; }}
    .instructions {{ padding:1rem 1.5rem; background:white; border-radius:8px; border-left:4px solid var(--blue-mid); font-size:0.85rem; color:var(--mid); line-height:1.6; }}
    .instructions strong {{ color:var(--navy); }}
    .toc {{ padding:1rem 1.5rem; background:white; border-radius:8px; border:1px solid var(--warm-mid); }}
    .toc h3 {{ font-size:0.78rem; text-transform:uppercase; letter-spacing:0.08em; color:var(--mid); margin-bottom:0.75rem; }}
    .toc-list {{ display:flex; flex-direction:column; gap:0.4rem; }}
    .toc-item {{ display:flex; align-items:center; gap:0.75rem; font-size:0.85rem; flex-wrap:wrap; }}
    .toc-item a {{ color:var(--blue); text-decoration:none; flex:1; }}
    .toc-item a:hover {{ text-decoration:underline; }}
    .toc-num {{ font-size:0.72rem; font-weight:700; color:var(--mid); width:22px; flex-shrink:0; }}
    .toc-date {{ font-size:0.72rem; color:var(--mid); white-space:nowrap; }}
    .draft-article {{ background:white; border:1px solid var(--warm-mid); border-radius:14px; overflow:hidden; }}
    .draft-header {{ padding:1.75rem 2rem; border-bottom:1px solid var(--warm-mid); }}
    .draft-meta-top {{ display:flex; align-items:center; gap:0.75rem; margin-bottom:0.75rem; flex-wrap:wrap; }}
    .draft-number {{ font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--blue-mid); background:var(--blue-pale); padding:0.2rem 0.6rem; border-radius:4px; }}
    .draft-date {{ font-size:0.78rem; color:var(--mid); font-weight:500; }}
    .status-badge {{ font-size:0.72rem; font-weight:700; padding:0.2rem 0.6rem; border-radius:4px; }}
    .status-approved {{ background:hsl(152,52%,93%); color:var(--green); }}
    .status-skipped {{ background:hsl(0,72%,95%); color:var(--red); }}
    .draft-title {{ font-family:'Lora',serif; font-size:1.4rem; font-weight:600; color:var(--navy); line-height:1.3; margin-bottom:0.75rem; }}
    .draft-meta {{ display:flex; gap:0.5rem; flex-wrap:wrap; margin-bottom:0.75rem; align-items:center; }}
    .cluster-badge {{ font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:var(--teal); }}
    .tag {{ background:var(--blue-pale); color:var(--navy); padding:0.15rem 0.55rem; border-radius:4px; font-size:0.72rem; font-weight:500; }}
    .draft-description {{ font-size:0.9rem; color:var(--mid); line-height:1.6; margin-bottom:1.25rem; font-style:italic; }}
    .draft-actions {{ display:flex; gap:0.6rem; flex-wrap:wrap; }}
    .draft-content {{ padding:2rem; border-bottom:1px solid var(--warm-mid); }}
    .article-body {{ max-width:680px; }}
    .article-body h2 {{ font-family:'Plus Jakarta Sans',sans-serif; font-size:1.2rem; font-weight:700; color:var(--navy); margin:2.25rem 0 0.6rem; padding-bottom:0.4rem; border-bottom:2px solid var(--blue-pale); }}
    .article-body h3 {{ font-size:1rem; font-weight:600; color:var(--navy-soft); margin:1.5rem 0 0.4rem; }}
    .article-body p {{ font-size:0.95rem; line-height:1.75; color:hsl(213,30%,25%); margin-bottom:1.1rem; }}
    .article-body ul, .article-body ol {{ margin:0 0 1.1rem 1.5rem; }}
    .article-body li {{ font-size:0.95rem; line-height:1.7; color:hsl(213,30%,25%); margin-bottom:0.4rem; }}
    .article-body strong {{ color:var(--navy); font-weight:600; }}
    .article-body blockquote {{ border-left:3px solid var(--blue-mid); margin:1.5rem 0; padding:0.6rem 1.25rem; background:var(--warm); border-radius:0 6px 6px 0; color:var(--mid); font-style:italic; font-size:0.9rem; }}
    .article-body ol.references {{ font-size:0.8rem; color:var(--mid); line-height:1.6; margin-top:0.5rem; }}
    .faq-section {{ margin-top:2rem; padding-top:1.5rem; border-top:1px solid var(--warm-mid); }}
    .faq-section h3 {{ font-size:1rem; font-weight:700; color:var(--navy); margin-bottom:1rem; }}
    .faq-item {{ border-bottom:1px solid var(--warm-mid); padding:0.9rem 0; }}
    .faq-item h4 {{ font-size:0.88rem; font-weight:600; color:var(--navy); margin-bottom:0.35rem; }}
    .faq-item p {{ font-size:0.85rem; color:var(--mid); margin-bottom:0; line-height:1.6; }}
    .draft-footer-actions {{ padding:1.25rem 2rem; background:var(--warm); display:flex; gap:0.6rem; flex-wrap:wrap; }}
    .btn {{ display:inline-block; padding:0.55rem 1.25rem; border-radius:7px; font-size:0.82rem; font-weight:700; text-decoration:none; transition:opacity 0.15s; white-space:nowrap; }}
    .btn:hover {{ opacity:0.8; text-decoration:none; }}
    .btn-approve {{ background:hsl(152,52%,93%); color:var(--green); border:1px solid hsl(152,52%,78%); }}
    .btn-skip {{ background:hsl(0,72%,95%); color:var(--red); border:1px solid hsl(0,72%,83%); }}
    .btn-edit {{ background:var(--blue-pale); color:var(--blue); border:1px solid var(--blue-light); }}
    .btn-delay {{ background:hsl(39,92%,94%); color:var(--amber); border:1px solid hsl(39,92%,78%); }}
    .empty-state {{ text-align:center; padding:4rem 2rem; color:var(--mid); background:white; border-radius:14px; border:1px solid var(--warm-mid); }}
    .empty-state h2 {{ color:var(--navy); margin-bottom:0.75rem; }}
    .empty-state p {{ font-size:0.9rem; max-width:400px; margin:0 auto; line-height:1.6; }}
    .site-footer {{ background:var(--navy); padding:2rem; text-align:center; color:rgba(255,255,255,0.35); font-size:0.78rem; margin-top:2rem; }}
    .site-footer a {{ color:rgba(255,255,255,0.5); text-decoration:none; }}
    .site-footer a:hover {{ color:white; }}
    @media (max-width:640px) {{
      .site-nav {{ padding:0 1.25rem; }}
      .draft-header, .draft-content, .draft-footer-actions {{ padding:1.25rem; }}
      .draft-title {{ font-size:1.2rem; }}
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
    <div class="nav-right">
      {f'<span class="draft-count">{len(drafts)} drafts</span>' if drafts else ''}
      <a href="{SITE_URL}" class="nav-back">&#8592; Live blog</a>
    </div>
  </nav>

  <div class="page-header">
    <h1>Weekly Draft Review</h1>
    <p>{week_start.strftime("%d %B")} &#8212; {week_end.strftime("%d %B %Y")} &middot; {len(drafts)} articles ready</p>
    <div class="generated">Generated: {generated}</div>
  </div>

  <div class="drafts-container">
    <div class="instructions">
      <strong>Review each article before it publishes.</strong>
      Posts go live daily at 07:00 UTC. Use the buttons at the top or bottom of each article to
      <strong>approve</strong>, <strong>skip</strong>, <strong>edit the title</strong>, or <strong>delay</strong>.
      All posts publish automatically unless you take action.
    </div>
    {toc_html}
    {draft_sections}
    {empty_html}
  </div>

  <footer class="site-footer">
    <a href="{SITE_URL}">Live blog</a> &middot;
    <a href="https://benchmarkps.org">benchmarkps.org</a> &middot;
    Internal review page
  </footer>
</body>
</html>"""


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    drafts = load_drafts()
    print(f"Found {len(drafts)} drafts.")
    html = build_preview_page(drafts)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Preview page generated: {OUTPUT_PATH}")
    print(f"Live at: {SITE_URL}/preview/")


if __name__ == "__main__":
    main()
