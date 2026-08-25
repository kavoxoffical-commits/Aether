"""
Render module.

Takes the oldest fact with visual_status == "done" and render_status ==
"pending", and combines:
- the voiceover audio
- the visual beat clips (scaled/cropped to 9:16, with a subtle Ken Burns
  zoom so nothing looks like a static slideshow)
- a hook "whoosh" + soft "pop" transitions between beats (synthesized with
  ffmpeg itself — zero cost, zero extra assets)
- burned-in captions: bold, bottom-third, semi-transparent background box
  (readable on any background, not floating in the middle of the frame)

into one final vertical (1080x1920) MP4 using ffmpeg.

Project rules honored here:
- No background music — SFX only (short whoosh/pop), per the project brief.
- 9:16 vertical, no single static image for the whole video, motion on
  every beat.
- Captions are large, clear, phone-friendly, synced to the audio, sit low
  on the frame (not centered) with a readable background box.

Requires: ffmpeg + ffprobe on PATH.

Output: data/render/<fact_id>.mp4
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACKING_FILE = ROOT / "data" / "tracking" / "facts.json"
RENDER_DIR = ROOT / "data" / "render"
CHARACTER_DIR = ROOT / "assets" / "character"

# Channel mascot: a small reaction bubble that sits in a corner the whole
# video and switches expression at key story moments (default/curious
# through most of it, shocked near the reveal/twist).
CHARACTER_SIZE = 230
CHARACTER_MARGIN = 36

TARGET_W, TARGET_H = 1080, 1920
WORDS_PER_CAPTION_CHUNK = 4
ZOOM_FPS = 30


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
    n_frames = int(per_beat_duration * ZOOM_FPS)

    for i, beat in enumerate(beats):
        clip_path = ROOT / beat["path"]
        inputs += ["-i", str(clip_path)]

        # Ken Burns: slow zoom-in over the beat's duration so nothing sits
        # frozen. Oversized scale first so the zoompan crop has room to move.
        if beat["type"] == "video":
            # Real video footage already has motion — just scale/crop/trim,
            # no zoompan (zoompan is for static images; applying it to a
            # multi-frame video multiplies frames catastrophically and hangs).
            base = (
                f"[{i}:v]scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,"
                f"crop={TARGET_W}:{TARGET_H},trim=duration={per_beat_duration:.3f},"
                f"setpts=PTS-STARTPTS,fps={ZOOM_FPS}"
            )
            filter_parts.append(f"{base}[v{i}]")
        else:
            # Static photo: this is exactly what zoompan is for — a slow
            # Ken Burns zoom so it doesn't look like a frozen slide.
            base = (
                f"[{i}:v]scale={TARGET_W * 2}:{TARGET_H * 2}:force_original_aspect_ratio=increase,"
                f"crop={TARGET_W * 2}:{TARGET_H * 2},loop=loop=-1:size=1,"
                f"trim=duration={per_beat_duration:.3f},setpts=PTS-STARTPTS,fps={ZOOM_FPS}"
            )
            zoom = (
                f",zoompan=z='min(zoom+0.0012,1.15)':d={max(n_frames,1)}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={TARGET_W}x{TARGET_H}:fps={ZOOM_FPS}"
            )
            filter_parts.append(f"{base}{zoom}[v{i}]")

    concat_inputs = "".join(f"[v{i}]" for i in range(len(beats)))
    filter_parts.append(f"{concat_inputs}concat=n={len(beats)}:v=1:a=0[vraw]")

    # Slight contrast/saturation lift + quick fade-in for a more "produced" look.
    filter_parts.append(
        "[vraw]eq=contrast=1.06:saturation=1.15,fade=t=in:st=0:d=0.25[vconcat]"
    )

    srt_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")
    filter_parts.append(
        f"[vconcat]subtitles='{srt_escaped}':force_style="
        f"'FontName=Arial Black,FontSize=64,Bold=1,PrimaryColour=&H00FFFFFF,"
        f"OutlineColour=&H00000000,Outline=3,BorderStyle=3,BackColour=&H99000000,"
        f"Alignment=2,MarginV=260'[vsubbed]"
    )

    # --- Channel mascot bubble (top-right corner, whole video) ---
    # Expression timeline: default (skeptical/idle) for the first ~45%,
    # curious for the next ~30% (escalation), shocked for the final ~25%
    # (reveal/twist) — until the script module tags beats with story roles
    # explicitly, this proportional split approximates it.
    char_x = TARGET_W - CHARACTER_SIZE - CHARACTER_MARGIN
    char_y = CHARACTER_MARGIN
    default_end = total_duration * 0.45
    curious_end = total_duration * 0.75

    # Character images are appended as inputs right after the beat clips
    # (before the audio input), so their indices are len(beats), len(beats)+1, len(beats)+2.
    default_idx = len(beats)
    curious_idx = len(beats) + 1
    shocked_idx = len(beats) + 2
    filter_parts.append(f"[{default_idx}:v]scale={CHARACTER_SIZE}:{CHARACTER_SIZE}[charA]")
    filter_parts.append(f"[{curious_idx}:v]scale={CHARACTER_SIZE}:{CHARACTER_SIZE}[charB]")
    filter_parts.append(f"[{shocked_idx}:v]scale={CHARACTER_SIZE}:{CHARACTER_SIZE}[charC]")
    filter_parts.append(
        f"[vsubbed][charA]overlay={char_x}:{char_y}:enable='between(t,0,{default_end:.3f})'[vc1]"
    )
    filter_parts.append(
        f"[vc1][charB]overlay={char_x}:{char_y}:enable='between(t,{default_end:.3f},{curious_end:.3f})'[vc2]"
    )
    filter_parts.append(
        f"[vc2][charC]overlay={char_x}:{char_y}:enable='between(t,{curious_end:.3f},{total_duration:.3f})'[vout]"
    )

    # --- SFX (synthesized, zero-cost): a rising "whoosh" right on the hook,
    # and a soft "pop" on every beat transition after that. Mixed under the
    # voice at low volume — no background music, per project rule.
    inputs += [
        "-i", str(CHARACTER_DIR / "bubble_default.png"),
        "-i", str(CHARACTER_DIR / "bubble_curious.png"),
        "-i", str(CHARACTER_DIR / "bubble_shocked.png"),
    ]
    audio_input_index = len(beats) + 3
    inputs += ["-i", str(audio_path)]

    sfx_parts = []
    sfx_labels = []

    # Hook whoosh: quick rising tone, 0.35s, fades out.
    sfx_parts.append(
        "aevalsrc=0.35*sin(2*PI*(500+2200*t/0.35)*t):d=0.35:s=44100,"
        "afade=t=out:st=0.2:d=0.15,volume=0.55[whoosh]"
    )
    sfx_labels.append(("[whoosh]", 0.0))

    # Soft pop at each beat transition (skip t=0, already covered by whoosh).
    t_cursor = per_beat_duration
    for i in range(1, len(beats)):
        label = f"[pop{i}]"
        sfx_parts.append(
            f"anoisesrc=d=0.08:c=pink:a=0.4,afade=t=out:st=0.02:d=0.06,volume=0.35{label}"
        )
        sfx_labels.append((label, t_cursor))
        t_cursor += per_beat_duration

    delayed_labels = []
    for idx, (label, t) in enumerate(sfx_labels):
        delay_ms = int(t * 1000)
        out_label = f"[sfxd{idx}]"
        sfx_parts.append(f"{label}adelay={delay_ms}|{delay_ms}{out_label}")
        delayed_labels.append(out_label)

    mix_inputs = "".join(delayed_labels) + f"[{audio_input_index}:a]"
    sfx_parts.append(
        f"{mix_inputs}amix=inputs={len(delayed_labels) + 1}:duration=longest:normalize=0[aout]"
    )

    filter_complex = ";".join(filter_parts + sfx_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
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
