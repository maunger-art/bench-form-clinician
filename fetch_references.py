"""
fetch_references.py — Fetches real, verified references from PubMed for a given topic.

Uses the NCBI Entrez API (free, no API key required for low volume).
Returns structured reference data with PMIDs, titles, authors, journal, year.
Each reference has a guaranteed-valid PubMed URL.

Called by generate_drafts.py before article generation to provide
Claude with real papers to cite rather than generating from memory.
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional


ENTREZ_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL = "BenchmarkPSBlog"
EMAIL = "info@benchmarkps.org"


def extract_keywords(topic: str) -> str:
    """Extract short search-friendly keywords from a topic string."""
    import re
    # Remove common stop words and keep clinical terms
    stop = {'why', 'how', 'what', 'does', 'the', 'a', 'an', 'and', 'or', 'to',
            'is', 'in', 'for', 'of', 'that', 'with', 'without', 'your', 'our',
            'clinics', 'actually', 'looks', 'like', 'can', 'do', 'good', 'more',
            'patients', 'from', 'are', 'its', 'this', 'at', 'we', 'it', 'be',
            'implement', 'reduce', 'improve', 'look', 'retain', 'percent'}
    words = re.findall(r'[a-zA-Z]+', topic.lower())
    keywords = [w for w in words if w not in stop and len(w) > 3]
    # Take top 4-5 most meaningful words
    return ' '.join(keywords[:5])


def build_search_queries(topic: str) -> list[str]:
    """
    Build multiple targeted PubMed search queries for a topic.
    Uses progressive fallback — starts specific, gets broader if needed.
    """
    keywords = extract_keywords(topic)
    words = keywords.split()
    msk_filter = '("physical therapy" OR "physiotherapy" OR "musculoskeletal" OR "rehabilitation")'

    queries = []

    # Tier 1: Full keywords with MSK filter
    queries.append(f'{keywords} AND {msk_filter}')

    # Tier 2: Full keywords with evidence filter
    queries.append(f'{keywords} AND ("systematic review" OR "randomised controlled trial" OR "meta-analysis")')

    # Tier 3: First 3 keywords only with MSK filter (broader)
    if len(words) > 2:
        short_kw = ' '.join(words[:3])
        queries.append(f'{short_kw} AND {msk_filter}')

    # Tier 4: First 2 keywords only (most broad)
    if len(words) > 1:
        shortest_kw = ' '.join(words[:2])
        queries.append(f'{shortest_kw} AND {msk_filter}')

    # Tier 5: Single most important keyword
    queries.append(f'{words[0]} AND {msk_filter}')

    return queries


def search_pubmed(query: str, max_results: int = 10) -> list[str]:
    """Search PubMed and return list of PMIDs."""
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": "relevance",
        "tool": TOOL,
        "email": EMAIL,
    })
    url = f"{ENTREZ_BASE}/esearch.fcgi?{params}"

    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                data = json.loads(r.read())
            return data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            print(f"    PubMed search attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
    return []


def fetch_pubmed_details(pmids: list[str]) -> list[dict]:
    """Fetch full details for a list of PMIDs."""
    if not pmids:
        return []

    params = urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "json",
        "rettype": "abstract",
        "tool": TOOL,
        "email": EMAIL,
    })
    url = f"{ENTREZ_BASE}/esummary.fcgi?{params}"

    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                data = json.loads(r.read())
            break
        except Exception as e:
            print(f"    PubMed fetch attempt {attempt+1} failed: {e}")
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

        # Extract authors
        authors_raw = paper.get("authors", [])
        authors = []
        for a in authors_raw[:6]:  # Max 6 authors then et al
            name = a.get("name", "")
            if name:
                authors.append(name)
        author_str = ", ".join(authors[:3])
        if len(authors) > 3:
            author_str += " et al"

        # Extract journal info
        journal = paper.get("fulljournalname") or paper.get("source", "")
        volume = paper.get("volume", "")
        issue = paper.get("issue", "")
        pages = paper.get("pages", "")
        pub_year = paper.get("pubdate", "")[:4]
        title = paper.get("title", "").rstrip(".")

        if not title or not author_str:
            continue

        # Build citation string
        vol_issue = f"{volume}({issue})" if volume and issue else volume
        citation = f"{author_str}. {title}. {journal}. {pub_year}"
        if vol_issue:
            citation += f";{vol_issue}"
        if pages:
            citation += f":{pages}"
        citation += "."

        papers.append({
            "pmid": uid,
            "title": title,
            "authors": author_str,
            "journal": journal,
            "year": pub_year,
            "volume": volume,
            "issue": issue,
            "pages": pages,
            "citation": citation,
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
        })

    return papers


def fetch_references_for_topic(topic: str, target_count: int = 15) -> list[dict]:
    """
    Main function: fetch real PubMed references for a topic.
    Returns up to target_count verified papers with full citation data.
    """
    print(f"  Fetching PubMed references for: {topic[:60]}...")

    queries = build_search_queries(topic)
    all_pmids = []
    seen = set()

    for query in queries:
        time.sleep(0.4)  # Respect NCBI rate limits (max 3 requests/second)
        pmids = search_pubmed(query, max_results=8)
        for pmid in pmids:
            if pmid not in seen:
                seen.add(pmid)
                all_pmids.append(pmid)
        if len(all_pmids) >= target_count * 2:
            break

    if not all_pmids:
        print("  No PubMed results found — article will use general guidance only")
        return []

    # Fetch details for top candidates
    time.sleep(0.4)
    papers = fetch_pubmed_details(all_pmids[:20])

    # Filter: must have title, authors, year, journal
    papers = [
        p for p in papers
        if p["title"] and p["authors"] and p["year"] and p["journal"]
    ]

    # Prioritise papers with pages (more complete citations)
    papers.sort(key=lambda p: (bool(p["pages"]), bool(p["volume"])), reverse=True)

    result = papers[:target_count]
    print(f"  Found {len(result)} verified references")
    return result


def format_references_for_prompt(references: list[dict]) -> str:
    """Format reference list for inclusion in Claude prompt."""
    if not references:
        return ""

    lines = ["VERIFIED REFERENCES FROM PUBMED (use these — do not fabricate additional ones):"]
    lines.append("")
    for i, ref in enumerate(references, 1):
        lines.append(f"[{i}] PMID: {ref['pmid']}")
        lines.append(f"    Citation: {ref['citation']}")
        lines.append(f"    URL: {ref['pubmed_url']}")
        lines.append("")

    lines.append("REFERENCE INSTRUCTIONS:")
    lines.append("- Cite ONLY the references listed above — do not invent any others")
    lines.append("- Use superscript numbers inline: <sup>1</sup>, <sup>2</sup> etc")
    lines.append("- The reference list must use <ol class=\"references\"> and include the exact citation text")
    lines.append("- Each <li> must end with: <a href=\"[URL]\" target=\"_blank\">[PMID]</a>")
    lines.append("- Only cite a reference if it is genuinely relevant to the claim being made")
    lines.append("- You may use a subset of provided references — quality over quantity")
    lines.append("- Minimum 5 references from the list must be used")

    return "\n".join(lines)


if __name__ == "__main__":
    # Test
    refs = fetch_references_for_topic("objective outcome measurement physiotherapy practice")
    print(f"\nFound {len(refs)} references:")
    for r in refs[:5]:
        print(f"  [{r['pmid']}] {r['citation'][:100]}")
