"""
scrape_topics.py — Automatically refills queue.json with high-value article topics.

Sources:
  - Reddit (17 subreddits)
  - Google People Also Ask
  - PubMed Entrez API (latest MSK research papers)
  - BJSM Blog RSS
  - NICE Guidelines RSS
  - Physio Edge Podcast RSS
  - The Running Physio RSS
  - The Sports Physio RSS
  - Physiopedia RSS
  - Curated fallback topics (50+)

Runs before generate_post.py in the daily GitHub Actions workflow.
Only refills when queue.json drops below REFILL_THRESHOLD items.
"""

import json
import re
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

import anthropic

BASE_DIR = Path(__file__).parent
QUEUE_PATH = BASE_DIR / "queue.json"
MANIFEST_PATH = BASE_DIR / "posts_manifest.json"

REFILL_THRESHOLD = 7
REFILL_COUNT = 14

# ─────────────────────────────────────────────
# SOURCE CONFIGURATION
# ─────────────────────────────────────────────

SUBREDDITS = [
    "physio",
    "physicaltherapy",
    "sportsrehab",
    "backpain",
    "kneeinjury",
    "ACL",
    "flexibility",
    "running",
    "cycling",
    "weightlifting",
    "tennis",
    "golf",
    "triathlon",
    "crossfit",
    "overcominggravity",
    "Rowing",
    "medicine",
]

SEARCH_QUERIES = [
    "physiotherapy assessment MSK",
    "how to treat knee osteoarthritis physiotherapy",
    "ACL rehabilitation return to sport",
    "low back pain physiotherapy treatment",
    "rotator cuff physiotherapy exercises",
    "hamstring strain rehabilitation protocol",
    "patellofemoral pain syndrome treatment",
    "Achilles tendinopathy physiotherapy",
    "hip pain physiotherapy assessment",
    "ankle sprain rehabilitation",
    "muscle strength testing physiotherapy",
    "outcome measures physiotherapy",
    "clinical decision making physiotherapy",
    "MSK triage physiotherapy",
    "sports injury rehabilitation protocol",
]

RSS_FEEDS = [
    {
        "name": "BJSM Blog",
        "url": "https://blogs.bmj.com/bjsm/feed/",
        "type": "rss",
    },
    {
        "name": "NICE MSK Guidelines",
        "url": "https://www.nice.org.uk/guidance/published?ngt=&ndt=Guideline&ndr=Musculoskeletal+conditions&nds=Published&format=rss",
        "type": "rss",
    },
    {
        "name": "Physio Edge Podcast",
        "url": "https://feeds.buzzsprout.com/1853414.rss",
        "type": "podcast_rss",
    },
    {
        "name": "The Running Physio",
        "url": "https://www.therunningphysio.com/feed/",
        "type": "rss",
    },
    {
        "name": "The Sports Physio",
        "url": "https://thesportsphysio.wordpress.com/feed/",
        "type": "rss",
    },
    {
        "name": "Physiopedia Latest",
        "url": "https://www.physio-pedia.com/index.php?title=Special:NewPages&feed=rss",
        "type": "rss",
    },
]

PUBMED_QUERIES = [
    "musculoskeletal physiotherapy outcomes measurement",
    "ACL rehabilitation return sport criteria",
    "clinical decision support physiotherapy",
    "MSK conservative care effectiveness",
    "physiotherapy outcome measures reliability",
]

