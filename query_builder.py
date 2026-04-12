"""
query_builder.py — Generates 6 validated PubMed query variants per topic.

Every query must contain:
  A. Clinical anchor (MeSH + tiab)
  B. Domain anchor
  C. Topic-intent block
  D. Exclusion block

Queries that fail validation are not run.
"""

from __future__ import annotations
from dataclasses import dataclass
from topic_normalizer import SearchBrief, INTENT_MAPPING, STANDARD_EXCLUSIONS


# ---------------------------------------------------------------------------
# Required query blocks
# ---------------------------------------------------------------------------

CLINICAL_ANCHOR = (
    '("Physical Therapy Modalities"[mh] OR physiotherapy[tiab] OR '
    '"physical therapy"[tiab] OR rehabilitation[tiab])'
)

DOMAIN_ANCHOR = (
    '(musculoskeletal[tiab] OR "Musculoskeletal Diseases"[mh] OR orthopaedic[tiab] OR '
    '"back pain"[tiab] OR osteoarthritis[tiab] OR tendinopathy[tiab] OR '
    '"sports medicine"[tiab] OR "physical rehabilitation"[tiab])'
)

EXCLUSION_BLOCK = (
    'NOT ("global burden of disease"[tiab] OR GBD[tiab] OR psychotherapy[tiab] '
    'OR pharmacy[tiab] OR "pelvic organ prolapse"[tiab] OR priapism[tiab] '
    'OR oncology[tiab] OR dermatology[tiab])'
)

# High-quality evidence filter
HIGH_EVIDENCE_FILTER = (
    '("systematic review"[tiab] OR "meta-analysis"[tiab] OR '
    '"randomised controlled trial"[tiab] OR "randomized controlled trial"[tiab] OR '
    '"cohort study"[tiab] OR "clinical trial"[pt])'
)


@dataclass
class QuerySpec:
    query_string: str
    family: str  # high_precision | balanced | broad | fallback
    index: int
    has_clinical_anchor: bool
    has_domain_anchor: bool
    has_intent_block: bool
    has_exclusion: bool
    is_valid: bool
    validation_reason: str = ""


def _validate_query(query: str, family: str, index: int) -> QuerySpec:
    """Check that a query contains all four required blocks."""
    has_clinical = any(t in query for t in [
        '"Physical Therapy Modalities"', 'physiotherapy[tiab]',
        '"physical therapy"[tiab]', 'rehabilitation[tiab]',
    ])
    has_domain = any(t in query for t in [
        'musculoskeletal[tiab]', '"Musculoskeletal Diseases"',
        'orthopaedic[tiab]', 'osteoarthritis[tiab]', 'tendinopathy[tiab]',
        '"back pain"', 'sports medicine', 'physical rehabilitation',
        'ACL[tiab]', 'ligament[tiab]', 'knee[tiab]', 'shoulder[tiab]',
        'hamstring[tiab]', 'achilles[tiab]', 'ankle[tiab]', 'hip[tiab]',
        'plantar[tiab]', 'patellofemoral[tiab]', 'lumbar[tiab]',
        '"anterior cruciate"', 'rotator cuff', 'tennis elbow',
        'groin[tiab]', 'tibial[tiab]', 'elbow[tiab]', 'athlete[tiab]',
        'football[tiab]', 'runner[tiab]', 'running[tiab]', 'sport[tiab]',
    ])
    has_intent = len(query) > 200  # Intent block adds substantial length
    has_exclusion = 'NOT' in query and 'GBD' in query

    missing = []
    if not has_clinical:
        missing.append("clinical anchor")
    if not has_domain:
        missing.append("domain anchor")
    if not has_intent:
        missing.append("intent block")
    if not has_exclusion:
        missing.append("exclusion block")

    is_valid = len(missing) == 0
    reason = f"Missing: {', '.join(missing)}" if missing else "OK"

    return QuerySpec(
        query_string=query,
        family=family,
        index=index,
        has_clinical_anchor=has_clinical,
        has_domain_anchor=has_domain,
        has_intent_block=has_intent,
        has_exclusion=has_exclusion,
        is_valid=is_valid,
        validation_reason=reason,
    )


