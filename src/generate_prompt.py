"""
Prompt generator for Paradise dreamscapes.

Generates unique, surreal place descriptions for AI image generation.
Each prompt creates an impossible, beautiful world.
"""

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

PLACES = [
    "floating city", "underwater kingdom", "crystalline desert",
    "bioluminescent forest", "abandoned space station", "time-twisted architecture",
    "mountain suspended in clouds", "mirror dimension", "neon canyon",
    "petrified ocean", "prismatic cavern", "inverted sky",
    "geometric island", "liquid architecture", "star-filled void",
]

AESTHETICS = [
    "surreal, dreamlike, ethereal",
    "cyberpunk, neon-lit, dystopian",
    "mystical, enchanted, magical",
    "minimalist, geometric, abstract",
    "lush, overgrown, organic",
    "icy, crystalline, frozen",
    "warm, golden, sunset-lit",
    "cool, blue, moonlit",
]

MOODS = [
    "peaceful and serene",
    "mysterious and eerie",
    "vibrant and energetic",
    "dark and contemplative",
    "whimsical and playful",
    "monumental and vast",
]

def generate_prompt():
    """Generate a unique dreamscape prompt."""
    place = random.choice(PLACES)
    aesthetic = random.choice(AESTHETICS)
    mood = random.choice(MOODS)
    
    prompt = (
        f"A {mood} dreamscape of a {place}. "
        f"Style: {aesthetic}. "
        f"Cinematic, highly detailed, impossible yet beautiful. "
        f"Surreal and otherworldly, no people."
    )
    return prompt

def save_prompt(prompt: str, dream_id: str):
    """Save prompt to tracking file."""
    tracking_file = DATA_DIR / "tracking.json"
    
    if tracking_file.exists():
        records = json.loads(tracking_file.read_text(encoding="utf-8"))
    else:
        records = []
    
    record = {
        "id": dream_id,
        "prompt": prompt,
        "image_status": "pending",
        "motion_status": "pending",
        "audio_status": "pending",
        "render_status": "pending",
        "created_at": None,  # timestamp added by workflow
    }
    records.append(record)
    tracking_file.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return record

if __name__ == "__main__":
    prompt = generate_prompt()
    print(prompt)
    # Dream ID: timestamp-based or sequential
    dream_id = f"dream_{len(Path('data/tracking.json').read_text().count('{dream_')) + 1:04d}" if Path("data/tracking.json").exists() else "dream_0001"
    record = save_prompt(prompt, dream_id)
    print(json.dumps(record, indent=2))
