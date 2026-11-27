# Universal Plot-to-Livestream Beat Translation / 任意剧情转直播视角四幕节奏法

Any third-person story—from burning midnight ramen to escaping a haunted hallway or hatching a mythic dragon—can be transformed into an unmistakable livestream short by restructuring narrative beats around **real-time audience witness**.

## 1. Third-Person Narrative vs. Livestream Perspective Mapping

| **Story Element** | **Ordinary Short-Video / Movie Treatment** | **Livestream Perspective (`livestream-style-video`) Treatment** |
| --- | --- | --- |
| **Opening** | Wide establishing shot of location | **Cold-Open Mid-Claim (`0–3.5s`)**: Already inside the rig, addressing `0°` lens ("家人们别刷屏说剧本，今天现场实测…") |
| **Exposition** | Voiceover narration or subtitle | **Close-Up Lens Proof (`3.5–7.5s`)**: Bringing prop `18cm` to autofocus lens with flat palm behind, or tilting selfie cam down to prove no wires/tricks |
| **Foreshadowing** | Dramatic music cue & cut-away close-up | **Dramatic Irony in Background (`Chat Sees It First`)**: Cat ears / monster eyes / smoke appear over host's shoulder while host calmly sips coffee reading `15°` chat warnings ("Wait why is chat spamming BEHIND YOU??") |
| **Climax** | Multi-angle action montage | **Unscripted Single-Rig Chaos (`7.5–11.5s`)**: Twist happens *inside the continuous live frame*, jolting the desk clamp or selfie arm |
| **Ending** | Fade out or pose | **Clip-That Meltdown / Freeze (`11.5–15s`)**: Speechless `15° → 0°` stare, rigid desk-slam, or frantic reach toward camera to "end stream" |

## 2. Pacing Budgets (`15s` vs. `30s` vs. `45s`)

AI video diffusion clips degrade rapidly if asked to perform sequential story arcs inside a single 5-second generation. Enforce **one primary verb per shot**:

- **`15s` Package (`4` unique shots)**:
  - `Shot 01 (0.0s–3.5s)`: Hook & `0°` Flag Claim + `join_toast` HUD popup.
  - `Shot 02 (3.5s–7.5s)`: Macro Proof / Approach + `commerce_card` or `qa_pinned` HUD popup.
  - `Shot 03 (7.5s–11.5s)`: Unscripted Live Twist + rig micro-shake + `gift_combo` HUD popup.
  - `Shot 04 (11.5s–15.0s)`: Chat-Flood Reaction / Loop Payoff + `gift_combo_peak` + high heart fountain.
- **`30s` Package (`8` unique shots, `3.75s` each)**:
  - Interleave each primary physical beat with a dedicated **Real-Time Chat Reaction Cut** (`15°` comment read + verbal clapback or skeptical double-check) so all 8 clips have distinct actions and zero repeated prompts.

## 3. Live Room Audio & Foley Signatures (`直播间真实收音设计`)

Clean studio foley makes a clip feel edited; **raw close-mic imperfections** sell the live broadcast immediately:
- **Close-Proximity Mic Plosives & Desk Thumps**: Crisp mechanical keyboard switches (`clack`), chair hydraulic creak, low-end mic boom thump when hands hit the desk.
- **Outdoor IRL Ambience**: Wind buffeting lavalier furry deadcat, sizzling street-stall oil, footsteps echoing in stairwell.
- **Subtle Room Notification Cues**: Soft dual-note join chime (`659Hz → 988Hz`), rapid danmaku tick bed, and combo gift ascending arpeggio (synthesized offline in `render_preview.mjs`'s `buildEpisodeWavBuffer`).
