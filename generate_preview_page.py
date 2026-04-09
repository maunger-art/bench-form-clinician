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


def extract_references(html_content: str) -> list[str]:
    """Extract reference list items from html_content."""
    import re
    refs = []
    # Match <ol class="references">...</ol>
    ol_match = re.search(r'<ol[^>]*class="references"[^>]*>(.*?)</ol>', html_content, re.DOTALL | re.IGNORECASE)
    if not ol_match:
        return refs
    ol_html = ol_match.group(1)
    # Extract each <li> item
    items = re.findall(r'<li[^>]*>(.*?)</li>', ol_html, re.DOTALL)
    for item in items:
        # Strip HTML tags
        clean = re.sub(r'<[^>]+>', '', item).strip()
        clean = re.sub(r'\s+', ' ', clean)
        if clean and len(clean) > 10:
            refs.append(clean)
    return refs


def build_pubmed_url(reference_text: str) -> str:
    """Build a PubMed search URL from reference text."""
    import urllib.parse
    # Extract likely searchable terms: author surname + key words from title
    # Strip journal/year info (usually after the last full stop before journal abbrev)
    text = reference_text[:120]
    # Remove common punctuation noise
    text = re.sub(r'\d{4};\d+.*$', '', text).strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    query = urllib.parse.quote(text[:100])
    return f"https://pubmed.ncbi.nlm.nih.gov/?term={query}"


