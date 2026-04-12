"""
evidence_memory.py — Persistent evidence usage tracking and anti-reuse control.

Tracks which papers have been used, how often, in which articles, and
applies reuse penalties during ranking to ensure evidence diversity.

Storage: evidence_usage.json (committed to repo alongside posts_manifest.json)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional


MEMORY_PATH = Path(__file__).parent / "evidence_usage.json"

# Topic cluster mapping for cluster-level reuse detection
# Topic clusters — aligned to the 5-tier content architecture
TOPIC_CLUSTERS = {
    # TIER 1: Condition-specific testing and benchmarks
    "acl_knee": [
        "acl", "anterior cruciate ligament", "knee", "patellofemoral",
        "return to sport", "quad strength", "hop test", "limb symmetry",
    ],
    "lower_limb_conditions": [
        "hamstring", "achilles", "ankle", "plantar fasciitis", "hip",
        "groin", "tibial", "lower limb", "calf",
    ],
    "upper_limb_conditions": [
        "shoulder", "rotator cuff", "elbow", "tennis elbow", "de quervain",
        "grip strength", "upper limb", "wrist",
    ],
    "spinal_conditions": [
        "low back pain", "lumbar", "cervical", "spine", "radiculopathy",
        "back pain", "trunk",
    ],
    "osteoarthritis": [
        "osteoarthritis", "knee oa", "hip oa", "conservative care",
        "non-surgical", "joint",
    ],
    "athletic_populations": [
        "athlete", "football", "rugby", "runner", "cyclist", "weightlifter",
        "sport", "athletic", "performance", "field test",
    ],
    # TIER 2: Assessment methodology
    "assessment_methodology": [
        "outcome measurement", "benchmark", "prom", "reliability", "validity",
        "handheld dynamometry", "hop test", "limb symmetry index", "grip strength",
        "mcid", "mdc", "inter-rater", "range of motion",
    ],
    # TIER 3: Clinical decision-making
    "clinical_decision": [
        "clinical decision", "criteria based", "discharge criteria",
        "progression", "return to sport", "plateau", "referral",
        "shared decision", "when to",
    ],
    # TIER 4: Technology / low-tech
    "technology_implementation": [
        "technology", "digital", "telehealth", "app", "wearable", "remote",
        "handheld dynamometry", "field test", "smartphone", "low cost",
        "without expensive", "implementation",
    ],
    # TIER 5: Business / economics
    "value_economics": [
        "business case", "economic", "cost", "value", "pricing",
        "health economics", "payer", "insurer", "variation", "staffing",
        "workforce", "margins", "skill mix", "defensible",
    ],
}


def detect_cluster(title: str) -> str:
    """Map an article title to its topic cluster."""
    title_lower = title.lower()
    best_cluster = "general"
    best_count = 0
    for cluster, signals in TOPIC_CLUSTERS.items():
        count = sum(1 for s in signals if s in title_lower)
        if count > best_count:
            best_count = count
            best_cluster = cluster
    return best_cluster


@dataclass
class PaperUsageRecord:
    pmid: str
    article_titles: list[str] = field(default_factory=list)
    topic_clusters: list[str] = field(default_factory=list)
    first_used_date: str = ""
    last_used_date: str = ""
    total_times_used: int = 0
    recent_use_count: int = 0  # Used in last 10 articles
    used_as_core: bool = False  # Was it a high-scoring core reference?


@dataclass
class ArticlePackRecord:
    article_title: str
    topic_cluster: str
    pmids: list[str]
    publish_date: str
    core_pmids: list[str] = field(default_factory=list)


class EvidenceMemory:
    """Manages persistent evidence usage tracking."""

    def __init__(self, path: Path = MEMORY_PATH):
        self.path = path
        self.paper_usage: dict[str, PaperUsageRecord] = {}
        self.article_packs: list[ArticlePackRecord] = []
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                for pmid, rec in data.get("paper_usage", {}).items():
                    self.paper_usage[pmid] = PaperUsageRecord(**rec)
                for pack in data.get("article_packs", []):
                    self.article_packs.append(ArticlePackRecord(**pack))
            except Exception as e:
                print(f"  Warning: Could not load evidence memory: {e}")

    def save(self):
        data = {
            "paper_usage": {pmid: asdict(rec) for pmid, rec in self.paper_usage.items()},
            "article_packs": [asdict(p) for p in self.article_packs],
            "last_updated": date.today().isoformat(),
        }
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_reuse_penalty(self, pmid: str, topic_cluster: str) -> float:
        """
        Calculate reuse penalty for a paper.
        Returns a negative float (0 = no penalty, -20 = strong penalty).
        """
        if pmid not in self.paper_usage:
            return 0.0  # Never used — no penalty

        rec = self.paper_usage[pmid]
        penalty = 0.0

        # Penalty for total usage
        if rec.total_times_used >= 5:
            penalty -= 15.0
        elif rec.total_times_used >= 3:
            penalty -= 10.0
        elif rec.total_times_used >= 1:
            penalty -= 5.0

        # Extra penalty for recent usage (last 5 articles)
        if rec.recent_use_count >= 3:
            penalty -= 10.0
        elif rec.recent_use_count >= 1:
            penalty -= 5.0

        # Extra penalty for same cluster reuse
        if topic_cluster in rec.topic_clusters:
            cluster_count = rec.topic_clusters.count(topic_cluster)
            penalty -= min(10.0, cluster_count * 4.0)

        return max(-25.0, penalty)

    def check_pack_originality(
        self, proposed_pmids: list[str], topic_cluster: str, min_novelty: float = 0.6
    ) -> tuple[bool, float, str]:
        """
        Check if a proposed evidence pack has sufficient novelty.

        Returns:
          (passes: bool, novelty_ratio: float, reason: str)
        """
        if not self.article_packs:
            return True, 1.0, "No prior articles — full novelty"

        # Recent articles (last 10)
        recent_packs = self.article_packs[-10:]

        # Count how many proposed PMIDs are new
        all_recent_pmids = set()
        for pack in recent_packs:
            all_recent_pmids.update(pack.pmids)

        new_pmids = [p for p in proposed_pmids if p not in all_recent_pmids]
        novelty_ratio = len(new_pmids) / len(proposed_pmids) if proposed_pmids else 1.0

        # Check overlap with any single recent article
        max_overlap = 0
        max_overlap_title = ""
        for pack in recent_packs:
            overlap = len(set(proposed_pmids) & set(pack.pmids))
            if overlap > max_overlap:
                max_overlap = overlap
                max_overlap_title = pack.article_title

        passes = novelty_ratio >= min_novelty
        if not passes:
            reason = (
                f"Novelty {novelty_ratio:.0%} below {min_novelty:.0%} threshold. "
                f"Highest overlap with: '{max_overlap_title[:50]}' ({max_overlap} papers)"
            )
        else:
            reason = f"Novelty {novelty_ratio:.0%} — {len(new_pmids)}/{len(proposed_pmids)} papers are new"

        return passes, novelty_ratio, reason

    def record_article(
        self,
        article_title: str,
        pmids: list[str],
        core_pmids: Optional[list[str]] = None,
    ):
        """Record a published article's evidence pack into memory."""
        today = date.today().isoformat()
        cluster = detect_cluster(article_title)
        core_pmids = core_pmids or pmids[:3]

        # Update paper usage records
        for pmid in pmids:
            if pmid not in self.paper_usage:
                self.paper_usage[pmid] = PaperUsageRecord(pmid=pmid)

            rec = self.paper_usage[pmid]
            rec.article_titles.append(article_title)
            rec.topic_clusters.append(cluster)
            rec.total_times_used += 1
            rec.last_used_date = today
            if not rec.first_used_date:
                rec.first_used_date = today
            if pmid in core_pmids:
                rec.used_as_core = True

        # Update recent_use_count (last 10 articles = recent)
        recent_pmids: set[str] = set()
        for pack in self.article_packs[-9:]:  # 9 existing + this new one = 10
            recent_pmids.update(pack.pmids)
        for pmid in pmids:
            if pmid in recent_pmids:
                self.paper_usage[pmid].recent_use_count += 1

        # Record the article pack
        self.article_packs.append(ArticlePackRecord(
            article_title=article_title,
            topic_cluster=cluster,
            pmids=pmids,
            publish_date=today,
            core_pmids=core_pmids,
        ))

        self.save()
        print(f"  Evidence memory updated: {len(pmids)} papers recorded for '{article_title[:50]}'")

    def get_diagnostics(self, proposed_pmids: list[str], topic_cluster: str) -> dict:
        """Return originality diagnostics for a proposed pack."""
        previously_used = [p for p in proposed_pmids if p in self.paper_usage]
        unused = [p for p in proposed_pmids if p not in self.paper_usage]

        reuse_counts = [
            self.paper_usage[p].total_times_used
            for p in previously_used
        ]
        avg_reuse = sum(reuse_counts) / len(reuse_counts) if reuse_counts else 0

        passes, novelty, reason = self.check_pack_originality(proposed_pmids, topic_cluster)

        return {
            "total_candidates": len(proposed_pmids),
            "previously_used": len(previously_used),
            "unused_papers": len(unused),
            "avg_reuse_count": round(avg_reuse, 1),
            "novelty_ratio": round(novelty, 2),
            "novelty_passes": passes,
            "novelty_reason": reason,
            "originality_decision": "PASS" if passes else "RETRY",
        }


# Singleton
_memory: Optional[EvidenceMemory] = None


def get_memory() -> EvidenceMemory:
    global _memory
    if _memory is None:
        _memory = EvidenceMemory()
    return _memory


if __name__ == "__main__":
    mem = get_memory()
    print(f"Loaded memory: {len(mem.paper_usage)} papers tracked, {len(mem.article_packs)} articles")
    diag = mem.get_diagnostics(["12345678", "99999999"], "msk_outcomes")
    print(f"Sample diagnostics: {diag}")
