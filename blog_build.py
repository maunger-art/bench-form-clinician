"""
blog_build.py — Benchmark PS static site HTML builder
Reads posts_manifest.json and generates a deployable static site in output/
Design matches the main benchmarkps.org landing page exactly.
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
SITE_URL = "https://benchmarkps.org/blog"
GA4_ID = "G-XXXXXXXXXX"
GSC_VERIFICATION = "google-site-verification=C9WQu-TDa_vbA_IuL9Y6WUumlKUUYlWBY3vXYMV6UkY"
AUTHOR_NAME = "Benchmark PS"
AUTHOR_URL = "https://benchmarkps.org"
PUBLISHER_LOGO = "https://benchmarkps.org/assets/benchmark-icon-nav-BhAe3FNc.png"
LOGO_URL = "/assets/benchmark-icon-nav-BhAe3FNc.png"

CTA_TEXT = "See how Benchmark PS works in practice"
CTA_URL = "https://platform.benchmarkps.org/login?signup=true"
BANNER_TEXT = "Now in early access — free to get started."
BANNER_SUBTEXT = "Join physiotherapy clinics already measuring outcomes with Benchmark PS."
BANNER_CTA = "Create Account"
BANNER_URL = "https://platform.benchmarkps.org/login?signup=true"

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
    nav_links = [
        {"label": "How It Works", "href": "https://benchmarkps.org/#how-it-works"},
        {"label": "Who It's For", "href": "https://benchmarkps.org/#who"},
        {"label": "Blog", "href": SITE_URL},
        {"label": "Contact", "href": "https://benchmarkps.org/#cta"},
    ]
    links_html = ""
    for link in nav_links:
        active = " active" if link["href"] == active_href else ""
        links_html += f'<a href="{link["href"]}" class="nav-link{active}">{link["label"]}</a>\n'

    return f"""
<nav class="site-nav">
  <a href="https://benchmarkps.org" class="nav-brand">
    <img src="{LOGO_URL}" alt="Benchmark PS" onerror="this.style.display='none'">
    <span class="nav-wordmark">
      <span class="nav-wordmark-main">Benchmark</span>
      <span class="nav-wordmark-sub">Performance Systems</span>
    </span>
  </a>
  <div class="nav-links">
    {links_html}
    <a href="https://platform.benchmarkps.org/login" class="nav-link">Login</a>
    <a href="https://platform.benchmarkps.org/login?signup=true" class="nav-cta">Create Account</a>
  </div>
</nav>
<div class="trial-banner">
  Try Benchmark PS free for 28 days — no obligations, no card required.
  <a href="{BANNER_URL}">Create Account</a>
</div>"""


def build_footer():
    return f"""
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <img src="{LOGO_URL}" alt="Benchmark PS" onerror="this.style.display='none'">
      <div>
        <div class="footer-wordmark-main">Benchmark</div>
        <div class="footer-wordmark-sub">Performance Systems</div>
      </div>
    </div>
    <p class="footer-tagline">Performance measurement and clinical decision-support for physiotherapy practices.</p>
    <div class="footer-links">
      <a href="https://benchmarkps.org/#how-it-works">How It Works</a>
      <a href="https://benchmarkps.org/#who">Who It's For</a>
      <a href="{SITE_URL}">Blog</a>
      <a href="https://benchmarkps.org/privacy-policy">Privacy</a>
      <a href="https://benchmarkps.org/terms-and-conditions">Terms</a>
      <a href="{SITE_URL}/feed.xml">RSS</a>
    </div>
    <div class="footer-copy">2025 Benchmark PS. All rights reserved.</div>
  </div>
</footer>"""


def build_banner():
    return f"""
<div class="early-access-banner" id="earlyAccessBanner">
  <span><strong>{BANNER_TEXT}</strong> {BANNER_SUBTEXT}</span>
  <a href="{BANNER_URL}" class="banner-cta">{BANNER_CTA} &rarr;</a>
  <button class="banner-close" onclick="document.getElementById('earlyAccessBanner').style.display='none'" aria-label="Close">&times;</button>
