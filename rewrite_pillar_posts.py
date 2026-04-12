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
from validate_repair_citations import run_pipeline as validate_and_repair

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
- Primary audience: practising physiotherapists and senior clinicians in UK MSK
  and sports settings who want to make better clinical decisions with data
- Secondary audience: physiotherapy clinic owners and practice managers who want
  to demonstrate clinical value and reduce treatment variation
- Core value: consistent measurement → better clinical decisions → better patient
  outcomes → more defensible, efficient practice
- Pilot data: 83% of patients improved; outcomes 39% more effective than standard
  physiotherapy benchmarks; 100% clinician recommendation rate
- MSK care problem: up to 43% of physiotherapy care is non-recommended; over 90% of
  physios rely on subjective strength testing; fewer than 10% use objective tools
- Do not position Benchmark PS as replacing physiotherapists — it is the infrastructure
  that makes clinical judgement more defensible and more consistent

CONTENT ARCHITECTURE — follow this for every article:
- 80% of content is clinically grounded: conditions, testing protocols, benchmarks,
  clinical decision-making, and measurement methodology
- 20% of content addresses business/economics — always framed as clinical consistency
  first, commercial consequences second
- For business articles: the argument structure is
    clinical variation is costly
    measurement reduces uncertainty
    reduced uncertainty improves decisions and consistency
    consistency improves outcomes and service defensibility
    defensible care is easier to contract, price, staff, and justify
- Never lead with money, marketing, or practice management language
- Draw on sports science and athletic performance research for testing variables
  and normative data — this population has richer benchmark data than clinical trials

OUTPUT FORMAT
Respond ONLY with a valid JSON object. No preamble, no markdown code fences.

{
  "meta_description": "150-160 character SEO meta description",
  "html_content": "<p>Article HTML with [PMID:xxxxx] tokens inline only — NO reference section...</p>",
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
- Do NOT include the FAQ in html_content"""


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def validate_citations(result: dict, references: list) -> dict:
    """Run deterministic validator to replace PMID tokens and build reference list."""
    import tempfile, json as _json
    from pathlib import Path as _Path

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
        input_path  = tmp_path / "article.html"
        refs_path   = tmp_path / "refs.json"
        output_path = tmp_path / "article.repaired.html"
        report_path = tmp_path / "report.json"

        input_path.write_text(result.get("html_content", ""), encoding="utf-8")
        refs_path.write_text(_json.dumps(ref_pack, ensure_ascii=False), encoding="utf-8")

        validate_and_repair(
            input_path=input_path,
            refs_path=refs_path,
            output_path=output_path,
            report_path=report_path,
            strict_inline_order=True,
            remove_unknown_inline=True,
            fail_on_unknown=False,
        )

        report = _json.loads(report_path.read_text(encoding="utf-8"))
        refs_written = report.get("references_written", [])
        unknown = report.get("unknown_inline_pmids", [])

        if unknown:
            print(f"  WARNING: Removed {len(unknown)} unknown PMIDs: {unknown}")
        print(f"  Validator: {len(refs_written)} verified references built")

        if output_path.exists():
            result["html_content"] = output_path.read_text(encoding="utf-8")

    return result


def rewrite_post(post: dict, references: list) -> dict:
    """Rewrite a single post using verified PubMed references."""
    client = anthropic.Anthropic()

    ref_block = format_references_for_prompt(references)

    # List PMIDs explicitly so Claude can't miss them
    pmid_list = ", ".join([f"[PMID:{r['pmid']}]" for r in references])

    user_message = (
        f"Rewrite the following blog article for the Benchmark PS blog.\n\n"
        f"TITLE (keep exactly): {post['title']}\n\n"
        f"MANDATORY: You MUST cite references inline using PMID tokens.\n"
        f"Available PMIDs to cite: {pmid_list}\n"
        f"Use at least 5 of these tokens in the article body like this: [PMID:12345678]\n"
        f"Do NOT write a References section — the validator builds it from your tokens.\n\n"
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
        references = fetch_references_for_topic(title, target_count=10)
        print(f"  Found {len(references)} verified references")

        if not references:
            print(f"  WARNING: No PubMed references found — skipping this post")
            continue

        # Rewrite the article
        try:
            result = rewrite_post(post, references)

            # Check if Claude used PMID tokens
            import re as _re
            tokens_found = _re.findall(r'\[PMID:\d+\]', result.get("html_content", ""))
            print(f"  PMID tokens in output: {len(tokens_found)}")
            if tokens_found:
                print(f"  Sample: {tokens_found[:3]}")
            else:
                print(f"  WARNING: Claude did not use [PMID:xxx] tokens — check first 200 chars:")
                print(f"  {result.get('html_content','')[:200]}")

            # Run citation validator to replace tokens and build reference list
            result = validate_citations(result, references)

            # Update the post in manifest — preserve slug, title, date, tags, cluster
            post["meta_description"] = result["meta_description"]
            post["html_content"] = result["html_content"]
            post["faq"] = result["faq"]
            post["verified_pmids"] = [r["pmid"] for r in references]
            post["rewritten_date"] = date.today().isoformat()

            # Record paper usage in evidence memory
            try:
                from evidence_memory import get_memory
                pmids = [r["pmid"] for r in references]
                get_memory().record_article(title, pmids, pmids[:3])
            except Exception:
                pass  # Memory recording is non-blocking

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
