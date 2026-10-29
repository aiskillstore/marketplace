# Evidence and export checks

Identify the exact export, SHA-256, duration and reviewed coverage. Inspect selected action and transitions in motion, not just contact sheets. Check all visible layers for repeated source ranges and repeated story content; a numerical duplicate detector cannot decide narrative necessity.

For speech, compare source and exported boundaries with surrounding context. Independent ASR families can reveal disagreement; variants within one family are not independent evidence. Empty ASR does not prove absence of speech or vocals. VAD detects activity, not a complete thought. Keep quiet answers and meaningful reactions.

Measure complete output decoding, loudness, peaks, channel configuration and mono compatibility where available. Investigate music entry/exit, new narration, discontinuities and source-to-output sync. Set delivery targets for the film; do not reuse another family's numeric target as a universal standard. `project.py measure` logs decoding, black/freeze detection and loudnorm measurements; stereo correlation and speech completeness need separate checks.

Prefer available local checks; no cloud reviewer is required. Whisper, GigaAM and Silero are optional speech tools, not bundled dependencies. Use audio models only for tasks they pass on controls: known silence, tone, speech, music, mixed speech/music and deliberately added clicks or clipping. A model that describes music well may still miss distortion or invent voices. Ask neutral questions, record versions/prompts and check findings against the signal. Do not repeat a failed tool without a concrete new reason.

The originating project retired Gemini review on 29 October 2026. Historical diagrams do not require reconnecting it. This is not a universal prohibition for other filmmakers: follow their explicit service choices. If reliable acoustic analysis or direct listening is unavailable, record the specific unverified aspect. ASR and peaks do not close it; never invent PASS. Music-only vocal checks and full mixed-export checks answer different questions.

Inspect the full stereo master and the encoded delivery: L/R balance, correlation, mono sum, levels, quiet replies, transients and seams. Do not infer that a whole clip needs amplification from low integrated loudness over long pauses. Compare suspect processing with the source at matched loudness before moving sync. These checks require tools beyond the bundled measurement helper.

Reuse results by source hash + range + processing/level + model/mode/prompt + coverage. Unchanged music does not prove an unchanged mix. Changed duration or levels require checking the new mix; identical PCM can support reuse with evidence and a new time mapping. Editorial text review is not listening.

Before delivery, compare all changes to the allowed scope, including atmosphere, titles, SFX and downstream ripple. Distinguish technical checks, sampled visual review, full viewing/listening and human acceptance. Preserve the previous version and report limitations with the exact exported file.