FALLBACK_TOPICS = [
    # ── TIER 1: Clinical conditions and testing protocols (24) ──
    "ACL Reconstruction: Objective Criteria for Return to Running",
    "ACL Return-to-Sport Testing Battery: Benchmark Thresholds That Actually Predict Re-Injury",
    "Knee Osteoarthritis Conservative Care: What Good Progress Looks Like in Numbers",
    "Patellofemoral Pain: Strength, Hop, and Load-Tolerance Benchmarks for Discharge",
    "Hamstring Strain: Eccentric Strength and Sprint-Readiness Criteria",
    "Achilles Tendinopathy: Calf Capacity Benchmarks and Pain-Monitoring Thresholds",
    "Rotator Cuff Related Shoulder Pain: The Strength and ROM Markers That Matter",
    "Frozen Shoulder: ROM Recovery Milestones and When Progress Is Too Slow",
    "Lateral Ankle Instability: Hop, Balance, and Calf Benchmarks for Safe Discharge",
    "Plantar Fasciitis: Load Tolerance, Calf Strength, and Morning Pain Trend Markers",
    "Low Back Pain Conservative Management: Functional Outcome Benchmarks That Guide Decisions",
    "Cervical Radiculopathy: Strength, Neurodynamic, and Symptom Response Markers",
    "Hip Osteoarthritis: Objective Testing for Function Before and After Rehab Blocks",
    "Athletic Groin Pain: Adductor Strength Benchmarks and Return-to-Play Criteria",
    "Tibial Stress Fracture: Loading Progression Markers and Return-to-Run Criteria",
    "Tennis Elbow: Grip-Strength Recovery Benchmarks and Pain-Load Relationships",
    "De Quervain Tenosynovitis: Grip, Pinch, and Function Recovery Tracking",
    "Meniscal Injury Managed Conservatively: What to Measure and When",
    "Post-Op Meniscus Repair: Progression Criteria Using Simple Field Tests",
    "Runners in Rehab: Lower-Limb Capacity Benchmarks That Change Clinical Decisions",
    "Cyclists: Objective Testing for Knee, Hip, and Back Symptom Patterns",
    "Weightlifters in Rehab: Shoulder, Hip, and Trunk Capacity Testing",
    "Football Players: Field-Based Return-to-Play Metrics Physiotherapists Can Use",
    "Rugby Players: Contact-Readiness and Lower-Limb Performance Benchmarks",

    # ── TIER 2: Assessment methodology and outcome measurement (10) ──
    "Handheld Dynamometry in MSK Practice: What It Can Reliably Tell You",
    "Isometric Testing in Physiotherapy: When to Use It and How to Interpret Change",
    "Limb Symmetry Index: Useful Metric or Misleading Shortcut",
    "Single-Leg Hop Tests: What They Measure and What They Miss",
    "Grip Strength as a Systemic Marker in MSK Physiotherapy",
    "Range-of-Motion Testing: Reliability, Error, and Reassessment Intervals",
    "PROMs in MSK Rehab: Which Measures Are Worth Collecting Routinely",
    "MCID Versus MDC: What Counts as Real Change in Physiotherapy Practice",
    "Between-Session Reliability: How Much Change Is Enough to Act On",
    "Inter-Rater Variability in MSK Assessment: How to Reduce Noise in Your Testing",

    # ── TIER 3: Clinical decision-making (6) ──
    "Criteria-Based Progression Versus Time-Based Rehab: What the Evidence Supports",
    "Return-to-Sport Decisions: How Objective Deficits Predict Re-Injury Risk",
    "Discharge Criteria in MSK Physiotherapy: What Good Enough Should Look Like Numerically",
    "When Test Results Should Trigger Referral Rather Than Progression",
    "Using Objective Data to Manage Plateaus in Rehabilitation",
    "Shared Decision Making With Numbers: Improving Patient Buy-In Without Overcomplicating Care",

    # ── TIER 4: Technology vs low-tech workflows (4) ──
    "What Handheld Dynamometry Can Replace in Everyday MSK Practice",
    "Smartphone Video Versus Lab Systems: When Low-Cost Tools Are Clinically Sufficient",
    "Stopwatch, Step, and Bodyweight Tests Versus Force Plates: What You Lose and Gain",
    "Telehealth Outcome Monitoring That Is Clinically Useful Rather Than Admin-Heavy",

    # ── TIER 5: Business and health economics (6) ──
    "The Business Case for Outcome Measurement in Private Physiotherapy",
    "What Objective Outcome Data Demonstrates to Payers and Insurers",
    "Reducing Treatment Variation: The Clinical and Commercial Upside",
    "Staffing Efficiency When Assessment and Progression Are Standardised",
    "Premium Pricing and Premium Evidence: When Objective Data Justifies the Difference",
    "Value-Based MSK Care: What Clinic Owners Need to Measure First",
]


# ─────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────

def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def fetch_url(url: str, headers: dict = None, timeout: int = 12) -> str | None:
    try:
        default_headers = {
            "User-Agent": "BenchmarkPS-BlogBot/2.0 (blog@benchmarkps.org)",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        }
        if headers:
            default_headers.update(headers)
        req = urllib.request.Request(url, headers=default_headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  Fetch error {url[:60]}: {e}")
        return None


# ─────────────────────────────────────────────
# SCRAPERS
# ─────────────────────────────────────────────

def get_reddit_topics(subreddit: str, limit: int = 20) -> list[str]:
    topics = []
    url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={limit}&t=month"
    content = fetch_url(url)
    if not content:
        return topics
    try:
        data = json.loads(content)
        posts = data.get("data", {}).get("children", [])
        for post in posts:
            title = post.get("data", {}).get("title", "").strip()
            if len(title) < 15:
                continue
            if any(kw in title.lower() for kw in [
                "how", "what", "why", "when", "should", "best", "help",
                "pain", "injury", "rehab", "physio", "exercise", "strength",
                "return", "surgery", "recovery", "assessment", "treatment",
                "muscle", "knee", "shoulder", "back", "hip", "ankle", "sport",
                "running", "cycling", "training", "load", "protocol", "evidence",
            ]):
                topics.append(title)
    except Exception as e:
        print(f"  Reddit parse error r/{subreddit}: {e}")
    return topics


def get_google_paa(query: str) -> list[str]:
    questions = []
    encoded = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded}&hl=en&gl=gb"
    content = fetch_url(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-GB,en;q=0.9",
    })
    if not content:
        return questions
    for pattern in [r'data-q="([^"]{20,120})"', r'"([A-Z][^"]{20,100}\?)"']:
        for match in re.findall(pattern, content):
            if "?" in match and 20 < len(match) < 120:
                questions.append(match)
    time.sleep(1.5)
    return questions


