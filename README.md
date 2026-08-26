# Paradise

**AI-Generated Dreamscapes | Ambient Worlds | Impossible Places**

Fully automated generator for surreal, ethereal video content. Each dreamscape is a unique impossible world with ambient soundscapes, generated and rendered daily.

## What is Paradise?

Paradise generates beautiful, surreal video dreamscapes with zero creative input required:
- 🎨 AI-generated surreal worlds (Gemini 2.0)
- 🎬 Subtle motion effects (Ken Burns zoom)
- 🔊 Ambient soundscapes (auto-selected per aesthetic)
- 🚀 Fully automated pipeline
- 📱 Optimized for YouTube Shorts (1080x1920, 30s)

## Features

✅ **Automated Daily Generation** — One complete dreamscape every day
✅ **No Manual Input** — Fully automated from prompt to final video
✅ **Free & Open** — Zero paid services, 100% free tier APIs
✅ **Quality Output** — Cinematic surreal visuals + atmospheric audio
✅ **Workflow Flexibility** — Run steps individually or full pipeline

## Pipeline

1. **Generate Prompt** — Random surreal place description
2. **Generate Image** — AI image from Gemini 2.0 Flash
3. **Add Motion** — Ken Burns zoom effect + fade-in
4. **Select Audio** — Ambient sounds matched to aesthetic
5. **Render Final** — Merge video + audio into MP4
6. **Prepare Upload** — Ready for YouTube Shorts

## Workflows

### Manual Execution (Test Mode)
Trigger individual steps via GitHub Actions:

- **1-prompt.yml** — Generate dreamscape prompt
- **2-image.yml** — Generate AI image (requires `GEMINI_API_KEY` secret)
- **3-motion.yml** — Add motion effects
- **4-audio.yml** — Select ambient audio
- **5-render.yml** — Render final video
- **6-upload.yml** — Prepare for upload

### Full Pipeline (Recommended)
Run entire pipeline in one go:

- **0-full-pipeline.yml** — Complete dreamscape generation (scheduled daily at 9 AM UTC)

## Setup

### Requirements
- Python 3.12+
- FFmpeg (auto-installed in workflows)
- GitHub Actions (free tier sufficient)

### Secrets
Add to GitHub repository Settings → Secrets and variables → Actions:

```
GEMINI_API_KEY = <your Gemini API key>
```

Get key: https://aistudio.google.com/apikey

## Directory Structure

```
Paradise/
├── README.md
├── requirements.txt
├── .gitignore
├── .github/workflows/
│   ├── 0-full-pipeline.yml
│   ├── 1-prompt.yml
│   ├── 2-image.yml
│   ├── 3-motion.yml
│   ├── 4-audio.yml
│   ├── 5-render.yml
│   └── 6-upload.yml
├── src/
│   ├── generate_prompt.py
│   ├── generate_image.py
│   ├── add_motion.py
│   ├── select_audio.py
│   ├── render_final.py
│   └── upload.py
└── data/
    ├── tracking.json
    ├── images/
    ├── render/
    │   ├── motion/
    │   └── final/
    └── audio/
```

## Tracking System

All dreamscapes are tracked in `data/tracking.json`:

```json
{
  "id": "dream_0001",
  "prompt": "A peaceful dreamscape of a floating city...",
  "image_status": "done",
  "motion_status": "done",
  "audio_status": "done",
  "render_status": "done",
  "upload_status": "pending_review",
  "image_path": "data/images/dream_0001.png",
  "motion_path": "data/render/dream_0001_motion.mp4",
  "final_path": "data/render/final/dream_0001.mp4",
  "created_at": "2026-08-27T09:00:00.000000"
}
```

## Quick Start

1. **Fork/Clone** this repo
2. **Add** `GEMINI_API_KEY` to GitHub Secrets
3. **Trigger** `0-full-pipeline.yml` (manual dispatch)
4. **Watch** it generate a complete dreamscape (~5-10 minutes)
5. **Review** final video in `data/render/final/`

## Technologies

- **Gemini 2.0 Flash** — AI image generation
- **FFmpeg** — Video processing & rendering
- **Python 3.12** — Orchestration
- **GitHub Actions** — CI/CD & scheduling

## Status

| Component | Status |
|-----------|--------|
| Prompt Generation | ✅ Working |
| Image Generation | ✅ Working |
| Motion Effects | ✅ Working |
| Audio Selection | ✅ Working |
| Video Rendering | ✅ Working |
| YouTube Upload | 🔄 Placeholder |
| Daily Scheduling | ✅ Ready |

## Notes

- Videos are 30 seconds long, optimized for Shorts
- No music, only ambient soundscapes (wind, rain, water, etc.)
- Each dreamscape is unique — prompts are randomized
- Full pipeline takes ~5-10 minutes to complete

## License

MIT

---

**Paradise** — Generate endless surreal worlds, automatically. 🌌
