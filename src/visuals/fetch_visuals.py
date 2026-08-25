"""
Visuals module.

Takes the oldest fact with audio_status == "done" and visual_status == "pending",
uses Gemini to break the script into 3-6 short visual "beats" (search queries
tied to what's being said at that moment), then fetches a matching photo or
video clip per beat from Pexels (free stock media).

Rules from the project brief:
- No single static image for the whole video — each beat gets its own visual.
- Visuals must actually relate to what the voice is saying at that moment.
- Mix of photos and video clips where available (prefer video clips; fall
  back to photos when no good video match exists).

Requires env vars: GEMINI_API_KEY, PEXELS_API_KEY

Downloads assets into data/visuals/<fact_id>/beat_<n>.<ext> and updates the
tracking record with the beat list + asset paths.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACKING_FILE = ROOT / "data" / "tracking" / "facts.json"
VISUALS_DIR = ROOT / "data" / "visuals"

GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

BEATS_PROMPT = """Break this Short video script into 3-6 sequential visual "beats".

SCRIPT:
{script}

For each beat, give a short stock-footage search query (2-4 words, concrete,
visual, in English) that matches what's being said at that point. Prefer
concrete nouns/scenes over abstract concepts (e.g. "pigeon close up" not
"intelligence"). Cover the whole script in order, roughly evenly spaced.

Respond ONLY with a JSON object, no markdown fences:
{{
  "beats": [
    {{"query": "search query here"}},
    ...
  ]
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


def pexels_search(query: str, kind: str):
    """kind: 'videos' or 'photos'"""
    api_key = os.environ["PEXELS_API_KEY"]
    path = "videos/search" if kind == "videos" else "v1/search"
    url = f"https://api.pexels.com/{path}?query={urllib.parse.quote(query)}&per_page=3&orientation=portrait"
    req = urllib.request.Request(url)
    req.add_header("Authorization", api_key)
    req.add_header("User-Agent", "Mozilla/5.0 (compatible; AetherBot/1.0)")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))



def best_video_url(video_obj):
    files = sorted(
        video_obj.get("video_files", []),
        key=lambda f: f.get("width", 0),
    )
    # prefer something reasonably small/portrait-ish for a Short, not the largest 4K file
    for f in files:
        if f.get("width", 0) and f["width"] <= 1080:
            return f["link"]
    return files[-1]["link"] if files else None


def download(url: str, dest: Path):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())


def fetch_visual_for_beat(query: str, out_dir: Path, index: int) -> dict | None:
    # Try video first
    try:
        video_results = pexels_search(query, "videos")
        videos = video_results.get("videos", [])
    except urllib.error.HTTPError as e:
        print(f"Pexels video search error for '{query}': {e.code}", file=sys.stderr)
        videos = []

    if videos:
        url = best_video_url(videos[0])
        if url:
            dest = out_dir / f"beat_{index}.mp4"
            download(url, dest)
            return {"query": query, "type": "video", "path": str(dest.relative_to(ROOT))}

    # Fall back to a photo
    try:
        photo_results = pexels_search(query, "photos")
        photos = photo_results.get("photos", [])
    except urllib.error.HTTPError as e:
        print(f"Pexels photo search error for '{query}': {e.code}", file=sys.stderr)
        photos = []

    if photos:
        url = photos[0]["src"]["large"]
        dest = out_dir / f"beat_{index}.jpg"
        download(url, dest)
        return {"query": query, "type": "photo", "path": str(dest.relative_to(ROOT))}

    return None


def fetch_visuals_for_next_fact():
    records = load_tracking()

    candidate = next(
        (r for r in records
         if r.get("audio_status") == "done"
         and r.get("visual_status", "pending") == "pending"),
        None,
    )
    if candidate is None:
        print("No fact is waiting for visuals.", file=sys.stderr)
        return None

    prompt = BEATS_PROMPT.format(script=candidate["script"])
    try:
        raw_text = call_gemini(prompt)
        beats_plan = extract_json(raw_text)["beats"]
    except (urllib.error.HTTPError, json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Could not get visual beats: {e}", file=sys.stderr)
        return None

    out_dir = VISUALS_DIR / candidate["id"]
    out_dir.mkdir(parents=True, exist_ok=True)

    assets = []
    for i, beat in enumerate(beats_plan):
        asset = fetch_visual_for_beat(beat["query"], out_dir, i)
        if asset:
            assets.append(asset)
        else:
            print(f"No visual found for beat query: {beat['query']}", file=sys.stderr)

    if not assets:
        print("No visuals could be fetched for this fact.", file=sys.stderr)
        return None

    candidate["visual_beats"] = assets
    candidate["visual_status"] = "done"
    save_tracking(records)
    return candidate


if __name__ == "__main__":
    result = fetch_visuals_for_next_fact()
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        sys.exit(1)
