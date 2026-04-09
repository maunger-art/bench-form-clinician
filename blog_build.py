"""
blog_build.py — Benchmark PS static site HTML builder
Reads posts_manifest.json and generates a deployable static site in output/
"""

import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

# ─────────────────────────────────────────────
# BRAND CONFIGURATION
# ─────────────────────────────────────────────
SITE_NAME = "Benchmark PS"
SITE_URL = "https://benchmarkps.org/blog/"
BRAND_PRIMARY_COLOR = "#1A3C5E"
BRAND_ACCENT_COLOR = "#2E86AB"
BRAND_FONT = "Inter, system-ui, sans-serif"
LOGO_URL = "/assets/logo.svg"
GA4_ID = "G-XXXXXXXXXX"
GSC_VERIFICATION = "google-site-verification=C9WQu-TDa_vbA_IuL9Y6WUumlKUUYlWBY3vXYMV6UkY"
AUTHOR_NAME = "Benchmark PS"
AUTHOR_URL = SITE_URL
PUBLISHER_LOGO = f"{SITE_URL}/assets/logo.png"

NAV_LINKS = [
    {"label": "Platform", "href": "https://benchmarkps.com/platform"},
    {"label": "Evidence", "href": "https://benchmarkps.com/evidence"},
    {"label": "For Clinics", "href": "https://benchmarkps.com/clinics"},
    {"label": "Blog", "href": SITE_URL},
    {"label": "Book a Demo", "href": "https://benchmarkps.com/demo"},
]

FOOTER_TEXT = (
    "© 2025 Benchmark PS. Performance measurement and clinical decision-support "
    "for physiotherapy practices."
)

CTA_TEXT = "See how Benchmark PS works in practice"
CTA_URL = "https://benchmarkps.com/demo"


# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
MANIFEST_PATH = BASE_DIR / "posts_manifest.json"
OUTPUT_DIR = BASE_DIR / "output"
POSTS_DIR = OUTPUT_DIR / "posts"


def load_manifest():
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def slug_to_url(slug):
    return f"{SITE_URL}/posts/{slug}/"


def build_nav(active_href=""):
    links_html = ""
    for link in NAV_LINKS:
        active = ' class="active"' if link["href"] == active_href else ""
        links_html += f'<a href="{link["href"]}"{active}>{link["label"]}</a>\n'
    return f"""
<nav class="site-nav">
  <a class="nav-logo" href="{SITE_URL}">
    <strong>{SITE_NAME}</strong>
  </a>
  <div class="nav-links">
    {links_html}
  </div>
</nav>"""


def build_footer():
    return f"""
<footer class="site-footer">
  <div class="footer-inner">
    <p>{FOOTER_TEXT}</p>
    <div class="footer-links">
      <a href="https://benchmarkps.com/privacy">Privacy</a>
      <a href="https://benchmarkps.com/terms">Terms</a>
      <a href="{SITE_URL}/feed.xml">RSS</a>
    </div>
  </div>
</footer>"""


