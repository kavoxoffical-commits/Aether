"""
Motion effects module for Paradise.

Adds subtle, slow motion to static images:
- Gentle zoom (Ken Burns)
- Panning
- Fade in/out
- Slight color shift
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "images"
RENDER_DIR = ROOT / "data" / "render"
RENDER_DIR.mkdir(parents=True, exist_ok=True)
TRACKING_FILE = ROOT / "data" / "tracking.json"

DURATION = 30  # seconds per dreamscape
TARGET_W, TARGET_H = 1080, 1920

def add_motion_to_image(image_path: Path, dream_id: str):
    """Add motion effects to static image using ffmpeg."""
    # Ken Burns zoom (slow zoom in over duration)
    # + gentle fade in
    # + slight color enhancement
    
    filter_chain = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        f"zoompan=z='min(zoom+0.0005,1.1)':d={DURATION * 30}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,"
        "fade=t=in:st=0:d=2,"
        "eq=contrast=1.05:saturation=1.1"
    )
    
    output_path = RENDER_DIR / f"{dream_id}_motion.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(DURATION), "-i", str(image_path),
        "-vf", filter_chain,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg failed: {result.stderr[-1000:]}", file=sys.stderr)
        return None
    
    return output_path

def add_motion_to_next():
    """Find next dreamscape with image but no motion, add effects."""
    records = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    candidate = next(
        (r for r in records 
         if r.get("image_status") == "done" and r.get("motion_status") == "pending"),
        None,
    )
    
    if not candidate:
        print("No dreamscape waiting for motion effects", file=sys.stderr)
        return None
    
    image_path = ROOT / candidate["image_path"]
    motion_path = add_motion_to_image(image_path, candidate["id"])
    
    if motion_path:
        for r in records:
            if r["id"] == candidate["id"]:
                r["motion_status"] = "done"
                r["motion_path"] = str(motion_path.relative_to(ROOT))
                break
        TRACKING_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        return candidate
    
    return None

if __name__ == "__main__":
    result = add_motion_to_next()
    if result:
        print(json.dumps(result, indent=2))
    else:
        sys.exit(1)
