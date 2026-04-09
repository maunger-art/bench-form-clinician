"""
scrape_topics.py — Automatically refills queue.json with high-value article topics
scraped from Reddit, Google People Also Ask, and curated MSK keyword clusters.

Runs before generate_post.py in the daily GitHub Actions workflow.
Only adds topics when queue.json has fewer than 7 items remaining.
"""

import json
import re
import time
import urllib.request
import urllib.parse
from pathlib import Path

import anthropic

BASE_DIR = Path(__file__).parent
QUEUE_PATH = BASE_DIR / "queue.json"
MANIFEST_PATH = BASE_DIR / "posts_manifest.json"

# Minimum queue size before we refill
REFILL_THRESHOLD = 7
# How many new topics to add per refill
REFILL_COUNT = 14

# Reddit communities to scrape for MSK questions
SUBREDDITS = [
    "physio",
    "physicaltherapy",
    "sportsrehab",
    "running",
    "cycling",
    "weightlifting",
    "tennis",
    "golf",
    "backpain",
    "kneeinjury",
    "ACL",
]

# Seed search queries for Google PAA scraping
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

# Curated fallback topics per cluster — used when scraping yields insufficient results
FALLBACK_TOPICS = [
    # Objective Assessment
    "How to Use Handheld Dynamometry in a Standard Physiotherapy Appointment",
    "Normative Strength Data for Lower Limb Rehabilitation: A Clinical Reference",
    "Single-Leg Hop Testing: How to Administer, Score, and Interpret Results",
    "Range of Motion Assessment in Physiotherapy: Improving Consistency Across Clinicians",
    "Functional Movement Screening in MSK Physiotherapy: What the Evidence Supports",
    # MSK Outcomes
    "Hamstring Strain Rehabilitation: Criteria-Based Return to Sport Protocols",
    "Patellofemoral Pain in Runners: Assessment Findings and Exercise Progressions",
    "Shoulder Impingement vs Rotator Cuff Tear: Clinical Differentiation and Management",
    "Ankle Sprain Rehabilitation: From Acute Management to Return to Sport",
    "Hip Osteoarthritis Conservative Management: What Physiotherapy Can and Cannot Do",
    "Achilles Tendinopathy: The Evidence for Loading vs Rest",
    "Meniscal Tear Without Surgery: When Physiotherapy Is Enough",
    "Plantar Fasciitis Management: Load Management and Exercise Protocols",
    "Cervical Radiculopathy: Conservative Management in Primary Care Physiotherapy",
    "Groin Pain in Athletes: Differential Diagnosis and Rehabilitation",
    # Clinical Decision-Making
    "Red Flags in MSK Assessment: What Every Physiotherapist Must Screen For",
    "When to Refer for Imaging in MSK Physiotherapy: Clinical Decision Rules",
    "Pain Education in Physiotherapy: How to Explain Central Sensitisation to Patients",
    "Setting Rehabilitation Goals with Patients: Outcome Measure Selection in Practice",
    "Stratifying MSK Patients by Complexity: A Framework for Caseload Management",
    # Clinic Business
    "How to Build a Physiotherapy Referral Network with GPs and Consultants",
    "Physiotherapy Outcome Reporting for Private Medical Insurance: What Insurers Want",
    "Patient Retention in Physiotherapy: Why Patients Drop Out and How to Reduce It",
    "Pricing Physiotherapy Services: How to Communicate Value Beyond Session Cost",
    "Building a Physiotherapy Brand on LinkedIn: What Actually Works",
    # Cost of MSK Inaction
    "The Cost of Delayed Physiotherapy: What the Evidence Says About Early Intervention",
    "MSK Conditions and Workplace Absence: The Case for Employer-Funded Physiotherapy",
    "Avoiding Unnecessary Physiotherapy Referrals: How Objective Data Changes the Picture",
    "Physiotherapy vs Surgery for Common MSK Conditions: A Comparative Evidence Review",
    "Value-Based Healthcare in Physiotherapy: What Outcomes-Based Contracting Looks Like",
    # Technology
    "Telehealth Physiotherapy for MSK Conditions: Evidence, Limitations, and Best Practice",
    "AI in Physiotherapy Clinical Decision Support: Where the Technology Actually Stands",
    "Digital Exercise Prescription in Physiotherapy: Platforms, Evidence, and Patient Uptake",
    "Wearable Technology in MSK Rehabilitation: What Data Is Actually Clinically Useful",
    "Electronic Outcome Measurement in Physiotherapy: Implementation Without the Burden",
]


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_reddit_questions(subreddit: str, limit: int = 25) -> list[str]:
    """Fetch top questions from a subreddit using Reddit's JSON API."""
    questions = []
    try:
        url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={limit}&t=month"
        req = urllib.request.Request(url, headers={"User-Agent": "BenchmarkPS-BlogBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            posts = data.get("data", {}).get("children", [])
            for post in posts:
                title = post.get("data", {}).get("title", "")
                # Only keep posts that look like questions or topics
                if any(kw in title.lower() for kw in [
                    "how", "what", "why", "when", "should", "best", "help",
                    "pain", "injury", "rehab", "physio", "exercise", "strength",
                    "return", "surgery", "recovery", "assessment", "treatment"
                ]):
                    questions.append(title)
    except Exception as e:
        print(f"  Reddit {subreddit}: {e}")
    return questions


def get_google_paa(query: str) -> list[str]:
    """Scrape Google's 'People Also Ask' questions for a search query."""
    questions = []
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded}&hl=en"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept-Language": "en-GB,en;q=0.9",
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
            # Extract PAA questions from data-q attributes and jsname patterns
            patterns = [
                r'data-q="([^"]{20,120})"',
                r'"([^"]{20,120}\?)"',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, html)
                for match in matches:
                    if "?" in match and len(match) > 20:
                        questions.append(match)
        time.sleep(1)  # Be polite
    except Exception as e:
        print(f"  Google PAA '{query}': {e}")
    return questions


def filter_and_rank_topics(
    raw_topics: list[str],
    existing_titles: list[str],
    existing_queue: list[str]
) -> list[str]:
    """Use Claude to filter, deduplicate, and rank topics by clinical relevance."""
    client = anthropic.Anthropic()

    existing_all = set(t.lower() for t in existing_titles + existing_queue)

    # Pre-filter obvious duplicates
    candidates = []
    for topic in raw_topics:
        topic = topic.strip()
        if len(topic) < 15 or len(topic) > 200:
            continue
        # Skip if too similar to existing
        if any(
            topic.lower()[:30] in existing.lower() or existing.lower()[:30] in topic.lower()
            for existing in existing_all
        ):
            continue
        candidates.append(topic)

    if not candidates:
        return []

    # Deduplicate
    candidates = list(dict.fromkeys(candidates))[:60]

    prompt = f"""You are a content strategist for Benchmark PS, a physiotherapy outcomes platform.

Below is a list of raw topic candidates scraped from Reddit and Google. Your job is to:
1. Select the {REFILL_COUNT} most valuable topics for a physiotherapy clinic audience
2. Rewrite each as a compelling, specific article title (not a question — a statement or guide title)
3. Prioritise topics about: MSK assessment, clinical decision-making, rehabilitation protocols, 
   outcomes measurement, clinic management, and the business case for physiotherapy
4. Avoid: generic wellness content, nutrition, mental health unless directly MSK-related,
   anything already well covered by the existing posts

Existing posts to avoid duplicating:
{chr(10).join(f"- {t}" for t in existing_titles[:20])}

Raw candidates:
{chr(10).join(f"- {t}" for t in candidates)}

Return ONLY a JSON array of {REFILL_COUNT} article title strings. No other text.
Example: ["Title one", "Title two", ...]"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


def main():
    queue = load_json(QUEUE_PATH)
    manifest = load_json(MANIFEST_PATH)

    print(f"Queue has {len(queue)} items. Threshold: {REFILL_THRESHOLD}")

    if len(queue) >= REFILL_THRESHOLD:
        print("Queue is sufficiently full. No refill needed.")
        return

    print(f"Refilling queue with {REFILL_COUNT} new topics...")

    existing_titles = [p["title"] for p in manifest]
    raw_topics = []

    # 1. Scrape Reddit
    print("Scraping Reddit...")
    for subreddit in SUBREDDITS[:6]:  # Limit to avoid rate limiting
        questions = get_reddit_questions(subreddit, limit=20)
        raw_topics.extend(questions)
        print(f"  r/{subreddit}: {len(questions)} candidates")
        time.sleep(0.5)

    # 2. Scrape Google PAA
    print("Scraping Google PAA...")
    for query in SEARCH_QUERIES[:5]:  # Limit to avoid blocks
        questions = get_google_paa(query)
        raw_topics.extend(questions)
        print(f"  '{query}': {len(questions)} candidates")

    # 3. Add curated fallbacks to ensure we always have enough
    raw_topics.extend(FALLBACK_TOPICS)

    print(f"Total raw candidates: {len(raw_topics)}")

    # 4. Filter and rank with Claude
    if raw_topics:
        try:
            new_topics = filter_and_rank_topics(raw_topics, existing_titles, queue)
            print(f"Claude selected {len(new_topics)} topics")
        except Exception as e:
            print(f"Claude filtering failed: {e}. Using fallback topics directly.")
            # Use fallbacks directly, filtering obvious duplicates
            existing_lower = {t.lower() for t in existing_titles + queue}
            new_topics = [
                t for t in FALLBACK_TOPICS
                if t.lower() not in existing_lower
            ][:REFILL_COUNT]

    # 5. Add to queue
    for topic in new_topics:
        if topic not in queue:
            queue.append(topic)

    save_json(QUEUE_PATH, queue)
    print(f"Queue now has {len(queue)} items.")
    for t in new_topics:
        print(f"  + {t}")


if __name__ == "__main__":
    main()
