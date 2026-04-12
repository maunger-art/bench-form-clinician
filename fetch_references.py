"""
fetch_references.py — Main entry point for PubMed evidence retrieval.

Now orchestrates the full pipeline via evidence_pack_builder.py:
  1. topic_normalizer.py — structured search brief
  2. query_builder.py — 6 validated query variants
  3. PubMed retrieval + abstract fetching
  4. paper_ranker.py — 100-point scoring + pool gating
  5. evidence_pack_builder.py — final pack selection

Falls back to legacy retrieval if new pipeline fails.
"""

from __future__ import annotations
import json
import time
import urllib.request
import urllib.parse

ENTREZ_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL = "BenchmarkPSBlog"
EMAIL = "info@benchmarkps.org"


def fetch_references_for_topic(topic: str, target_count: int = 10) -> list[dict]:
    """
    Main function: fetch real PubMed references for a topic.
    Uses the full gated pipeline: normalize -> query -> retrieve -> score -> pack.
    Returns up to target_count verified, ranked papers.
    """
    print(f"  Fetching PubMed references for: {topic[:60]}...")

    try:
        from evidence_pack_builder import build_evidence_pack, PoolFailure
        pack = build_evidence_pack(topic, target_pack_size=target_count, verbose=True)
        refs = pack.approved_references

        if not refs:
            print(f"  Pipeline returned 0 references — falling back to legacy retrieval")
            return _legacy_fetch(topic, target_count)

        print(f"  Found {len(refs)} verified references (pool: {pack.pool_decision})")
        return refs

    except Exception as e:
        print(f"  Pipeline error: {e} — falling back to legacy retrieval")
        return _legacy_fetch(topic, target_count)


def _legacy_fetch(topic: str, target_count: int = 10) -> list[dict]:
    """Legacy retrieval as fallback."""
    from topic_normalizer import normalize_topic
    brief = normalize_topic(topic)
    
    # Simple keyword queries as fallback
    kw = " ".join(brief.intent_terms[:3])
    msk = '("physiotherapy"[tiab] OR "physical therapy"[tiab] OR "musculoskeletal"[tiab])'
    excl = 'NOT ("global burden of disease"[tiab] OR GBD[tiab])'
    
    queries = [
        f'{kw} AND {msk} {excl}',
        f'physiotherapy outcome measurement systematic review {excl}',
        f'musculoskeletal rehabilitation evidence-based {excl}',
    ]
    
    all_pmids = []
    seen = set()
    for query in queries:
        time.sleep(0.4)
        params = urllib.parse.urlencode({
            "db": "pubmed", "term": query, "retmax": 15,
            "retmode": "json", "tool": TOOL, "email": EMAIL,
        })
        try:
            with urllib.request.urlopen(
                f"{ENTREZ_BASE}/esearch.fcgi?{params}", timeout=20
            ) as r:
                data = json.loads(r.read())
            for pmid in data.get("esearchresult", {}).get("idlist", []):
                if pmid not in seen:
                    seen.add(pmid)
                    all_pmids.append(pmid)
        except Exception:
            continue
        if len(all_pmids) >= target_count * 2:
            break

    if not all_pmids:
        return []

    time.sleep(0.4)
    papers = _fetch_details(all_pmids[:40])
    papers = [p for p in papers if p["title"] and p["authors"] and p["year"]]
    papers.sort(key=lambda p: (bool(p["pages"]), bool(p["volume"])), reverse=True)
    return papers[:target_count]


def _fetch_details(pmids: list[str]) -> list[dict]:
    """Fetch ESummary details for a list of PMIDs."""
    if not pmids:
        return []
    params = urllib.parse.urlencode({
        "db": "pubmed", "id": ",".join(pmids), "retmode": "json",
        "tool": TOOL, "email": EMAIL,
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(
                f"{ENTREZ_BASE}/esummary.fcgi?{params}", timeout=25
            ) as r:
                data = json.loads(r.read())
            break
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                return []

    results = data.get("result", {})
    uids = results.get("uids", [])
    papers = []

    for uid in uids:
        paper = results.get(uid, {})
        if not paper or paper.get("error"):
            continue

        authors_raw = paper.get("authors", [])
        authors = [a.get("name", "") for a in authors_raw[:6] if a.get("name")]
        author_str = ", ".join(authors[:3]) + (" et al" if len(authors) > 3 else "")

        journal = paper.get("fulljournalname") or paper.get("source", "")
        volume = paper.get("volume", "")
        issue = paper.get("issue", "")
        pages = paper.get("pages", "")
        pub_year = paper.get("pubdate", "")[:4]
        title = paper.get("title", "").rstrip(".")

        if not title or not author_str:
            continue

        vol_issue = f"{volume}({issue})" if volume and issue else volume
        citation = f"{author_str}. {title}. {journal}. {pub_year}"
        if vol_issue:
            citation += f";{vol_issue}"
        if pages:
            citation += f":{pages}"
        citation += "."

        first_surname = authors[0].split(" ")[0] if authors else "Unknown"
        short_cite = (
            f"{first_surname} et al., {pub_year}" if len(authors) > 1
            else f"{first_surname}, {pub_year}"
        )

        papers.append({
            "pmid": uid, "title": title, "authors": author_str,
            "journal": journal, "year": pub_year, "volume": volume,
            "issue": issue, "pages": pages, "citation": citation,
            "citation_text": citation, "short_cite": short_cite,
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
        })

    return papers


def format_references_for_prompt(references: list[dict]) -> str:
    """Format reference list for Claude prompt using token workflow."""
    if not references:
        return ""

    lines = ["APPROVED REFERENCE PACK — these are the ONLY sources you may cite:"]
    lines.append("")
    for i, ref in enumerate(references, 1):
        lines.append(f"[{i}] PMID: {ref['pmid']}")
        lines.append(f"    {ref['citation']}")
        lines.append(f"    Short cite: {ref.get('short_cite', '')}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    refs = fetch_references_for_topic("The Business Case for Outcome Measurement in Physiotherapy Clinics")
    print(f"\nReturned {len(refs)} references")
    for r in refs[:3]:
        print(f"  [{r.get('_score','?')}/{r.get('_decision','?')}] {r['citation'][:80]}")
