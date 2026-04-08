"""
social_snippets.py — Social asset generator for Benchmark PS blog posts
Reads the most recently added post from posts_manifest.json and generates
LinkedIn, Twitter/X thread, and short insight copy.

Usage:
  python social_snippets.py                   # uses latest post
  python social_snippets.py --slug my-slug    # specific post
"""

import argparse
import json
import os
import re
from pathlib import Path

import anthropic

BASE_DIR = Path(__file__).parent
MANIFEST_PATH = BASE_DIR / "posts_manifest.json"
OUTPUT_DIR = BASE_DIR / "output" / "social"

SITE_URL = "https://benchmarkps.com/blog"

SOCIAL_SYSTEM_PROMPT = """You are a social media copywriter for Benchmark PS, a 
performance measurement platform for physiotherapy practices.

Benchmark PS's audience on LinkedIn and Twitter/X is primarily:
- Physiotherapy clinic owners and practice managers
- Senior physiotherapists with an interest in evidence-based practice
- Healthcare investors and HealthTech operators

VOICE
- Direct and credible — like a senior clinician sharing a professional observation
- No hype, no motivational language, no em dashes
- No emojis unless a hashtag
- UK English spelling
- Specific over general: use data points where available
- Shorter is better

LINKEDIN FORMAT
- Line 1: A single bold claim or sharp observation — no emoji, no preamble
- Lines 2-4: Core insight in short paragraphs (2-3 sentences each)
- Line 5: One practical takeaway
- Line 6: CTA with URL
- End with 3-5 relevant hashtags on a new line
- Total length: 150-250 words

TWITTER/X THREAD FORMAT
- Tweet 1: Hook + promise (max 280 chars)
- Tweets 2-4: One concrete insight per tweet
- Tweet 5: CTA with URL
- Each tweet stands alone but connects to the thread
- No emojis
- Total: 4-6 tweets

SHORT INSIGHT FORMAT
- One paragraph, 60-90 words
- Standalone — no CTA, no hashtags
- Written for re-use in newsletters, email footers, or pull quotes
- First sentence carries the full point; the rest supports it

OUTPUT FORMAT
Return only a valid JSON object. No preamble, no markdown fences.

{
  "linkedin": "Full LinkedIn post text",
  "twitter_thread": ["Tweet 1", "Tweet 2", "Tweet 3", "Tweet 4", "Tweet 5"],
  "insight": "Short standalone insight paragraph"
}"""


def load_manifest():
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def get_post(manifest, slug=None):
    if slug:
        for post in manifest:
            if post["slug"] == slug:
                return post
        raise ValueError(f"No post found with slug: {slug}")
    return manifest[-1]


def strip_html(html):
    return re.sub(r"<[^>]+>", " ", html).strip()


def generate_social(post):
    client = anthropic.Anthropic()

    post_url = f"{SITE_URL}/posts/{post['slug']}/"
    body_text = strip_html(post["html_content"])[:3000]

    faq_text = ""
    if post.get("faq"):
        faq_text = "\n\nFAQ:\n" + "\n".join(
            f"Q: {item['q']}\nA: {item['a']}" for item in post["faq"]
        )

    user_message = f"""Generate social media assets for this Benchmark PS blog post.

TITLE: {post['title']}
META: {post['meta_description']}
CLUSTER: {post.get('cluster', '')}
TAGS: {', '.join(post.get('tags', []))}
POST URL: {post_url}

ARTICLE BODY (excerpt):
{body_text}
{faq_text}

Return the JSON object as described. Replace any placeholder URLs with: {post_url}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SOCIAL_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


def save_snippets(slug, snippets):
    post_dir = OUTPUT_DIR / slug
    post_dir.mkdir(parents=True, exist_ok=True)

    (post_dir / "linkedin.txt").write_text(snippets["linkedin"], encoding="utf-8")

    thread_text = "\n\n---\n\n".join(
        f"[{i+1}/{len(snippets['twitter_thread'])}] {tweet}"
        for i, tweet in enumerate(snippets["twitter_thread"])
    )
    (post_dir / "twitter.txt").write_text(thread_text, encoding="utf-8")

    (post_dir / "insight.txt").write_text(snippets["insight"], encoding="utf-8")

    print(f"  Saved to output/social/{slug}/")
    print(f"    linkedin.txt  ({len(snippets['linkedin'])} chars)")
    print(f"    twitter.txt   ({len(snippets['twitter_thread'])} tweets)")
    print(f"    insight.txt   ({len(snippets['insight'])} chars)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Specific post slug to generate social for")
    args = parser.parse_args()

    manifest = load_manifest()
    if not manifest:
        print("posts_manifest.json is empty.")
        return

    post = get_post(manifest, args.slug)
    print(f"Generating social snippets for: {post['title']}")

    snippets = generate_social(post)
    save_snippets(post["slug"], snippets)

    print("\nDone.")


if __name__ == "__main__":
    main()
