"""
evidence_pack_builder.py — Orchestrates the full evidence retrieval pipeline.

Stages:
1. Topic normalization
2. Query generation + validation
3. PubMed retrieval + deduplication
4. Abstract fetching
5. Relevance scoring + pool gating
6. Evidence pack selection (5-7 papers)
7. Diagnostic output

Returns an approved evidence pack or raises if pool fails gating.
"""

from __future__ import annotations

import json
import time
import urllib.request
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional

from topic_normalizer import normalize_topic, SearchBrief
from query_builder import get_valid_queries, QuerySpec
from paper_ranker import rank_papers, PoolDiagnostics
from evidence_memory import detect_cluster
from multi_source_retriever import retrieve_candidates as multi_retrieve

ENTREZ_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL = "BenchmarkPSBlog"
EMAIL = "info@benchmarkps.org"

MAX_RETRIES = 2
MIN_POOL_SIZE = 20


@dataclass
class EvidencePack:
    article_title: str
    topic_cluster: str
    brief: SearchBrief
    approved_references: list[dict]
    diagnostics: PoolDiagnostics
    pool_decision: str
    retry_count: int = 0


class PoolFailure(Exception):
    """Raised when the evidence pool fails gating thresholds after retries."""
    pass


def _search_pubmed(query: str, max_results: int = 20) -> list[str]:
    """Run a PubMed esearch and return PMIDs."""
    params = urllib.parse.urlencode({
        "db": "pubmed", "term": query, "retmax": max_results,
        "retmode": "json", "sort": "relevance", "tool": TOOL, "email": EMAIL,
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(
                f"{ENTREZ_BASE}/esearch.fcgi?{params}", timeout=20
            ) as r:
                data = json.loads(r.read())
            return data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
    return []


def _fetch_summaries(pmids: list[str]) -> list[dict]:
    """Fetch ESummary metadata for a list of PMIDs."""
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
            "pmid": uid,
            "title": title,
            "authors": author_str,
            "journal": journal,
            "year": pub_year,
            "volume": volume,
            "issue": issue,
            "pages": pages,
            "citation": citation,
            "citation_text": citation,
            "short_cite": short_cite,
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
            "abstract": "",  # Will be enriched below
        })

    return papers


def _fetch_abstracts(pmids: list[str]) -> dict[str, str]:
    """Fetch abstracts via EFetch in MEDLINE format. Returns {pmid: abstract_text}."""
    if not pmids:
        return {}
    params = urllib.parse.urlencode({
        "db": "pubmed", "id": ",".join(pmids[:20]),
        "rettype": "medline",  # MEDLINE tagged format — has PMID- and AB  - tags
        "retmode": "text",
        "tool": TOOL, "email": EMAIL,
    })
    try:
        with urllib.request.urlopen(
            f"{ENTREZ_BASE}/efetch.fcgi?{params}", timeout=30
        ) as r:
            text = r.read().decode("utf-8", errors="replace")

        abstracts: dict[str, str] = {}
        current_pmid = None
        current_ab_lines: list[str] = []
        in_abstract = False

        for line in text.splitlines():
            # New record
            if line.startswith("PMID-"):
                # Save previous record
                if current_pmid and current_ab_lines:
                    abstracts[current_pmid] = " ".join(current_ab_lines)
                current_pmid = line.replace("PMID-", "").strip()
                current_ab_lines = []
                in_abstract = False

            # Abstract start
            elif line.startswith("AB  -"):
                in_abstract = True
                ab_text = line.replace("AB  -", "").strip()
                if ab_text:
                    current_ab_lines.append(ab_text)

            # Abstract continuation (6-space indent in MEDLINE)
            elif in_abstract and line.startswith("      "):
                ab_text = line.strip()
                if ab_text:
                    current_ab_lines.append(ab_text)

            # Any other tag ends the abstract
            elif line and not line.startswith(" ") and "  -" in line:
                in_abstract = False

        # Save last record
        if current_pmid and current_ab_lines:
            abstracts[current_pmid] = " ".join(current_ab_lines)

        return abstracts
    except Exception:
        return {}


def _retrieve_candidates(
    queries: list[QuerySpec],
    pmids_per_query: int = 20,
) -> list[dict]:
    """
    Run all valid queries, deduplicate, fetch metadata + abstracts.
    Tags each paper with its query family.
    """
    all_pmids: list[str] = []
    seen: set[str] = set()
    pmid_to_family: dict[str, str] = {}

    for query in queries:
        if not query.is_valid:
            continue
        time.sleep(0.4)
        pmids = _search_pubmed(query.query_string, max_results=pmids_per_query)
        new_pmids = [p for p in pmids if p not in seen]
        for pmid in new_pmids:
            seen.add(pmid)
            all_pmids.append(pmid)
            if pmid not in pmid_to_family:
                pmid_to_family[pmid] = query.family

    if not all_pmids:
        return []

    # Fetch metadata for up to 40 candidates
    time.sleep(0.4)
    papers = _fetch_summaries(all_pmids[:40])

    # Fetch abstracts for top candidates (improves scoring)
    time.sleep(0.4)
    top_pmids = [p["pmid"] for p in papers[:20]]
    abstracts = _fetch_abstracts(top_pmids)

    # Attach query family and abstract
    for paper in papers:
        paper["_query_family"] = pmid_to_family.get(paper["pmid"], "unknown")
        paper["abstract"] = abstracts.get(paper["pmid"], "")

    # Filter: require title and authors
    papers = [p for p in papers if p["title"] and p["authors"] and p["year"]]
    return papers


