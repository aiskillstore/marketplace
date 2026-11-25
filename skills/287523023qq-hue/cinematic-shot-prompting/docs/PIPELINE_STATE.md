# Pipeline State

- Source: `/Users/guopeng/Desktop/332b1c163f4b2f16dec89dbcbf319e59.mp4`
- Video SHA-256: `055ef1a9cc342cc071453d42ad9a57454d03de3ef72a9608ef0287ec5093c143`
- Transcript: `work/video_review/transcript.txt`
- Transcript SHA-256: `51c0bf3fc3cd0fc359bc1711923480de5c69ac81db3387457aaf779a9e866dc4`
- Duration: 17:49.292
- Frame count: 17,108
- Processing date: 2026-08-31
- Goal: Distill a model-agnostic skill for turning shot intent into precise, executable camera-motion prompts.

## Current Stage

- [x] Stage 0: global map and critical reading
- [x] Stage 1: five extraction passes（3 independent; 2 main-agent fallback after subagent quota failure）
- [x] Stage 1.5: triple verification
- [x] Stage 2: RIA++ skill construction
- [x] Stage 3: links and index
- [x] Stage 4: pressure tests (main-agent fallback; independent blind test pending)
- [x] Stage 5: delivery package
- [ ] Installation: requires separate user confirmation of user-level or project-level target

## Validation

- Codex skill structure: passed (`quick_validate.py`)
- Test prompt JSON: valid
- Markdown local links: passed
- `agents/openai.yaml`: generated with the official skill-creator helper; default prompt names `$cinematic-shot-prompting`
- Pressure tests: 12/12 main-agent self-test; independent blind test remains pending because the subagent usage limit was reached

## Scope Decisions

- Keep: shot selection, camera-motion wording, subject/environment constraints, reference-frame compatibility, iteration, and high-risk keyframe planning.
- Exclude: platform recommendations, pricing, credit costs, queue times, and model rankings.
- Treat the transcript as an aid only. Resolve important claims against the video frames and timestamps because the automatic transcript contains recognition errors.

## Resume Note

Continue from the first unchecked stage. Do not reinstall or overwrite a global skill without explicit user confirmation.
