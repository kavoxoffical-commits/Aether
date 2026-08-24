"""
Research + Verification module.

Uses the Anthropic API (with web_search tool) to:
1. Discover a candidate "weird fact" in one of the project's categories.
2. Cross-check it against sources before accepting it as verified.
3. Reject duplicates by checking data/tracking/facts.json.

Requires env var: ANTHROPIC_API_KEY

Output: appends a verified fact object to data/tracking/facts.json
{
  "id": "fact_0001",
  "topic": "...",
  "category": "...",
  "fact": "...",
  "sources": ["..."],
  "verification_status": "verified" | "unverified" | "rejected",
  "script_status": "pending",
  "audio_status": "pending",
  "visual_status": "pending",
  "render_status": "pending",
  "upload_status": "pending",
  "youtube_url": null,
  "published_date": null
}
"""

import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parents[2]
TRACKING_FILE = ROOT / "data" / "tracking" / "facts.json"

CATEGORIES = [
    "Weird Facts", "Strange Facts", "Science", "Animals", "Human Body",
    "Space", "History", "Geography", "Nature", "Psychology",
    "Technology", "Strange Events",
]

RESEARCH_PROMPT = """You are a fact-finding researcher for a "Weird Facts" YouTube Shorts channel.

Find ONE surprising, verifiable, "I didn't know that!" fact in the category: {category}

Rules:
- It must be genuinely surprising, not a commonly-known fact.
- It must be checkable against real sources (use web search).
- Do NOT invent or embellish anything.
- Avoid these already-used facts (do not repeat or lightly rephrase them):
{used_facts}

Respond ONLY with a JSON object, no other text, no markdown fences:
{{
  "topic": "short topic name",
  "fact": "the fact, 1-3 sentences, written for a voiceover script",
  "sources": ["source name or url", "..."],
  "confidence": "high" | "medium" | "low"
}}

Set confidence to "low" if you could not find at least one credible source confirming it.
"""


def load_tracking():
    if TRACKING_FILE.exists():
        return json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    return []


def save_tracking(records):
    TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRACKING_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def next_fact_id(records):
    return f"fact_{len(records) + 1:04d}"


def extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text, flags=re.MULTILINE)
    return json.loads(text)


def find_and_verify_fact(category: str | None = None) -> dict | None:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    records = load_tracking()
    used_facts = "\n".join(f"- {r['fact']}" for r in records) or "(none yet)"
    category = category or CATEGORIES[len(records) % len(CATEGORIES)]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": RESEARCH_PROMPT.format(category=category, used_facts=used_facts),
        }],
    )

    text_blocks = [b.text for b in response.content if b.type == "text"]
    if not text_blocks:
        return None

    try:
        parsed = extract_json(text_blocks[-1])
    except (json.JSONDecodeError, IndexError):
        return None

    if parsed.get("confidence") == "low":
        return None  # not confident enough — discard, don't publish as fact

    record = {
        "id": next_fact_id(records),
        "topic": parsed["topic"],
        "category": category,
        "fact": parsed["fact"],
        "sources": parsed.get("sources", []),
        "verification_status": "verified" if parsed["confidence"] == "high" else "needs_review",
        "script_status": "pending",
        "audio_status": "pending",
        "visual_status": "pending",
        "render_status": "pending",
        "upload_status": "pending",
        "youtube_url": None,
        "published_date": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    records.append(record)
    save_tracking(records)
    return record


if __name__ == "__main__":
    category_arg = sys.argv[1] if len(sys.argv) > 1 else None
    result = find_and_verify_fact(category_arg)
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("No fact met the verification bar this run.", file=sys.stderr)
        sys.exit(1)
