"""
query_builder.py — Generates compact PubMed retrieval queries.

Architecture:
  RETRIEVAL layer (this file): short, candidate-generating, no NOT blocks
  RANKING layer (paper_ranker.py): strict filtering, penalties, exclusions

Key rule: Do NOT put NOT/exclusion logic in retrieval queries.
PubMed's URL encoding corrupts NOT operators, silently returning 0 results.
Exclusion is handled downstream by the ranker's domain penalty system.

Each topic gets 5 compact queries:
  Q1-Q2: high precision (condition + intent, with evidence filter)
  Q3-Q4: balanced (condition + intent, no evidence filter)
  Q5: broad recall (clinical anchor + condition only)
"""

from __future__ import annotations
from dataclasses import dataclass
from topic_normalizer import SearchBrief, INTENT_MAPPING


# ---------------------------------------------------------------------------
# Core blocks — kept short
# ---------------------------------------------------------------------------

# Short clinical anchor — just the most common terms
CLINICAL_ANCHOR = (
    '(physiotherapy[tiab] OR "physical therapy"[tiab] OR rehabilitation[tiab])'
)

# Short domain anchor
DOMAIN_ANCHOR = (
    '(musculoskeletal[tiab] OR orthopaedic[tiab] OR "sports medicine"[tiab] OR rehabilitation[tiab])'
)

# High-quality evidence filter (short version)
HIGH_EVIDENCE = (
    '("systematic review"[tiab] OR "meta-analysis"[tiab] OR "randomised controlled trial"[tiab] OR "randomized controlled trial"[tiab] OR "clinical trial"[pt])'
)


# ---------------------------------------------------------------------------
# Condition-specific domain blocks — compact, single condition
# ---------------------------------------------------------------------------

CONDITION_BLOCKS = {
    "acl":          '(ACL[tiab] OR "anterior cruciate ligament"[tiab])',
    "patellofemoral": '("patellofemoral pain"[tiab] OR "patellofemoral syndrome"[tiab])',
    "knee":         '(knee[tiab] OR "knee osteoarthritis"[tiab])',
    "hamstring":    '("hamstring strain"[tiab] OR "hamstring injury"[tiab])',
    "achilles":     '("Achilles tendinopathy"[tiab] OR "Achilles tendon"[tiab])',
    "shoulder":     '(shoulder[tiab] OR "rotator cuff"[tiab])',
    "ankle":        '("ankle instability"[tiab] OR "ankle sprain"[tiab] OR ankle[tiab])',
    "plantar":      '("plantar fasciitis"[tiab] OR "heel pain"[tiab])',
    "back":         '("low back pain"[tiab] OR lumbar[tiab] OR "back pain"[tiab])',
    "hip":          '(hip[tiab] OR "hip osteoarthritis"[tiab])',
    "elbow":        '("tennis elbow"[tiab] OR "lateral epicondylitis"[tiab])',
    "runner":       '(runner[tiab] OR running[tiab] OR "running injury"[tiab])',
    "athlete":      '(athlete[tiab] OR athletic[tiab] OR "return to sport"[tiab])',
    "football":     '(football[tiab] OR soccer[tiab] OR "return to play"[tiab])',
    "osteoarthritis": '(osteoarthritis[tiab] OR "knee OA"[tiab])',
    "msk":          DOMAIN_ANCHOR,
    "conservative": '("conservative care"[tiab] OR "non-surgical"[tiab] OR physiotherapy[tiab])',
}


# ---------------------------------------------------------------------------
# Intent blocks — compact
# ---------------------------------------------------------------------------

