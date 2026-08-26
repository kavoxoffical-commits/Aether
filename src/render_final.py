"""
Render module for Paradise.

Combines motion video + ambient audio into final Shorts video.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RENDER_DIR = DATA_DIR / "render"
OUTPUT_DIR = RENDER_DIR / "final"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TRACKING_FILE = DATA_DIR / "tracking.json"

def render_final_video(motion_video_path: Path, audio_path: Path, dream_id: str):
    """Merge motion video + audio into final output."""
    output_path = OUTPUT_DIR / f"{dream_id}_final.mp4"
    
    # Simple merge: video + audio (audio loops if shorter)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(motion_video_path),
        "-i", str(audio_path),
        "-c:v", "copy",  # re-encode video isn't needed, already H.264
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(output_path),
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg render failed: {result.stderr[-1000:]}", file=sys.stderr)
        return None
    
    return output_path

def render_next_dreamscape():
    """Find next complete dreamscape and render final video."""
    records = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    candidate = next(
        (r for r in records 
         if r.get("audio_status") == "done" and r.get("render_status") == "pending"),
        None,
    )
    
    if not candidate:
        print("No complete dreamscape waiting for render", file=sys.stderr)
        return None
    
    # For MVP: use silent audio (no actual audio files yet)
    # In real implementation: find the audio file path
    motion_video = ROOT / candidate.get("motion_path", "")
    
    if not motion_video.exists():
        print(f"Motion video not found: {motion_video}", file=sys.stderr)
        return None
    
    # Generate silent audio track (fallback)
    # TODO: integrate actual audio files from Freesound
    silent_audio = DATA_DIR / "audio" / "silent.wav"
    if not silent_audio.exists():
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
            "-t", "30", "-q:a", "9",
            str(silent_audio),
        ]
        subprocess.run(cmd, capture_output=True)
    
    output_path = render_final_video(motion_video, silent_audio, candidate["id"])
    
    if output_path:
        for r in records:
            if r["id"] == candidate["id"]:
                r["render_status"] = "done"
                r["final_path"] = str(output_path.relative_to(ROOT))
                break
        TRACKING_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        return candidate
    
    return None

if __name__ == "__main__":
    result = render_next_dreamscape()
    if result:
        print(json.dumps(result, indent=2))
    else:
        sys.exit(1)
