"""Generate dreamscape prompt"""
import json
import random
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
TRACKING_FILE = DATA_DIR / "tracking.json"

PLACES = ["floating city", "underwater kingdom", "crystalline desert", "bioluminescent forest", "abandoned space station"]
AESTHETICS = ["surreal, dreamlike", "cyberpunk, neon-lit", "mystical, enchanted"]
MOODS = ["peaceful and serene", "mysterious and eerie"]

def init_tracking():
    if not TRACKING_FILE.exists():
        TRACKING_FILE.write_text(json.dumps([], ensure_ascii=False, indent=2), encoding="utf-8")

def generate():
    init_tracking()
    records = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    dream_id = f"dream_{len(records) + 1:04d}"
    prompt = f"A {random.choice(MOODS)} dreamscape of a {random.choice(PLACES)}. Style: {random.choice(AESTHETICS)}."
    record = {"id": dream_id, "prompt": prompt, "image_status": "pending", "motion_status": "pending", "audio_status": "pending", "render_status": "pending", "created_at": datetime.now().isoformat()}
    records.append(record)
    TRACKING_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Generated: {dream_id}")

if __name__ == "__main__":
    generate()