</div>"""


def build_css():
    return """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

  :root {
    --navy:       hsl(213, 66%, 16%);
    --navy-soft:  hsl(211, 53%, 23%);
    --blue:       hsl(207, 75%, 40%);
    --blue-mid:   hsl(199, 68%, 51%);
    --blue-pale:  hsl(202, 78%, 91%);
    --blue-light: hsl(206, 64%, 83%);
    --teal:       hsl(172, 82%, 30%);
    --warm:       hsl(213, 33%, 97%);
    --warm-mid:   hsl(212, 26%, 90%);
    --sand:       hsl(210, 24%, 84%);
    --mid:        hsl(211, 27%, 39%);
    --light:      hsl(209, 22%, 59%);
    --max-width:  740px;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 17px;
    line-height: 1.75;
    color: var(--navy);
    background: var(--warm);
  }

  a { color: var(--blue); text-decoration: none; }
  a:hover { text-decoration: underline; }

  .site-nav {
    position: sticky;
    top: 0;
    z-index: 100;
    background: var(--navy);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 3rem;
    height: 66px;
  }
  .nav-brand { display: flex; align-items: center; gap: 12px; text-decoration: none; }
  .nav-brand img { height: 44px; width: auto; }
  .nav-wordmark { display: flex; flex-direction: column; justify-content: center; line-height: 1; }
  .nav-wordmark-main { font-size: 18px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: white; line-height: 1; }
  .nav-wordmark-sub { font-size: 8px; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase; color: hsl(199, 68%, 51%); margin-top: 4px; line-height: 1; }
  .nav-links { display: flex; align-items: center; gap: 2rem; }
  .nav-link { color: rgba(255,255,255,0.6); font-size: 13px; font-weight: 500; text-decoration: none; transition: color 0.2s; }
  .nav-link:hover, .nav-link.active { color: white; text-decoration: none; }
  .nav-cta { background: hsl(199, 68%, 51%); color: white; padding: 0.45rem 1.25rem; border-radius: 6px; font-weight: 600; font-size: 13px; text-decoration: none; }
  .nav-cta:hover { opacity: 0.85; text-decoration: none; }

  .trial-banner {
    background: hsl(199, 68%, 51%);
    color: white;
    text-align: center;
    padding: 0.6rem 1rem;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.01em;
  }
  .trial-banner a { color: white; text-decoration: underline; font-weight: 700; }

  .article-wrap { max-width: var(--max-width); margin: 3rem auto; padding: 0 1.5rem; }
  .article-meta { font-size: 0.82rem; color: var(--mid); margin-bottom: 1.25rem; display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center; }
  .tag { background: var(--blue-pale); color: var(--navy); padding: 0.2rem 0.65rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }

  h1 { font-family: 'Lora', serif; font-size: 2.2rem; line-height: 1.2; color: var(--navy); margin-bottom: 1.25rem; font-weight: 600; }
  h2 { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.3rem; font-weight: 700; color: var(--navy); margin: 2.75rem 0 0.75rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--blue-pale); }
  h3 { font-size: 1.05rem; font-weight: 600; color: var(--navy-soft); margin: 1.75rem 0 0.5rem; }
  p { margin-bottom: 1.25rem; color: hsl(213, 30%, 25%); }
  ul, ol { margin: 0 0 1.25rem 1.5rem; }
  li { margin-bottom: 0.5rem; color: hsl(213, 30%, 25%); }
  strong { color: var(--navy); font-weight: 600; }

  blockquote { border-left: 3px solid hsl(199, 68%, 51%); margin: 1.75rem 0; padding: 0.75rem 1.5rem; background: white; border-radius: 0 8px 8px 0; color: var(--mid); font-style: italic; }

  ol.references { font-size: 0.82rem; color: var(--mid); line-height: 1.6; margin-top: 0.5rem; }
  ol.references li { margin-bottom: 0.4rem; }

  .trial-banner { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; background: var(--navy); color: white; padding: 1.25rem 2rem; border-radius: 10px; margin: 3.5rem 0; flex-wrap: wrap; }
  .trial-banner span { font-size: 0.98rem; color: rgba(255,255,255,0.9); }
  .trial-banner a { display: inline-block; background: hsl(199, 68%, 51%); color: white; padding: 0.65rem 1.75rem; border-radius: 7px; font-weight: 700; font-size: 0.92rem; text-decoration: none; white-space: nowrap; flex-shrink: 0; }
  .trial-banner a:hover { opacity: 0.85; text-decoration: none; }

  .faq-section { margin-top: 3rem; }
  .faq-item { border-bottom: 1px solid var(--warm-mid); padding: 1.25rem 0; }
  .faq-item h3 { color: var(--navy); font-size: 0.95rem; margin: 0 0 0.5rem; font-weight: 600; border: none; padding: 0; }
  .faq-item p { font-size: 0.9rem; margin-bottom: 0; }

  .blog-hero { background: var(--navy); color: white; padding: 5rem 2rem; text-align: center; }
  .blog-hero h1 { font-family: 'Lora', serif; color: white; font-size: 2.5rem; margin-bottom: 0.75rem; border: none; padding: 0; }
  .blog-hero p { color: rgba(255,255,255,0.7); font-size: 1.1rem; max-width: 520px; margin: 0 auto; }

  .post-grid { max-width: 1100px; margin: 2.5rem auto 4rem; padding: 0 1.5rem; display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }
  .post-card { background: white; border: 1px solid var(--warm-mid); border-radius: 12px; padding: 1.75rem; transition: box-shadow 0.2s, transform 0.2s; display: flex; flex-direction: column; }
  .post-card:hover { box-shadow: 0 8px 30px rgba(30, 58, 92, 0.1); transform: translateY(-2px); }
  .post-card .cluster { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: hsl(172, 82%, 30%); font-weight: 700; margin-bottom: 0.6rem; }
  .post-card h2 { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1rem; font-weight: 700; margin: 0 0 0.6rem; color: var(--navy); line-height: 1.4; border: none; padding: 0; }
  .post-card p { font-size: 0.875rem; color: var(--mid); margin-bottom: 1.25rem; flex: 1; line-height: 1.6; }
  .post-card .read-more { font-size: 0.85rem; font-weight: 700; color: var(--blue); }
  .post-card .read-more::after { content: ' →'; }

  .site-footer { background: var(--navy); padding: 3rem 2rem; }
  .footer-inner { max-width: 1100px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 1.25rem; text-align: center; }
  .footer-brand { display: flex; align-items: center; gap: 10px; }
  .footer-brand img { height: 36px; width: auto; opacity: 0.9; }
  .footer-wordmark-main { font-size: 15px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: white; line-height: 1; }
  .footer-wordmark-sub { font-size: 7px; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase; color: hsl(199, 68%, 51%); margin-top: 3px; line-height: 1; }
  .footer-tagline { font-size: 0.82rem; max-width: 380px; color: rgba(255,255,255,0.5); }
  .footer-links { display: flex; gap: 1.5rem; flex-wrap: wrap; justify-content: center; }
  .footer-links a { color: rgba(255,255,255,0.5); font-size: 0.82rem; text-decoration: none; }
  .footer-links a:hover { color: white; }
  .footer-copy { font-size: 0.75rem; color: rgba(255,255,255,0.3); padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); width: 100%; text-align: center; }

  /* ── Early access banner ── */
  .early-access-banner {
    background: hsl(199, 68%, 51%);
    color: white;
    padding: 0.65rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    font-size: 0.85rem;
    font-weight: 500;
    flex-wrap: wrap;
    text-align: center;
    position: relative;
  }
  .early-access-banner strong { font-weight: 700; }
  .early-access-banner a.banner-cta {
    background: white;
    color: hsl(199, 68%, 51%);
    padding: 0.3rem 1rem;
    border-radius: 5px;
    font-weight: 700;
    font-size: 0.8rem;
    text-decoration: none;
    white-space: nowrap;
    transition: opacity 0.2s;
  }
  .early-access-banner a.banner-cta:hover { opacity: 0.85; text-decoration: none; }
  .banner-close {
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: rgba(255,255,255,0.7);
    cursor: pointer;
    font-size: 1.1rem;
    line-height: 1;
    padding: 0.25rem;
  }
  .banner-close:hover { color: white; }

  @media (max-width: 640px) {
    .site-nav { padding: 0 1.25rem; }
    .nav-links { display: none; }
    h1 { font-size: 1.7rem; }
    .blog-hero h1 { font-size: 1.9rem; }
    .post-grid { grid-template-columns: 1fr; }
    .early-access-banner { font-size: 0.78rem; padding: 0.5rem 2.5rem 0.5rem 1rem; }
  }
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
    for post in all_posts:
        if post["slug"] == current_slug:
            continue
        title = post["title"]
        url = slug_to_url(post["slug"])
        escaped = re.escape(title)
        pattern = rf"(?<!href=\")(?<!</a>)({escaped})"
        replacement = f'<a href="{url}">{title}</a>'
        html_content, _ = re.subn(pattern, replacement, html_content, count=1)
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
  <meta property="og:title" content="{post['title']}">
  <meta property="og:description" content="{post['meta_description']}">
  <meta property="og:url" content="{url}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{post['title']}">
  <meta name="twitter:description" content="{post['meta_description']}">
  <meta name="google-site-verification" content="{GSC_VERIFICATION}">
  {build_json_ld(post)}
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>
  {build_css()}
</head>
<body>
  {build_banner()}
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
    <div class="trial-banner">
      <span>Try Benchmark PS free for 28 days — no obligations, no card required.</span>
      <a href="{CTA_URL}">Create Account</a>
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
  <a class="read-more" href="{url}">Read article</a>
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
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>
  {build_css()}
</head>
<body>
  {build_banner()}
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
