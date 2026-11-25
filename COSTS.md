# Compute, API & Cost Accounting: The Clean Sieve

## 1. Summary
Total direct monetary expenditure for developing, testing, and rendering *The Clean Sieve* was **$0.00 USD**, achieved by combining free-tier APIs, local CPU FFmpeg mastering, Kaggle free GPU quota, and SHA-256 artifact caching.

## 2. Breakdown by Pipeline Stage & Provider

| Stage | Provider / Model | Compute / Tier | Units Executed | Unit Cost | Total Cost (USD) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Storyboard & Validation** | Local Python (`jsonschema`) | Local CPU (Windows) | 10+ validation runs | $0.00 | $0.00 |
| **Narration (TTS)** | Gemini 2.5 Flash TTS (initial test) + `edge-tts` (`am-ET-AmehaNeural`) | Free Tier / Local Network | 8 shots (~78s total audio) | $0.00 | $0.00 |
| **Keyframes (v1 & v2)** | Cloudflare Workers AI (`@cf/black-forest-labs/flux-1-schnell`) & Gemini Image (`v1beta`) | Free Tier / Neurons Quota | 2 reference sheets + 8 shot keyframes | $0.00 | $0.00 |
| **Image-to-Video (`shot_04`)** | `Wan-AI/Wan2.2-TI2V-5B-Diffusers` | Kaggle Notebook (Tesla T4, 16 GB VRAM) | 1 clip (49 frames @ 24fps) | $0.00 (Free Quota) | $0.00 |
| **Motion Synthesis (Shots 1–8)** | Local FFmpeg (`zoompan` / `xfade`) | Local CPU (`imageio_ffmpeg` 9.0.2) | 8 clips @ 1280x720, 24fps | $0.00 | $0.00 |
| **Music Score (3 Candidates)** | `ACE-Step/acestep-v15-xl-base-diffusers` + FFmpeg fallback | Kaggle Notebook (Tesla T4) / Local CPU | 3 candidates x 78s WAV | $0.00 (Free Quota) | $0.00 |
| **Final Mastering & Exports** | Local FFmpeg (`sidechaincompress`, `loudnorm`, `subtitles`, `libx264`) | Local CPU | `radio_cut.mp4`, `final_16x9.mp4`, `final_9x16.mp4` | $0.00 | $0.00 |
| **Total** | | | | | **$0.00** |

## 3. Cost-Control Engineering
- **SHA-256 Caching (`outputs/.cache/`):** Prevented redundant image and audio API calls whenever downstream assembly parameters (subtitle font size, ducking ratio, 9:16 crop) were tuned.
- **Radio-Cut Gate:** Validated narrative pacing and Amharic voice timing on a black-screen audio cut (`radio_cut.mp4`) before running visual generation.
- **Selective GPU Offload:** Used Kaggle T4 GPU exclusively for heavy diffusion workloads (Wan 2.2 TI2V and ACE-Step 78s audio synthesis) while keeping deterministic video editing local.