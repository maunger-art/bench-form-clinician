"""
generate_drafts.py — Pre-generates 7 full articles every Monday and stores as drafts.

Drafts are saved to drafts/{slug}.json and rendered in the preview page.
The daily publisher reads approved drafts rather than generating on the fly.

Run every Monday at 07:00 UTC via GitHub Actions (before preview page generation).
"""

import json
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

import anthropic
from fetch_references import fetch_references_for_topic, format_references_for_prompt
from validate_repair_citations import run_pipeline as validate_and_repair

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

CITATION RULES — READ CAREFULLY
You will receive an APPROVED REFERENCE PACK below. These are the only sources you may cite.

Your task:
1. Write the article body in clean HTML
2. Cite references ONLY using inline PMID tokens in this exact format: [PMID:12345678]
3. Do NOT write clickable links yourself — a separate validation script handles this
4. Do NOT write or format the final References section — the script builds it
5. Do NOT invent references, substitute alternatives, or use anything from memory
6. Every inline citation must map to a PMID in the provided reference pack
7. If there are not enough suitable references for a claim, leave it uncited rather than inventing

HARD RULES:
- Only use PMIDs from the supplied reference pack — nothing else
- Never output author-year inline citations unless backed by a valid [PMID:xxxxx] token
- Never output raw bibliography HTML from memory
- Never add a paper not present in the reference pack
- 5-7 well-chosen citations beats padding with 12 weak ones

STRUCTURE
- 4-6 H2 sections, each covering a distinct sub-topic
- Each section: 2-4 tight paragraphs with inline [PMID:xxxxx] tokens where claims need support
- Practical, numbered or bulleted takeaways where useful
- One CTA section at the end — not a sales pitch, a natural next step
- Target length: 1,200-1,800 words
- Do NOT include a References section — the validation script builds it

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
  "meta_description": "150-160 character SEO meta description",
  "slug": "url-friendly-slug-all-lowercase-hyphens",
  "html_content": "<p>Article HTML with [PMID:xxxxx] tokens inline — NO reference section...</p>",
  "tags": ["tag1", "tag2", "tag3"],
  "cluster": "Cluster name",
  "faq": [
    {"q": "Question one?", "a": "Answer one."},
    {"q": "Question two?", "a": "Answer two."},
    {"q": "Question three?", "a": "Answer three."}
  ]
}

CRITICAL OUTPUT RULES:
- html_content uses semantic HTML: <h2>, <h3>, <p>, <ul>, <ol>, <li>, <strong>
- Do NOT include <html>, <head>, <body>, or <h1> tags in html_content
- Do NOT include a References section in html_content — the validator builds it
- Cite ONLY with [PMID:xxxxx] tokens inline in the body — example: [PMID:27539507]
- Do NOT include the FAQ in html_content
- slug must be lowercase with hyphens only, no spaces or special characters"""


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def validate_citations(article: dict, references: list) -> dict:
    """
    Run the deterministic citation validator on the generated article.
    Replaces [PMID:xxxxx] tokens with clickable links and builds the reference list.
    Returns updated article dict with repaired html_content.
    """
    import tempfile, json as _json
    from pathlib import Path as _Path

    # Build reference pack in the format validate_repair_citations.py expects
    ref_pack = []
    for r in references:
        ref_pack.append({
            "pmid": r["pmid"],
            "pubmed_url": r["pubmed_url"],
            "citation_text": r.get("citation_text", r.get("citation", "")),
            "short_cite": r.get("short_cite", f"{r.get('authors','').split(',')[0].strip()}, {r.get('year','')}")
        })

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = _Path(tmp)
        input_path = tmp_path / "article.html"
        refs_path = tmp_path / "refs.json"
        output_path = tmp_path / "article.repaired.html"
        report_path = tmp_path / "report.json"

        # Write input files
        input_path.write_text(article.get("html_content", ""), encoding="utf-8")
        refs_path.write_text(_json.dumps(ref_pack, ensure_ascii=False), encoding="utf-8")

        # Run validator
        result = validate_and_repair(
            input_path=input_path,
            refs_path=refs_path,
            output_path=output_path,
            report_path=report_path,
            strict_inline_order=True,
            remove_unknown_inline=True,
            fail_on_unknown=False,
        )

        # Read report
        report = _json.loads(report_path.read_text(encoding="utf-8"))
        refs_written = report.get("references_written", [])
        unknown = report.get("unknown_inline_pmids", [])

        if unknown:
            print(f"  WARNING: Removed {len(unknown)} unknown inline PMIDs: {unknown}")
        if refs_written:
            print(f"  Validator: {len(refs_written)} verified references in final article")
        else:
            print(f"  WARNING: Validator found no valid inline citations")

        # Update article with repaired html_content
        if output_path.exists():
            article["html_content"] = output_path.read_text(encoding="utf-8")

    return article


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

    pmid_list = ", ".join([f"[PMID:{r['pmid']}]" for r in references]) if references else "none"

    user_message = (
        f"Write a full blog article on the following topic for the Benchmark PS blog:\n\n"
        f"TOPIC: {topic}"
        f"{existing_context}\n\n"
        f"MANDATORY: Cite references inline using PMID tokens.\n"
        f"Available PMIDs: {pmid_list}\n"
        f"Use at least 5 of these tokens in the article body like this: [PMID:12345678]\n"
        f"Do NOT write a References section — the validator builds it.\n\n"
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

            # Run citation validator to replace [PMID:xxxxx] tokens and build reference list
            if references:
                article = validate_citations(article, references)

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
