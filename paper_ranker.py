"""
paper_ranker.py — Scores and ranks PubMed candidate papers before passing to Claude.

Full 100-point scoring rubric with hard pool-level thresholds and memory integration.
"""

from __future__ import annotations
import re
import statistics
from dataclasses import dataclass, field
from typing import Optional

CLINICAL_DOMAIN_TERMS = {
    "physiotherapy","physical therapy","musculoskeletal","rehabilitation",
    "orthopaedic","orthopedic","msk","physiotherapist","physio",
    "exercise therapy","manual therapy","sports medicine","tendinopathy",
    "tendon","ligament","muscle","joint","cartilage","osteoarthritis","acl",
    "rotator cuff","low back pain","lumbar","cervical","knee","shoulder",
    "hip","ankle","spine","spinal","strength training","range of motion",
    "balance","proprioception","return to sport","return to play",
    "injury prevention","functional","biomechanical",
    # Full-form synonyms
    "anterior cruciate ligament","posterior cruciate ligament",
    "cruciate ligament","medial collateral","lateral collateral",
    "knee replacement","total knee","hip replacement","total hip",
    "rotator cuff repair","shoulder impingement","frozen shoulder",
    "exercise rehabilitation","physical rehabilitation","functional rehabilitation",
    "outpatient physiotherapy","outpatient rehabilitation","community rehabilitation",
    "sport rehabilitation","athletic rehabilitation","sports injury",
    "back rehabilitation","spinal rehabilitation","neck pain",
    "chronic pain","persistent pain","pain management",
    "strengthening","stretching","mobilisation","mobilization",
    "gait","walking","running","movement","mobility","flexibility",
    "conservative management","conservative treatment","non-operative",
}

HEALTH_SERVICES_TERMS = {
    "outcome measure","outcome measurement","patient reported outcome",
    "prom","proms","clinical outcome","functional outcome",
    "health services","service delivery","care model","model of care",
    "staffing","workforce","skill mix","clinical efficiency",
    "cost effectiveness","cost-effectiveness","health economic",
    "value-based","value based care","adherence","compliance",
    "patient retention","dropout","attendance","engagement",
    "clinical practice","evidence-based practice","guideline",
    "benchmarking","quality improvement","audit","performance",
    "routine outcome monitoring","standardised assessment",
    # Additional health services terms
    "patient satisfaction","patient experience","patient outcomes",
    "treatment outcomes","clinical outcomes","functional outcomes",
    "return to function","return to work","return to activity",
    "discharge","follow-up","reassessment","review",
    "evidence based","clinical guideline","best practice",
    "musculoskeletal outcomes","rehabilitation outcomes",
}

HIGH_QUALITY_EVIDENCE = {
    "randomised controlled trial","randomized controlled trial",
    "systematic review","meta-analysis","meta analysis","cochrane review","clinical trial",
}

MODERATE_QUALITY_EVIDENCE = {
    "cohort study","prospective study","observational study",
    "controlled trial","comparative study","implementation study","service evaluation",
}

PRACTICE_RELEVANCE_TERMS = {
    "clinic","clinical practice","practice","practitioner","physiotherapist",
    "therapist","clinician","patient care","treatment","intervention",
    "protocol","guideline","implementation","service","discharge","assessment",
}

HIGH_VALUE_JOURNALS = {
    "physical therapy","physiotherapy",
    "journal of orthopaedic & sports physical therapy",
    "journal of orthopaedic and sports physical therapy",
    "british journal of sports medicine","bmc musculoskeletal disorders",
    "musculoskeletal science and practice","journal of physiotherapy",
    "archives of physical medicine and rehabilitation","clinical rehabilitation",
    "disability and rehabilitation","health services research",
    "bmc health services research","health policy","osteoarthritis and cartilage",
    "american journal of sports medicine",
    "knee surgery sports traumatology arthroscopy",
    "scandinavian journal of medicine & science in sports",
    "journal of science and medicine in sport","sports medicine","manual therapy",
}