INTENT_BLOCKS = {
    "outcome measurement":     '(outcome measure*[tiab] OR PROM*[tiab] OR "functional outcome"[tiab])',
    "discharge criteria":      '("return to sport"[tiab] OR "return to play"[tiab] OR criteria[tiab] OR discharge[tiab])',
    "return to sport":         '("return to sport"[tiab] OR "return to play"[tiab] OR criteria[tiab])',
    "testing methodology":     '(dynamometry[tiab] OR "hop test"[tiab] OR "limb symmetry"[tiab] OR reliability[tiab])',
    "adherence":               '(adherence[tiab] OR compliance[tiab] OR retention[tiab])',
    "staffing":                '(staffing[tiab] OR workforce[tiab] OR "skill mix"[tiab])',
    "value":                   '(cost[tiab] OR value[tiab] OR "cost-effectiveness"[tiab] OR efficiency[tiab])',
    "technology":              '(telehealth[tiab] OR digital[tiab] OR smartphone[tiab] OR wearable*[tiab])',
    "progression":             '(progression[tiab] OR "criteria-based"[tiab] OR "treatment protocol"[tiab])',
    "conservative care":       '("conservative care"[tiab] OR "non-surgical"[tiab] OR "conservative treatment"[tiab])',
    "clinical decision":       '("clinical decision"[tiab] OR "clinical reasoning"[tiab] OR criteria[tiab])',
    "low tech implementation": '(dynamometry[tiab] OR "field test"[tiab] OR "handheld"[tiab] OR implementation[tiab])',
}


@dataclass
class QuerySpec:
    query_string: str
    family: str
    index: int
    is_valid: bool = True
    validation_reason: str = "OK"


def build_queries(brief: SearchBrief) -> list[QuerySpec]:
    """
    Generate 5 compact retrieval queries.
    No NOT blocks. No complex multi-layer structures.
    Exclusion is handled by the ranker.
    """
    # Get condition block
    cond = brief.detected_conditions[0] if brief.detected_conditions else "msk"
    cond_block = CONDITION_BLOCKS.get(cond, DOMAIN_ANCHOR)

    # Get primary and secondary intent blocks
    primary_intent_key = brief.detected_intents[0] if brief.detected_intents else "outcome measurement"
    secondary_intent_key = brief.detected_intents[1] if len(brief.detected_intents) > 1 else primary_intent_key

    primary_intent = INTENT_BLOCKS.get(primary_intent_key, '(outcome*[tiab] OR function*[tiab])')
    secondary_intent = INTENT_BLOCKS.get(secondary_intent_key, '(assessment[tiab] OR measure*[tiab])')

    queries = []

    # Q1: High precision — condition + primary intent + evidence filter
    q1 = f"{CLINICAL_ANCHOR} AND {cond_block} AND {primary_intent} AND {HIGH_EVIDENCE}"
    queries.append(QuerySpec(q1, "high_precision", 1))

    # Q2: High precision — condition + primary intent (no evidence filter)
    q2 = f"{CLINICAL_ANCHOR} AND {cond_block} AND {primary_intent}"
    queries.append(QuerySpec(q2, "high_precision", 2))

    # Q3: Balanced — condition + secondary intent
    q3 = f"{CLINICAL_ANCHOR} AND {cond_block} AND {secondary_intent}"
    queries.append(QuerySpec(q3, "balanced", 3))

    # Q4: Balanced — domain + primary intent (broader condition)
    q4 = f"{CLINICAL_ANCHOR} AND {DOMAIN_ANCHOR} AND {primary_intent}"
    queries.append(QuerySpec(q4, "balanced", 4))

    # Q5: Broad recall — clinical anchor + condition only
    q5 = f"{CLINICAL_ANCHOR} AND {cond_block}"
    queries.append(QuerySpec(q5, "broad", 5))

    return queries


def get_valid_queries(brief: SearchBrief) -> list[QuerySpec]:
    """Return all queries (all are valid — no NOT blocks to fail)."""
    queries = build_queries(brief)
    # Log lengths for diagnostics
    for q in queries:
        if len(q.query_string) > 400:
            print(f"    WARNING: Q{q.index} is {len(q.query_string)} chars — consider shortening")
    return queries


if __name__ == "__main__":
    from topic_normalizer import normalize_topic
    import urllib.parse

    topics = [
        "ACL Return-to-Sport Testing: Which Criteria Actually Predict Re-Injury Risk",
        "Knee Osteoarthritis and Conservative Care: Setting Realistic Expectations",
        "The Business Case for Outcome Measurement in Physiotherapy Clinics",
    ]

    for title in topics:
        brief = normalize_topic(title)
        queries = get_valid_queries(brief)
        print(f"\n{title[:65]}")
        for q in queries:
            encoded_len = len(urllib.parse.quote(q.query_string))
            print(f"  Q{q.index} [{q.family}] raw={len(q.query_string)} encoded={encoded_len}")
            print(f"    {q.query_string[:80]}...")
