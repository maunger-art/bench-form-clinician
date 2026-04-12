"""
multi_source_retriever.py — Retrieves candidate papers from multiple sources.

Sources:
  1. PubMed (NCBI Entrez) — primary, best for clinical MSK/physio evidence
  2. Europe PMC — broader indexing, better for health policy/economics/workforce
  3. OpenAlex — fallback for topics with sparse PubMed/EuropePMC coverage

Each source returns a normalised paper dict with:
  pmid, title, authors, journal, year, abstract, citation, citation_text,
  short_cite, pubmed_url, source_name

Papers without a PMID get a synthetic ID (EPMC:xxx or OAlex:xxx) so the
validator can handle them. Only papers with real PMIDs get canonical PubMed URLs.
"""

from __future__ import annotations

import json
import time
import urllib.request
import urllib.parse
from dataclasses import dataclass

ENTREZ_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EUROPEPMC_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"
OPENALEX_BASE = "https://api.openalex.org"

TOOL = "BenchmarkPSBlog"
EMAIL = "info@benchmarkps.org"
USER_AGENT = f"BenchmarkPSBlog/1.0 ({EMAIL})"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _get(url: str, headers: dict = None, timeout: int = 20) -> bytes:
    """HTTP GET with retries."""
    req = urllib.request.Request(url, headers=headers or {"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise
    return b""


def _build_citation(authors: str, title: str, journal: str, year: str,
                    volume: str = "", issue: str = "", pages: str = "") -> str:
    vol_issue = f"{volume}({issue})" if volume and issue else volume
    c = f"{authors}. {title}. {journal}. {year}"
    if vol_issue:
        c += f";{vol_issue}"
    if pages:
        c += f":{pages}"
    return c + "."


def _short_cite(authors: str, year: str) -> str:
    surname = authors.split(",")[0].split(" ")[0] if authors else "Unknown"
    if " et al" in authors or "," in authors:
        return f"{surname} et al., {year}"
    return f"{surname}, {year}"


# ---------------------------------------------------------------------------
# PubMed
# ---------------------------------------------------------------------------

def search_pubmed(query: str, max_results: int = 20) -> list[str]:
    params = urllib.parse.urlencode({
        "db": "pubmed", "term": query, "retmax": max_results,
        "retmode": "json", "sort": "relevance", "tool": TOOL, "email": EMAIL,
    })
    try:
        data = json.loads(_get(f"{ENTREZ_BASE}/esearch.fcgi?{params}"))
        return data.get("esearchresult", {}).get("idlist", [])
    except Exception:
        return []


def fetch_pubmed_papers(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    params = urllib.parse.urlencode({
        "db": "pubmed", "id": ",".join(pmids), "retmode": "json",
        "tool": TOOL, "email": EMAIL,
    })
    try:
        data = json.loads(_get(f"{ENTREZ_BASE}/esummary.fcgi?{params}"))
    except Exception:
        return []

    results = data.get("result", {})
    papers = []
    for uid in results.get("uids", []):
        p = results.get(uid, {})
        if not p or p.get("error"):
            continue
        authors_raw = [a.get("name", "") for a in p.get("authors", [])[:6] if a.get("name")]
        author_str = ", ".join(authors_raw[:3]) + (" et al" if len(authors_raw) > 3 else "")
        journal = p.get("fulljournalname") or p.get("source", "")
        year = p.get("pubdate", "")[:4]
        title = p.get("title", "").rstrip(".")
        volume = p.get("volume", "")
        issue = p.get("issue", "")
        pages = p.get("pages", "")
        if not title or not author_str:
            continue
        citation = _build_citation(author_str, title, journal, year, volume, issue, pages)
        papers.append({
            "pmid": uid,
            "title": title,
            "authors": author_str,
            "journal": journal,
            "year": year,
            "volume": volume,
            "issue": issue,
            "pages": pages,
            "abstract": "",
            "citation": citation,
            "citation_text": citation,
            "short_cite": _short_cite(author_str, year),
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
            "source_name": "pubmed",
        })
    return papers


def fetch_pubmed_abstracts(pmids: list[str]) -> dict[str, str]:
    if not pmids:
        return {}
    params = urllib.parse.urlencode({
        "db": "pubmed", "id": ",".join(pmids[:20]),
        "rettype": "medline", "retmode": "text",
        "tool": TOOL, "email": EMAIL,
    })
    try:
        text = _get(f"{ENTREZ_BASE}/efetch.fcgi?{params}").decode("utf-8", errors="replace")
    except Exception:
        return {}

    abstracts: dict[str, str] = {}
    current_pmid = None
    current_lines: list[str] = []
    in_abstract = False

    for line in text.splitlines():
        if line.startswith("PMID-"):
            if current_pmid and current_lines:
                abstracts[current_pmid] = " ".join(current_lines)
            current_pmid = line.replace("PMID-", "").strip()
            current_lines = []
            in_abstract = False
        elif line.startswith("AB  -"):
            in_abstract = True
            ab = line.replace("AB  -", "").strip()
            if ab:
                current_lines.append(ab)
        elif in_abstract and line.startswith("      "):
            ab = line.strip()
            if ab:
                current_lines.append(ab)
        elif line and not line.startswith(" ") and "  -" in line:
            in_abstract = False

    if current_pmid and current_lines:
        abstracts[current_pmid] = " ".join(current_lines)

    return abstracts


# ---------------------------------------------------------------------------
# Europe PMC
# ---------------------------------------------------------------------------

def search_europepmc(query: str, max_results: int = 15) -> list[dict]:
    """Search Europe PMC and return normalised paper dicts with abstracts."""
    params = urllib.parse.urlencode({
        "query": query,
        "resultType": "core",
        "pageSize": max_results,
        "format": "json",
        "sort": "RELEVANCE",
    })
    try:
        time.sleep(0.4)
        data = json.loads(_get(f"{EUROPEPMC_BASE}/search?{params}"))
    except Exception as e:
        print(f"    Europe PMC error: {e}")
        return []

    papers = []
    for r in data.get("resultList", {}).get("result", []):
        title = r.get("title", "").rstrip(".")
        if not title:
            continue

        authors_raw = []
        author_list = r.get("authorList", {})
        if isinstance(author_list, dict):
            for a in author_list.get("author", [])[:6]:
                name = a.get("fullName", "") or f"{a.get('lastName','')} {a.get('firstName','')}".strip()
                if name:
                    authors_raw.append(name)
        author_str = ", ".join(authors_raw[:3]) + (" et al" if len(authors_raw) > 3 else "")
        if not author_str:
            author_str = r.get("authorString", "")[:80]

        journal_info = r.get("journalInfo", {}) or {}
        journal = journal_info.get("journal", {}).get("title", "") or r.get("journalTitle", "")
        year = str(r.get("pubYear", ""))
        pmid = r.get("pmid", "") or ""
        abstract = r.get("abstractText", "") or ""

        citation = _build_citation(author_str, title, journal, year)

        # Use real PMID if available, else synthetic ID
        if pmid:
            uid = pmid
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        else:
            uid = f"EPMC:{r.get('id','')}"
            doi = r.get("doi", "")
            url = f"https://doi.org/{doi}" if doi else f"https://europepmc.org/article/med/{r.get('id','')}"

        papers.append({
            "pmid": uid,
            "title": title,
            "authors": author_str,
            "journal": journal,
            "year": year,
            "volume": "",
            "issue": "",
            "pages": "",
            "abstract": abstract,
            "citation": citation,
            "citation_text": citation,
            "short_cite": _short_cite(author_str, year),
            "pubmed_url": url,
            "source_name": "europepmc",
        })

    return papers


# ---------------------------------------------------------------------------
# OpenAlex (fallback)
# ---------------------------------------------------------------------------

def _reconstruct_abstract(inverted_index: dict) -> str:
    """Reconstruct abstract text from OpenAlex inverted index."""
    if not inverted_index:
        return ""
    try:
        words = sorted(
            [(pos, word) for word, positions in inverted_index.items() for pos in positions]
        )
        return " ".join(w for _, w in words)
    except Exception:
        return ""


def search_openalex(query: str, max_results: int = 10) -> list[dict]:
    """Search OpenAlex and return normalised paper dicts."""
    params = urllib.parse.urlencode({
        "search": query,
        "filter": "type:article,publication_year:>2012",
        "sort": "relevance_score:desc",
        "per-page": max_results,
        "select": "id,doi,title,publication_year,primary_location,abstract_inverted_index,authorships",
    })
    try:
        time.sleep(0.4)
        data = json.loads(_get(
            f"{OPENALEX_BASE}/works?{params}",
            headers={"User-Agent": USER_AGENT}
        ))
    except Exception as e:
        print(f"    OpenAlex error: {e}")
        return []

    papers = []
    for r in data.get("results", []):
        title = r.get("title", "")
        if not title:
            continue

        abstract = _reconstruct_abstract(r.get("abstract_inverted_index"))
        loc = r.get("primary_location") or {}
        source = (loc.get("source") or {}).get("display_name", "")
        year = str(r.get("publication_year", ""))
        doi = r.get("doi", "") or ""
        openalex_id = r.get("id", "").replace("https://openalex.org/", "")

        authors_raw = r.get("authorships", [])
        authors = [a.get("author", {}).get("display_name", "") for a in authors_raw[:6]]
        author_str = ", ".join(authors[:3]) + (" et al" if len(authors) > 3 else "")

        uid = f"OAlex:{openalex_id}"
        url = f"https://doi.org/{doi}" if doi else f"https://openalex.org/{openalex_id}"

        citation = _build_citation(author_str, title, source, year)

        papers.append({
            "pmid": uid,
            "title": title,
            "authors": author_str,
            "journal": source,
            "year": year,
            "volume": "",
            "issue": "",
            "pages": "",
            "abstract": abstract,
            "citation": citation,
            "citation_text": citation,
            "short_cite": _short_cite(author_str, year),
            "pubmed_url": url,
            "source_name": "openalex",
        })

    return papers


# ---------------------------------------------------------------------------
# Multi-source retrieval
# ---------------------------------------------------------------------------

# Topic clusters that should use Europe PMC as primary source
EUROPEPMC_PRIMARY_CLUSTERS = {
    "staffing", "value_economics",
}

# Topic clusters that should use OpenAlex as additional source
OPENALEX_ADDITIONAL_CLUSTERS = {
    "staffing", "value_economics",
}

# Europe PMC query templates for clusters PubMed fails on
EUROPEPMC_QUERIES = {
    "staffing": [
        'physiotherapy "staffing model" OR "skill mix" OR "workforce" outcomes clinical',
        'physiotherapy "delegation" OR "task shifting" OR "staff mix" outcomes',
        '"allied health" staffing workforce outcomes efficiency',
        'physiotherapy "clinical governance" OR "service delivery" workforce',
    ],
    "value_economics": [
        'physiotherapy "cost effectiveness" OR "health economics" outcomes musculoskeletal',
        'physiotherapy "value based" OR "value-based care" outcomes rehabilitation',
        'musculoskeletal "cost effectiveness" OR "economic evaluation" physiotherapy',
        'physiotherapy "return on investment" OR "cost benefit" outcomes',
    ],
}


def retrieve_candidates(
    pubmed_queries: list,  # QuerySpec list from query_builder
    topic: str,
    topic_cluster: str,
    pmids_per_query: int = 20,
) -> list[dict]:
    """
    Retrieve candidate papers from all appropriate sources.
    Returns deduplicated list with abstracts attached.
    """
    all_papers: list[dict] = []
    seen_paper_ids: set[str] = set()  # tracks papers already in all_papers
    seen_pmids: set[str] = set()      # tracks PMIDs already queued for fetch

    def add_papers(new_papers: list[dict]):
        for p in new_papers:
            uid = p["pmid"]
            if uid and uid not in seen_paper_ids:
                seen_paper_ids.add(uid)
                all_papers.append(p)

    # --- PubMed retrieval ---
    pubmed_pmids: list[str] = []
    pmid_to_family: dict[str, str] = {}

    for query_spec in pubmed_queries:
        if not getattr(query_spec, "is_valid", True):
            continue
        time.sleep(0.4)
        pmids = search_pubmed(query_spec.query_string, max_results=pmids_per_query)
        for pmid in pmids:
            if pmid not in seen_pmids:
                seen_pmids.add(pmid)
                pubmed_pmids.append(pmid)
                if pmid not in pmid_to_family:
                    pmid_to_family[pmid] = getattr(query_spec, "family", "unknown")

    # Fetch PubMed metadata for up to 40 candidates
    if pubmed_pmids:
        time.sleep(0.4)
        pubmed_papers = fetch_pubmed_papers(pubmed_pmids[:40])
        for p in pubmed_papers:
            p["_query_family"] = pmid_to_family.get(p["pmid"], "pubmed")
        add_papers(pubmed_papers)

        # Fetch abstracts for PubMed papers
        time.sleep(0.4)
        top_pmids = [p["pmid"] for p in pubmed_papers[:20] if p["pmid"].isdigit()]
        abstracts = fetch_pubmed_abstracts(top_pmids)
        for p in all_papers:
            if p["pmid"] in abstracts:
                p["abstract"] = abstracts[p["pmid"]]

    pubmed_count = len(all_papers)
    print(f"    PubMed: {pubmed_count} candidates")

    # --- Europe PMC retrieval ---
    # Use for staffing/economics topics, or whenever PubMed returns < 15 candidates
    should_use_europepmc = (
        topic_cluster in EUROPEPMC_PRIMARY_CLUSTERS or
        pubmed_count < 15
    )

    if should_use_europepmc:
        epmc_queries = EUROPEPMC_QUERIES.get(topic_cluster, [])

        # If no cluster-specific queries, build generic ones from topic
        if not epmc_queries:
            words = [w for w in topic.lower().split() if len(w) > 4][:5]
            generic = " ".join(words[:4])
            epmc_queries = [
                f'physiotherapy {generic}',
                f'rehabilitation {generic} outcomes',
            ]

        epmc_count = 0
        for q in epmc_queries[:3]:
            time.sleep(0.5)
            papers = search_europepmc(q, max_results=10)
            before = len(all_papers)
            for p in papers:
                p["_query_family"] = "europepmc"
            add_papers(papers)
            epmc_count += len(all_papers) - before

        print(f"    Europe PMC: {epmc_count} new candidates added")

    # --- OpenAlex retrieval (additional fallback) ---
    total_so_far = len(all_papers)
    if topic_cluster in OPENALEX_ADDITIONAL_CLUSTERS and total_so_far < 25:
        oa_query = f"physiotherapy {' '.join(topic.lower().split()[:5])}"
        time.sleep(0.5)
        oa_papers = search_openalex(oa_query, max_results=10)
        oa_count = 0
        for p in oa_papers:
            p["_query_family"] = "openalex"
            # Filter obvious noise
            if not any(noise in p["title"].lower() for noise in
                       ["global burden", "gbd 20", "global incidence", "lancet series call"]):
                if p not in all_papers:
                    uid = p["pmid"]
                    if uid not in seen_ids:
                        seen_ids.add(uid)
                        all_papers.append(p)
                        oa_count += 1
        if oa_count:
            print(f"    OpenAlex: {oa_count} new candidates added")

    # Filter: require title
    all_papers = [p for p in all_papers if p["title"] and p["year"]]

    print(f"    Total candidates: {len(all_papers)} (PubMed:{pubmed_count} + other sources)")
    return all_papers


if __name__ == "__main__":
    from query_builder import QuerySpec

    # Test staffing topic
    class FakeQuery:
        query_string = '("Physical Therapy Modalities"[mh] OR physiotherapy[tiab]) AND ("Musculoskeletal Diseases"[mh] OR musculoskeletal[tiab]) AND ("Personnel Staffing and Scheduling"[mh] OR staffing[tiab] OR workforce[tiab]) NOT ("global burden of disease"[tiab] OR GBD[tiab])'
        is_valid = True
        family = "balanced"

    papers = retrieve_candidates(
        [FakeQuery()],
        topic="Staffing Mix and Physiotherapy Margins",
        topic_cluster="staffing",
    )
    print(f"\nTotal: {len(papers)}")
    for p in papers[:5]:
        print(f"  [{p['source_name']}] {p['title'][:70]}")
        print(f"    {p['year']} | {p['journal'][:40]} | abstract: {len(p['abstract'])} chars")