WRONG_DOMAIN_SIGNALS = {
    "global burden":"epidemiology/GBD drift","gbd":"epidemiology/GBD drift",
    "cancer":"wrong specialty","cardiovascular":"wrong specialty",
    "diabetes":"wrong specialty","stroke":"wrong specialty",
    "alzheimer":"wrong specialty","dementia":"wrong specialty",
    "oncology":"wrong specialty","hiv":"wrong specialty",
    "priapism":"wrong specialty","urogynecology":"unrelated setting",
    "pelvic organ prolapse":"unrelated setting","ophthalmology":"wrong specialty",
    "dermatology":"wrong specialty",
}


@dataclass
class ScoredPaper:
    pmid: str
    title: str
    authors: str
    journal: str
    year: str
    citation: str
    citation_text: str
    short_cite: str
    pubmed_url: str
    volume: str = ""
    issue: str = ""
    pages: str = ""
    abstract: str = ""
    query_family: str = ""
    clinical_domain_score: float = 0.0
    topic_relevance_score: float = 0.0
    claim_utility_score: float = 0.0
    evidence_quality_score: float = 0.0
    practice_relevance_score: float = 0.0
    journal_score: float = 0.0
    recency_score: float = 0.0
    reuse_penalty: float = 0.0
    domain_penalty: float = 0.0
    total_score: float = 0.0
    decision: str = ""
    why_selected: list[str] = field(default_factory=list)
    why_rejected: list[str] = field(default_factory=list)
    supports_claims: list[str] = field(default_factory=list)
    does_not_support: list[str] = field(default_factory=list)
    rejection_reason: str = ""


@dataclass
class PoolDiagnostics:
    topic: str
    total_candidates: int
    core_count: int
    strong_count: int
    usable_count: int
    rejected_count: int
    wrong_domain_count: int
    top_score: float
    median_score: float
    rejection_reasons: dict
    query_family_contributions: dict
    pool_decision: str
    failure_reasons: list
    originality_decision: str = "N/A"
    novelty_ratio: float = 1.0


def _hits(text: str, terms: set) -> list:
    tl = text.lower()
    return [t for t in terms if t in tl]


