# The Clean Sieve (የጠራው ወንፊት) — Deterministic AI Short-Film Pipeline

An end-to-end, contract-driven Python pipeline that produces **The Clean Sieve (`የጠራው ወንፊት`)**, a ~78-second philosophical Ethiopian parable told in **Amharic** with **English subtitles**, mastered in both **16:9 widescreen** and **9:16 vertical** formats.

## Project Structure

```text
ai-short-film/
├── storyboard.json                 # Single source of truth (8 shots, prompts, seeds, narration, subtitles)
├── schema/
│   └── storyboard.schema.json      # JSON Schema contract enforced before every stage
├── pipeline/
│   ├── core.py                     # SHA-256 content-addressed caching & runs.jsonl logger
│   ├── validate.py                 # Storyboard schema & duration validator
│   ├── smoke_test.py               # Connectivity checks for Gemini & Cloudflare APIs
│   ├── narration.py                # Amharic TTS synthesis, manifest timing & Phase 1 radio cut
│   ├── keyframes.py                # Character/sieve reference sheets + shot keyframes (with manual lock)
│   ├── shots.py                    # Wan 2.2 I2V import, multi-frame xfade & FFmpeg motion clips
│   ├── music.py                    # ACE-Step score selector & pentatonic ambient fallback
│   └── assemble.py                 # Sidechain ducking, -14 LUFS loudness, SRT burn-in & 16:9/9:16 export
├── runs.jsonl                      # Append-only execution telemetry (models, seeds, latency, cache hits)
├── DESIGN.md                       # Narrative design, shot rationale & user test logs
├── ARCHITECTURE.md                 # System design & audio-visual synchronization details
├── EXPERIMENTS.md                  # Iteration log (TTS quotas, character consistency, Wan 2.2, ACE-Step)
├── FAILURES.md                     # Logged API/schema/FFmpeg errors and resolutions
├── ETHICS.md                       # Cultural stewardship, provenance & AI disclosure policy
└── COSTS.md                        # Compute & API cost accounting ($0.00 total)

Quickstart
1. Environment Setup
PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Create a .env file in the repository root:

Code snippet


GEMINI_API_KEY=your_gemini_api_key
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
KEEP_MANUAL_KEYFRAMES=1
2. Run the Pipeline Stage by Stage
PowerShell


# Validate storyboard contract
python -m pipeline.validate

# Phase 1: Generate Amharic narration + timing manifest + black-screen radio cut
python -m pipeline.narration --radio-cut

# Phase 2: Generate or register character/sieve references & shot keyframes
python -m pipeline.keyframes

# Phase 2: Render motion clips (uses outputs/wan22/<id>.mp4 if present, else FFmpeg motion)
python -m pipeline.shots

# Phase 2: Prepare selected musical score (uses outputs/music/candidate_01.wav if present)
python -m pipeline.music

# Phase 3: Master audio (-14 LUFS + sidechain ducking), burn subtitles & export 16:9 + 9:16
python -m pipeline.assemble
Key Outputs (Generated Locally in outputs/)
outputs/radio_cut.mp4 — Phase 1 audio-only pacing cut for early audience testing.

outputs/final_16x9.mp4 — Horizontal master (1280x720, 24fps, burned English subtitles, AI disclosure end card).

outputs/final_9x16.mp4 — Vertical social master (1080x1920, blurred background fill, mobile-safe captions).

runs.jsonl — Full reproducibility and caching log across all runs.