def _select_pack(ranked: list[dict], target: int = 7) -> list[dict]:
    """
    Select final 5-7 paper evidence pack.
    Rules:
      - At least 3 direct-topic papers (core/strong)
      - At least 1 systematic review or high-quality evidence if available
      - No more than 1 marginal paper (usable-tier)
      - Diversity across score levels
    """
    core_strong = [p for p in ranked if p.get("_decision") in ("core", "strong")]
    usable = [p for p in ranked if p.get("_decision") == "usable"]

    selected = []

    # Add core/strong papers first (up to target-1)
    selected.extend(core_strong[:target - 1])

    # Add at most 1 usable/marginal paper
    if len(selected) < target and usable:
        selected.append(usable[0])

    # If we have fewer than 5, add more from ranked regardless of tier
    if len(selected) < 5:
        remaining = [p for p in ranked if p not in selected]
        selected.extend(remaining[:5 - len(selected)])

    return selected[:target]


def build_evidence_pack(
    title: str,
    target_pack_size: int = 7,
    max_retries: int = MAX_RETRIES,
    verbose: bool = True,
) -> EvidencePack:
    """
    Full pipeline: normalize → query → retrieve → score → gate → pack.

    Returns EvidencePack. Raises PoolFailure if pool fails after retries.
    """
    brief = normalize_topic(title)
    topic_cluster = detect_cluster(title)

    if verbose:
        print(f"  Topic cluster: {topic_cluster} | Business: {brief.is_business_topic}")
        print(f"  Intents: {brief.detected_intents} | Conditions: {brief.detected_conditions}")

    last_diag: Optional[PoolDiagnostics] = None
    retry_count = 0

    for attempt in range(max_retries + 1):
        # Generate validated queries
        queries = get_valid_queries(brief)
        if verbose:
            valid_count = sum(1 for q in queries if q.is_valid)
            print(f"  Queries: {valid_count} valid (attempt {attempt + 1})")

        # Retrieve candidates from all sources
        candidates = multi_retrieve(queries, topic=title, topic_cluster=topic_cluster, pmids_per_query=20)

        if len(candidates) < MIN_POOL_SIZE and attempt < max_retries:
            if verbose:
                print(f"  Only {len(candidates)} candidates — broadening queries")
            # Fallback: try broader search on retry
            retry_count += 1
            time.sleep(1)
            continue

        # Score and gate
        ranked, diag = rank_papers(
            candidates,
            topic=title,
            brief_intent_terms=brief.intent_terms,
            claim_clusters=brief.claim_clusters,
            topic_cluster=topic_cluster,
            top_n=target_pack_size,
            verbose=verbose,
        )
        last_diag = diag

        if diag.pool_decision == "PASS":
            pack = _select_pack(ranked, target=target_pack_size)
            return EvidencePack(
                article_title=title,
                topic_cluster=topic_cluster,
                brief=brief,
                approved_references=pack,
                diagnostics=diag,
                pool_decision="PASS",
                retry_count=retry_count,
            )

        elif diag.pool_decision == "RETRY" and attempt < max_retries:
            if verbose:
                print(f"  Pool RETRY — {diag.failure_reasons[0] if diag.failure_reasons else 'threshold not met'}")
            retry_count += 1
            time.sleep(1)
            continue

        else:
            # FAIL or out of retries
            break

    # Return best available even if below thresholds, with RETRY decision
    if last_diag and ranked:
        pack = _select_pack(ranked, target=target_pack_size)
        return EvidencePack(
            article_title=title,
            topic_cluster=topic_cluster,
            brief=brief,
            approved_references=pack,
            diagnostics=last_diag,
            pool_decision="RETRY",
            retry_count=retry_count,
        )

    # Graceful fallback: return best available papers with FAIL decision
    # Never block generation entirely — let Claude and the validator handle quality
    print(f"  WARNING: Pool below threshold — returning best available papers")
    if last_diag:
        print(f"  Failures: {last_diag.failure_reasons}")

    # Fall back to legacy retrieval if pipeline returned nothing useful
    if not ranked:
        print(f"  Falling back to legacy retrieval...")
        from fetch_references import _legacy_fetch
        legacy_refs = _legacy_fetch(title, target_count=target_pack_size)
        if legacy_refs:
            return EvidencePack(
                article_title=title, topic_cluster=topic_cluster,
                brief=brief, approved_references=legacy_refs,
                diagnostics=last_diag, pool_decision="FALLBACK",
                retry_count=retry_count,
            )

    pack = _select_pack(ranked, target=target_pack_size) if ranked else []
    return EvidencePack(
        article_title=title, topic_cluster=topic_cluster, brief=brief,
        approved_references=pack, diagnostics=last_diag,
        pool_decision="RETRY", retry_count=retry_count,
    )


if __name__ == "__main__":
    title = "The Business Case for Outcome Measurement in Physiotherapy Clinics"
    print(f"\nBuilding evidence pack for: {title}\n")
    try:
        pack = build_evidence_pack(title, target_pack_size=7, verbose=True)
        print(f"\n{'='*60}")
        print(f"Pack decision: {pack.pool_decision}")
        print(f"Approved references: {len(pack.approved_references)}")
        for r in pack.approved_references:
            print(f"  [{r['_score']:.0f}/{r['_decision']}] {r['citation'][:80]}")
    except PoolFailure as e:
        print(f"\nFAIL: {e}")