def score_paper(paper: dict, brief_intent_terms: list, claim_clusters: list,
                topic_cluster: str = "general", query_family: str = "") -> ScoredPaper:
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    journal = paper.get("journal", "")
    year = paper.get("year", "0")
    combined = f"{title} {abstract} {journal}".lower()

    sp = ScoredPaper(
        pmid=paper["pmid"], title=title, authors=paper.get("authors",""),
        journal=journal, year=year, citation=paper.get("citation",""),
        citation_text=paper.get("citation_text", paper.get("citation","")),
        short_cite=paper.get("short_cite",""), pubmed_url=paper.get("pubmed_url",""),
        volume=paper.get("volume",""), issue=paper.get("issue",""),
        pages=paper.get("pages",""), abstract=abstract, query_family=query_family,
    )

    # Domain penalties first
    for signal, category in WRONG_DOMAIN_SIGNALS.items():
        if signal in combined:
            pen = -25.0 if category in ("epidemiology/GBD drift","wrong specialty") else -15.0
            sp.domain_penalty = min(sp.domain_penalty + pen, 0)
            sp.why_rejected.append(f"PENALTY ({category}: {signal})")
            if not sp.rejection_reason:
                sp.rejection_reason = category

    # Clinical/domain relevance (25)
    ch = _hits(combined, CLINICAL_DOMAIN_TERMS)
    sp.clinical_domain_score = min(25.0, len(ch) * 5.0)
    if ch: sp.why_selected.append(f"Clinical: {', '.join(ch[:3])}")

    # Topic relevance (25)
    ih = [t for t in brief_intent_terms if t.lower() in combined]
    sp.topic_relevance_score = min(25.0, len(ih) * 8.0)
    if ih: sp.why_selected.append(f"Topic terms: {', '.join(ih[:3])}")

    # Claim utility (20)
    useful = 0
    for claim in claim_clusters:
        words = [w for w in re.findall(r'[a-z]+', claim.lower()) if len(w) > 4]
        if sum(1 for w in words if w in combined) >= 2:
            useful += 1
            sp.supports_claims.append(claim)
        else:
            sp.does_not_support.append(claim)
    sp.claim_utility_score = min(20.0, useful * 8.0) if claim_clusters else 10.0
    if useful: sp.why_selected.append(f"Supports {useful} claim clusters")

    # Evidence quality (10)
    hq = _hits(combined, HIGH_QUALITY_EVIDENCE)
    mq = _hits(combined, MODERATE_QUALITY_EVIDENCE)
    if hq:
        sp.evidence_quality_score = 10.0
        sp.why_selected.append(f"Evidence: {hq[0]}")
    elif mq:
        sp.evidence_quality_score = 6.0
        sp.why_selected.append(f"Evidence: {mq[0]}")
    else:
        sp.evidence_quality_score = 3.0

    # Practice relevance (10)
    ph = _hits(combined, PRACTICE_RELEVANCE_TERMS)
    sp.practice_relevance_score = min(10.0, len(ph) * 2.5)
    if ph: sp.why_selected.append(f"Practice: {', '.join(ph[:2])}")

    # Journal (5)
    jl = journal.lower()
    if any(hj in jl for hj in HIGH_VALUE_JOURNALS):
        sp.journal_score = 5.0
        sp.why_selected.append(f"Journal: {journal[:40]}")

    # Recency (5)
    try:
        yr = int(year[:4])
        sp.recency_score = 5.0 if yr >= 2022 else 4.0 if yr >= 2019 else 2.0 if yr >= 2015 else 1.0
        sp.why_selected.append(f"Year: {yr}")
    except:
        sp.recency_score = 1.0

    # Reuse penalty from memory
    try:
        from evidence_memory import get_memory
        sp.reuse_penalty = get_memory().get_reuse_penalty(paper["pmid"], topic_cluster)
        if sp.reuse_penalty < 0:
            sp.why_rejected.append(f"Reuse penalty: {sp.reuse_penalty}")
    except:
        pass

    sp.total_score = max(0.0,
        sp.clinical_domain_score + sp.topic_relevance_score + sp.claim_utility_score +
        sp.evidence_quality_score + sp.practice_relevance_score + sp.journal_score +
        sp.recency_score + sp.domain_penalty + sp.reuse_penalty
    )

    # Thresholds calibrated for title+journal scoring
    if sp.total_score >= 60: sp.decision = "core"
    elif sp.total_score >= 45: sp.decision = "strong"
    elif sp.total_score >= 30: sp.decision = "usable"
    else:
        sp.decision = "rejected"
        if not sp.why_rejected:
            sp.why_rejected.append("Below threshold (30)")

    return sp


