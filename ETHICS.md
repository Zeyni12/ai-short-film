# Ethics, Cultural Representation & AI Disclosure: The Clean Sieve

## 1. Cultural Grounding & Narrative Stewardship
- **Source Inspiration:** *The Clean Sieve* (`የጠራው ወንፊት`) draws from traditional Ethiopian oral wisdom traditions centered on discernment, humility, and letting go of unproductive mental baggage.
- **Linguistic Authenticity:** Narration is written and voiced in natural Amharic (`am-ET`) rather than translating an English script word-for-word, preserving idiomatic cadence and respectful elder-to-youth register, paired with accessible English subtitles for broader audiences.
- **Visual Respect:** Prompts explicitly specify traditional Ethiopian highland attire (handwoven cotton *gabi* shawl, earthy linen tunic) and authentic household craft objects (woven reed and split-bamboo *wonfit* sieve) while avoiding caricatured or exoticized tropes.

## 2. Provenance & Transparency
- **Visible End-Card Disclosure:** Both `final_16x9.mp4` and `final_9x16.mp4` conclude with a 4-second on-screen disclosure stating that visuals, voice synthesis, and musical accompaniment were produced using generative AI tools under human direction.
- **Audit Trail (`runs.jsonl`):** Every visual, audio, and musical asset is logged with its exact model identifier, parameters, seed, and provenance (`gemini-image`, `@cf/black-forest-labs/flux-1-schnell`, `edge-tts-am-ET-AmehaNeural`, `wan-2.2-i2v`, `ace-step-3.5b`, or `manual-external-asset`).
- **External / Manual Assets:** Where external reference keyframes are curated or placed manually into `outputs/keyframes/`, `keyframes.py` logs them with `model: "manual-external-asset"` and their SHA-256 digest so human-curated vs. AI-generated frames remain distinguishable.

## 3. Likeness, Copyright & Safety Guardrails
- **No Real-Person Likeness Cloning:** Character designs depict fictional archetypes (an unnamed elder mentor and a young seeker) generated from descriptive text and reference sheets rather than living public figures or private individuals.
- **Synthetic Voice Selection:** Narration uses standard neural text-to-speech (`am-ET-AmehaNeural`) without voice cloning of any real actor or speaker.
- **Dataset & Weight Hygiene:** All open-weight models executed on Kaggle (`Wan-AI/Wan2.2-TI2V-5B-Diffusers` and `ACE-Step/acestep-v15-xl-base-diffusers`) are run via official Hugging Face repositories under their respective open research/community licenses.