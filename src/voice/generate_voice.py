"""
Voice module (Voiceover generation).

Uses edge-tts (free, no API key — uses Microsoft Edge's public neural TTS
service) to turn the script into a natural-sounding voiceover.

Takes the oldest fact with script_status == "done" and audio_status == "pending",
generates an MP3, saves it under data/audio/<fact_id>.mp3, and updates the
tracking record.

Rules from the project brief:
- Natural, clear, curious, slightly dramatic — not robotic.
- We rotate between a few different neural voices across videos so not
  every video sounds identical (project rule: avoid "same everything").
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACKING_FILE = ROOT / "data" / "tracking" / "facts.json"
AUDIO_DIR = ROOT / "data" / "audio"

# A rotating pool of natural-sounding English neural voices (free via edge-tts).
# Mixed genders/accents so consecutive videos don't sound identical.
VOICE_POOL = [
    "en-US-AndrewNeural",
    "en-US-AriaNeural",
    "en-GB-RyanNeural",
    "en-US-GuyNeural",
    "en-AU-NatashaNeural",
]

# Slightly brisk, energetic pace fits a Shorts hook-driven script.
RATE = "+2%"  # slower, more natural dramatic pacing (was too rushed at +8%)


def load_tracking():
    return json.loads(TRACKING_FILE.read_text(encoding="utf-8"))


def save_tracking(records):
    TRACKING_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def pick_voice(records):
    # Rotate based on how many facts already have audio, so we cycle
    # through the pool instead of repeating the same voice back-to-back.
    used_count = sum(1 for r in records if r.get("voice_used"))
    return VOICE_POOL[used_count % len(VOICE_POOL)]


def generate_voiceover_for_next_fact():
    records = load_tracking()

    candidate = next(
        (r for r in records
         if r.get("script_status") == "done"
         and r.get("audio_status", "pending") == "pending"),
        None,
    )
    if candidate is None:
        print("No fact is waiting for a voiceover.", file=sys.stderr)
        return None

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    out_path = AUDIO_DIR / f"{candidate['id']}.mp3"
    voice = pick_voice(records)

    result = subprocess.run(
        [
            "edge-tts",
            "--voice", voice,
            "--rate", RATE,
            "--text", candidate["script"],
            "--write-media", str(out_path),
        ],
        capture_output=True, text=True,
    )

    if result.returncode != 0 or not out_path.exists():
        print(f"edge-tts failed: {result.stderr}", file=sys.stderr)
        return None

    candidate["voice_used"] = voice
    candidate["audio_path"] = str(out_path.relative_to(ROOT))
    candidate["audio_status"] = "done"

    save_tracking(records)
    return candidate


if __name__ == "__main__":
    result = generate_voiceover_for_next_fact()
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        sys.exit(1)
