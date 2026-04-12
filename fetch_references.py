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


# Maps business/management topic signals to structured PubMed queries
# Uses three-layer approach: clinical anchor + economics layer + topic intent
# with explicit GBD/epidemiology exclusion
TOPIC_CLINICAL_MAPPING = [
    # Outcome measurement / business case / retention / pricing
    (["business case", "outcome measurement", "retain", "retention",
      "pricing", "charge more", "hidden cost", "inconsistent"],
     [
      '("Physical Therapy Modalities"[MeSH] OR physiotherapy[tiab]) AND ("Outcome Assessment, Health Care"[MeSH] OR outcome measure*[tiab] OR PROMs[tiab]) AND (cost[tiab] OR value[tiab] OR efficiency[tiab]) NOT (global burden of disease[tiab] OR GBD[tiab])',
      '(physiotherapy[tiab] OR "physical therapy"[tiab]) AND (PROMs[tiab] OR "patient reported outcome"[tiab]) AND ("Health Services Research"[MeSH] OR value[tiab] OR utilization[tiab])',
      '("Outcome Assessment, Health Care"[MeSH]) AND ("Physical Therapy Modalities"[MeSH]) AND ("Cost-Benefit Analysis"[MeSH] OR economic*[tiab])',
      '(physiotherapy[tiab]) AND (benchmarking[tiab] OR "outcome tracking"[tiab] OR "routine outcome"[tiab]) AND (efficiency[tiab] OR value[tiab])',
      '("Rehabilitation"[MeSH]) AND ("Outcome Assessment, Health Care"[MeSH]) AND (resource[tiab] OR cost[tiab])',
     ]),

    # Patient adherence / dropout / engagement
    (["adherence", "dropout", "dropout", "engagement", "patient retention"],
     [
      '("Patient Compliance"[MeSH] OR adherence[tiab]) AND (physiotherapy[tiab] OR rehabilitation[MeSH]) AND (outcome*[tiab] OR cost[tiab])',
      '(physiotherapy[tiab]) AND (dropout[tiab] OR retention[tiab] OR adherence[tiab]) AND (effectiveness[tiab] OR outcome*[tiab])',
      '("Patient Compliance"[MeSH]) AND ("Physical Therapy Modalities"[MeSH]) AND (utilization[tiab] OR cost[tiab])',
      '(physiotherapy[tiab]) AND (engagement[tiab] OR adherence[tiab]) AND ("health outcomes"[tiab] OR value[tiab])',
      '("Rehabilitation"[MeSH]) AND (attendance[tiab] OR adherence[tiab]) AND (efficiency[tiab] OR utilization[tiab])',
     ]),

    # Staffing / workforce / margins
    (["staffing", "margins", "workforce", "senior clinician",
      "standardised care", "skill mix", "staffing mix"],
     [
      '("Health Workforce"[MeSH] OR staffing[tiab] OR workforce[tiab]) AND (physiotherapy[tiab] OR rehabilitation[MeSH]) AND (efficiency[tiab] OR productivity[tiab] OR cost[tiab])',
      '("Personnel Staffing and Scheduling"[MeSH]) AND ("Rehabilitation"[MeSH]) AND (model of care[tiab] OR service delivery[tiab])',
      '(allied health[tiab] OR physiotherapy[tiab]) AND (staffing model*[tiab] OR skill mix[tiab]) AND (cost[tiab] OR efficiency[tiab])',
      '("Delivery of Health Care"[MeSH]) AND (rehabilitation[MeSH]) AND (workforce[tiab] OR staffing[tiab]) AND (outcome*[tiab])',
      '(physiotherapy[tiab]) AND (task shifting[tiab] OR delegation[tiab]) AND (cost[tiab] OR productivity[tiab])',
     ]),

    # Economic / value-based / cost-effectiveness
    (["economic case", "economic", "value-based", "cost-effective"],
     [
      '("Value-Based Health Care"[tiab] OR "value-based care"[tiab]) AND (physiotherapy[tiab] OR rehabilitation[MeSH])',
      '("Cost-Benefit Analysis"[MeSH]) AND ("Musculoskeletal Diseases"[MeSH]) AND ("Physical Therapy Modalities"[MeSH])',
      '(physiotherapy[tiab]) AND (value[tiab] OR cost-effectiveness[tiab]) AND (outcome*[tiab])',
      '("Health Care Costs"[MeSH]) AND (rehabilitation[MeSH]) AND (musculoskeletal[tiab])',
      '(physiotherapy[tiab]) AND ("bundled payment"[tiab] OR "value-based care"[tiab]) AND (outcome*[tiab] OR cost[tiab])',
     ]),

    # Technology / digital / telehealth
    (["technology", "digital", "telehealth", "app", "wearable", "remote"],
     [
      '("Telemedicine"[MeSH] OR telehealth[tiab]) AND (physiotherapy[tiab] OR rehabilitation[MeSH]) AND (outcome*[tiab])',
      '("Mobile Applications"[MeSH] OR digital health[tiab] OR mHealth[tiab]) AND (physiotherapy[tiab]) AND (outcome*[tiab])',
      '(physiotherapy[tiab]) AND (technology[tiab] OR wearable*[tiab]) AND (outcome*[tiab] OR effectiveness[tiab])',
      '("Physical Therapy Modalities"[MeSH]) AND (remote[tiab] OR digital[tiab]) AND (outcome*[tiab])',
     ]),
]


