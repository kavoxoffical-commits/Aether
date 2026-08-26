"""Upload dreamscape videos to YouTube Shorts."""
import json, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACKING_FILE = ROOT / "data" / "tracking.json"

# NOTE: Actual YouTube upload requires:
# 1. google-auth-oauthlib (pip install)
# 2. OAuth 2.0 credentials from Google Cloud Console
# 3. YouTube Data API enabled
# This is a placeholder for manual review before upload

def upload_next_dreamscape():
    records = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    candidate = next((r for r in records if r.get("render_status") == "done" and r.get("upload_status") != "done"), None)
    
    if not candidate:
        print("No dreamscapes ready for upload", file=sys.stderr)
        return None
    
    video_path = ROOT / candidate.get("final_path", "")
    
    if not video_path.exists():
        print(f"Video file not found: {video_path}", file=sys.stderr)
        return None
    
    # Placeholder: Mark as pending review
    for r in records:
        if r["id"] == candidate["id"]:
            r["upload_status"] = "pending_review"
            r["video_ready"] = str(video_path)
    
    TRACKING_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Video ready for review: {video_path}")
    return candidate

if __name__ == "__main__":
    result = upload_next_dreamscape()
    if result:
        print(json.dumps(result, indent=2))
    else:
        sys.exit(1)
