"""
Script module.

Takes the oldest fact with verification_status in {"verified", "needs_review"}
and script_status == "pending", and writes a Short-ready script for it:
- A strong, varied hook (first 1-2 seconds)
- A natural, spoken-style script body (20-40 seconds when read aloud)
- No "Did you know...?" hook (explicitly banned by the project brief)
- No filler, no "Hey guys", no intro/outro fluff

Requires env var: GEMINI_API_KEY

Updates the fact record in-place in data/tracking/facts.json:
  script_status -> "done"
  adds "hook" and "script" fields
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACKING_FILE = ROOT / "data" / "tracking" / "facts.json"

GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# Track recently-used hook openings so we don't repeat the same pattern
# across consecutive videos (project rule: vary hooks, avoid "Did you know").
RECENT_HOOKS_TO_AVOID_COUNT = 8

SCRIPT_PROMPT = """You are writing a script for a "Weird Facts" YouTube Short (faceless channel).

FACT TO USE:
{fact}

STRICT RULES:
- Total spoken length: 28-38 seconds when read aloud at a natural, energetic pace (~85-115 words). Do not undershoot — a 15-second script is a FAILURE for this format.
- The hook (first 1-2 seconds / first sentence) must grab attention immediately. NO intro, no "Hey guys", no logo/channel mention, no "Did you know...?" (banned — overused).
- Do NOT reuse any of these recent hook styles/openings (write something structurally different):
{recent_hooks}
- Tone: natural, curious, dramatic and energetic — like a real person who is genuinely shocked and can't wait to tell you. Build tension before the payoff, add a vivid comparison or a 'wait, it gets weirder' beat in the middle. NOT robotic, NOT a flat list of facts, NOT boring.
- End on a punchy closing line (not a question dump, not "subscribe for more").
- Do not add any facts beyond what's provided — stay faithful to the source fact.
- Write for the ear (spoken), not for the eye (no headers, no bullet points).

Respond ONLY with a JSON object, no markdown fences:
{{
  "hook": "the opening 1-2 sentences only",
  "script": "the full script including the hook, ready for voiceover, one continuous spoken paragraph"
}}
"""


def load_tracking():
    return json.loads(TRACKING_FILE.read_text(encoding="utf-8"))


def save_tracking(records):
    TRACKING_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text, flags=re.MULTILINE)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise


def call_gemini(prompt: str) -> str:
    api_key = os.environ["GEMINI_API_KEY"]
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"},
    }
    req = urllib.request.Request(
        GEMINI_URL, data=json.dumps(body).encode("utf-8"), method="POST"
    )
    req.add_header("x-goog-api-key", api_key)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    parts = result["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts)


def recent_hooks(records):
    hooks = [r["hook"] for r in records if r.get("hook")]
    return hooks[-RECENT_HOOKS_TO_AVOID_COUNT:]


def write_script_for_next_fact():
    records = load_tracking()

    candidate = next(
        (r for r in records
         if r.get("verification_status") in ("verified", "needs_review")
         and r.get("script_status", "pending") == "pending"),
        None,
    )
    if candidate is None:
        print("No fact is waiting for a script.", file=sys.stderr)
        return None

    used_hooks = recent_hooks(records)
    hooks_text = "\n".join(f"- {h}" for h in used_hooks) or "(none yet)"

    prompt = SCRIPT_PROMPT.format(fact=candidate["fact"], recent_hooks=hooks_text)

    try:
        raw_text = call_gemini(prompt)
    except urllib.error.HTTPError as e:
        print(f"Gemini API error: {e.code} {e.read().decode()}", file=sys.stderr)
        return None

    try:
        parsed = extract_json(raw_text)
    except (json.JSONDecodeError, IndexError):
        print(f"Could not parse Gemini response as JSON. Raw response was:\n---\n{raw_text}\n---", file=sys.stderr)
        return None

    candidate["hook"] = parsed["hook"]
    candidate["script"] = parsed["script"]
    candidate["script_status"] = "done"

    save_tracking(records)
    return candidate


if __name__ == "__main__":
    result = write_script_for_next_fact()
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        sys.exit(1)