def build_reference_checklist(references: list[str]) -> str:
    """Build an HTML reference verification checklist."""
    if not references:
        return ""

    items = ""
    for i, ref in enumerate(references):
        pubmed_url = build_pubmed_url(ref)
        short_ref = ref[:120] + ("..." if len(ref) > 120 else "")
        items += f"""
<div class="ref-check-item">
  <label class="ref-check-label">
    <input type="checkbox" class="ref-checkbox" onchange="updateRefProgress(this)">
    <span class="ref-num">{i+1}</span>
    <span class="ref-text">{short_ref}</span>
  </label>
  <a href="{pubmed_url}" target="_blank" rel="noopener" class="pubmed-link">
    Search PubMed &#8599;
  </a>
</div>"""

    return f"""
<div class="ref-checklist">
  <div class="ref-checklist-header">
    <span class="ref-checklist-title">&#10003; Reference verification</span>
    <span class="ref-checklist-subtitle">Check each citation exists before approving</span>
    <span class="ref-progress" id="ref-progress-{{draft_id}}">0 / {len(references)} verified</span>
  </div>
  <div class="ref-checklist-items">
    {items}
  </div>
  <div class="ref-checklist-note">
    Click "Search PubMed" to verify each reference exists. Tick when confirmed.
    If a reference cannot be found, edit the title or skip this draft.
  </div>
</div>"""


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
        references = extract_references(html_content)
        ref_checklist = build_reference_checklist(references).replace('{draft_id}', str(i+1))

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

        draft_file = draft.get("_file", "unknown.json")
        draft_slug = draft.get("slug", f"draft-{i+1}")
        draft_sections += f"""
<div class="draft-article" id="draft-{i+1}" data-draft-file="{draft_file}" data-draft-slug="{draft_slug}">
  <div class="draft-header">
    <div class="draft-meta-top">
      <span class="draft-number">Draft #{i+1}</span>
      <span class="draft-date">Scheduled: {scheduled_date}</span>
      {status_badge}
    </div>
    <h2 class="draft-title" id="draft-title-{i+1}">{title}</h2>
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
      <button class="btn btn-edit-content" onclick="toggleContentEditor({i+1}, this)">&#9998; Edit content</button>
    </div>
  </div>
  <div class="draft-content">
    <div class="article-body" id="article-body-{i+1}">
      {html_content}
      {faq_html}
    </div>
    <div class="content-editor" id="content-editor-{i+1}" style="display:none;">
      <div class="editor-toolbar">
        <span class="editor-label">Editing article content — sections highlighted below</span>
        <div class="editor-toolbar-actions">
          <button class="btn btn-save" onclick="saveContent({i+1})">&#10003; Save changes</button>
          <button class="btn btn-cancel-edit" onclick="cancelEdit({i+1})">Cancel</button>
        </div>
      </div>
      <div class="sections-editor" id="sections-editor-{i+1}"></div>
      <div class="save-status" id="save-status-{i+1}"></div>
    </div>
    {ref_checklist}
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
    /* Reference checklist */
    .ref-checklist {{ margin:2rem 0 0; padding:1.5rem; background:hsl(39,92%,97%); border:1px solid hsl(39,92%,85%); border-radius:10px; }}
    .ref-checklist-header {{ display:flex; align-items:baseline; gap:1rem; flex-wrap:wrap; margin-bottom:1rem; }}
    .ref-checklist-title {{ font-size:0.85rem; font-weight:700; color:hsl(35,88%,30%); }}
    .ref-checklist-subtitle {{ font-size:0.78rem; color:var(--mid); flex:1; }}
    .ref-progress {{ font-size:0.75rem; font-weight:700; color:hsl(35,88%,35%); background:white; padding:0.2rem 0.6rem; border-radius:4px; border:1px solid hsl(39,92%,78%); }}
    .ref-checklist-items {{ display:flex; flex-direction:column; gap:0.6rem; margin-bottom:1rem; }}
    .ref-check-item {{ display:flex; align-items:flex-start; gap:0.75rem; padding:0.6rem 0.75rem; background:white; border-radius:6px; border:1px solid hsl(39,92%,85%); }}
    .ref-check-label {{ display:flex; align-items:flex-start; gap:0.6rem; flex:1; cursor:pointer; }}
    .ref-checkbox {{ margin-top:2px; flex-shrink:0; width:14px; height:14px; accent-color:var(--green); }}
    .ref-num {{ font-size:0.72rem; font-weight:700; color:var(--mid); min-width:18px; flex-shrink:0; margin-top:1px; }}
    .ref-text {{ font-size:0.78rem; color:var(--navy); line-height:1.5; }}
    .ref-check-item.verified {{ background:hsl(152,52%,97%); border-color:hsl(152,52%,80%); }}
    .ref-check-item.verified .ref-text {{ color:var(--mid); }}
    .pubmed-link {{ flex-shrink:0; font-size:0.72rem; font-weight:700; color:var(--blue); text-decoration:none; white-space:nowrap; padding:0.2rem 0.5rem; background:var(--blue-pale); border-radius:4px; margin-top:1px; }}
    .pubmed-link:hover {{ background:var(--blue-light); text-decoration:none; }}
    .ref-checklist-note {{ font-size:0.75rem; color:var(--mid); line-height:1.5; font-style:italic; }}
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
    /* Checked state */
    /* Content editor */
    .btn-edit-content {{ background:hsl(211,27%,93%); color:var(--mid); border:1px solid var(--warm-mid); }}
    .btn-edit-content:hover {{ background:var(--blue-pale); color:var(--navy); }}
    .btn-save {{ background:var(--green); color:white; border:none; padding:0.55rem 1.25rem; border-radius:7px; font-size:0.82rem; font-weight:700; cursor:pointer; }}
    .btn-save:hover {{ opacity:0.85; }}
    .btn-cancel-edit {{ background:white; color:var(--mid); border:1px solid var(--warm-mid); padding:0.55rem 1.25rem; border-radius:7px; font-size:0.82rem; font-weight:700; cursor:pointer; }}
    .content-editor {{ padding:1.5rem 2rem; background:hsl(213,33%,98%); border-top:2px solid var(--blue-pale); }}
    .editor-toolbar {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:1.25rem; flex-wrap:wrap; gap:0.75rem; }}
    .editor-label {{ font-size:0.82rem; font-weight:600; color:var(--mid); }}
    .editor-toolbar-actions {{ display:flex; gap:0.5rem; }}
    .sections-editor {{ display:flex; flex-direction:column; gap:1rem; }}
    .section-block {{ background:white; border:1px solid var(--warm-mid); border-radius:8px; overflow:hidden; }}
    .section-block-header {{ display:flex; align-items:center; justify-content:space-between; padding:0.75rem 1rem; background:var(--warm); border-bottom:1px solid var(--warm-mid); }}
    .section-block-title {{ font-size:0.82rem; font-weight:700; color:var(--navy); }}
    .section-edit-btn {{ font-size:0.75rem; font-weight:600; color:var(--blue); background:none; border:none; cursor:pointer; padding:0.2rem 0.5rem; }}
    .section-edit-btn:hover {{ text-decoration:underline; }}
    .section-preview {{ padding:1rem; font-size:0.88rem; line-height:1.65; color:hsl(213,30%,25%); max-height:200px; overflow-y:auto; }}
    .section-preview h2 {{ font-size:1rem; font-weight:700; color:var(--navy); margin-bottom:0.4rem; }}
    .section-preview h3 {{ font-size:0.9rem; font-weight:600; color:var(--navy-soft); margin:0.75rem 0 0.3rem; }}
    .section-preview p {{ margin-bottom:0.6rem; }}
    .section-textarea {{ width:100%; min-height:180px; padding:1rem; border:none; border-top:2px solid var(--blue-mid); font-family:monospace; font-size:0.8rem; line-height:1.6; color:var(--navy); background:hsl(207,75%,98%); resize:vertical; outline:none; }}
    .save-status {{ margin-top:0.75rem; font-size:0.82rem; font-weight:600; padding:0.5rem 0.75rem; border-radius:6px; display:none; }}
    .save-status.success {{ display:block; background:hsl(152,52%,93%); color:var(--green); }}
    .save-status.error {{ display:block; background:hsl(0,72%,95%); color:var(--red); }}
    .save-status.saving {{ display:block; background:var(--blue-pale); color:var(--blue); }}
    @media (max-width:640px) {{
      .site-nav {{ padding:0 1.25rem; }}
      .draft-header, .draft-content, .draft-footer-actions {{ padding:1.25rem; }}
      .draft-title {{ font-size:1.2rem; }}
    }}
  </style>
<script>
const GITHUB_OWNER = 'maunger-art';
const GITHUB_REPO = 'bench-form-clinician';
const FEEDBACK_TOKEN = 'BPSfeedback2026';

// ── Reference verification ──────────────────────────────
function updateRefProgress(checkbox) {{
  var item = checkbox.closest('.ref-check-item');
  if (checkbox.checked) {{ item.classList.add('verified'); }}
  else {{ item.classList.remove('verified'); }}
  var checklist = checkbox.closest('.ref-checklist');
  var total = checklist.querySelectorAll('.ref-checkbox').length;
  var checked = checklist.querySelectorAll('.ref-checkbox:checked').length;
  var progressEl = checklist.querySelector('.ref-progress');
  if (progressEl) {{
    progressEl.textContent = checked + ' / ' + total + ' verified';
    if (checked === total) {{
      progressEl.style.background = 'hsl(152,52%,93%)';
      progressEl.style.color = 'hsl(152,69%,25%)';
      progressEl.style.borderColor = 'hsl(152,52%,78%)';
    }}
  }}
}}

// ── Section editor ──────────────────────────────────────
function parseSections(html) {{
  // Split html_content by H2 headings into sections
  var sections = [];
  var parts = html.split(/(?=<h2[^>]*>)/i);
  parts.forEach(function(part, idx) {{
    if (!part.trim()) return;
    var titleMatch = part.match(/<h2[^>]*>(.*?)<\/h2>/i);
    var title = titleMatch ? titleMatch[1].replace(/<[^>]+>/g,'') : (idx === 0 ? 'Introduction' : 'Section ' + idx);
    sections.push({{ title: title, html: part }});
  }});
  return sections;
}}

function toggleContentEditor(draftNum, btn) {{
  var editor = document.getElementById('content-editor-' + draftNum);
  var body = document.getElementById('article-body-' + draftNum);
  if (editor.style.display === 'none') {{
    // Build sections editor
    var sectionsEl = document.getElementById('sections-editor-' + draftNum);
    var html = body.innerHTML;
    var sections = parseSections(html);
    sectionsEl.innerHTML = '';
    sections.forEach(function(sec, i) {{
      var block = document.createElement('div');
      block.className = 'section-block';
      block.dataset.index = i;
      block.innerHTML =
        '<div class="section-block-header">' +
          '<span class="section-block-title">' + sec.title + '</span>' +
          '<button class="section-edit-btn" onclick="toggleSectionEdit(this)">&#9998; Edit this section</button>' +
        '</div>' +
        '<div class="section-preview">' + sec.html + '</div>' +
        '<textarea class="section-textarea" style="display:none" spellcheck="true">' + sec.html.replace(/</g,'&lt;').replace(/>/g,'&gt;') + '</textarea>';
      sectionsEl.appendChild(block);
    }});
    editor.style.display = 'block';
    btn.textContent = '&#10007; Close editor';
    body.style.opacity = '0.4';
  }} else {{
    editor.style.display = 'none';
    btn.innerHTML = '&#9998; Edit content';
    body.style.opacity = '1';
  }}
}}

function toggleSectionEdit(btn) {{
  var block = btn.closest('.section-block');
  var preview = block.querySelector('.section-preview');
  var textarea = block.querySelector('.section-textarea');
  if (textarea.style.display === 'none') {{
    // Decode HTML entities for editing
    var raw = textarea.value.replace(/&lt;/g,'<').replace(/&gt;/g,'>');
    textarea.value = raw;
    textarea.style.display = 'block';
    preview.style.display = 'none';
    btn.textContent = '&#10007; Close';
    textarea.focus();
  }} else {{
    // Update preview with edited content
    var newHtml = textarea.value;
    preview.innerHTML = newHtml;
    textarea.value = newHtml.replace(/</g,'&lt;').replace(/>/g,'&gt;');
    textarea.style.display = 'none';
    preview.style.display = 'block';
    btn.innerHTML = '&#9998; Edit this section';
  }}
}}

function getReconstructedHtml(draftNum) {{
  var sectionsEl = document.getElementById('sections-editor-' + draftNum);
  var blocks = sectionsEl.querySelectorAll('.section-block');
  var html = '';
  blocks.forEach(function(block) {{
    var textarea = block.querySelector('.section-textarea');
    var preview = block.querySelector('.section-preview');
    // Use textarea value if currently being edited, otherwise use preview
    if (textarea.style.display !== 'none') {{
      html += textarea.value;
    }} else {{
      html += preview.innerHTML;
    }}
  }});
  return html;
}}

async function saveContent(draftNum) {{
  var article = document.getElementById('draft-' + draftNum);
  var draftFile = article.dataset.draftFile;
  var statusEl = document.getElementById('save-status-' + draftNum);

  statusEl.className = 'save-status saving';
  statusEl.textContent = 'Saving...';

  try {{
    // Get current draft from GitHub
    var getRes = await fetch(
      'https://api.github.com/repos/' + GITHUB_OWNER + '/' + GITHUB_REPO + '/contents/drafts/' + draftFile,
      {{ headers: {{ 'Accept': 'application/vnd.github.v3+json' }} }}
    );
    if (!getRes.ok) throw new Error('Could not read draft file');
    var fileData = await getRes.json();
    var draft = JSON.parse(atob(fileData.content.replace(/\n/g, '')));

    // Update html_content with edited sections
    draft.html_content = getReconstructedHtml(draftNum);

    // Push back to GitHub
    var putRes = await fetch(
      'https://api.github.com/repos/' + GITHUB_OWNER + '/' + GITHUB_REPO + '/contents/drafts/' + draftFile,
      {{
        method: 'PUT',
        headers: {{ 'Accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          message: 'Edit draft: ' + (draft.title || draftFile),
          content: btoa(unescape(encodeURIComponent(JSON.stringify(draft, null, 2)))),
          sha: fileData.sha,
          branch: 'main'
        }})
      }}
    );

    if (!putRes.ok) {{
      var err = await putRes.json();
      throw new Error(err.message || 'Save failed');
    }}

    // Update live preview
    var body = document.getElementById('article-body-' + draftNum);
    body.innerHTML = draft.html_content;
    body.style.opacity = '1';

    statusEl.className = 'save-status success';
    statusEl.textContent = '&#10003; Saved successfully. Changes will appear when preview page next regenerates.';

  }} catch(err) {{
    statusEl.className = 'save-status error';
    statusEl.textContent = 'Error: ' + err.message;
  }}
}}
</script>
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
