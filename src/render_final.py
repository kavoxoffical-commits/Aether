"""Merge motion video + ambient audio."""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RENDER_DIR = DATA_DIR / "render"
OUTPUT_DIR = RENDER_DIR / "final"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TRACKING_FILE = DATA_DIR / "tracking.json"

def render_final_video(motion_video_path, dream_id):
    output_path = OUTPUT_DIR / f"{dream_id}.mp4"
    cmd = ["ffmpeg", "-y", "-i", str(motion_video_path), "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", str(output_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return output_path if result.returncode == 0 else None

def render_next_dreamscape():
    records = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    candidate = next((r for r in records if r.get("audio_status") == "done" and r.get("render_status") == "pending"), None)
    if not candidate:
        print("No complete dreamscapes waiting", file=sys.stderr)
        return None
    motion_video = ROOT / candidate.get("motion_path", "")
    if not motion_video.exists():
        print(f"Motion video not found", file=sys.stderr)
        return None
    output_path = render_final_video(motion_video, candidate["id"])
    if output_path:
        for r in records:
            if r["id"] == candidate["id"]:
                r["render_status"] = "done"
                r["final_path"] = str(output_path.relative_to(ROOT))
        TRACKING_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return candidate

if __name__ == "__main__":
    result = render_next_dreamscape()
    if result:
        print(json.dumps(result, indent=2))
    else:
        sys.exit(1)
