"""Select ambient audio for dreamscape."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACKING_FILE = ROOT / "data" / "tracking.json"

SOUND_PACKS = {
    "ethereal": "ambient.wav",
    "cyberpunk": "synth.wav",
    "nature": "forest.wav",
    "underwater": "water.wav",
    "space": "cosmic.wav",
}

def select_audio_for_next():
    records = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    candidate = next((r for r in records if r.get("motion_status") == "done" and r.get("audio_status") == "pending"), None)
    if not candidate:
        print("No videos waiting for audio", file=sys.stderr)
        return None
    prompt = candidate.get("prompt", "").lower()
    if any(w in prompt for w in ["cyber", "neon", "tech"]):
        aesthetic = "cyberpunk"
    elif any(w in prompt for w in ["water", "ocean"]):
        aesthetic = "underwater"
    elif any(w in prompt for w in ["forest", "nature"]):
        aesthetic = "nature"
    elif any(w in prompt for w in ["space", "star"]):
        aesthetic = "space"
    else:
        aesthetic = "ethereal"
    
    for r in records:
        if r["id"] == candidate["id"]:
            r["audio_status"] = "done"
            r["audio_aesthetic"] = aesthetic
    TRACKING_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return candidate

if __name__ == "__main__":
    result = select_audio_for_next()
    if result:
        print(json.dumps(result, indent=2))
    else:
        sys.exit(1)
