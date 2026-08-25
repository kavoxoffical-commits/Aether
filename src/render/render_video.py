"""
Render module.

Takes the oldest fact with visual_status == "done" and render_status ==
"pending", and combines:
- the voiceover audio
- the visual beat clips (scaled/cropped to 9:16)
- burned-in captions (synced to the audio duration, split by word count)

into one final vertical (1080x1920) MP4 using ffmpeg (pre-installed on
GitHub Actions runners — no paid service, no extra install needed).

Project rules honored here:
- No background music — voice + SFX-free for now (SFX pass can be layered
  in later without changing this module's contract).
- 9:16 vertical, no single static image for the whole video.
- Captions are large, clear, phone-friendly, synced to the audio.

Requires: ffmpeg + ffprobe on PATH (present by default on ubuntu-latest).

Output: data/render/<fact_id>.mp4
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACKING_FILE = ROOT / "data" / "tracking" / "facts.json"
RENDER_DIR = ROOT / "data" / "render"

TARGET_W, TARGET_H = 1080, 1920
WORDS_PER_CAPTION_CHUNK = 5


def load_tracking():
    return json.loads(TRACKING_FILE.read_text(encoding="utf-8"))


def save_tracking(records):
    TRACKING_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def ffprobe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def format_srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def build_srt(script: str, total_duration: float, out_path: Path):
    words = script.split()
    chunks = [
        words[i:i + WORDS_PER_CAPTION_CHUNK]
        for i in range(0, len(words), WORDS_PER_CAPTION_CHUNK)
    ]
    per_chunk = total_duration / max(len(chunks), 1)

    lines = []
    for i, chunk in enumerate(chunks):
        start = i * per_chunk
        end = start + per_chunk
        lines.append(str(i + 1))
        lines.append(f"{format_srt_time(start)} --> {format_srt_time(end)}")
        lines.append(" ".join(chunk))
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def render_video(fact: dict, out_path: Path):
    audio_path = ROOT / fact["audio_path"]
    beats = fact["visual_beats"]
    total_duration = ffprobe_duration(audio_path)
    per_beat_duration = total_duration / len(beats)

    srt_path = RENDER_DIR / f"{fact['id']}.srt"
    build_srt(fact["script"], total_duration, srt_path)

    inputs = []
    filter_parts = []
    for i, beat in enumerate(beats):
        clip_path = ROOT / beat["path"]
        inputs += ["-i", str(clip_path)]
        if beat["type"] == "video":
            filter_parts.append(
                f"[{i}:v]scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,"
                f"crop={TARGET_W}:{TARGET_H},trim=duration={per_beat_duration:.3f},"
                f"setpts=PTS-STARTPTS,fps=30[v{i}]"
            )
        else:
            # static photo: loop it for the beat's duration
            filter_parts.append(
                f"[{i}:v]scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,"
                f"crop={TARGET_W}:{TARGET_H},loop=loop=-1:size=1,"
                f"trim=duration={per_beat_duration:.3f},setpts=PTS-STARTPTS,fps=30[v{i}]"
            )

    concat_inputs = "".join(f"[v{i}]" for i in range(len(beats)))
    filter_parts.append(f"{concat_inputs}concat=n={len(beats)}:v=1:a=0[vconcat]")

    # Burn in captions (subtitles filter needs a POSIX-escaped path)
    srt_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")
    filter_parts.append(
        f"[vconcat]subtitles='{srt_escaped}':force_style="
        f"'FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,"
        f"OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=120'[vout]"
    )

    filter_complex = ";".join(filter_parts)

    audio_input_index = len(beats)
    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", f"{audio_input_index}:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k",
        "-shortest",
        str(out_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ffmpeg failed:\n" + result.stderr[-4000:], file=sys.stderr)
        return False
    return True


def render_next_fact():
    records = load_tracking()

    candidate = next(
        (r for r in records
         if r.get("visual_status") == "done"
         and r.get("render_status", "pending") == "pending"),
        None,
    )
    if candidate is None:
        print("No fact is waiting for render.", file=sys.stderr)
        return None

    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RENDER_DIR / f"{candidate['id']}.mp4"

    if not render_video(candidate, out_path):
        return None

    candidate["render_status"] = "done"
    candidate["render_path"] = str(out_path.relative_to(ROOT))
    save_tracking(records)
    return candidate


if __name__ == "__main__":
    result = render_next_fact()
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        sys.exit(1)
