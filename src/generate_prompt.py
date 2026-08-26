"""Prompt generator for Paradise dreamscapes."""

import json
import random
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
TRACKING_FILE = DATA_DIR / "tracking.json"

PLACES = ["floating city", "underwater kingdom", "crystalline desert", "bioluminescent forest", "abandoned space station", "time-twisted architecture", "mountain suspended in clouds", "mirror dimension", "neon canyon", "petrified ocean", "prismatic cavern", "inverted sky", "geometric island", "liquid architecture", "star-filled void"]

AESTHETICS = ["surreal, dreamlike, ethereal", "cyberpunk, neon-lit, dystopian", "mystical, enchanted, magical", "minimalist, geometric, abstract", "lush, overgrown, organic", "icy, crystalline, frozen", "warm, golden, sunset-lit", "cool, blue, moonlit"]

MOODS = ["peaceful and serene", "mysterious and eerie", "vibrant and energetic", "dark and contemplative", "whimsical and playful", "monumental and vast"]

def init_tracking():
    if not TRACKING_FILE.exists():
        TRACKING_FILE.write_text(json.dumps([], ensure_ascii=False, indent=2), encoding="utf-8")

def generate_next_dreamscape():
    init_tracking()
    records = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    dream_id = f"dream_{len(records) + 1:04d}"
    place, aesthetic, mood = random.choice(PLACES), random.choice(AESTHETICS), random.choice(MOODS)
    prompt = f"A {mood} dreamscape of a {place}. Style: {aesthetic}. Cinematic, highly detailed, impossible yet beautiful. Surreal and otherworldly, no people."
    record = {"id": dream_id, "prompt": prompt, "image_status": "pending", "motion_status": "pending", "audio_status": "pending", "render_status": "pending", "created_at": datetime.utcnow().isoformat()}
    records.append(record)
    TRACKING_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(record, indent=2))

if __name__ == "__main__":
    generate_next_dreamscape()
