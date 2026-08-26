"""
Audio selection module for Paradise.

Selects appropriate ambient sounds based on dreamscape aesthetic.
For MVP: uses a small library of free ambient sounds.
(Can be extended to fetch from Freesound API later)
"""

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
AUDIO_DIR = DATA_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TRACKING_FILE = DATA_DIR / "tracking.json"

# Minimal sound palette (these would come from Freesound or generated)
SOUND_PACKS = {
    "ethereal": ["ambient_pad_1.wav", "wind_soft.wav", "chime_distant.wav"],
    "cyberpunk": ["synth_drone.wav", "digital_beep.wav", "electronic_ambient.wav"],
    "nature": ["forest_ambience.wav", "rain_light.wav", "birds_chirp.wav"],
    "underwater": ["water_flow.wav", "bubble.wav", "ocean_deep.wav"],
    "space": ["sci_fi_hum.wav", "static_cosmic.wav", "digital_sweep.wav"],
}

def get_aesthetic_from_prompt(prompt: str) -> str:
    """Infer sound pack from prompt keywords."""
    prompt_lower = prompt.lower()
    
    if any(w in prompt_lower for w in ["cyber", "neon", "tech", "digital"]):
        return "cyberpunk"
    elif any(w in prompt_lower for w in ["water", "ocean", "underwater"]):
        return "underwater"
    elif any(w in prompt_lower for w in ["forest", "nature", "organic", "garden"]):
        return "nature"
    elif any(w in prompt_lower for w in ["space", "star", "void", "cosmic"]):
        return "space"
    else:
        return "ethereal"

def select_audio_for_dreamscape(dream_id: str, prompt: str):
    """Select ambient audio based on dreamscape."""
    aesthetic = get_aesthetic_from_prompt(prompt)
    sounds = SOUND_PACKS.get(aesthetic, SOUND_PACKS["ethereal"])
    
    # For MVP: just pick one sound (later: mix multiple)
    selected_sound = random.choice(sounds)
    
    # Update tracking
    records = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    for r in records:
        if r["id"] == dream_id:
            r["audio_status"] = "done"
            r["audio_aesthetic"] = aesthetic
            r["audio_selected"] = selected_sound
            break
    
    TRACKING_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return aesthetic, selected_sound

def select_audio_for_next():
    """Find next dreamscape waiting for audio."""
    records = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    candidate = next(
        (r for r in records 
         if r.get("motion_status") == "done" and r.get("audio_status") == "pending"),
        None,
    )
    
    if not candidate:
        print("No dreamscape waiting for audio", file=__import__("sys").stderr)
        return None
    
    aesthetic, sound = select_audio_for_dreamscape(candidate["id"], candidate["prompt"])
    return candidate

if __name__ == "__main__":
    import sys
    result = select_audio_for_next()
    if result:
        print(json.dumps(result, indent=2))
    else:
        sys.exit(1)
