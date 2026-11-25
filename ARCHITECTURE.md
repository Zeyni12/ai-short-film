Markdown


# System Architecture: The Clean Sieve (የጠራው ወንፊት)

## 1. Overview
The Clean Sieve is a deterministic, contract-driven AI short-film production pipeline written in Python 3.12. Rather than relying on monolithic one-off scripts, the system decouples narrative planning (`storyboard.json`) from media synthesis (`narration.py`, `keyframes.py`, `shots.py`, `music.py`) and final multi-format mastering (`assemble.py`).

## 2. End-to-End Pipeline Flow

storyboard.json
│
▼
[pipeline/validate.py] ──▶ schema/storyboard.schema.json (JSON Schema Draft-07)
│
├──▶ [pipeline/narration.py] ──▶ Amharic TTS + Loudnorm (-16 LUFS) ──▶ outputs/audio/manifest.json
│                                                                      └──▶ outputs/radio_cut.mp4
│
├──▶ [pipeline/keyframes.py] ──▶ Character & Sieve Lock + Image Gen ──▶ outputs/keyframes/.png
│
├──▶ [pipeline/shots.py]     ──▶ Wan 2.2 I2V / Multi-Frame / Ken Burns ──▶ outputs/shots/.mp4
│
├──▶ [pipeline/music.py]     ──▶ ACE-Step 3.5B WAV / Pentatonic Pad ──▶ outputs/music/selected_score.wav
│
└──▶ [pipeline/assemble.py]  ──▶ Sidechain Ducking + Subtitles + End Card
├──▶ outputs/final_16x9.mp4 (1280x720, 24fps, -14 LUFS)
└──▶ outputs/final_9x16.mp4 (1080x1920, blurred fill + safe captions)


## 3. Core Engineering Mechanisms

### A. Contract-First Validation (`pipeline/validate.py`)
- Every stage loads `storyboard.json` through `load_and_validate()`, enforcing structural integrity against `schema/storyboard.schema.json` before any API call or FFmpeg subprocess executes.
- Guarantees required fields (`id`, `duration_sec`, `seed`, `narration`, `subtitle_en`, `image_prompt`, `motion_mode`, `motion_prompt`) and non-empty shot arrays.

### B. Content-Addressed Caching & Telemetry (`pipeline/core.py`)
- **`run_with_cache(...)`:** Computes a SHA-256 key over `(stage, item_id, model, canonical_json(params), seed)`.
- **Idempotency & Hot-Swapping:** Re-running downstream stages hits `outputs/.cache/` with `0 ms` API latency and `$0.00` cost unless upstream inputs change (e.g., swapping a keyframe PNG or adding a Kaggle Wan 2.2 `.mp4` clip, whose file SHA-256 or presence invalidates only that specific shot).
- **Observability (`runs.jsonl`):** Every generation, fallback, and cache hit appends a structured JSON record containing `timestamp`, `stage`, `item_id`, `model`, `params`, `seed`, `latency_ms`, `cost_usd`, and `cache_hit`.

### C. Audio-Driven Timeline Synchronization
- `narration.py` measures exact synthesized WAV durations (`wave` frame count / sample rate) and computes `slot_dur = max(storyboard.duration_sec, audio_dur + 0.8s)` in `outputs/audio/manifest.json`.
- `shots.py` and `assemble.py` read `slot_dur` directly from `manifest.json`, preventing voice truncation or drift between spoken Amharic lines, English `.srt` subtitles, and video cuts.

### D. Audio Mastering & Multi-Ratio Rendering (`pipeline/assemble.py`)
- **Sidechain Ducking:** Uses FFmpeg `sidechaincompress` (`threshold=0.02`, `ratio=6`, `attack=50ms`, `release=400ms`) keyed to the Amharic voice track so the musical score automatically dips during speech and swells during pauses.
- **Broadcast Loudness:** Applies `loudnorm=I=-14:TP=-1.5:LRA=11` across the final stereo mix.
- **Dual Aspect Ratios:** Renders `final_16x9.mp4` (widescreen) and `final_9x16.mp4` (1080x1920 v