def get_rss_topics(feed: dict) -> list[str]:
    topics = []
    content = fetch_url(feed["url"])
    if not content:
        return topics
    try:
        content_clean = re.sub(r' xmlns[^"]*"[^"]*"', '', content)
        content_clean = re.sub(r'<[a-z]+:', '<', content_clean)
        content_clean = re.sub(r'</[a-z]+:', '</', content_clean)
        root = ET.fromstring(content_clean)
        for item in root.findall(".//item")[:20]:
            title = item.findtext("title", "").strip()
            description = item.findtext("description", "").strip()
            description = re.sub(r'<[^>]+>', ' ', description)
            description = re.sub(r'\s+', ' ', description).strip()[:300]
            if title and len(title) > 15:
                topics.append(title)
            if description and len(description) > 50:
                for sentence in re.split(r'[.!?]', description)[:2]:
                    sentence = sentence.strip()
                    if 30 < len(sentence) < 150:
                        topics.append(sentence)
    except Exception as e:
        print(f"  RSS parse error {feed['name']}: {e}")
    return topics


def get_pubmed_topics() -> list[str]:
    topics = []
    base_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    base_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    for query in PUBMED_QUERIES[:3]:
        try:
            encoded = urllib.parse.quote(query)
            search_url = f"{base_search}?db=pubmed&term={encoded}&retmax=8&sort=date&retmode=json"
            content = fetch_url(search_url)
            if not content:
                continue
            data = json.loads(content)
            ids = data.get("esearchresult", {}).get("idlist", [])
            if not ids:
                continue
            summary_url = f"{base_fetch}?db=pubmed&id={','.join(ids)}&retmode=json"
            content2 = fetch_url(summary_url)
            if not content2:
                continue
            data2 = json.loads(content2)
            for uid, item in data2.get("result", {}).items():
                if uid == "uids":
                    continue
                title = item.get("title", "").strip().rstrip(".")
                if title and len(title) > 20:
                    topics.append(title)
            time.sleep(0.4)
        except Exception as e:
            print(f"  PubMed '{query[:40]}': {e}")

    return topics


# ─────────────────────────────────────────────
# CLAUDE FILTER
# ─────────────────────────────────────────────

