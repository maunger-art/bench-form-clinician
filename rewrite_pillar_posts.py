"""
rewrite_pillar_posts.py — Rewrites the 10 pillar posts with verified PubMed references.

Preserves:
- Exact slugs (so all URLs stay the same)
- Exact titles
- Tags, cluster, date
- posts_manifest.json structure

Replaces:
- html_content (rewritten with PubMed-verified citations)
- meta_description (refreshed)
- faq (refreshed)
- verified_pmids (new field added)

Run locally:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 rewrite_pillar_posts.py

Rewrites one post at a time. Safe to re-run — skips posts that already
have verified_pmids unless you pass --force.
"""

import json
import sys
import time
from datetime import date
from pathlib import Path

import anthropic
from fetch_references import fetch_references_for_topic, format_references_for_prompt

BASE_DIR = Path(__file__).parent
MANIFEST_PATH = BASE_DIR / "posts_manifest.json"

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
- Use UK English spelling throughout

REFERENCES — ABSOLUTE RULES — READ BEFORE WRITING ANYTHING

The user will provide a numbered list of VERIFIED PubMed references below.
These are the ONLY sources you are permitted to cite. No exceptions.

BEFORE YOU WRITE A SINGLE WORD of the article, read the provided references carefully.
Build your arguments around what these papers actually say.
Do not write a claim and then look for a reference to support it.
Write claims that are directly supported by the provided references.

HARD RULES — violating any of these makes the output unusable:
1. You MUST NOT cite any source not in the provided list — not books, not guidelines,
   not papers you know from training, not anything. Only the provided list.
2. Every factual claim must be supported by a reference from the provided list.
   If a claim cannot be supported by the provided list, do not make that claim.
3. Use 5-7 of the MOST RELEVANT references — do not use all of them.
   Quality and relevance matter far more than quantity.
   A tight article with 5 highly relevant citations is better than a padded one with 12.
4. Use superscript numbers inline: <sup>1</sup> where 1 matches the reference number
5. The reference list MUST use <ol class="references"> at the end of html_content
6. Every <li> MUST include the citation text AND a direct PubMed link using the exact URL:
   <li>Author et al. Title. Journal. Year;Vol(Issue):Pages. <a href="https://pubmed.ncbi.nlm.nih.gov/PMID/" target="_blank">PubMed</a></li>
   Replace PMID with the actual PMID number from the provided list.
7. The reference numbers in the text must match the reference list exactly

STRUCTURE
- 4–6 H2 sections, each covering a distinct sub-topic
- Each section: 2–4 tight paragraphs with inline superscript citations
- Practical, numbered or bulleted takeaways where useful
- One CTA section at the end — not a sales pitch, a natural next step
- Reference list at the very end inside html_content
- Target length: 1,200–1,800 words (excluding references)

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
  "meta_description": "150-160 character SEO meta description",
  "html_content": "<p>Full article HTML with inline citations and reference list...</p>",
  "faq": [
    {"q": "Question one?", "a": "Answer one."},
    {"q": "Question two?", "a": "Answer two."},
    {"q": "Question three?", "a": "Answer three."}
  ]
}

The html_content should use semantic HTML: <h2>, <h3>, <p>, <ul>, <ol>, <li>,
<blockquote>, <strong>. Do not include <html>, <head>, <body>, or <h1> tags.
Do not include the FAQ in html_content; it is handled separately via the faq array."""


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def rewrite_post(post: dict, references: list) -> dict:
    """Rewrite a single post using verified PubMed references."""
    client = anthropic.Anthropic()

    ref_block = format_references_for_prompt(references)

    user_message = (
        f"Rewrite the following blog article for the Benchmark PS blog.\n\n"
        f"TITLE (keep exactly): {post['title']}\n\n"
        f"TOPIC CONTEXT: This article covers {post['title'].lower()}. "
        f"Preserve the core argument and practical focus of the original, "
        f"but rewrite with fresh content and the verified references provided below.\n\n"
        f"{ref_block}\n\n"
        f"Return only the JSON object as described. No other text."
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


def main():
    force = "--force" in sys.argv

    manifest = load_json(MANIFEST_PATH)
    print(f"Rewriting {len(manifest)} pillar posts with verified PubMed references\n")

    updated = 0
    for i, post in enumerate(manifest):
        title = post["title"]
        slug = post["slug"]

        # Skip if already has verified PMIDs (unless --force)
        if post.get("verified_pmids") and not force:
            print(f"[{i+1}/{len(manifest)}] SKIP (already verified): {title[:60]}")
            continue

        print(f"[{i+1}/{len(manifest)}] Rewriting: {title[:65]}")

        # Fetch real PubMed references
        print(f"  Querying PubMed...")
        references = fetch_references_for_topic(title, target_count=15)
        print(f"  Found {len(references)} verified references")

        if not references:
            print(f"  WARNING: No PubMed references found — skipping this post")
            continue

        # Rewrite the article
        try:
            result = rewrite_post(post, references)

            # Update the post in manifest — preserve slug, title, date, tags, cluster
            post["meta_description"] = result["meta_description"]
            post["html_content"] = result["html_content"]
            post["faq"] = result["faq"]
            post["verified_pmids"] = [r["pmid"] for r in references]
            post["rewritten_date"] = date.today().isoformat()

            print(f"  ✓ Rewritten: {slug}")
            updated += 1

            # Save after each post so progress isn't lost
            save_json(MANIFEST_PATH, manifest)
            print(f"  Saved to posts_manifest.json")

        except Exception as e:
            print(f"  ✗ Failed: {e}")

        # Respect API rate limits
        if i < len(manifest) - 1:
            time.sleep(2)

    print(f"\n{updated}/{len(manifest)} posts rewritten successfully.")
    if updated > 0:
        print("\nNext steps:")
        print("  python3 blog_build.py   — rebuild the HTML output")
        print("  git add posts_manifest.json output/")
        print("  git commit -m 'Rewrite pillar posts with verified PubMed references'")
        print("  git push")


if __name__ == "__main__":
    main()
