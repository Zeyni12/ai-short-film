# Design Document: The Clean Sieve (የጠራው ወንፊት)

## 1. Intended Audience & Viewing Context
- **Audience:** Young adults, students, and early-career professionals (especially Ethiopian viewers at home and in the diaspora, plus international peers via English subtitles) watching on mobile feeds (9:16) or desktop/YouTube (16:9).
- **Emotional & Cognitive Intent:** Viewers should initially share the young man's frustration at an apparently pointless task, then experience a quiet moment of clarity—understanding that letting go of mental baggage and questioning *why* we do things matters more than trying to hold onto everything.

## 2. Shot-by-Shot Visual & Narrative Rationale
- **shot_01 (9s):** Establish serene dawn lake setting and the seeker's journey.
- **shot_02 (9s):** Introduce the wise elder and the dirty, soot-stained sieve—visual anchor of "baggage."
- **shot_03 (9s):** Close-up on the clogged mesh to make the impossibility of holding water tangible.
- **shot_04 (10s):** Action sequence at the lake—water pouring straight through the sieve repeatedly.
- **shot_05 (9s):** Exhaustion and questioning ("Why did you make me do this?").
- **shot_06 (9s):** The elder's calm, knowing reaction—shifting focus from the water to the vessel.
- **shot_07 (9s):** Macro reveal of the spotless, gleaming sieve—visual payoff of purification.
- **shot_08 (10s):** Wide sunset silhouette pairing stillness with the final philosophical takeaway.

## 3. User Test #1 — Phase 1 Radio Cut (3 Participants)
- **Participant 1 (Family member, Addis Ababa):** *[Record exact quote—e.g., "The Amharic tone is calm and respectful, though the pause after Shot 5 felt slightly quick."]*
- **Participant 2 (Software engineering colleague, Slack):** *[Record exact quote—e.g., "The parable twist lands well at the end; make sure the English subtitle on Shot 8 isn't too dense."]*
- **Participant 3 (Peer/friend):** *[Record exact quote—e.g., "Clear voice pacing; background noise in the radio cut was subtle enough not to distract."]*
- **Changes Applied to `storyboard.json`:**
  - Refined Shot 8 English subtitle phrasing for faster reading on mobile screens.
  - Added `0.8s` breathing room padding after each narration line in `manifest.json` so emotional beats settle before the next shot cuts.

## 4. User Test #2 — Near-Final Cut (3 Participants)
*(To be completed after `assemble.py` generates `final_16x9.mp4` and `final_9x16.mp4`)*