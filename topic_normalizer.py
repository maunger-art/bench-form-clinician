"""
topic_normalizer.py — Converts article titles into structured search briefs.

Translates business-framed titles into clinical/search language before query
generation. Produces structured concepts used by query_builder.py.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Business-to-clinical translation map
# ---------------------------------------------------------------------------

BUSINESS_TO_CLINICAL = {
    "business case": ["outcome assessment", "PROMs", "value", "efficiency"],
    "margins": ["cost effectiveness", "resource use", "health economics"],
    "staffing mix": ["workforce", "skill mix", "personnel staffing"],
    "revenue": ["cost effectiveness", "service utilisation"],
    "pricing": ["value-based care", "cost effectiveness"],
    "charge more": ["value-based care", "outcome measurement"],
    "hidden cost": ["cost effectiveness", "resource utilisation", "efficiency"],
    "economic case": ["cost effectiveness", "health economics", "MSK burden"],
    "standardised care": ["clinical guidelines", "protocol adherence", "standardisation"],
    "senior clinician dependency": ["skill mix", "workforce delegation", "task shifting"],
}

# Condition-specific term enrichment — maps conditions to testing variables
# Sources: JOSPT, BJSM, PTJ, JSCR, sports science literature
CONDITION_TERMS = {
    "acl": [
        "anterior cruciate ligament", "ACL reconstruction", "knee", "return to sport",
        "quadriceps strength", "hamstring strength", "quad hamstring ratio",
        "limb symmetry index", "single leg hop", "triple hop", "crossover hop",
        "countermovement jump", "timed hop", "return to play",
    ],
    "knee": [
        "knee", "osteoarthritis", "patellofemoral", "musculoskeletal",
        "knee extensor strength", "quadriceps", "sit to stand", "stair function",
        "KOOS", "WOMAC", "walking speed", "load tolerance",
    ],
    "patellofemoral": [
        "patellofemoral pain", "patellofemoral syndrome", "knee", "running",
        "quadriceps strength", "hip abductor", "hip external rotator",
        "single leg squat", "step down", "hop performance",
    ],
    "hamstring": [
        "hamstring strain", "hamstring injury", "posterior chain",
        "eccentric hamstring strength", "nordic hamstring", "sprint readiness",
        "posterior chain asymmetry", "single leg bridge",
    ],
    "achilles": [
        "Achilles tendinopathy", "Achilles tendon", "tendinopathy",
        "single leg calf raise", "isometric plantarflexion", "calf strength",
        "VISA-A", "hop tolerance", "ankle dorsiflexion",
    ],
    "shoulder": [
        "shoulder", "rotator cuff", "shoulder impingement", "musculoskeletal",
        "external rotation strength", "internal rotation strength",
        "abduction strength", "range of motion", "SPADI", "QuickDASH",
        "scapular control",
    ],
    "ankle": [
        "ankle", "lateral ankle instability", "ankle sprain", "musculoskeletal",
        "hop test", "dynamic balance", "calf strength", "inversion strength",
        "eversion strength", "star excursion balance",
    ],
    "back": [
        "low back pain", "lumbar", "spine", "musculoskeletal",
        "trunk endurance", "disability score", "risk stratification",
        "fear avoidance", "repeated movement", "STarT Back", "Oswestry",
    ],
    "hip": [
        "hip", "hip osteoarthritis", "femoroacetabular", "musculoskeletal",
        "hip strength", "adductor strength", "hip abductor", "sit to stand",
        "Copenhagen", "groin pain",
    ],
    "plantar": [
        "plantar fasciitis", "heel pain", "plantar fascia",
        "calf endurance", "single leg calf raise", "load tolerance",
        "walking tolerance", "morning pain",
    ],
    "elbow": [
        "tennis elbow", "lateral epicondylitis", "elbow", "upper limb",
        "grip strength", "pain free grip", "DASH", "PRTEE",
    ],
    "tendon": ["tendinopathy", "tendon", "musculoskeletal", "load tolerance"],
    "osteoarthritis": ["osteoarthritis", "musculoskeletal", "conservative care", "function"],
    "runner": [
        "runner", "running", "running injury", "lower limb capacity",
        "single leg hop", "calf strength", "tibial stress", "load monitoring",
    ],
    "athlete": [
        "athlete", "athletic", "sports rehabilitation", "return to sport",
        "return to play", "field test", "performance testing",
    ],
    "football": [
        "football", "soccer", "return to play", "sprint readiness",
        "adductor strength", "hamstring", "lower limb capacity",
    ],
    "msk": ["musculoskeletal", "rehabilitation", "physiotherapy"],
    "conservative": ["conservative care", "non-surgical", "physiotherapy"],
}

# Intent-to-search mapping
INTENT_MAPPING = {
    "outcome measurement": {
        "intent_terms": [
            "outcome measure", "PROM", "functional outcome", "benchmarking",
            "clinical outcome", "patient reported outcome", "outcome assessment",
            "standardised measure", "standardized measure", "routine outcome",
            "outcome monitoring", "treatment outcome", "rehabilitation outcome",
        ],
        "mesh_block": '("Outcome Assessment, Health Care"[mh] OR outcome measure*[tiab] OR PROM*[tiab] OR functional outcome*[tiab])',
    },
    "adherence": {
        "intent_terms": ["adherence", "compliance", "retention", "dropout"],
        "mesh_block": '("Patient Compliance"[mh] OR adherence[tiab] OR attendance[tiab] OR retention[tiab] OR dropout[tiab])',
    },
    "staffing": {
        "intent_terms": ["staffing", "workforce", "skill mix", "delegation"],
        "mesh_block": '("Personnel Staffing and Scheduling"[mh] OR staffing[tiab] OR workforce[tiab] OR "skill mix"[tiab] OR task shifting[tiab])',
    },
    "value": {
        "intent_terms": ["cost effectiveness", "value", "efficiency", "economics"],
        "mesh_block": '("Health Care Costs"[mh] OR "Cost-Benefit Analysis"[mh] OR value[tiab] OR cost-effectiveness[tiab] OR efficiency[tiab])',
    },
    "technology": {
        "intent_terms": ["telehealth", "digital health", "mHealth", "wearable"],
        "mesh_block": '("Telemedicine"[mh] OR telehealth[tiab] OR digital health[tiab] OR mHealth[tiab] OR wearable*[tiab])',
    },
    "progression": {
        "intent_terms": ["progression", "treatment protocol", "clinical decision", "exercise"],
        "mesh_block": '(progression[tiab] OR "treatment protocol"[tiab] OR "clinical decision"[tiab] OR "exercise therapy"[mh])',
    },
    "conservative care": {
        "intent_terms": ["conservative treatment", "non-surgical", "rehabilitation", "physiotherapy"],
        "mesh_block": '(conservative[tiab] OR "non-surgical"[tiab] OR "Physical Therapy Modalities"[mh] OR rehabilitation[tiab])',
    },
    "return to sport": {
        "intent_terms": [
            "return to sport", "return to play", "sport rehabilitation", "athletic",
            "anterior cruciate ligament", "acl reconstruction", "acl rehabilitation",
            "functional testing", "hop test", "strength testing", "criteria",
            "re-injury", "reinjury", "second acl", "sport clearance",
        ],
        "mesh_block": '("return to sport"[tiab] OR "return to play"[tiab] OR "anterior cruciate ligament"[tiab] OR "ACL"[tiab])',
    },
    "clinical decision": {
        "intent_terms": ["clinical decision", "clinical reasoning", "assessment", "diagnosis"],
        "mesh_block": '("clinical decision"[tiab] OR "clinical reasoning"[tiab] OR "Clinical Decision-Making"[mh])',
    },
    "testing methodology": {
        "intent_terms": [
            "handheld dynamometry", "isometric testing", "hop test", "limb symmetry index",
            "grip strength", "reliability", "validity", "MCID", "MDC", "inter-rater",
            "outcome measure", "PROM", "range of motion", "between-session",
        ],
        "mesh_block": '("handheld dynamometry"[tiab] OR "isometric testing"[tiab] OR "hop test"[tiab] OR "limb symmetry"[tiab] OR reliability[tiab] OR validity[tiab] OR MCID[tiab])',
    },
    "discharge criteria": {
        "intent_terms": [
            "discharge criteria", "return to sport", "return to play", "progression criteria",
            "criteria based", "objective criteria", "benchmark threshold", "clearance",
        ],
        "mesh_block": '("discharge"[tiab] OR "return to sport"[tiab] OR "return to play"[tiab] OR criteria[tiab] OR benchmark*[tiab])',
    },
    "low tech implementation": {
        "intent_terms": [
            "handheld dynamometry", "field test", "bodyweight test", "smartphone",
            "low cost", "without equipment", "clinical setting", "implementation",
        ],
        "mesh_block": '("handheld dynamometry"[tiab] OR "field test"[tiab] OR smartphone[tiab] OR "low-cost"[tiab] OR feasibility[tiab])',
    },
}

# Standard exclusions for all queries
STANDARD_EXCLUSIONS = [
    '"global burden of disease"[tiab]',
    'GBD[tiab]',
    'psychotherapy[tiab]',
    'pharmacy[tiab]',
    '"pelvic organ prolapse"[tiab]',
    'oncology[tiab]',
    'dermatology[tiab]',
    'ophthalmology[tiab]',
    'priapism[tiab]',
]


@dataclass
class SearchBrief:
    title: str
    primary_domain: str
    population_terms: list[str]
    intent_terms: list[str]
    business_terms: list[str]
    must_have_terms: list[str]
    nice_to_have_terms: list[str]
    exclude_terms: list[str]
    required_evidence_types: list[str]
    claim_clusters: list[str]
    is_business_topic: bool
    detected_intents: list[str]
    detected_conditions: list[str]
    clinical_translations: list[str]


def _detect_intents(title_lower: str) -> list[str]:
    intents = []
    # Testing methodology
    if any(t in title_lower for t in ["dynamometry", "hop test", "limb symmetry", "grip strength",
            "reliability", "validity", "mcid", "mdc", "inter-rater", "prom", "range of motion",
            "isometric testing", "between-session"]):
        intents.append("testing methodology")
    # Outcome measurement
    if any(t in title_lower for t in ["outcome", "measure", "benchmark", "assess", "threshold",
            "marker", "benchmark", "normative", "what to measure"]):
        intents.append("outcome measurement")
    # Discharge / return to sport criteria
    if any(t in title_lower for t in ["discharge", "return to sport", "return to play",
            "criteria", "clearance", "progression criteria", "return to run"]):
        intents.append("discharge criteria")
    # Low-tech implementation
    if any(t in title_lower for t in ["without expensive", "low cost", "field test",
            "smartphone", "bodyweight", "stopwatch", "replac"]):
        intents.append("low tech implementation")
    # Adherence
    if any(t in title_lower for t in ["adhere", "dropout", "retain", "engagement", "compli"]):
        intents.append("adherence")
    # Staffing
    if any(t in title_lower for t in ["staffing", "workforce", "margins", "senior clinician", "skill mix"]):
        intents.append("staffing")
    # Value / economics
    if any(t in title_lower for t in ["economic", "cost", "value", "business case", "pricing",
            "payer", "insurer", "variation", "defensible"]):
        intents.append("value")
    # Technology
    if any(t in title_lower for t in ["technology", "digital", "telehealth", "app", "wearable", "remote"]):
        intents.append("technology")
    # Progression / frameworks
    if any(t in title_lower for t in ["progress", "framework", "criteria-based", "time-based"]):
        intents.append("progression")
    # Conservative care
    if any(t in title_lower for t in ["conservative", "non-surgical", "non surgical"]):
        intents.append("conservative care")
    # Return to sport / sport-specific
    if any(t in title_lower for t in ["return to sport", "return to play", "acl", "sport",
            "athlete", "football", "rugby", "runner", "cyclist"]):
        intents.append("return to sport")
    # Clinical decision
    if any(t in title_lower for t in ["decision making", "clinical decision", "reasoning",
            "plateau", "referral", "when to"]):
        intents.append("clinical decision")
    return intents if intents else ["outcome measurement"]  # default


def _detect_conditions(title_lower: str) -> list[str]:
    found = []
    for key in CONDITION_TERMS:
        if key in title_lower:
            found.append(key)
    if not found:
        found.append("msk")
    return found


def _is_business_topic(title_lower: str) -> bool:
    business_signals = [
        "business case", "margins", "staffing mix", "revenue", "pricing",
        "charge more", "hidden cost", "economic case", "standardised care",
        "senior clinician dependency", "cost", "economic", "value-based",
    ]
    return any(s in title_lower for s in business_signals)


def normalize_topic(title: str) -> SearchBrief:
    """Convert an article title into a structured search brief."""
    title_lower = title.lower()

    is_business = _is_business_topic(title_lower)
    intents = _detect_intents(title_lower)
    conditions = _detect_conditions(title_lower)

    # Build clinical translations for business terms
    clinical_translations = []
    for biz_term, clinical_terms in BUSINESS_TO_CLINICAL.items():
        if biz_term in title_lower:
            clinical_translations.extend(clinical_terms)

    # Population terms
    population_terms = ["physiotherapy", "rehabilitation", "musculoskeletal"]
    for cond in conditions:
        population_terms.extend(CONDITION_TERMS.get(cond, []))
    population_terms = list(dict.fromkeys(population_terms))[:6]

    # Intent terms
    intent_terms = []
    for intent in intents:
        intent_terms.extend(INTENT_MAPPING.get(intent, {}).get("intent_terms", []))
    if clinical_translations:
        intent_terms.extend(clinical_translations)
    intent_terms = list(dict.fromkeys(intent_terms))[:8]

    # Must-have terms
    must_have = ["physiotherapy OR rehabilitation"]
    if conditions and conditions[0] != "msk":
        must_have.append(conditions[0])
    if intents:
        primary_intent = INTENT_MAPPING.get(intents[0], {})
        if primary_intent.get("intent_terms"):
            must_have.append(" OR ".join(primary_intent["intent_terms"][:3]))
    must_have = must_have[:4]

    # Nice-to-have terms from clinical translations
    nice_to_have = clinical_translations[:4] if clinical_translations else intent_terms[2:5]

    # Exclude terms
    exclude_terms = ["GBD", "global burden of disease", "psychotherapy", "pharmacy"]
    if "acl" not in title_lower and "knee" not in title_lower:
        exclude_terms.append("urogynecology")

    # Evidence types
    evidence_types = ["systematic review", "randomised controlled trial", "cohort study"]
    if is_business:
        evidence_types.append("health economic evaluation")
        evidence_types.append("implementation study")

    # Claim clusters - what the article will likely argue
    claim_clusters = []
    for intent in intents[:3]:
        if intent == "outcome measurement":
            claim_clusters.append("outcome measurement improves clinical decisions")
            claim_clusters.append("standardised measurement leads to better patient outcomes")
        elif intent == "adherence":
            claim_clusters.append("measurement improves patient retention and engagement")
        elif intent == "staffing":
            claim_clusters.append("standardised care enables better workforce utilisation")
        elif intent == "value":
            claim_clusters.append("outcome measurement demonstrates clinical value and cost effectiveness")
        elif intent == "return to sport":
            claim_clusters.append("objective criteria predict return to sport outcomes")
            claim_clusters.append("evidence-based criteria reduce re-injury risk")

    # Primary domain
    if is_business:
        primary_domain = "musculoskeletal rehabilitation health services"
    elif "acl" in title_lower or "return to sport" in title_lower:
        primary_domain = "sports rehabilitation"
    elif "osteoarthritis" in title_lower or "conservative" in title_lower:
        primary_domain = "musculoskeletal conservative care"
    else:
        primary_domain = "musculoskeletal rehabilitation"

    # Enrich with protocol library terms if available
    try:
        from protocol_knowledge import PROTOCOL_LIBRARY
        for test in PROTOCOL_LIBRARY:
            if test.test_name.lower() in title_lower or test.body_region.lower() in title_lower:
                intent_terms.extend(test.pubmed_search_terms)
                if test.conditions:
                    conditions = list(set(conditions + [test.body_region.lower().replace(' ', '_')]))
                break
        intent_terms = list(dict.fromkeys(intent_terms))[:10]
    except Exception:
        pass

    return SearchBrief(
        title=title,
        primary_domain=primary_domain,
        population_terms=population_terms,
        intent_terms=intent_terms,
        business_terms=clinical_translations if is_business else [],
        must_have_terms=must_have,
        nice_to_have_terms=nice_to_have,
        exclude_terms=exclude_terms,
        required_evidence_types=evidence_types,
        claim_clusters=claim_clusters,
        is_business_topic=is_business,
        detected_intents=intents,
        detected_conditions=conditions,
        clinical_translations=clinical_translations,
    )


if __name__ == "__main__":
    import json
    from dataclasses import asdict
    titles = [
        "The Business Case for Outcome Measurement in Physiotherapy Clinics",
        "ACL Return-to-Sport Testing: Which Criteria Actually Predict Re-Injury",
        "Staffing Mix and Physiotherapy Margins: How Standardised Care Reduces Senior Clinician Dependency",
        "MSK Outcome Benchmarks: What Good Conservative Care Actually Looks Like",
    ]
    for t in titles:
        brief = normalize_topic(t)
        print(f"\nTitle: {t[:70]}")
        print(f"  Domain: {brief.primary_domain}")
        print(f"  Business: {brief.is_business_topic}")
        print(f"  Intents: {brief.detected_intents}")
        print(f"  Conditions: {brief.detected_conditions}")
        print(f"  Must-have: {brief.must_have_terms}")
        print(f"  Claim clusters: {brief.claim_clusters[:2]}")
