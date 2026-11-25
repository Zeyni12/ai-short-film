# Failures, Errors & Recovery Log: The Clean Sieve (የጠራው ወንፊት)

This document records actual runtime errors, quota limits, API schema mismatches, and environment pitfalls encountered during development, along with how each was diagnosed and resolved in code.

---

## 1. Gemini TTS Free Tier Rate Limit (`429 RESOURCE_EXHAUSTED`)
- **Stage / Component:** Phase 1 Narration (`pipeline/narration.py` / `gemini-2.5-flash-tts`)
- **Symptom:** After synthesizing the first few shots, `gemini-2.5-flash-tts` returned `429 RESOURCE_EXHAUSTED` (`GenerateRequestsPerMinutePerProjectPerModel-FreeTier`, limit `3` RPM), triggering fallback to `am-ET-AmehaNeural` (`edge-tts`) starting mid-storyboard.
- **Root Cause:** Free-tier quota enforcement on `gemini-2.5-flash-tts` allows only 3 requests per minute per project, while batch generation looped across all 8 shots without pacing or uniform fallback selection.
- **Resolution:** Standardized all 8 Amharic narration slots on `edge-tts` (`am-ET-AmehaNeural` at `rate="-6%"`) with per-shot `loudnorm=I=-16` normalization, avoiding mid-film voice timbre shifts and eliminating `429` failures.

---

## 2. Silent / Low-Volume Audio in Initial Radio Cut
- **Stage / Component:** Phase 1 Narration & Mixing (`pipeline/narration.py` / `pipeline/assemble.py`)
- **Symptom:** Playback of the early `outputs/radio_cut.mp4` appeared silent or overly quiet to the listener.
- **Root Cause:** Two compounding issues:
  1. Default FFmpeg `amix` normalization (`normalize=1`) scaled down combined audio levels when mixing speech with background audio.
  2. Differences in raw PCM/base64 decoding and gain staging across TTS outputs reduced perceived vocal loudness.
- **Resolution:** Configured explicit `amix` weighting (`weights=1 0.15:normalize=0`), normalized individual narration clips (`loudnorm=I=-16:TP=-1.5:LRA=11`), and applied `sidechaincompress` + `loudnorm=I=-14:TP=-1.5:LRA=11` during final assembly (`assemble.py`).

---

## 3. Cloudflare Workers AI FLUX Input Schema Error (`Additional or unevaluated properties '/seed'`)
- **Stage / Component:** Phase 2 Keyframes (`pipeline/keyframes.py` / `@cf/black-forest-labs/flux-1-schnell`)
- **Symptom:** `keyframes.py` failed on `character_sheet` after 3 retries with `Cloudflare FLUX 400: {"errors":[{"message":"AiError: Bad input: Error: Additional or unevaluated properties '/seed' at '/' not allowed ...","code":5006}]}`. Cascading downstream runs of `shots.py` and `assemble.py` then failed with `FileNotFoundError` on missing `outputs/keyframes/shot_01.png` and `outputs/shots/*.mp4`.
- **Root Cause:** Passing `"seed"` inside the JSON request body to Cloudflare's `@cf/black-forest-labs/flux-1-schnell` endpoint violated its strict JSON input schema, while `shots.py` and `assemble.py` lacked an early guard when upstream keyframes were absent.
- **Resolution:** Removed `"seed"` from the HTTP JSON payload sent to Cloudflare FLUX (retaining `seed` in `run_with_cache` metadata and `runs.jsonl`), and added a Gemini image generation fallback (`gemini-2.5-flash-image` / `gemini-3.1-flash-image`) plus character/sieve visual reference conditioning.

---

## 4. FFmpeg Concat Stream-Copy Failure (`exit status 4294967294`)
- **Stage / Component:** Phase 3 Final Assembly (`pipeline/assemble.py` / `imageio_ffmpeg` v9.0.2 on Windows)
- **Symptom:** Concatenating generated shot clips and the 4-second end card into `outputs/raw_video.mp4` failed with `subprocess.CalledProcessError` returning non-zero exit status `4294967294` (unsigned 32-bit representation of `-2` on Windows).
- **Root Cause:** Using `-c copy` on concatenated segments with varying encoder/packet headers or timestamps can fail stream demuxing/muxing in FFmpeg.
- **Resolution:** Updated `raw_video.mp4` concatenation in `pipeline/assemble.py` to re-encode cleanly with `-c:v libx264 -crf 20 -pix_fmt yuv420p` and `-safe 0` on Windows `Path.resolve().as_posix()` file lists.

---

## 5. PowerShell Syntax Error When Pasting Notebook Code
- **Stage / Component:** Local CLI vs. Kaggle Notebook Workflow
- **Symptom:** Pasting Python notebook cells (`!pip install ...`, `from pathlib import Path ...`) directly into Windows PowerShell produced `ReservedKeywordNotAllowed` (`The 'from' keyword is not supported in this version of the language`) and parser errors.
- **Root Cause:** The snippet was intended for a Jupyter/Kaggle Python cell rather than PowerShell.
- **Resolution:** Separated local PowerShell pipeline commands (`python -m pipeline.*`) from Kaggle GPU notebook cells, keeping notebook code inside notebook cells or `.py` files rather than invoking Python statements in PowerShell.

---

## 6. Kaggle Input Path Mismatch (`/kaggle/input/...` vs. `/kaggle/working/shot_04.png`)
- **Stage / Component:** Kaggle GPU Notebook — Cell 2 (`Tesla T4`)
- **Symptom:** Cell 3 raised `FileNotFoundError: [Errno 2] No such file or directory: '/kaggle/working/shot_04.png'` after uploading the keyframe via Kaggle's dataset/input UI.
- **Root Cause:** Kaggle mounts attached datasets under `/kaggle/input/<dataset-slug>/...` rather than copying them automatically into `/kaggle/working/`.
- **Resolution:** Updated Cell 2 to scan `/kaggle/input` and `/kaggle/working` with `rglob("*")` for uploaded image files, locate `shot_04.png`, and copy it to `/kaggle/working/shot_04.png` before inference.

---

## 7. `WanPipeline.__call__()` Unexpected Keyword Argument `'image'`
- **Stage / Component:** Kaggle GPU Notebook — Cell 3 (`Wan-AI/Wan2.2-TI2V-5B-Diffusers` on Tesla T4)
- **Symptom:** After downloading the `34.2 GB` model weights, calling `pipe(image=init_image, ...)` raised `TypeError: WanPipeline.__call__() got an unexpected keyword argument 'image'`.
- **Root Cause:** The loaded `WanPipeline` class signature in `diffusers` did not accept `image` as a direct keyword argument for that pipeline variant.
- **Resolution:** Used `inspect.signature(pipe.__call__)` to conditionally pass `image` only when declared in `pipe.__call__` parameters while reusing the already-cached local weights (`local_files_only=True`) and `torch.float16` + `enable_model_cpu_offload()` for 16 GB T4 VRAM compatibility.