def filter_and_rank_topics(
    raw_topics: list[str],
    existing_titles: list[str],
    existing_queue: list[str],
    source_summary: str = "",
) -> list[str]:
    client = anthropic.Anthropic()

    existing_all = set(t.lower() for t in existing_titles + existing_queue)

    candidates = []
    seen = set()
    for topic in raw_topics:
        topic = topic.strip()
        if len(topic) < 15 or len(topic) > 250:
            continue
        key = topic.lower()[:40]
        if key in seen:
            continue
        seen.add(key)
        if any(
            topic.lower()[:35] in existing.lower() or existing.lower()[:35] in topic.lower()
            for existing in existing_all
        ):
            continue
        candidates.append(topic)

    if not candidates:
        return []

    candidates = candidates[:80]

    prompt = f"""You are a content strategist for Benchmark PS, a UK physiotherapy performance measurement platform.

Sources scraped today: {source_summary}

Select and rewrite the {REFILL_COUNT} best article topics for a UK physiotherapy clinic audience.

CONTENT ARCHITECTURE (strict 80/20 split):

TIER 1 — Clinical conditions and testing protocols (40% of output)
  Select topics about objective testing, benchmark thresholds, and measurable
  recovery criteria for specific MSK conditions. Include athletic populations
  (football, rugby, running, cycling, weightlifting) alongside clinical populations.
  Draw from sports science research as well as physiotherapy literature.

TIER 2 — Assessment methodology and outcome measurement (20% of output)
  Select topics about how to measure, what to measure, and what the numbers mean.
  Reliability, validity, MCID, inter-rater variability, handheld dynamometry,
  hop tests, grip strength, ROM, PROMs.

TIER 3 — Clinical decision-making (15% of output)
  Select topics where objective data changes a specific clinical decision:
  progression, discharge, return to sport, referral, plateau management.
  Frame as: clinical problem → decision point → objective variable → threshold.

TIER 4 — Low-tech implementation (5% of output)
  Select topics about implementing objective testing without expensive equipment.
  Handheld dynamometry vs force plates. Smartphone tools. Field tests.

TIER 5 — Business and health economics (20% of output)
  Select topics aimed at clinic owners and practice managers.
  Frame as: clinical consistency first, commercial consequences second.
  Topics: payer requirements, outcome data and defensible care, staffing
  efficiency, reducing treatment variation, value-based contracting.
  NEVER frame as practice management or marketing advice.

REWRITE RULES:
- Convert questions to declarative titles
- Convert academic titles to practitioner-friendly language
- Keep titles specific — include condition names, techniques, thresholds, or specific tests
- Clinical topics: "[Condition]: [Specific Testing Variable or Decision]"
- Assessment topics: "[Test/Tool]: What It Can and Cannot Tell You"
- Decision-making topics: focus on the decision, not the condition
- Business topics: clinical framing first, never lead with money or marketing
- No em dashes, no clickbait, no superlatives, no vague titles like "the importance of X"

EXISTING POSTS — do not duplicate:
{chr(10).join(f"- {t}" for t in existing_titles[:25])}

RAW CANDIDATES:
{chr(10).join(f"- {t}" for t in candidates)}

Return ONLY a valid JSON array of exactly {REFILL_COUNT} strings. No preamble, no markdown fences.
["Title one", "Title two", ...]"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    queue = load_json(QUEUE_PATH)
    manifest = load_json(MANIFEST_PATH)

    print(f"Queue: {len(queue)} items | Threshold: {REFILL_THRESHOLD}")

    if len(queue) >= REFILL_THRESHOLD:
        print("Queue sufficiently full. No refill needed.")
        return

    print(f"Refilling — targeting {REFILL_COUNT} new topics...\n")

    existing_titles = [p["title"] for p in manifest]
    raw_topics = []
    source_log = []

    # 1. Reddit
    print("[Reddit]")
    for subreddit in SUBREDDITS:
        results = get_reddit_topics(subreddit)
        raw_topics.extend(results)
        print(f"  r/{subreddit}: {len(results)}")
        time.sleep(0.4)
    source_log.append(f"Reddit ({len(SUBREDDITS)} subreddits)")

    # 2. Google PAA
    print("\n[Google PAA]")
    for query in SEARCH_QUERIES[:6]:
        results = get_google_paa(query)
        raw_topics.extend(results)
        print(f"  '{query[:45]}': {len(results)}")
    source_log.append("Google PAA")

    # 3. PubMed
    print("\n[PubMed]")
    pubmed = get_pubmed_topics()
    raw_topics.extend(pubmed)
    print(f"  Papers: {len(pubmed)}")
    source_log.append(f"PubMed ({len(pubmed)} papers)")

    # 4. RSS feeds
    print("\n[RSS Feeds]")
    for feed in RSS_FEEDS:
        results = get_rss_topics(feed)
        raw_topics.extend(results)
        print(f"  {feed['name']}: {len(results)}")
        time.sleep(0.3)
    source_log.append(f"RSS ({len(RSS_FEEDS)} feeds)")

    # 5. Fallbacks
    raw_topics.extend(FALLBACK_TOPICS)
    source_log.append("Curated fallbacks")

    print(f"\nTotal raw candidates: {len(raw_topics)}")

    # 6. Claude filter
    try:
        new_topics = filter_and_rank_topics(
            raw_topics, existing_titles, queue, " | ".join(source_log)
        )
        print(f"\nClaude selected {len(new_topics)} topics:")
    except Exception as e:
        print(f"\nClaude filtering failed: {e} — using fallbacks")
        existing_lower = {t.lower() for t in existing_titles + queue}
        new_topics = [
            t for t in FALLBACK_TOPICS
            if t.lower() not in existing_lower
        ][:REFILL_COUNT]

    # 7. Update queue
    added = 0
    for topic in new_topics:
        if topic not in queue:
            queue.append(topic)
            added += 1
            print(f"  + {topic}")

    save_json(QUEUE_PATH, queue)
    print(f"\nQueue: {added} added, {len(queue)} total.")


if __name__ == "__main__":
    main()
