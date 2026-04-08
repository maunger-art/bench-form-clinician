"""
generate_post.py — Claude-powered weekly article generator for Benchmark PS
Reads queue.json, generates the next article, appends to posts_manifest.json,
then triggers blog_build.py to rebuild the site.
"""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import anthropic

BASE_DIR = Path(__file__).parent
MANIFEST_PATH = BASE_DIR / "posts_manifest.json"
QUEUE_PATH = BASE_DIR / "queue.json"

SYSTEM_PROMPT = """You are a specialist content writer for Benchmark PS, a performance 
measurement and clinical decision-support platform for physiotherapy practices.

Your readers are practising physiotherapists, clinic owners, and practice managers 
in the UK. They are clinically trained, time-pressed, and sceptical of anything that 
sounds like marketing. Write for someone who has been doing this job for ten years and 
wants substance, not encouragement.

VOICE AND STYLE
- Authoritative and evidence-grounded, but conversational — not academic
- Direct and specific; never vague or abstract
- Practical takeaways in every section; clinicians should be able to act on what they read
- No em dashes
- No filler phrases: never use "it's worth noting", "in conclusion", "importantly", 
  "it's important to", "at the end of the day", "needless to say", "as we all know",
  "game-changer", "landscape", "unlock potential", "leverage", "drive outcomes"
- No AI-sounding language
- No excessive bold text — only use bold for genuinely critical terms
- Use UK English spelling throughout (practise not practice for the verb, etc.)

STRUCTURE
- One H1 (the article title)
- 4–6 H2 sections, each covering a distinct sub-topic
- Each section: 2–4 tight paragraphs
- Practical, numbered or bulleted takeaways where useful
- One CTA section at the end — not a sales pitch, a natural next step
- Target length: 1,200–1,800 words

BENCHMARK PS CONTEXT
- Benchmark PS replaces subjective clinical assessment with standardised, objective 
  testing using low-tech, software-enabled tools — no expensive hardware required
- Key audiences: physiotherapy clinic owners, senior clinicians, practice managers, 
  and insurers/payers commissioning MSK services
- Core value: consistent measurement leads to better clinical decisions, which leads 
  to better patient outcomes and more efficient staffing
- Pilot data: 83% of patients improved; outcomes 39% more effective than standard 
  physiotherapy benchmarks; 100% clinician recommendation rate
- MSK care problem: up to 43% of physiotherapy care is non-recommended; over 90% of 
  physios rely on subjective strength testing; fewer than 10% use objective tools
- Do not position Benchmark PS as replacing physiotherapists — it is infrastructure 
  that supports clinical judgement

OUTPUT FORMAT
Respond ONLY with a valid JSON object. No preamble, no markdown code fences.

{
  "title": "The exact article title",
  "meta_description": "150–160 character SEO meta description",
  "slug": "url-friendly-slug-all-lowercase-hyphens",
  "html_content": "<p>Full article HTML...</p>",
  "tags": ["tag1", "tag2", "tag3"],
  "cluster": "Cluster name from the keyword clusters",
  "faq": [
    {"q": "Question one?", "a": "Answer one."},
    {"q": "Question two?", "a": "Answer two."},
    {"q": "Question three?", "a": "Answer three."}
  ]
}

The html_content should use semantic HTML: <h2>, <h3>, <p>, <ul>, <ol>, <li>, 
<blockquote>, <strong>. Do not include <html>, <head>, <body>, or <h1> tags — 
those are added by the site builder. Do not include the FAQ in html_content; 
it is handled separately via the faq array."""


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_post(topic: str, existing_posts: list) -> dict:
    client = anthropic.Anthropic()

    existing_titles = [p["title"] for p in existing_posts]
    existing_context = (
        f"\n\nExisting articles (do not duplicate these topics):\n"
        + "\n".join(f"- {t}" for t in existing_titles)
        if existing_titles
        else ""
    )

    user_message = (
        f"Write a full blog article on the following topic for the Benchmark PS blog:\n\n"
        f"TOPIC: {topic}"
        f"{existing_context}\n\n"
        f"Return only the JSON object as described. No other text."
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = message.content[0].text.strip()

    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


def main():
    queue = load_json(QUEUE_PATH)
    if not queue:
        print("queue.json is empty — nothing to generate.")
        sys.exit(0)

    topic = queue[0]
    print(f"Generating article: {topic}")

    manifest = load_json(MANIFEST_PATH)
    post = generate_post(topic, manifest)

    # Inject today's date if not provided
    if "date" not in post:
        post["date"] = date.today().isoformat()

    # Validate required keys
    required = ["title", "meta_description", "slug", "html_content", "tags", "cluster"]
    for key in required:
        if key not in post:
            print(f"ERROR: Generated post missing required key: {key}")
            sys.exit(1)

    # Check for slug collision
    existing_slugs = {p["slug"] for p in manifest}
    if post["slug"] in existing_slugs:
        post["slug"] = post["slug"] + f"-{date.today().strftime('%Y%m%d')}"

    manifest.append(post)
    save_json(MANIFEST_PATH, manifest)
    print(f"  Appended to manifest: {post['slug']}")

    queue.pop(0)
    save_json(QUEUE_PATH, queue)
    print(f"  Removed from queue. {len(queue)} articles remaining.")

    print("  Triggering site rebuild...")
    subprocess.run([sys.executable, str(BASE_DIR / "blog_build.py")], check=True)

    print(f"\nDone. New post: {post['title']}")
    return post


if __name__ == "__main__":
    main()
