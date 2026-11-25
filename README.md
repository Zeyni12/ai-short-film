# The Clean Sieve (የጠራው ወንፊት)
### A Deterministic, Contract-Driven AI Short-Film Pipeline

An end-to-end Python pipeline for producing **The Clean Sieve (የጠራው ወንፊት)**, a ~78-second philosophical Ethiopian parable told in Amharic with English subtitles.

The project combines AI-assisted storytelling, character-consistent keyframe generation, AI video generation, Amharic narration, generative music, and automated audiovisual mastering into a reproducible production workflow.

The final film is mastered in two formats:

- **16:9 Widescreen** — 1280 × 720, 24 FPS
- **9:16 Vertical** — 1080 × 1920, optimized for mobile platforms

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Creative Concept](#creative-concept)
3. [Key Features](#key-features)
4. [System Architecture](#system-architecture)
5. [Technology Stack](#technology-stack)
6. [Project Structure](#project-structure)
7. [Installation and Setup](#installation-and-setup)
8. [Running the Pipeline](#running-the-pipeline)
9. [Generated Outputs](#generated-outputs)
10. [Determinism and Reproducibility](#determinism-and-reproducibility)
11. [Documentation](#documentation)
12. [Ethics and Cultural Stewardship](#ethics-and-cultural-stewardship)
13. [Cost Accounting](#cost-accounting)
14. [Future Improvements](#future-improvements)

---

## Project Overview

**The Clean Sieve** is both a short-film production project and an engineering experiment in building a deterministic, contract-driven AI media pipeline.

Instead of manually coordinating separate AI tools and editing workflows, this project organizes the production process into independently executable Python stages.

A single storyboard specification controls the production process, including:

- Shot descriptions and visual prompts.
- Character and object references.
- Random seeds and generation settings.
- Amharic narration.
- English subtitles.
- Shot durations and sequencing.
- Audio and video assembly requirements.

A JSON Schema contract validates the storyboard before production stages execute.

The pipeline also implements SHA-256 content-addressed caching and append-only execution logging to improve reproducibility, traceability, and debugging.

## Creative Concept

**Title:** The Clean Sieve (የጠራው ወንፊት)

**Genre:** Philosophical parable

**Language:** Amharic

**Subtitles:** English

**Duration:** Approximately 78 seconds

**Structure:** 8 cinematic shots

The film explores a philosophical parable through Ethiopian cultural storytelling, using visual symbolism, narration, and music to communicate its central message.

The production combines traditional storytelling principles with modern generative AI techniques.

## Key Features

### 1. Contract-Driven Production

- A single `storyboard.json` acts as the source of truth.
- JSON Schema validation enforces the storyboard contract.
- Duration validation helps maintain the intended film length.
- Pipeline stages consume the same structured production specification.

### 2. Reproducible Execution

- SHA-256 content-addressed caching.
- Configurable generation seeds.
- Append-only `runs.jsonl` execution telemetry.
- Tracking of models, latency, cache hits, and execution details.

### 3. Character and Visual Consistency

- Character and sieve reference sheets.
- Shot-specific keyframe generation.
- Manual keyframe locking.
- Reference-based visual continuity across shots.

### 4. AI Video Generation

- Wan 2.2 image-to-video integration.
- Support for importing externally generated video clips.
- Multi-frame crossfades.
- FFmpeg-based motion fallback when generated clips are unavailable.

### 5. Amharic Narration

- Amharic text-to-speech synthesis.
- Narration timing manifests.
- Phase 1 radio-cut generation for early pacing evaluation.

### 6. AI-Generated Soundtrack

- ACE-Step music candidate selection.
- Pentatonic ambient fallback.
- Audio mixing and narration-aware sidechain ducking.

### 7. Automated Video Mastering

- FFmpeg-based video assembly.
- Audio loudness normalization targeting -14 LUFS.
- Sidechain audio ducking.
- English subtitle rendering and burn-in.
- Automated horizontal and vertical video exports.
- AI disclosure end card.

---

## System Architecture

The pipeline follows a staged production architecture:

```text
              storyboard.json
                     |
                     v
             Contract Validation
                     |
                     v
          Amharic Narration (Phase 1)
                     |
                     v
          Character & Keyframe Generation
                     |
                     v
             Video Generation
              (Wan 2.2 / FFmpeg)
                     |
                     v
              Music Selection
                (ACE-Step)
                     |
                     v
             Video Assembly
                     |
                     v
          Audio & Subtitle Mastering
                     |
             +-------+-------+
             |               |
             v               v
        16:9 Master      9:16 Master
```

### Pipeline Phases

| Phase | Responsibility | Main Module |
|---|---|---|
| Validation | Storyboard and duration contracts | `validate.py` |
| Phase 1 | Narration and radio-cut generation | `narration.py` |
| Phase 2 | Character references and keyframes | `keyframes.py` |
| Phase 2 | Motion and shot rendering | `shots.py` |
| Phase 2 | Music preparation | `music.py` |
| Phase 3 | Final audiovisual assembly | `assemble.py` |

Each stage can be executed independently, making the system easier to debug, test, and extend.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline orchestration |
| Gemini API | AI-assisted generation and connectivity integration |
| Cloudflare API | Configured AI service integration |
| Wan 2.2 | Image-to-video generation |
| ACE-Step | AI music generation |
| FFmpeg | Video and audio processing |
| JSON Schema | Storyboard contract validation |
| SHA-256 | Content-addressed caching |
| Amharic TTS | Narration synthesis |
| SRT | English subtitle management |

---

## Project Structure

```text
ai-short-film/
│
├── run_pipeline.py
├── storyboard.json
├── requirements.txt
├── .env
├── runs.jsonl
│
├── schema/
│   └── storyboard.schema.json
│
├── pipeline/
│   ├── core.py
│   ├── validate.py
│   ├── smoke_test.py
│   ├── narration.py
│   ├── keyframes.py
│   ├── shots.py
│   ├── music.py
│   └── assemble.py
│
├── outputs/
│   ├── radio_cut.mp4
│   ├── audio/
│   ├── keyframes/
│   ├── wan22/
│   ├── shots/
│   ├── music/
│   ├── final_16x9.mp4
│   └── final_9x16.mp4
│
├── DESIGN.md
├── ARCHITECTURE.md
├── EXPERIMENTS.md
├── FAILURES.md
├── ETHICS.md
└── COSTS.md
```

Generated assets and additional working directories may vary depending on the production stage.

---

## Installation and Setup

### Prerequisites

- Python 3.10 or later.
- FFmpeg installed and available in PATH.
- Windows PowerShell or a compatible terminal.
- Required API credentials for the configured services.
- Access to generated Wan 2.2 and ACE-Step assets when using externally generated media.

### 1. Clone the Repository

```powershell
git clone https://github.com/Zeyni12/ai-short-film.git

cd ai-short-film
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv

.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the repository root:

```env
GEMINI_API_KEY=your_gemini_api_key

CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id

CLOUDFLARE_API_TOKEN=your_cloudflare_api_token

KEEP_MANUAL_KEYFRAMES=1
```

**Important:** Never commit `.env` or expose API credentials in the repository. Use `.env.example` with placeholder values when documenting configuration.

---

## Running the Pipeline

The production pipeline is executed stage by stage.

### Step 1: Validate the Storyboard

```powershell
python -m pipeline.validate
```

Validates the storyboard structure against the JSON Schema contract and checks production duration constraints.

### Step 2: Generate Amharic Narration

```powershell
python -m pipeline.narration --radio-cut
```

Generates:

- Amharic narration audio.
- Narration timing manifest.
- Phase 1 radio cut for early pacing and audience evaluation.

### Step 3: Generate Character References and Keyframes

```powershell
python -m pipeline.keyframes
```

Generates or registers:

- Character reference sheets.
- Sieve reference sheets.
- Shot-specific keyframes.
- Manually locked keyframes when configured.

### Step 4: Generate Motion Clips

```powershell
python -m pipeline.shots
```

The video stage supports:

- Importing Wan 2.2 image-to-video clips from `outputs/wan22/`.
- Multi-frame crossfade transitions.
- FFmpeg-based motion fallback when external generated clips are unavailable.

### Step 5: Prepare the Musical Score

```powershell
python -m pipeline.music
```

Selects an available ACE-Step musical candidate or uses the configured pentatonic ambient fallback.

### Step 6: Assemble and Master the Final Film

```powershell
python -m pipeline.assemble
```

Performs:

- Video sequencing.
- Narration and soundtrack synchronization.
- Sidechain audio ducking.
- Loudness normalization targeting -14 LUFS.
- English subtitle burn-in.
- 16:9 and 9:16 video rendering.
- AI disclosure end-card integration.

---

## Generated Outputs

All generated production assets are stored locally in `outputs/`.

| Output | Description |
|---|---|
| `radio_cut.mp4` | Phase 1 audio-only pacing cut |
| `final_16x9.mp4` | Horizontal cinematic master |
| `final_9x16.mp4` | Vertical social-media master |
| `wan22/` | Imported Wan 2.2 video clips |
| `music/` | Music candidates and selected score |

### Final Master Specifications

| Specification | 16:9 Widescreen | 9:16 Vertical |
|---|---|---|
| Resolution | 1280 × 720 | 1080 × 1920 |
| Frame rate | 24 FPS | 24 FPS |
| Subtitles | Burned-in English | Mobile-safe English captions |
| Audio | Mastered narration and score | Mastered narration and score |
| Background | Cinematic composition | Blurred background fill |
| Disclosure | AI disclosure end card | AI disclosure end card |

---

## Determinism and Reproducibility

A major engineering objective is making production runs traceable and repeatable.

The pipeline implements:

**Content-addressed caching**

SHA-256 hashes are used to identify content and support cache reuse when inputs remain unchanged.

**Storyboard contracts**

A single structured storyboard controls the production specification, reducing inconsistencies between stages.

**Execution telemetry**

`runs.jsonl` records production execution information, including:

- Model information.
- Generation seeds.
- Execution latency.
- Cache hits.
- Pipeline execution details.

**Manual keyframe locking**

Allows selected visual references and keyframes to remain fixed during subsequent production runs.

Note: Reproducibility does not guarantee bit-identical outputs from external generative AI services. Results can still vary because of model versions, service changes, and nondeterministic inference.

---

## Documentation

The repository includes additional technical documentation:

| Document | Description |
|---|---|
| `DESIGN.md` | Narrative design, shot rationale, and user testing |
| `ARCHITECTURE.md` | System architecture and audiovisual synchronization |
| `EXPERIMENTS.md` | Experiments involving TTS quotas, character consistency, Wan 2.2, and ACE-Step |
| `FAILURES.md` | Recorded API, schema, and FFmpeg errors with resolutions |
| `ETHICS.md` | Cultural stewardship, provenance, and AI disclosure |
| `COSTS.md` | Compute and API cost accounting |

---

## Ethics and Cultural Stewardship

The project aims to combine generative AI with responsible cultural storytelling.

Key considerations include:

- Respectful representation of Ethiopian cultural storytelling.
- Clear documentation of AI-generated media.
- Provenance and transparency of generated assets.
- Appropriate disclosure of AI-assisted production.
- Avoiding misleading claims about human-created or AI-generated content.

See [ETHICS.md](ETHICS.md) for the project's detailed policy.

---

## Cost Accounting

The project's recorded production cost is:

**$0.00 total**

See [COSTS.md](COSTS.md) for the recorded compute and API cost accounting.

This figure reflects the project's documented accounting and should not be interpreted as a claim that all infrastructure, hardware, or services are universally free.

---

## Future Improvements

Potential future development directions include:

- More robust automatic character consistency evaluation.
- Automated shot-quality assessment.
- Improved Amharic narration timing and pronunciation evaluation.
- Automated subtitle alignment.
- More advanced transitions and cinematic motion controls.
- Expanded production metrics and run comparisons.
- Additional video aspect ratios and export profiles.
- A reusable interface for configuring and running new short-film projects.

---

## Project Status

**Production pipeline:** Three-phase workflow implemented.

**Final outputs:** 16:9 and 9:16 masters.

**Reproducibility:** SHA-256 caching and execution telemetry.

**Documentation:** Technical, creative, experimental, and ethical documentation included.

---

## Acknowledgment

**The Clean Sieve (የጠራው ወንፊት)** demonstrates how structured software engineering, generative AI, and traditional storytelling can work together to create a reproducible AI-assisted filmmaking workflow.

The goal is not simply to generate a short film, but to engineer a transparent, modular, and reusable production pipeline.