def rank_papers(papers: list, topic: str, brief_intent_terms: list,
                claim_clusters: list, topic_cluster: str = "general",
                top_n: int = 10, verbose: bool = True) -> tuple:

    if not papers:
        diag = PoolDiagnostics(
            topic=topic, total_candidates=0, core_count=0, strong_count=0,
            usable_count=0, rejected_count=0, wrong_domain_count=0,
            top_score=0, median_score=0, rejection_reasons={},
            query_family_contributions={}, pool_decision="FAIL",
            failure_reasons=["No candidates"],
        )
        return [], diag

    scored = [score_paper(p, brief_intent_terms, claim_clusters,
                         topic_cluster, p.get("_query_family","unknown")) for p in papers]
    scored.sort(key=lambda s: s.total_score, reverse=True)

    core = [p for p in scored if p.decision == "core"]
    strong = [p for p in scored if p.decision in ("core","strong")]
    usable = [p for p in scored if p.decision in ("core","strong","usable")]
    rejected = [p for p in scored if p.decision == "rejected"]
    wrong_domain = [p for p in scored if p.rejection_reason in ("wrong specialty","epidemiology/GBD drift","unrelated setting")]

    scores = [p.total_score for p in scored]
    median_score = statistics.median(scores) if scores else 0

    rejection_reasons: dict = {}
    for p in rejected:
        r = p.rejection_reason or "below threshold"
        rejection_reasons[r] = rejection_reasons.get(r, 0) + 1

    qf_contributions: dict = {}
    for p in strong:
        fam = p.query_family or "unknown"
        qf_contributions[fam] = qf_contributions.get(fam, 0) + 1

    # Pool-level gating
    failures = []
    # Thresholds calibrated for title+journal scoring (abstracts may not be available)
    if len(usable) < 6: failures.append(f"Only {len(usable)} usable papers (need 6+)")
    if len(strong) < 3: failures.append(f"Only {len(strong)} strong papers (need 3+)")
    if scored and len(wrong_domain) / len(scored) > 0.5:
        failures.append(f"{len(wrong_domain)/len(scored):.0%} wrong domain (limit 50%)")

    if not failures: pool_decision = "PASS"
    elif len(failures) <= 1 and len(usable) >= 4: pool_decision = "RETRY"
    else: pool_decision = "FAIL"

    # Originality
    originality_decision = "N/A"
    novelty_ratio = 1.0
    if pool_decision == "PASS":
        try:
            from evidence_memory import get_memory
            top_pmids = [p.pmid for p in scored[:top_n]]
            passes, novelty_ratio, reason = get_memory().check_pack_originality(top_pmids, topic_cluster)
            originality_decision = "PASS" if passes else "RETRY"
            if not passes:
                pool_decision = "RETRY"
                failures.append(f"Originality: {reason}")
        except:
            originality_decision = "SKIP"

    diag = PoolDiagnostics(
        topic=topic, total_candidates=len(scored), core_count=len(core),
        strong_count=len(strong), usable_count=len(usable), rejected_count=len(rejected),
        wrong_domain_count=len(wrong_domain), top_score=max(scores) if scores else 0,
        median_score=round(median_score,1), rejection_reasons=rejection_reasons,
        query_family_contributions=qf_contributions, pool_decision=pool_decision,
        failure_reasons=failures, originality_decision=originality_decision,
        novelty_ratio=novelty_ratio,
    )

    if verbose:
        icon = "✓" if pool_decision == "PASS" else "⚠" if pool_decision == "RETRY" else "✗"
        print(f"\n  Pool: {len(scored)} candidates | Core:{len(core)} Strong:{len(strong)} Usable:{len(usable)} Rejected:{len(rejected)}")
        print(f"  Scores: top={max(scores):.0f} median={median_score:.1f} | Wrong domain: {len(wrong_domain)}")
        if rejection_reasons:
            print(f"  Rejections: {' | '.join(f'{r}:{c}' for r,c in rejection_reasons.items())}")
        if originality_decision not in ("N/A","SKIP"):
            print(f"  Originality: {originality_decision} (novelty {novelty_ratio:.0%})")
        print(f"  Decision: {icon} {pool_decision}" + (f" — {failures[0]}" if failures else ""))

    if pool_decision == "FAIL":
        return [], diag

    result = []
    for sp in scored[:top_n]:
        if sp.decision != "rejected":
            result.append({
                "pmid": sp.pmid, "title": sp.title, "authors": sp.authors,
                "journal": sp.journal, "year": sp.year, "volume": sp.volume,
                "issue": sp.issue, "pages": sp.pages, "citation": sp.citation,
                "citation_text": sp.citation_text, "short_cite": sp.short_cite,
                "pubmed_url": sp.pubmed_url, "_score": round(sp.total_score,1),
                "_decision": sp.decision, "_why": sp.why_selected[:3],
            })

    return result[:top_n], diag
