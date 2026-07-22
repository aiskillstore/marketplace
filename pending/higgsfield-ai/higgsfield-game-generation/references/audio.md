# Game Audio

Use this reference for music, SFX, ambience, and spoken character lines. Generate through Higgsfield CLI, then normalize and mix locally for predictable in-game loudness.

## Discover the live contracts

Run before the first audio job:

```bash
higgsfield model list --audio --json
higgsfield model get seed_audio
```

Use `seed_audio` by default. Use `sonilo_music` or `mirelo_text_to_audio` only when the user requests those specialist models or their live contracts fit better. Use `inworld_text_to_speech` only for explicit TTS with one of its listed voices.

## Commands

General audio, SFX, or ambience:

```bash
higgsfield generate create seed_audio \
  --prompt "short isolated sword impact, dry studio recording, no music" \
  --wait \
  --json
```

Specialist instrumental music:

```bash
higgsfield model get sonilo_music
higgsfield generate create sonilo_music \
  --prompt "instrumental cozy forest loop, warm marimba and soft strings, no vocals" \
  --duration 30 \
  --wait \
  --json
```

Specialist legacy SFX:

```bash
higgsfield model get mirelo_text_to_audio
higgsfield generate create mirelo_text_to_audio \
  --prompt "single heavy wooden door slam, close microphone, no ambience" \
  --duration 2 \
  --wait \
  --json
```

Explicit TTS:

```bash
higgsfield model get inworld_text_to_speech
higgsfield generate create inworld_text_to_speech \
  --prompt "The gate is open. Move!" \
  --voice "<exact voice value from model get>" \
  --wait \
  --json
```

Pass only parameters shown by `model get`; do not forward provider-specific keys.

## Scope

- Music: at most two looping tracks for a small game; one per major scene is usually enough.
- SFX: prioritize the primary verb, damage/feedback, pickup/reward, important environment, then one ambience layer. Keep small games to roughly five essential effects.
- Voice: lock one voice per speaking entity and reuse it. Keep lines short enough not to block gameplay.
- Generate independent clips concurrently, but wait for every manifest row and save its result under the project `assets/` directory.

## Prompt rules

- Describe one sound per SFX prompt. Do not request a complete mixed scene.
- State `no music`, `no voice`, or `no ambience` when isolation matters.
- Music prompts specify mood, tempo, instrumentation, and `instrumental/no vocals` when lyrics are unwanted.
- Voice prompts contain the exact line; performance direction belongs in the model-supported prompt, not undocumented flags.
- Preserve the game's STYLE FORMULA conceptually through material, era, energy, and tonal language even though audio is not visual.

## Mix and ear safety

Normalize locally before wiring clips into the game:

- Voice around -6 dBFS.
- SFX around -10 to -12 dBFS.
- Music around -18 to -20 dBFS.
- Final true peak at or below -3 dBFS.

Voice stays above SFX; SFX stays above music. Loop ambience/music in playback code and add short fades at loop boundaries. Never stack raw model outputs at full gain.

## Verification

- Every audio manifest row resolves without a 404.
- Autoplay restrictions are handled: start/resume the audio context from a user gesture.
- Pause or mute audio when the page loses focus if that matches the game profile.
- The game remains playable with sound disabled.
- Test on phone speakers as well as headphones when mobile is in scope.