def get_clinical_queries(topic: str) -> list[str] | None:
    """Return clinical PubMed queries for business/management topics that lack direct evidence."""
    topic_lower = topic.lower()
    for signals, queries in TOPIC_CLINICAL_MAPPING:
        if any(signal in topic_lower for signal in signals):
            return queries
    return None


def extract_keywords(topic: str) -> str:
    """Extract short search-friendly keywords from a topic string."""
    import re
    stop = {'why', 'how', 'what', 'does', 'the', 'a', 'an', 'and', 'or', 'to',
            'is', 'in', 'for', 'of', 'that', 'with', 'without', 'your', 'our',
            'clinics', 'actually', 'looks', 'like', 'can', 'do', 'good', 'more',
            'patients', 'from', 'are', 'its', 'this', 'at', 'we', 'it', 'be',
            'implement', 'reduce', 'improve', 'look', 'retain', 'percent'}
    words = re.findall(r'[a-zA-Z]+', topic.lower())
    keywords = [w for w in words if w not in stop and len(w) > 3]
    return ' '.join(keywords[:5])


def build_search_queries(topic: str) -> list[str]:
    """
    Build multiple targeted PubMed search queries for a topic.
    For business/management topics, uses curated clinical queries.
    For clinical topics, uses progressive keyword fallback.
    """
    # Check if topic needs clinical query substitution
    clinical_queries = get_clinical_queries(topic)
    if clinical_queries:
        return clinical_queries

    # Standard keyword-based queries for clinical topics
    keywords = extract_keywords(topic)
    words = keywords.split()
    msk_filter = '("physical therapy" OR "physiotherapy" OR "musculoskeletal" OR "rehabilitation")'

    queries = []
    queries.append(f'{keywords} AND {msk_filter}')
    queries.append(f'{keywords} AND ("systematic review" OR "randomised controlled trial" OR "meta-analysis")')

    if len(words) > 2:
        short_kw = ' '.join(words[:3])
        queries.append(f'{short_kw} AND {msk_filter}')

    if len(words) > 1:
        shortest_kw = ' '.join(words[:2])
        queries.append(f'{shortest_kw} AND {msk_filter}')

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

        # Build short_cite: "First Author et al., YEAR" or "Author, YEAR"
        first_author_surname = authors[0].split(" ")[0] if authors else "Unknown"
        if len(authors) > 1:
            short_cite = f"{first_author_surname} et al., {pub_year}"
        else:
            short_cite = f"{first_author_surname}, {pub_year}"

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
            "citation_text": citation,   # alias for validate_repair_citations.py
            "short_cite": short_cite,
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
        })

    return papers


def fetch_references_for_topic(topic: str, target_count: int = 10) -> list[dict]:
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
    """Format reference list for inclusion in Claude prompt using token workflow."""
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
    # Test
    refs = fetch_references_for_topic("objective outcome measurement physiotherapy practice")
    print(f"\nFound {len(refs)} references:")
    for r in refs[:5]:
        print(f"  [{r['pmid']}] {r['citation'][:100]}")