def build_css():
    return f"""
<style>
  :root {{
    --primary: {BRAND_PRIMARY_COLOR};
    --accent: {BRAND_ACCENT_COLOR};
    --text: #1a1a1a;
    --muted: #555;
    --bg: #ffffff;
    --border: #e5e7eb;
    --max-width: 740px;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: {BRAND_FONT};
    font-size: 17px;
    line-height: 1.7;
    color: var(--text);
    background: var(--bg);
  }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  /* Nav */
  .site-nav {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 2rem;
    border-bottom: 1px solid var(--border);
    background: var(--bg);
    position: sticky;
    top: 0;
    z-index: 100;
  }}
  .nav-logo {{ font-size: 1.1rem; color: var(--primary); font-weight: 700; }}
  .nav-links {{ display: flex; gap: 1.5rem; align-items: center; }}
  .nav-links a {{ color: var(--muted); font-size: 0.95rem; }}
  .nav-links a.active {{ color: var(--primary); font-weight: 600; }}
  .nav-links a[href*="demo"] {{
    background: var(--primary);
    color: white;
    padding: 0.45rem 1rem;
    border-radius: 6px;
    font-weight: 600;
  }}

  /* Article */
  .article-wrap {{
    max-width: var(--max-width);
    margin: 3rem auto;
    padding: 0 1.5rem;
  }}
  .article-meta {{
    font-size: 0.85rem;
    color: var(--muted);
    margin-bottom: 1rem;
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }}
  .tag {{
    background: #f0f4f8;
    color: var(--primary);
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.78rem;
    font-weight: 500;
  }}
  h1 {{ font-size: 2rem; line-height: 1.25; color: var(--primary); margin-bottom: 1rem; }}
  h2 {{ font-size: 1.35rem; color: var(--primary); margin: 2.5rem 0 0.75rem; }}
  h3 {{ font-size: 1.1rem; margin: 1.5rem 0 0.5rem; }}
  p {{ margin-bottom: 1.2rem; }}
  ul, ol {{ margin: 0 0 1.2rem 1.5rem; }}
  li {{ margin-bottom: 0.4rem; }}
  blockquote {{
    border-left: 4px solid var(--accent);
    margin: 1.5rem 0;
    padding: 0.75rem 1.25rem;
    background: #f8fafc;
    color: var(--muted);
    font-style: italic;
  }}
  .cta-box {{
    background: var(--primary);
    color: white;
    padding: 2rem;
    border-radius: 10px;
    margin: 3rem 0;
    text-align: center;
  }}
  .cta-box a {{
    display: inline-block;
    background: white;
    color: var(--primary);
    padding: 0.75rem 2rem;
    border-radius: 6px;
    font-weight: 700;
    margin-top: 0.75rem;
    font-size: 1rem;
  }}
  .faq-section {{ margin-top: 3rem; }}
  .faq-item {{ border-bottom: 1px solid var(--border); padding: 1.25rem 0; }}
  .faq-item h3 {{ color: var(--primary); font-size: 1rem; margin: 0 0 0.5rem; }}

  /* Index grid */
  .blog-hero {{
    background: var(--primary);
    color: white;
    padding: 4rem 2rem;
    text-align: center;
  }}
  .blog-hero h1 {{ color: white; font-size: 2.25rem; }}
  .blog-hero p {{ color: rgba(255,255,255,0.8); font-size: 1.1rem; margin-top: 0.75rem; }}
  .post-grid {{
    max-width: 1100px;
    margin: 3rem auto;
    padding: 0 1.5rem;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.75rem;
  }}
  .post-card {{
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.5rem;
    transition: box-shadow 0.2s;
  }}
  .post-card:hover {{ box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
  .post-card .cluster {{
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--accent);
    font-weight: 600;
    margin-bottom: 0.5rem;
  }}
  .post-card h2 {{ font-size: 1.1rem; margin: 0 0 0.5rem; color: var(--text); }}
  .post-card p {{ font-size: 0.9rem; color: var(--muted); margin-bottom: 1rem; }}
  .post-card .read-more {{
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--accent);
  }}

  /* Footer */
  .site-footer {{
    border-top: 1px solid var(--border);
    padding: 2rem;
    text-align: center;
    color: var(--muted);
    font-size: 0.875rem;
    margin-top: 4rem;
  }}
  .footer-links {{ display: flex; gap: 1.5rem; justify-content: center; margin-top: 0.75rem; }}

  @media (max-width: 640px) {{
    .site-nav {{ flex-direction: column; gap: 0.75rem; }}
    .nav-links {{ flex-wrap: wrap; justify-content: center; }}
    h1 {{ font-size: 1.6rem; }}
  }}
</style>"""


def build_json_ld(post):
    url = slug_to_url(post["slug"])
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post["title"],
        "description": post["meta_description"],
        "datePublished": post["date"],
        "dateModified": post.get("updated", post["date"]),
        "author": {"@type": "Organization", "name": AUTHOR_NAME, "url": AUTHOR_URL},
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "logo": {"@type": "ImageObject", "url": PUBLISHER_LOGO},
        },
        "url": url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }

    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Blog", "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": post["title"], "item": url},
        ],
    }

    schemas = [article_schema, breadcrumb_schema]

    if post.get("faq"):
        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item["q"],
                    "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
                }
                for item in post["faq"]
            ],
        }
        schemas.append(faq_schema)

    return "\n".join(
        f'<script type="application/ld+json">{json.dumps(s, indent=2)}</script>'
        for s in schemas
    )


def auto_interlink(html_content, current_slug, all_posts):
    """Wrap the first occurrence of each other post's title with an <a> tag."""
    for post in all_posts:
        if post["slug"] == current_slug:
            continue
        title = post["title"]
        url = slug_to_url(post["slug"])
        escaped = re.escape(title)
        pattern = rf"(?<!href=\")(?<!</a>)({escaped})"
        replacement = f'<a href="{url}">{title}</a>'
        html_content, count = re.subn(pattern, replacement, html_content, count=1)
    return html_content


def build_faq_html(faq):
    if not faq:
        return ""
    items = ""
    for item in faq:
        items += f"""
<div class="faq-item">
  <h3>{item['q']}</h3>
  <p>{item['a']}</p>
</div>"""
    return f'<div class="faq-section"><h2>Frequently Asked Questions</h2>{items}</div>'


