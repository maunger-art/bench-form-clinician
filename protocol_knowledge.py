"""
protocol_knowledge.py — Benchmark PS protocol knowledge system.

This module is the spine of the content engine. It:
  1. Holds the structured test library (55 tests from the platform)
  2. Provides condition-to-test and test-to-condition mappings
  3. Generates article topic ideas from any test or condition
  4. Defines the reveal boundary (public vs proprietary)
  5. Provides PubMed search terms per test for evidence retrieval

The system makes Benchmark PS synonymous with:
  "what to measure, and what it means"

REVEAL BOUNDARY:
  PUBLIC (blog content):
    - Test names and what they measure
    - Why a test matters clinically
    - When to use a test (decision points)
    - Conceptual interpretation (e.g. "more reps = better calf endurance")
    - Evidence references for the test methodology
    - General guidance on meaningful change

  PROPRIETARY (stays inside the platform):
    - Exact normative values by age/sex
    - Full scoring algorithms
    - Benchmark PS composite scores
    - Progression thresholds and cutoffs
    - Rate-of-change calculations
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Test data structures
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkTest:
    test_id: int
    test_name: str
    full_name: str
    body_region: str
    category: str          # strength | endurance | ROM | power
    unit: str
    technology_level: str  # low-tech | mid-tech | high-tech
    has_rate_of_change: bool
    admin_time_mins: float
    conditions: list[str]
    decision_points: list[str]
    populations: list[str]
    pubmed_search_terms: list[str]
    article_angles: list[str]
    evidence_refs: list[str]
    is_public: bool = True  # All tests are publicly nameable


# ---------------------------------------------------------------------------
# Full test library — built from benchmark_protocols.csv + Normative_data.xlsx
# ---------------------------------------------------------------------------

PROTOCOL_LIBRARY: list[BenchmarkTest] = [

    # ── ANKLE ──────────────────────────────────────────────────────────────
    BenchmarkTest(
        test_id=1, test_name="Plantarflexion strength", full_name="Ankle Strength Plantarflexion",
        body_region="Ankle", category="strength", unit="Newtons", technology_level="low-tech",
        has_rate_of_change=False, admin_time_mins=4.5,
        conditions=["Achilles tendinopathy", "calf strain", "ankle rehab", "plantar fasciitis"],
        decision_points=["baseline assessment", "progression", "discharge"],
        populations=["adult", "runner", "athlete"],
        pubmed_search_terms=["plantarflexion strength", "calf strength dynamometry", "ankle strength rehabilitation"],
        article_angles=["Plantarflexion Strength in Achilles Rehab: Why Newtons Matter More Than Symptoms",
                        "Measuring Calf Strength With a Dynamometer: What the Evidence Supports",
                        "Ankle Strength After Tendinopathy: How Much Recovery Is Enough?"],
        evidence_refs=["Moraux et al. (2013). Ankle dorsi- and plantar-flexion torques. BMC Musculoskeletal Disorders."],
    ),
    BenchmarkTest(
        test_id=2, test_name="Single leg calf raise", full_name="Ankle Endurance Single leg calf raise",
        body_region="Ankle", category="endurance", unit="Repetitions", technology_level="low-tech",
        has_rate_of_change=True, admin_time_mins=3.3,
        conditions=["Achilles tendinopathy", "calf strain", "return to running", "plantar fasciitis"],
        decision_points=["baseline assessment", "progression", "return to running", "monitoring over time"],
        populations=["runner", "adult", "recreational athlete"],
        pubmed_search_terms=["single leg calf raise test", "calf endurance Achilles", "heel raise repetitions rehabilitation"],
        article_angles=["Single-Leg Calf Raise: The Test That Tells You More Than Pain Alone",
                        "How Many Calf Raises Is Normal? Interpreting Endurance in Achilles Rehab",
                        "Single-Leg Calf Raise as a Return-to-Running Criterion",
                        "Why Calf Endurance Matters More Than Calf Strength in Tendinopathy"],
        evidence_refs=["Hebert-Losier et al. (2024). Effects of foot starting position on calf raise test outcomes. The Foot."],
    ),
    BenchmarkTest(
        test_id=3, test_name="Weight bearing lunge test", full_name="Ankle Range of movement Weight bearing lunge test",
        body_region="Ankle", category="ROM", unit="Degrees", technology_level="low-tech",
        has_rate_of_change=False, admin_time_mins=1.7,
        conditions=["ankle mobility deficit", "Achilles tendinopathy", "patellofemoral pain", "running assessment"],
        decision_points=["baseline assessment", "monitoring over time", "progression"],
        populations=["runner", "adult", "athlete"],
        pubmed_search_terms=["weight bearing lunge test dorsiflexion", "ankle dorsiflexion range of motion", "lunge test reliability"],
        article_angles=["Weight-Bearing Lunge Test: Why Dorsiflexion Range Affects More Than Just the Ankle",
                        "Ankle Mobility Assessment: What the Lunge Test Tells You in Under Two Minutes"],
        evidence_refs=["Hankemeier & Thrasher (2014). Weight-bearing lunge and dorsiflexion ROM. Athletic Training & Sports Health Care."],
    ),
    BenchmarkTest(
        test_id=4, test_name="Drop jump", full_name="Ankle Power Drop jump",
        body_region="Ankle", category="power", unit="RSI", technology_level="mid-tech",
        has_rate_of_change=False, admin_time_mins=2.5,
        conditions=["return to sport", "ACL rehab", "plyometric readiness", "lower limb power assessment"],
        decision_points=["return to sport", "plyometric readiness", "discharge"],
        populations=["athlete", "football", "rugby", "basketball"],
        pubmed_search_terms=["drop jump reactive strength index", "drop jump return to sport", "plyometric readiness assessment"],
        article_angles=["Drop Jump and Reactive Strength Index: What It Tells You About Sport Readiness",
                        "Plyometric Readiness After Injury: Why RSI Matters Before Return to Sport"],
        evidence_refs=["Wang & Peng (2014). Biomechanical comparisons of drop jumps. International Journal of Sports Medicine."],
    ),
    BenchmarkTest(
        test_id=5, test_name="Single leg drop jump", full_name="Ankle Power Single leg drop jump",
        body_region="Ankle", category="power", unit="RSI", technology_level="mid-tech",
        has_rate_of_change=False, admin_time_mins=2.5,
        conditions=["return to sport", "ACL rehab", "limb symmetry", "plyometric readiness"],
        decision_points=["return to sport", "plyometric readiness", "limb symmetry assessment"],
        populations=["athlete", "football", "rugby"],
        pubmed_search_terms=["single leg drop jump reactive strength", "limb symmetry RSI", "return to sport power testing"],
        article_angles=["Single-Leg Drop Jump: The Asymmetry Test Most Clinicians Skip",
                        "Return-to-Sport Power Testing: Why Single-Leg RSI Matters"],
        evidence_refs=["Wang & Peng (2014). Biomechanical comparisons of drop jumps. International Journal of Sports Medicine."],
    ),

    # ── CERVICAL SPINE ─────────────────────────────────────────────────────
    BenchmarkTest(
        test_id=6, test_name="Cervical flexion strength", full_name="Cervical spine Strength Flexion",
        body_region="Cervical spine", category="strength", unit="Newtons", technology_level="low-tech",
        has_rate_of_change=False, admin_time_mins=2.5,
        conditions=["neck pain", "cervical radiculopathy", "whiplash", "postural dysfunction"],
        decision_points=["baseline assessment", "progression", "return to work"],
        populations=["adult", "worker", "overhead athlete"],
        pubmed_search_terms=["cervical flexion strength dynamometry", "neck flexion force measurement", "cervical muscle strength rehabilitation"],
        article_angles=["Cervical Flexion Strength: What Handheld Dynamometry Tells You About Neck Pain",
                        "Measuring Neck Strength in Clinic: Evidence for Handheld Dynamometry"],
        evidence_refs=["Krause et al. (2019). Cervical muscle strength testing with handheld dynamometer. Sports Health."],
    ),
    BenchmarkTest(
        test_id=9, test_name="Deep neck flexor endurance test", full_name="Cervical spine Endurance Deep neck flexor endurance test",
        body_region="Cervical spine", category="endurance", unit="Seconds", technology_level="low-tech",
        has_rate_of_change=False, admin_time_mins=1.8,
        conditions=["neck pain", "cervical instability", "headache", "postural dysfunction"],
        decision_points=["baseline assessment", "progression", "monitoring over time"],
        populations=["adult", "worker", "screen user"],
        pubmed_search_terms=["deep neck flexor endurance test", "cranio-cervical flexion test", "neck stabiliser endurance"],
        article_angles=["Deep Neck Flexor Endurance: What the Test Reveals That Strength Testing Misses",
                        "Neck Pain and Postural Endurance: Why Duration Matters More Than Force"],
        evidence_refs=["Painkra et al. (2014). Deep neck flexor muscle endurance test reliability. International Journal of Therapy and Rehabilitation."],
    ),

    # ── ELBOW ──────────────────────────────────────────────────────────────
    BenchmarkTest(
        test_id=14, test_name="Elbow flexion strength", full_name="Elbow Strength Flexion",
        body_region="Elbow", category="strength", unit="Newtons", technology_level="low-tech",
        has_rate_of_change=False, admin_time_mins=3.0,
        conditions=["tennis elbow", "biceps tendinopathy", "upper limb rehab", "return to work"],
        decision_points=["baseline assessment", "progression", "discharge", "return to work"],
        populations=["adult", "manual worker", "overhead athlete"],
        pubmed_search_terms=["elbow flexion strength dynamometry", "bicep strength measurement rehabilitation", "upper limb isometric strength"],
        article_angles=["Elbow Flexion Strength in Rehab: What the Numbers Tell You",
                        "Upper Limb Strength Testing With a Dynamometer: Reference Values in Practice"],
        evidence_refs=["Douma et al. (2014). Reference values for isometric muscle force. BMC Sports Science, Medicine and Rehabilitation."],
    ),
    BenchmarkTest(
        test_id=18, test_name="Push up endurance", full_name="Elbow Endurance Push up",
        body_region="Elbow", category="endurance", unit="Repetitions", technology_level="low-tech",
        has_rate_of_change=False, admin_time_mins=3.5,
        conditions=["upper limb function", "return to sport", "shoulder rehab", "elbow rehab"],
        decision_points=["baseline assessment", "progression", "return to sport"],
        populations=["adult", "athlete", "manual worker"],
        pubmed_search_terms=["push up test upper extremity function", "push up reliability normative", "upper body endurance assessment"],
        article_angles=["The Push-Up Test in MSK Practice: What It Measures Beyond Gym Performance",
                        "Upper Limb Functional Endurance: Why Push-Up Capacity Matters in Rehab"],
        evidence_refs=["Negrete et al. (2010). Reliability and normative values for upper extremity function and power. Journal of Strength and Conditioning Research."],
    ),

    # ── HIP ────────────────────────────────────────────────────────────────
    BenchmarkTest(
        test_id=19, test_name="Hip adduction strength", full_name="Hip Strength Adduction",
        body_region="Hip", category="strength", unit="Newtons", technology_level="low-tech",
        has_rate_of_change=True, admin_time_mins=2.8,
        conditions=["athletic groin pain", "adductor strain", "hip rehab", "groin injury prevention"],
        decision_points=["baseline assessment", "return to play", "progression", "injury prevention screening"],
        populations=["football", "rugby", "ice hockey", "athlete"],
        pubmed_search_terms=["hip adductor strength dynamometry", "groin pain adductor strength", "Copenhagen adductor strength"],
        article_angles=["Hip Adductor Strength and Groin Injury: What the Evidence Says About Asymmetry",
                        "Adductor-to-Abductor Ratio in Footballers: Why the Balance Matters",
                        "Measuring Hip Adduction Strength: The Case for Handheld Dynamometry in Groin Assessment"],
        evidence_refs=["Thorborg et al. (2010). Clinical assessment of hip strength using a hand-held dynamometer. Scandinavian Journal of Medicine & Science in Sports."],
    ),
    BenchmarkTest(
        test_id=20, test_name="Hip abduction strength", full_name="Hip Strength Abduction",
        body_region="Hip", category="strength", unit="Newtons", technology_level="low-tech",
        has_rate_of_change=True, admin_time_mins=2.8,
        conditions=["ITB syndrome", "patellofemoral pain", "gluteal tendinopathy", "hip OA", "low back pain"],
        decision_points=["baseline assessment", "progression", "discharge"],
        populations=["runner", "adult", "older adult", "athlete"],
        pubmed_search_terms=["hip abductor strength dynamometry", "gluteal strength patellofemoral pain", "hip abduction force measurement"],
        article_angles=["Hip Abductor Strength: The Underused Assessment in Knee and Running Injuries",
                        "Gluteal Strength and Patellofemoral Pain: What the Research Shows",
                        "Hip Abduction Testing With Handheld Dynamometry: Reliability and Clinical Utility"],
        evidence_refs=["Thorborg et al. (2010). Clinical assessment of hip strength using a hand-held dynamometer. Scandinavian Journal of Medicine & Science in Sports."],
    ),
    BenchmarkTest(
        test_id=27, test_name="Single leg hamstring bridge", full_name="Hip Endurance Single leg hamstring bridge",
        body_region="Hip", category="endurance", unit="Repetitions", technology_level="low-tech",
        has_rate_of_change=True, admin_time_mins=2.3,
        conditions=["hamstring strain", "ACL rehab", "posterior chain assessment", "return to running"],
        decision_points=["progression", "return to running", "return to play"],
        populations=["football", "rugby", "runner", "athlete"],
        pubmed_search_terms=["single leg hamstring bridge test", "hamstring bridge endurance injury prediction", "posterior chain assessment field test"],
        article_angles=["Single-Leg Hamstring Bridge: A Simple Test With Significant Predictive Value",
                        "Posterior Chain Endurance in Football: Why Bridge Reps Predict Hamstring Injury",
                        "Hamstring Rehabilitation Progression: Using Bridge Capacity to Guide Loading"],
        evidence_refs=["Freckleton et al. (2014). Predictive validity of single leg bridge test for hamstring injuries. British Journal of Sports Medicine."],
    ),
    BenchmarkTest(
        test_id=28, test_name="Single leg broad jump", full_name="Hip Power Single leg broad jump",
        body_region="Hip", category="power", unit="Centimeters", technology_level="low-tech",
        has_rate_of_change=False, admin_time_mins=2.8,
        conditions=["return to sport", "lower limb power", "ACL rehab", "hip rehab"],
        decision_points=["return to sport", "limb symmetry assessment", "discharge"],
        populations=["athlete", "football", "recreational", "adult"],
        pubmed_search_terms=["single leg broad jump normative", "horizontal hop test limb symmetry", "broad jump return to sport"],
        article_angles=["Single-Leg Broad Jump: What Horizontal Power Tells You About Sport Readiness",
                        "Hop Testing Without Specialist Equipment: The Case for the Broad Jump",
                        "Limb Symmetry in Hop Testing: Which Side Matters and How Big Is the Gap?"],
        evidence_refs=["Almalki et al. (2021). Normative values for single-leg hop performance. Saudi Journal of Sports Medicine."],
    ),

    # ── KNEE ───────────────────────────────────────────────────────────────
    BenchmarkTest(
        test_id=29, test_name="Knee extension strength", full_name="Knee Strength Extension",
        body_region="Knee", category="strength", unit="Newtons", technology_level="low-tech",
        has_rate_of_change=True, admin_time_mins=4.3,
        conditions=["ACL reconstruction", "knee OA", "patellofemoral pain", "total knee arthroplasty"],
        decision_points=["baseline assessment", "progression", "return to running", "return to sport", "discharge"],
        populations=["adult", "athlete", "footballer", "older adult"],
        pubmed_search_terms=["knee extension strength dynamometry", "quadriceps strength ACL rehabilitation", "knee extensor force measurement"],
        article_angles=["Knee Extension Strength After ACL Reconstruction: What the Numbers Actually Mean",
                        "Quadriceps Strength and Return-to-Sport Criteria: How Much Is Enough?",
                        "Measuring Knee Extension Force With Handheld Dynamometry: Reliability in Practice",
                        "Limb Symmetry in Quadriceps Strength: Why 90% May Not Be Safe Enough"],
        evidence_refs=["Koblbauer et al. (2011). Reliability of maximal isometric knee strength testing with modified hand-held dynamometry. BMC Musculoskeletal Disorders."],
    ),
    BenchmarkTest(
        test_id=30, test_name="Knee flexion strength", full_name="Knee Strength Flexion",
        body_region="Knee", category="strength", unit="Newtons", technology_level="low-tech",
        has_rate_of_change=False, admin_time_mins=3.3,
        conditions=["knee OA", "hamstring injury", "ACL rehab", "knee rehab"],
        decision_points=["baseline assessment", "progression", "return to sport"],
        populations=["adult", "footballer", "athlete"],
        pubmed_search_terms=["knee flexion strength dynamometry", "hamstring strength isometric", "posterior knee strength measurement"],
        article_angles=["Hamstring Strength Testing at the Knee: What Isometric Force Tells You",
                        "Quad-to-Hamstring Ratio: Why the Balance Matters in ACL Rehab"],
        evidence_refs=["McCall et al. (2015). Reliability and sensitivity of isometric posterior lower limb muscle test in professional football. Journal of Sports Sciences."],
    ),
    BenchmarkTest(
        test_id=31, test_name="Single leg sit to stand", full_name="Knee Endurance Single leg sit to stand",
        body_region="Knee", category="endurance", unit="Repetitions", technology_level="low-tech",
        has_rate_of_change=True, admin_time_mins=3.0,
        conditions=["knee OA", "ACL rehab", "lower limb function", "return to work", "total knee arthroplasty"],
        decision_points=["baseline assessment", "progression", "discharge", "return to work"],
        populations=["adult", "older adult", "post-op"],
        pubmed_search_terms=["single leg sit to stand test", "five times sit to stand knee", "lower limb functional capacity test"],
        article_angles=["Single-Leg Sit-to-Stand: The Functional Test That Connects Strength to Daily Life",
                        "Knee OA Progression: Why Sit-to-Stand Capacity Is a Better Marker Than Pain",
                        "Functional Lower Limb Assessment Without Equipment: The Sit-to-Stand Test"],
        evidence_refs=["Waldhelm et al. (2020). Inter-rater and test-retest reliability of single leg sit-to-stand tests. International Journal of Sports Physical Therapy."],
    ),
    BenchmarkTest(
        test_id=34, test_name="Countermovement jump", full_name="Knee Power Countermovement jump",
        body_region="Knee", category="power", unit="Centimeters", technology_level="low-tech",
        has_rate_of_change=False, admin_time_mins=2.8,
        conditions=["ACL return to sport", "lower limb power", "athletic assessment"],
        decision_points=["return to sport", "plyometric readiness", "limb symmetry"],
        populations=["athlete", "footballer", "recreational"],
        pubmed_search_terms=["countermovement jump ACL return to sport", "CMJ limb symmetry index", "vertical jump lower limb power"],
        article_angles=["Countermovement Jump in ACL Rehab: What Jump Height Tells You About Power Readiness",
                        "CMJ Without a Force Plate: What You Can and Cannot Measure",
                        "Jump Testing and Return-to-Sport Criteria: Interpreting the Evidence"],
        evidence_refs=["Chow et al. (2023). Validity and test-retest reliability of remote countermovement jump assessments. Applied Sciences."],
    ),
    BenchmarkTest(
        test_id=35, test_name="Single leg jump", full_name="Knee Power Single leg jump",
        body_region="Knee", category="power", unit="Centimeters", technology_level="low-tech",
        has_rate_of_change=False, admin_time_mins=3.3,
        conditions=["ACL return to sport", "limb symmetry", "lower limb power"],
        decision_points=["return to sport", "limb symmetry assessment", "discharge"],
        populations=["athlete", "footballer", "recreational"],
        pubmed_search_terms=["single leg vertical jump ACL", "single limb jump height normative", "limb symmetry index jump testing"],
        article_angles=["Single-Leg Jump Testing: The Most Informative Five Minutes in ACL Rehab",
                        "Limb Symmetry in Single-Leg Jump: What the Research Tells Us About Safe Return",
                        "Jump Height vs Limb Symmetry: Which Matters More in Return-to-Sport Decisions?"],
        evidence_refs=["Chow et al. (2023). Validity and test-retest reliability of remote countermovement jump assessments. Applied Sciences."],
    ),

    # ── LUMBAR SPINE ───────────────────────────────────────────────────────
    BenchmarkTest(
        test_id=36, test_name="Plank endurance", full_name="Lumbar spine Endurance Plank",
        body_region="Lumbar spine", category="endurance", unit="Seconds", technology_level="low-tech",
        has_rate_of_change=True, admin_time_mins=2.8,
        conditions=["low back pain", "core stability", "lumbar rehab", "return to sport"],
        decision_points=["baseline assessment", "progression", "return to sport", "monitoring over time"],
        populations=["adult", "worker", "athlete", "recreational"],
        pubmed_search_terms=["plank test core endurance", "abdominal plank hold normative values", "trunk endurance assessment low back"],
        article_angles=["Plank Endurance in Low Back Rehab: What Duration Actually Tells You",
                        "Core Endurance Testing: Why Time Matters More Than Technique in Clinical Assessment",
                        "Trunk Stability Assessment Without Equipment: Interpreting Plank Results in Practice"],
        evidence_refs=["McGill et al. (2010). Clinical tools to quantify torso flexion endurance: normative data. Occupational Ergonomics."],
    ),
    BenchmarkTest(
        test_id=37, test_name="Side plank endurance", full_name="Lumbar spine Endurance Side plank",
        body_region="Lumbar spine", category="endurance", unit="Seconds", technology_level="low-tech",
        has_rate_of_change=True, admin_time_mins=2.8,
        conditions=["low back pain", "lateral core stability", "lumbar rehab"],
        decision_points=["baseline assessment", "progression", "monitoring over time"],
        populations=["adult", "worker", "athlete"],
        pubmed_search_terms=["side plank endurance normative", "lateral trunk endurance test", "McGill side bridge test"],
        article_angles=["Side Plank Endurance: The Lateral Core Test Often Left Out of Assessments",
                        "Plank Asymmetry and Low Back Pain: What Side-to-Side Differences Mean Clinically"],
        evidence_refs=["McGill et al. (2010). Clinical tools to quantify torso flexion endurance: normative data. Occupational Ergonomics."],
    ),
    BenchmarkTest(
        test_id=38, test_name="Sorenson hold", full_name="Lumbar spine Endurance Sorenson hold",
        body_region="Lumbar spine", category="endurance", unit="Seconds", technology_level="low-tech",
        has_rate_of_change=True, admin_time_mins=2.3,
        conditions=["low back pain", "lumbar extensor endurance", "return to work"],
        decision_points=["baseline assessment", "progression", "return to work"],
        populations=["adult", "manual worker", "athlete"],
        pubmed_search_terms=["Sorenson back extensor endurance test", "lumbar extension endurance normative", "back endurance hold reliability"],
        article_angles=["Sorenson Hold: The Extensor Endurance Test That Predicts More Than Fitness",
                        "Lumbar Extensor Endurance and Low Back Pain: What Duration Tells You"],
        evidence_refs=["McGill et al. (2010). Clinical tools to quantify torso flexion endurance: normative data. Occupational Ergonomics."],
    ),

    # ── SHOULDER ───────────────────────────────────────────────────────────
    BenchmarkTest(
        test_id=44, test_name="Shoulder internal rotation strength", full_name="Shoulder Strength Internal rotation",
        body_region="Shoulder", category="strength", unit="Newtons", technology_level="low-tech",
        has_rate_of_change=True, admin_time_mins=2.8,
        conditions=["rotator cuff", "shoulder impingement", "overhead athlete", "shoulder instability"],
        decision_points=["baseline assessment", "progression", "return to overhead sport"],
        populations=["overhead athlete", "swimmer", "cricket", "tennis", "adult"],
        pubmed_search_terms=["shoulder internal rotation strength dynamometry", "rotator cuff internal rotation isometric", "shoulder strength overhead athlete"],
        article_angles=["Shoulder Rotation Strength: Why the ER/IR Ratio Matters More Than Absolute Force",
                        "Rotator Cuff Strength Testing in Overhead Athletes: What Handheld Dynamometry Can Tell You",
                        "Internal Rotation Strength After Shoulder Injury: When Is It Enough to Return to Sport?"],
        evidence_refs=["Cools et al. (2016). Eccentric and isometric shoulder rotator cuff strength testing using a hand-held dynamometer. Knee Surgery, Sports Traumatology, Arthroscopy."],
    ),
    BenchmarkTest(
        test_id=45, test_name="Shoulder external rotation strength", full_name="Shoulder Strength External rotation",
        body_region="Shoulder", category="strength", unit="Newtons", technology_level="low-tech",
        has_rate_of_change=True, admin_time_mins=2.8,
        conditions=["rotator cuff", "shoulder impingement", "overhead athlete", "shoulder instability"],
        decision_points=["baseline assessment", "progression", "return to overhead sport"],
        populations=["overhead athlete", "swimmer", "cricket", "tennis", "adult"],
        pubmed_search_terms=["shoulder external rotation strength dynamometry", "rotator cuff external rotation isometric", "shoulder strength rehab"],
        article_angles=["External Rotation Strength: The Rotator Cuff Test That Predicts Most About Shoulder Rehab",
                        "ER:IR Ratio in Shoulder Assessment: What Balance Tells You About Risk",
                        "Shoulder External Rotation After Impingement: How Much Strength Is Enough?"],
        evidence_refs=["Cools et al. (2016). Eccentric and isometric shoulder rotator cuff strength testing using a hand-held dynamometer. Knee Surgery, Sports Traumatology, Arthroscopy."],
    ),
    BenchmarkTest(
        test_id=46, test_name="Athletic shoulder test T", full_name="Shoulder Strength Athletic shoulder test T",
        body_region="Shoulder", category="strength", unit="Newtons", technology_level="low-tech",
        has_rate_of_change=False, admin_time_mins=3.0,
        conditions=["rotator cuff", "scapular stability", "overhead sport", "rugby"],
        decision_points=["baseline assessment", "return to sport", "progression"],
        populations=["overhead athlete", "rugby", "swimmer"],
        pubmed_search_terms=["athletic shoulder test scapular stability", "shoulder Y T I test sphygmomanometer", "lower trapezius serratus strength assessment"],
        article_angles=["Athletic Shoulder Test Y-T-I: What Scapular Endurance Tests Tell You About Overhead Risk",
                        "Testing Shoulder Stability Without a Lab: The Case for Athletic Shoulder Testing"],
        evidence_refs=["Morrison et al. (2021). Validity of the sphygmomanometer for shoulder strength assessment in amateur rugby. Physical Therapy in Sport."],
    ),
    BenchmarkTest(
        test_id=52, test_name="Posterior shoulder endurance test", full_name="Shoulder Endurance Posterior shoulder endurance test",
        body_region="Shoulder", category="endurance", unit="Seconds", technology_level="low-tech",
        has_rate_of_change=True, admin_time_mins=3.5,
        conditions=["rotator cuff fatigue", "overhead athlete", "return to overhead sport", "shoulder impingement"],
        decision_points=["baseline assessment", "return to sport", "progression", "monitoring over time"],
        populations=["overhead athlete", "swimmer", "cricket", "tennis"],
        pubmed_search_terms=["posterior shoulder endurance test", "lower trapezius endurance overhead athlete", "shoulder fatigue assessment"],
        article_angles=["Posterior Shoulder Endurance: The Test That Predicts Overhead Fatigue Before It Becomes Injury",
                        "Shoulder Endurance vs Shoulder Strength: Why Both Matter in Overhead Sport Rehab"],
        evidence_refs=["Evans et al. (2018). EMG study of muscular endurance during posterior shoulder endurance test. Journal of Electromyography and Kinesiology."],
    ),
    BenchmarkTest(
        test_id=53, test_name="Forward medicine ball throw", full_name="Shoulder Power Forward medicine ball throw",
        body_region="Shoulder", category="power", unit="Centimeters", technology_level="low-tech",
        has_rate_of_change=False, admin_time_mins=3.8,
        conditions=["upper limb power", "return to sport", "shoulder rehab", "overhead athlete"],
        decision_points=["return to sport", "upper limb power assessment", "discharge"],
        populations=["overhead athlete", "older adult", "adult"],
        pubmed_search_terms=["seated medicine ball throw upper body power", "medicine ball throw shoulder rehabilitation", "upper extremity power assessment"],
        article_angles=["Medicine Ball Throw in Shoulder Rehab: Testing Upper Limb Power Without a Lab",
                        "Upper Limb Power Assessment: Why Distance Predicts More Than Strength Alone"],
        evidence_refs=["Harris et al. (2011). Seated medicine ball throw as a test of upper body power. Journal of Strength and Conditioning Research."],
    ),
    BenchmarkTest(
        test_id=54, test_name="Lumbar locked rotation test", full_name="Thoracic spine Range of movement Lumbar locked rotation test",
        body_region="Thoracic spine", category="ROM", unit="Degrees", technology_level="low-tech",
        has_rate_of_change=False, admin_time_mins=2.3,
        conditions=["thoracic mobility restriction", "overhead sport", "swimmer assessment", "back pain"],
        decision_points=["baseline assessment", "monitoring over time", "sport-specific assessment"],
        populations=["swimmer", "overhead athlete", "adult"],
        pubmed_search_terms=["lumbar locked thoracic rotation test", "thoracic rotation range of motion", "thoracic mobility assessment swimmer"],
        article_angles=["Thoracic Rotation and Lumbar-Locked Testing: Why Regional Mobility Assessment Changes Management",
                        "Swimmer Thoracic Assessment: What the Lumbar-Locked Rotation Test Reveals"],
        evidence_refs=["Feijen et al. (2018). Intra- and interrater reliability of the lumbar-locked thoracic rotation test in swimmers. Physical Therapy in Sport."],
    ),
]


# ---------------------------------------------------------------------------
# Condition-to-test graph
# ---------------------------------------------------------------------------

CONDITION_TEST_GRAPH: dict[str, dict] = {
    "ACL reconstruction": {
        "tests": ["Knee Strength Extension", "Knee Strength Flexion", "Knee Power Countermovement jump",
                  "Knee Power Single leg jump", "Knee Endurance Single leg sit to stand",
                  "Hip Strength Abduction", "Hip Endurance Single leg hamstring bridge",
                  "Ankle Power Drop jump", "Ankle Power Single leg drop jump"],
        "key_metrics": ["quad:hamstring ratio", "limb symmetry index", "single leg jump height",
                        "knee extension strength", "bridge reps", "RSI"],
        "decision_points": ["return to running", "return to full training", "return to contact sport"],
        "populations": ["athlete", "recreational", "football", "rugby"],
        "article_angles": ["ACL Return-to-Sport Testing Battery: What Each Test Actually Contributes",
                           "Quad-to-Hamstring Ratio After ACL Reconstruction: Why the Balance Predicts Re-Injury",
                           "Limb Symmetry Index in ACL Rehab: The One Number That Changes Decisions"],
    },
    "Achilles tendinopathy": {
        "tests": ["Ankle Endurance Single leg calf raise", "Ankle Strength Plantarflexion",
                  "Ankle Power Drop jump", "Ankle Power Single leg drop jump",
                  "Ankle Range of movement Weight bearing lunge test"],
        "key_metrics": ["calf raise repetitions", "plantarflexion strength", "dorsiflexion range", "RSI"],
        "decision_points": ["load tolerance baseline", "progression threshold", "return to running", "return to sport"],
        "populations": ["runner", "recreational", "athlete"],
        "article_angles": ["Achilles Tendinopathy Testing Battery: The Five Measures That Guide Every Decision",
                           "Calf Capacity and Achilles Rehab: Why Endurance Beats Strength as a Progression Marker"],
    },
    "Rotator cuff / shoulder impingement": {
        "tests": ["Shoulder Strength External rotation", "Shoulder Strength Internal rotation",
                  "Shoulder Strength Athletic shoulder test T", "Shoulder Strength Athletic shoulder test Y",
                  "Shoulder Strength Athletic shoulder test I", "Shoulder Endurance Posterior shoulder endurance test",
                  "Shoulder Range of movement External rotation", "Shoulder Range of movement Internal rotation"],
        "key_metrics": ["ER:IR ratio", "shoulder strength", "ROM deficit", "posterior shoulder endurance"],
        "decision_points": ["baseline", "progression", "return to overhead sport", "discharge"],
        "populations": ["overhead athlete", "swimmer", "rugby", "cricket", "tennis"],
        "article_angles": ["Shoulder Strength Testing in Overhead Athletes: The ER/IR Ratio That Changes Management",
                           "Return to Overhead Sport After Shoulder Injury: A Testing Battery That Works"],
    },
    "Low back pain": {
        "tests": ["Lumbar spine Endurance Plank", "Lumbar spine Endurance Side plank",
                  "Lumbar spine Endurance Sorenson hold", "Lumbar spine Strength Extension",
                  "Lumbar spine Strength Flexion", "Lumbar spine Strength Lateral flexion",
                  "Lumbar spine Strength Pallof press", "Hip Strength Extension"],
        "key_metrics": ["plank duration", "Sorenson hold time", "trunk strength", "flexion:extension ratio"],
        "decision_points": ["baseline", "progression", "return to work", "return to sport"],
        "populations": ["worker", "athlete", "recreational", "older adult"],
        "article_angles": ["Trunk Endurance Testing in Low Back Rehab: What Three Tests Can Tell You",
                           "McGill Endurance Tests in Practice: Reference Values and Clinical Interpretation"],
    },
    "Hip and groin": {
        "tests": ["Hip Strength Adduction", "Hip Strength Abduction", "Hip Strength Extension",
                  "Hip Strength Flexion", "Hip Strength External rotation", "Hip Strength Internal rotation",
                  "Hip Range of movement Internal rotation", "Hip Endurance Single leg hamstring bridge",
                  "Hip Power Single leg broad jump"],
        "key_metrics": ["adductor:abductor ratio", "hip strength", "ROM", "hop distance"],
        "decision_points": ["baseline", "progression", "return to sport", "discharge"],
        "populations": ["football", "athlete", "adult", "older adult"],
        "article_angles": ["Hip Strength Testing: The Six Movements That Define a Complete Assessment",
                           "Groin Injury and Adductor Strength: Using the Evidence to Guide Return-to-Play"],
    },
}


# ---------------------------------------------------------------------------
# Topic generation
# ---------------------------------------------------------------------------

ARTICLE_ANGLE_TEMPLATES = {
    "strength": [
        "{test_name}: What {unit} of Force Actually Tells You in {condition} Rehab",
        "{test_name} Reference Values: Interpreting Strength in Clinical Practice",
        "When Is {test_name} Strong Enough? Setting Meaningful Thresholds",
        "{region} Strength Testing Without Expensive Equipment: The Case for {test_name}",
        "Limb Asymmetry in {test_name}: How Big a Difference Should You Act On?",
    ],
    "endurance": [
        "{test_name}: What the Repetition Count Actually Means",
        "{test_name} as a Progression Marker: Interpreting Change Over Time",
        "{test_name} in {condition}: Setting Realistic Targets for Rehab",
        "Monitoring Recovery With {test_name}: What Improving Endurance Tells You",
        "Why {test_name} Endurance Matters More Than Pain Alone",
    ],
    "ROM": [
        "{test_name}: Reliability, Error, and What to Actually Measure",
        "How Much {test_name} Is Normal? Interpreting Range of Motion in Clinical Practice",
        "{test_name} as a Clinical Decision Tool: When Range Changes Management",
        "Reassessing {region} Mobility: Using {test_name} to Track Real Progress",
    ],
    "power": [
        "{test_name}: What Reactive Strength Tells You About Sport Readiness",
        "Power Testing Without a Force Plate: The {test_name} in Clinical Practice",
        "Return-to-Sport Power Criteria: Where Does {test_name} Fit?",
        "{test_name} and Limb Symmetry: What the Research Says About Safe Return",
        "Interpreting {test_name} Results: What the Numbers Mean Beyond Performance",
    ],
}


def generate_topics_from_test(test: BenchmarkTest, n: int = 3) -> list[str]:
    """Generate article topic ideas from a single test object."""
    templates = ARTICLE_ANGLE_TEMPLATES.get(test.category, ARTICLE_ANGLE_TEMPLATES["strength"])
    primary_condition = test.conditions[0] if test.conditions else test.body_region + " rehab"
    topics = []
    for template in templates[:n]:
        topic = template.format(
            test_name=test.test_name,
            region=test.body_region,
            condition=primary_condition,
            unit=test.unit,
        )
        topics.append(topic)
    return topics


def get_tests_for_condition(condition_key: str) -> list[BenchmarkTest]:
    """Return test objects for a given condition."""
    graph = CONDITION_TEST_GRAPH.get(condition_key, {})
    test_names = graph.get("tests", [])
    return [t for t in PROTOCOL_LIBRARY if t.full_name in test_names]


def get_pubmed_terms_for_test(test: BenchmarkTest) -> list[str]:
    """Return compact PubMed search terms for a test."""
    return test.pubmed_search_terms


def get_all_article_topics(n_per_test: int = 2) -> list[dict]:
    """Generate all article topics from the full protocol library."""
    topics = []
    for test in PROTOCOL_LIBRARY:
        for topic in generate_topics_from_test(test, n=n_per_test):
            topics.append({
                "topic": topic,
                "test_id": test.test_id,
                "test_name": test.full_name,
                "body_region": test.body_region,
                "category": test.category,
                "conditions": test.conditions[:3],
                "pubmed_terms": test.pubmed_search_terms[:2],
            })
    return topics


# ---------------------------------------------------------------------------
# Content architecture summary
# ---------------------------------------------------------------------------

CONTENT_ARCHITECTURE = {
    "ratio": {
        "protocol_led": 0.35,      # 35% — individual test explainers
        "condition_led": 0.25,     # 25% — condition synthesis articles
        "decision_making": 0.15,   # 15% — how data changes clinical decisions
        "low_tech": 0.05,          # 5%  — implementation without expensive equipment
        "business_economics": 0.20, # 20% — clinic owner / payer audience
    },
    "rationale": """
    Protocol-led content (35%) is the highest priority because:
    - It is directly anchored to the platform's test library
    - It builds authority on specific measurements
    - It creates curiosity about what Benchmark PS measures and why
    - It is evergreen and highly searchable by condition-specific terms

    Condition-led content (25%) synthesises multiple tests into clinical pictures,
    showing how tests work together rather than in isolation.

    Decision-making content (15%) shows how objective data changes specific clinical
    decisions — this is where Benchmark PS's positioning is strongest.

    Low-tech content (5%) reinforces the platform's accessibility message.

    Business/economics content (20%) is clinically grounded — it follows from
    the clinical case rather than leading with practice management language.
    """,
}

REVEAL_BOUNDARY = {
    "public": [
        "Test names and what they measure",
        "Why a test matters clinically",
        "When to use a test (decision points)",
        "Conceptual interpretation (more reps = better capacity)",
        "Evidence references for test methodology",
        "General guidance on meaningful change",
        "Condition-to-test relationships",
        "Populations where a test is most relevant",
    ],
    "proprietary": [
        "Exact normative values by age/sex from the platform dataset",
        "Full Benchmark PS scoring algorithms",
        "Composite performance scores",
        "Specific progression thresholds and cutoffs",
        "Rate-of-change calculations",
        "Full normative tables",
    ],
}


if __name__ == "__main__":
    print(f"Protocol library: {len(PROTOCOL_LIBRARY)} tests")
    print(f"Conditions mapped: {len(CONDITION_TEST_GRAPH)}")
    total_topics = get_all_article_topics(n_per_test=2)
    print(f"Total article topics generatable: {len(total_topics)}")
    print("\nSample topics from 5 tests:")
    for t in total_topics[:10]:
        print(f"  [{t['test_name']}]")
        print(f"  → {t['topic']}")
