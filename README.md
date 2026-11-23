# Faceless YouTube Video Pipeline (n8n + Gemini + Python + FFmpeg)

A fully scheduled automation that researches what is trending, writes fact-checked scripts, renders short and standard videos, and uploads them to YouTube with no manual steps after setup.

I built it to run a faceless educational channel. Everything here is generic, so you can point it at any channel you own.

## What it does

```
01:00  Workflow 1: pick today's niche -> read trending sources -> Gemini picks topics
                   -> fetch Wikipedia text -> Gemini writes script from that text only
                   -> verify quotes and numbers against the source -> add to render queue
02:00  Workflow 2: render queued videos (TTS + AI images + FFmpeg)
09:00  Workflow 2: upload one by one (40 min apart) -> set AI-content flag
                   -> mark uploaded -> daily summary email
```

Output per day: a mix of vertical Shorts and 16:9 videos of 25 to 40 seconds, in a rotating niche (technology, kids learning, science and nature, history, trending explained).

## Architecture

| Part | File | Role |
| --- | --- | --- |
| Trend and script workflow | `n8n/build_n8n_trends.py` | Generates the n8n workflow that researches topics and writes verified scripts |
| Render and upload workflow | `n8n/build_n8n_workflow.py` | Generates the schedules, upload loop, AI-disclosure update and email |
| Renderer | `doc_short.py` | Reads a scene JSON, narrates it, gets images (an image generation API, NASA, or gradient fallback), builds overlays and encodes with FFmpeg |
| Batch runner | `run_daily.py` | Picks the next N scripts, alternating wide and Shorts, renders them, records state |
| Bridge server | `video_server.py` | Small HTTP service so n8n (in Docker) can queue scripts, request renders and download finished files |
| Examples | `queue-examples/`, `topics_gen.py`, `topics_wide.py` | Script format and hand-written fact-checked examples |

Why a bridge server: n8n runs in a container and cannot execute host tools like FFmpeg, so the container calls `http://host.docker.internal:8300`.

## Design decisions worth noting

- **Grounded scripts.** The model may only use facts from the Wikipedia text I fetch. Every factual scene must quote a source sentence, and every number in the scene must appear in that sentence. Scenes that fail the check are dropped, and a video with too few verified scenes is not produced.
- **Niche rotation and trend inputs.** Wikipedia most-read, Hacker News and Google Trends feed the topic picker. Kids days draw only from an evergreen, child-safe topic list.
- **Platform compliance.** Every upload sets `containsSyntheticMedia: true` through the YouTube API, descriptions credit the source (CC BY-SA) and state that narration and images are AI generated, kids videos are marked made for kids, and no copyrighted footage or music is used.
- **Conservative volume.** Four uploads a day with 40 minute gaps for a new channel. The YouTube Data API also allows roughly 6 uploads a day by default.
- **Cost guard.** A hard cap on image-API credits stops generation once the budget is reached, and the renderer falls back to a gradient background instead of failing.
- **Resilient by default.** Model calls retry, a failed script drops that video instead of the whole run, and `state.json` makes uploads idempotent so nothing posts twice.

## Setup

1. Install Python 3.11+, FFmpeg on PATH, and `pip install -r requirements.txt`.
2. Optional environment variables: `ELEVENLABS_API_KEY` for narration (otherwise free `edge-tts` is used) and `IMAGE_API_KEY`, `IMAGE_API_URL` and `IMAGE_API_HEADER` for an AI image generation API of your choice (the request format is in `get_image_api` in `doc_short.py`).
3. Start the bridge server: `python video_server.py` (port 8300). Add it to Task Scheduler or systemd so it starts at login.
4. Generate and import both workflows:
   ```
   cd n8n
   python build_n8n_workflow.py
   python build_n8n_trends.py
   docker cp youtube-daily-videos.json n8n:/home/node/a.json
   docker cp youtube-trends-scripts.json n8n:/home/node/b.json
   docker exec n8n n8n import:workflow --input=/home/node/a.json
   docker exec n8n n8n import:workflow --input=/home/node/b.json
   ```
5. In Google Cloud, enable YouTube Data API v3, create a Web OAuth client with redirect `http://localhost:5678/rest/oauth2-credential/callback`, and publish the consent screen (Testing mode logins expire every 7 days; publishing needs a homepage and privacy policy URL).
6. In n8n create credentials for YouTube OAuth2, Google Gemini and SMTP. Replace the `YOUR_..._CREDENTIAL_ID` placeholders in the workflow files, set your email address, and activate both workflows.

## Limits and honesty notes

- AI-generated content at volume can be treated as inauthentic by YouTube, so keep volume low, review the daily email, and keep scripts fact-based and varied.
- Model availability changes quickly. The Gemini model name in `build_n8n_trends.py` may need updating.
- The credit cost in the renderer is an estimate. Compare it with your provider dashboard.

## Stack

n8n, Gemini API, Python, Pillow, NumPy, FFmpeg, ElevenLabs / edge-tts, an image generation API, YouTube Data API v3, Docker.
