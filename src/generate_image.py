"""Generate AI image from prompt using Gemini."""
import json, os, sys, urllib.error, urllib.request, base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "images"
DATA_DIR.mkdir(parents=True, exist_ok=True)
TRACKING_FILE = ROOT / "data" / "tracking.json"

def generate_image_for_prompt(prompt: str, dream_id: str):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set", file=sys.stderr)
        return None
    
    payload = {"prompt": prompt, "number_of_images": 1, "height": 1920, "width": 1080}
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateImage",
                                  data=json.dumps(payload).encode(), method="POST")
    req.add_header("x-goog-api-key", api_key)
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"Gemini API error: {e.code}", file=sys.stderr)
        return None
    
    if "images" not in result or not result["images"]:
        return None
    
    image_data = result["images"][0]["imageData"]["data"]
    image_bytes = base64.b64decode(image_data)
    image_path = DATA_DIR / f"{dream_id}.png"
    image_path.write_bytes(image_bytes)
    
    records = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    for r in records:
        if r["id"] == dream_id:
            r["image_status"] = "done"
            r["image_path"] = str(image_path.relative_to(ROOT))
    TRACKING_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return image_path

def generate_next_dreamscape():
    records = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    candidate = next((r for r in records if r.get("image_status") == "pending"), None)
    if not candidate:
        print("No pending prompts", file=sys.stderr)
        return None
    result = generate_image_for_prompt(candidate["prompt"], candidate["id"])
    if result:
        print(json.dumps(candidate, indent=2))
    return result

if __name__ == "__main__":
    generate_next_dreamscape()