def build_post_page(post, all_posts):
    url = slug_to_url(post["slug"])
    tags_html = " ".join(f'<span class="tag">{t}</span>' for t in post.get("tags", []))
    body = auto_interlink(post["html_content"], post["slug"], all_posts)
    faq_html = build_faq_html(post.get("faq", []))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{post['title']} | {SITE_NAME}</title>
  <meta name="description" content="{post['meta_description']}">
  <link rel="canonical" href="{url}">

  <!-- OG -->
  <meta property="og:title" content="{post['title']}">
  <meta property="og:description" content="{post['meta_description']}">
  <meta property="og:url" content="{url}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="{SITE_NAME}">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{post['title']}">
  <meta name="twitter:description" content="{post['meta_description']}">

  <!-- GSC -->
  <meta name="google-site-verification" content="{GSC_VERIFICATION}">

  <!-- JSON-LD -->
  {build_json_ld(post)}

  <!-- GA4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>

  {build_css()}
</head>
<body>
  {build_nav(SITE_URL)}

  <main class="article-wrap">
    <div class="article-meta">
      <span>{post['date']}</span>
      <span>{post.get('cluster', '')}</span>
      {tags_html}
    </div>
    <h1>{post['title']}</h1>

    {body}

    {faq_html}

    <div class="cta-box">
      <p><strong>{CTA_TEXT}</strong></p>
      <a href="{CTA_URL}">Book a Demo</a>
    </div>
  </main>

  {build_footer()}
</body>
</html>"""


def build_index(all_posts):
    cards = ""
    for post in sorted(all_posts, key=lambda p: p["date"], reverse=True):
        url = slug_to_url(post["slug"])
        cards += f"""
<div class="post-card">
  <div class="cluster">{post.get('cluster', '')}</div>
  <h2><a href="{url}">{post['title']}</a></h2>
  <p>{post['meta_description'][:120]}...</p>
  <a class="read-more" href="{url}">Read article →</a>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Blog | {SITE_NAME}</title>
  <meta name="description" content="Practical insights on physiotherapy outcomes, MSK measurement, and evidence-based practice from the Benchmark PS team.">
  <link rel="canonical" href="{SITE_URL}/">
  <meta name="google-site-verification" content="{GSC_VERIFICATION}">
  {build_css()}
</head>
<body>
  {build_nav(SITE_URL)}

  <div class="blog-hero">
    <h1>Benchmark PS Blog</h1>
    <p>Practical insights on physiotherapy outcomes, MSK measurement, and evidence-based practice.</p>
  </div>

  <div class="post-grid">
    {cards}
  </div>

  {build_footer()}
</body>
</html>"""


def build_sitemap(all_posts):
    urls = f"""  <url>
    <loc>{SITE_URL}/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>"""
    for post in all_posts:
        urls += f"""
  <url>
    <loc>{slug_to_url(post['slug'])}</loc>
    <lastmod>{post.get('updated', post['date'])}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>"""


def build_rss(all_posts):
    items = ""
    for post in sorted(all_posts, key=lambda p: p["date"], reverse=True)[:20]:
        url = slug_to_url(post["slug"])
        items += f"""
  <item>
    <title><![CDATA[{post['title']}]]></title>
    <link>{url}</link>
    <guid isPermaLink="true">{url}</guid>
    <description><![CDATA[{post['meta_description']}]]></description>
    <pubDate>{post['date']}</pubDate>
  </item>"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{SITE_NAME} Blog</title>
  <link>{SITE_URL}/</link>
  <description>Practical insights on physiotherapy outcomes, MSK measurement, and evidence-based practice.</description>
  <language>en-gb</language>
  <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
  {items}
</channel>
</rss>"""


def build_robots():
    return f"""User-agent: *
Allow: /
Sitemap: {SITE_URL}/sitemap.xml"""


def build_site():
    posts = load_manifest()
    OUTPUT_DIR.mkdir(exist_ok=True)
    POSTS_DIR.mkdir(exist_ok=True)

    for post in posts:
        post_dir = POSTS_DIR / post["slug"]
        post_dir.mkdir(exist_ok=True)
        html = build_post_page(post, posts)
        (post_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"  Built: /posts/{post['slug']}/")

    (OUTPUT_DIR / "index.html").write_text(build_index(posts), encoding="utf-8")
    (OUTPUT_DIR / "sitemap.xml").write_text(build_sitemap(posts), encoding="utf-8")
    (OUTPUT_DIR / "feed.xml").write_text(build_rss(posts), encoding="utf-8")
    (OUTPUT_DIR / "robots.txt").write_text(build_robots(), encoding="utf-8")

    print(f"\nBuild complete. {len(posts)} posts in output/")


if __name__ == "__main__":
    build_site()