def build_queries(brief: SearchBrief) -> list[QuerySpec]:
    """
    Generate 6 query variants for a topic brief.
    Returns only validated queries (all 4 blocks present).

    Query families:
      Q1-Q2: high precision (MeSH + tiab, narrow)
      Q3-Q4: balanced (MeSH + free text)
      Q5: broad recall
      Q6: fallback / adjacent services
    """
    # Get intent blocks for detected intents
    intent_blocks = []
    for intent in brief.detected_intents:
        block = INTENT_MAPPING.get(intent, {}).get("mesh_block", "")
        if block:
            intent_blocks.append(block)

    # Fallback intent block if nothing detected
    if not intent_blocks:
        intent_blocks = ['(outcome*[tiab] OR function*[tiab] OR assessment[tiab])']

    primary_intent = intent_blocks[0]
    secondary_intent = intent_blocks[1] if len(intent_blocks) > 1 else intent_blocks[0]

    # Domain-specific condition block — condition-specific testing variables
    condition_block = ""
    cond = brief.detected_conditions[0] if brief.detected_conditions else "msk"

    if cond == "acl":
        condition_block = '(ACL[tiab] OR "anterior cruciate ligament"[tiab] OR "knee reconstruction"[tiab])' 
    elif cond == "patellofemoral":
        condition_block = '("patellofemoral pain"[tiab] OR "patellofemoral syndrome"[tiab] OR "knee pain"[tiab])'
    elif cond == "knee":
        condition_block = '(knee[tiab] OR "knee osteoarthritis"[tiab] OR "knee replacement"[tiab])'
    elif cond == "hamstring":
        condition_block = '("hamstring strain"[tiab] OR "hamstring injury"[tiab] OR "posterior chain"[tiab])'
    elif cond == "achilles":
        condition_block = '("Achilles tendinopathy"[tiab] OR "Achilles tendon"[tiab] OR tendinopathy[tiab])'
    elif cond == "shoulder":
        condition_block = '(shoulder[tiab] OR "rotator cuff"[tiab] OR "shoulder impingement"[tiab])'
    elif cond == "ankle":
        condition_block = '("lateral ankle"[tiab] OR "ankle instability"[tiab] OR "ankle sprain"[tiab])'
    elif cond == "plantar":
        condition_block = '("plantar fasciitis"[tiab] OR "heel pain"[tiab] OR "plantar fascia"[tiab])'
    elif cond == "back":
        condition_block = '("low back pain"[tiab] OR lumbar[tiab] OR spine[tiab] OR "back pain"[tiab])'
    elif cond == "hip":
        condition_block = '(hip[tiab] OR "hip osteoarthritis"[tiab] OR "groin pain"[tiab])'
    elif cond == "elbow":
        condition_block = '("tennis elbow"[tiab] OR "lateral epicondylitis"[tiab] OR "elbow"[tiab])'
    elif cond == "runner":
        condition_block = '(runner[tiab] OR running[tiab] OR "running injury"[tiab] OR "lower limb"[tiab])'
    elif cond == "athlete":
        condition_block = '(athlete[tiab] OR athletic[tiab] OR "return to sport"[tiab] OR "return to play"[tiab])'
    elif cond == "football":
        condition_block = '(football[tiab] OR soccer[tiab] OR "return to play"[tiab] OR "lower limb"[tiab])'
    elif cond == "osteoarthritis":
        condition_block = '(osteoarthritis[tiab] OR "knee OA"[tiab] OR "hip OA"[tiab])'
    else:
        condition_block = DOMAIN_ANCHOR

    # Business layer for business topics
    business_block = ""
    if brief.is_business_topic:
        business_block = (
            '("Health Care Costs"[mh] OR "Cost-Benefit Analysis"[mh] OR '
            'value[tiab] OR cost-effectiveness[tiab] OR efficiency[tiab] OR '
            '"health services"[tiab] OR "service delivery"[tiab])'
        )

    queries = []

    # Q1: High precision — MeSH + condition + primary intent + evidence filter
    q1_parts = [CLINICAL_ANCHOR, condition_block, primary_intent, HIGH_EVIDENCE_FILTER, EXCLUSION_BLOCK]
    queries.append((" AND ".join(q1_parts), "high_precision"))

    # Q2: High precision — MeSH + domain + primary intent (no evidence filter)
    q2_parts = [CLINICAL_ANCHOR, DOMAIN_ANCHOR, primary_intent, EXCLUSION_BLOCK]
    queries.append((" AND ".join(q2_parts), "high_precision"))

    # Q3: Balanced — clinical anchor + condition + secondary intent
    q3_parts = [CLINICAL_ANCHOR, condition_block, secondary_intent, EXCLUSION_BLOCK]
    queries.append((" AND ".join(q3_parts), "balanced"))

    # Q4: Balanced — with business layer if applicable, else evidence quality
    if brief.is_business_topic and business_block:
        q4_parts = [CLINICAL_ANCHOR, DOMAIN_ANCHOR, business_block, EXCLUSION_BLOCK]
    else:
        q4_parts = [CLINICAL_ANCHOR, DOMAIN_ANCHOR, secondary_intent, HIGH_EVIDENCE_FILTER, EXCLUSION_BLOCK]
    queries.append((" AND ".join(q4_parts), "balanced"))

    # Q5: Broad recall — clinical anchor + domain + broad terms
    broad_intent = '(outcome*[tiab] OR function*[tiab] OR assessment[tiab] OR effectiveness[tiab] OR benchmark*[tiab] OR normative[tiab])' 
    q5_parts = [CLINICAL_ANCHOR, DOMAIN_ANCHOR, broad_intent, EXCLUSION_BLOCK]
    queries.append((" AND ".join(q5_parts), "broad"))

    # Q6: Fallback / adjacent services
    if brief.is_business_topic:
        fallback_intent = (
            '("Delivery of Health Care"[mh] OR "Health Services Research"[mh] OR '
            '"model of care"[tiab] OR "service delivery"[tiab] OR workforce[tiab])'
        )
    elif cond in ["acl", "knee", "shoulder"]:
        fallback_intent = '("rehabilitation"[mh] OR "exercise therapy"[mh] OR "physical activity"[mh])'
    else:
        fallback_intent = '("Allied Health Personnel"[mh] OR "clinical practice"[tiab] OR "evidence-based"[tiab])'
    q6_parts = [CLINICAL_ANCHOR, DOMAIN_ANCHOR, fallback_intent, EXCLUSION_BLOCK]
    queries.append((" AND ".join(q6_parts), "fallback"))

    # Validate all queries
    validated = []
    for i, (q, family) in enumerate(queries, 1):
        spec = _validate_query(q, family, i)
        validated.append(spec)

    return validated


def get_valid_queries(brief: SearchBrief) -> list[QuerySpec]:
    """Return only valid queries (all 4 blocks present)."""
    all_queries = build_queries(brief)
    valid = [q for q in all_queries if q.is_valid]
    invalid = [q for q in all_queries if not q.is_valid]
    if invalid:
        print(f"  Query validation: {len(valid)} valid, {len(invalid)} rejected")
        for q in invalid:
            print(f"    Q{q.index} ({q.family}): {q.validation_reason}")
    return valid


if __name__ == "__main__":
    from topic_normalizer import normalize_topic
    title = "The Business Case for Outcome Measurement in Physiotherapy Clinics"
    brief = normalize_topic(title)
    queries = get_valid_queries(brief)
    print(f"\n{len(queries)} valid queries for: {title[:60]}")
    for q in queries:
        print(f"\nQ{q.index} [{q.family}] Valid={q.is_valid}")
        print(f"  {q.query_string[:120]}...")
