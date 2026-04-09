"""
process_feedback.py — Processes email replies to the weekly preview email.

Runs every Wednesday at 07:00 UTC via GitHub Actions.
Reads feedback from feedback.json (manually updated from email replies for now).
Updates queue.json based on APPROVE / SKIP / EDIT / DELAY instructions.

USAGE:
After receiving the preview email, add feedback to feedback.json like:
[
  {"action": "SKIP", "number": 2},
  {"action": "EDIT", "number": 1, "new_title": "Better title here"},
  {"action": "DELAY", "number": 4}
]

Then push to GitHub — the Wednesday workflow will process it automatically.
Or run manually: python process_feedback.py
"""

import json
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).parent
QUEUE_PATH = BASE_DIR / "queue.json"
FEEDBACK_PATH = BASE_DIR / "feedback.json"
LOG_PATH = BASE_DIR / "feedback_log.json"


def load_json(path):
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def process_feedback(queue: list, feedback: list) -> tuple[list, list]:
    """Apply feedback instructions to the queue. Returns updated queue and log."""
    log = []

    # Process in reverse number order to avoid index shifting on deletes
    skips = sorted([f for f in feedback if f["action"] == "SKIP"], key=lambda x: x["number"], reverse=True)
    edits = [f for f in feedback if f["action"] == "EDIT"]
    delays = sorted([f for f in feedback if f["action"] == "DELAY"], key=lambda x: x["number"], reverse=True)
    approves = [f for f in feedback if f["action"] == "APPROVE"]

    # Log approvals
    for item in approves:
        idx = item["number"] - 1
        if 0 <= idx < len(queue):
            log.append({
                "date": date.today().isoformat(),
                "action": "APPROVE",
                "number": item["number"],
                "topic": queue[idx],
            })
            print(f"  APPROVE #{item['number']}: {queue[idx][:60]}")

    # Process SKIPs
    for item in skips:
        idx = item["number"] - 1
        if 0 <= idx < len(queue):
            topic = queue[idx]
            queue.pop(idx)
            log.append({
                "date": date.today().isoformat(),
                "action": "SKIP",
                "number": item["number"],
                "topic": topic,
            })
            print(f"  SKIP #{item['number']}: {topic[:60]}")

    # Process EDITs
    for item in edits:
        idx = item["number"] - 1
        if 0 <= idx < len(queue):
            old_topic = queue[idx]
            new_title = item.get("new_title", "").strip()
            if new_title:
                queue[idx] = new_title
                log.append({
                    "date": date.today().isoformat(),
                    "action": "EDIT",
                    "number": item["number"],
                    "old_topic": old_topic,
                    "new_topic": new_title,
                })
                print(f"  EDIT #{item['number']}: '{old_topic[:40]}' → '{new_title[:40]}'")

    # Process DELAYs
    for item in delays:
        idx = item["number"] - 1
        if 0 <= idx < len(queue):
            topic = queue.pop(idx)
            queue.append(topic)
            log.append({
                "date": date.today().isoformat(),
                "action": "DELAY",
                "number": item["number"],
                "topic": topic,
            })
            print(f"  DELAY #{item['number']}: {topic[:60]} → moved to end")

    return queue, log


def main():
    queue = load_json(QUEUE_PATH)
    feedback = load_json(FEEDBACK_PATH)

    if not feedback:
        print("No feedback to process.")
        return

    print(f"Processing {len(feedback)} feedback items...")

    updated_queue, new_log = process_feedback(queue, feedback)

    # Save updated queue
    save_json(QUEUE_PATH, updated_queue)
    print(f"\nQueue updated: {len(updated_queue)} items remaining.")

    # Append to log
    existing_log = load_json(LOG_PATH)
    existing_log.extend(new_log)
    save_json(LOG_PATH, existing_log)

    # Clear processed feedback
    save_json(FEEDBACK_PATH, [])
    print("Feedback processed and cleared.")


if __name__ == "__main__":
    main()
