"""
generate_drafts.py — Pre-generates 7 full articles every Monday and stores as drafts.

Drafts are saved to drafts/{slug}.json and rendered in the preview page.
The daily publisher reads approved drafts rather than generating on the fly.

Run every Monday at 07:00 UTC via GitHub Actions (before preview page generation).
"""

import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import anthropic
from fetch_references import fetch_references_for_topic, format_references_for_prompt

BASE_DIR = Path(__file__).parent
QUEUE_PATH = BASE_DIR / "queue.json"
MANIFEST_PATH = BASE_DIR / "posts_manifest.json"
DRAFTS_DIR = BASE_DIR / "drafts"

DRAFT_COUNT = 7  # Number of articles to pre-generate each Monday

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
- One H1 (the article title)
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
<blockquote>, <strong>. Do not include <html>, <head>, <body>, or <h1> tags.
Do not include the FAQ in html_content; it is handled separately via the faq array."""


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_article(topic: str, existing_posts: list, references: list) -> dict:
    client = anthropic.Anthropic()

    existing_titles = [p["title"] for p in existing_posts]
    existing_context = (
        f"\n\nExisting articles (do not duplicate these topics):\n"
        + "\n".join(f"- {t}" for t in existing_titles)
        if existing_titles else ""
    )

    ref_block = format_references_for_prompt(references) if references else (
        "No pre-fetched references available. Use your best knowledge but be conservative "
        "— only cite sources you are highly confident exist. Prefer systematic reviews and "
        "NICE guidelines over individual studies."
    )

    user_message = (
        f"Write a full blog article on the following topic for the Benchmark PS blog:\n\n"
        f"TOPIC: {topic}"
        f"{existing_context}\n\n"
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
    DRAFTS_DIR.mkdir(exist_ok=True)

    queue = load_json(QUEUE_PATH)
    manifest = load_json(MANIFEST_PATH)

    if not queue:
        print("Queue is empty — no drafts to generate.")
        return

    # Get existing draft slugs to avoid regenerating
    existing_drafts = {f.stem for f in DRAFTS_DIR.glob("*.json")}
    existing_slugs = {p["slug"] for p in manifest}

    topics_to_draft = queue[:DRAFT_COUNT]
    print(f"Generating {len(topics_to_draft)} draft articles...\n")

    generated = 0
    for i, topic in enumerate(topics_to_draft):
        print(f"[{i+1}/{len(topics_to_draft)}] {topic[:70]}")

        try:
            # Fetch real PubMed references first
            print(f"  Querying PubMed...")
            references = fetch_references_for_topic(topic, target_count=15)
            print(f"  PubMed returned {len(references)} references")

            article = generate_article(topic, manifest, references)

            # Store verified reference PMIDs for audit trail
            if references:
                article["verified_pmids"] = [r["pmid"] for r in references]
                print(f"  Stored {len(references)} verified PMIDs")
            else:
                print(f"  WARNING: No PubMed references — article will use Claude memory only")

            # Ensure no slug collision
            slug = article.get("slug", "")
            if slug in existing_slugs or slug in existing_drafts:
                slug = slug + f"-draft-{date.today().strftime('%Y%m%d')}"
                article["slug"] = slug

            # Add metadata
            article["date"] = (date.today() + timedelta(days=i+1)).isoformat()
            article["draft"] = True
            article["queue_position"] = i + 1
            article["original_topic"] = topic
            article["status"] = "pending"  # pending | approved | skipped

            # Save draft
            draft_path = DRAFTS_DIR / f"{slug}.json"
            save_json(draft_path, article)
            existing_drafts.add(slug)

            print(f"  ✓ Saved: drafts/{slug}.json")
            generated += 1

        except Exception as e:
            print(f"  ✗ Failed: {e}")

    print(f"\n{generated}/{len(topics_to_draft)} drafts generated successfully.")
    print("Run generate_preview_page.py to update the preview page.")


if __name__ == "__main__":
    main()
