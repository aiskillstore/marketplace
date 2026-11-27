# 05 · Wuxia Flying-Sword Cloud Commute Selfie Live (Genre Plot -> Live POV) / 仙侠御剑飞行早高峰户外直播（任意架空剧情转直播）

15-second (`9:16`, 4-shot) **Livestream POV** package compiled with `--template wuxia-sword-flight-live --engine hailuo --platform douyin`.

| 9:16 Animated Preview (Post-HUD) | 4-Shot Storyboard Contact Sheet |
| :---: | :---: |
| <a href="assets/wuxia_sword_flight_live.mp4"><img src="assets/wuxia_sword_flight_live.gif" width="185" alt="Wuxia Flying-Sword Cloud Commute Selfie Live (Genre Plot -> Live POV) 9:16 preview" /></a> | <img src="assets/storyboard_sheet.zh.png" width="540" alt="Wuxia Flying-Sword Cloud Commute Selfie Live (Genre Plot -> Live POV) 4-shot contact sheet" /> |

## Package contents

- [`assets/wuxia_sword_flight_live.mp4`](assets/wuxia_sword_flight_live.mp4): offline 9:16 preview video (`H.264 MP4 + synthesized live audio + douyin HUD`)
- [`assets/storyboard_sheet.zh.png`](assets/storyboard_sheet.zh.png) · [`en`](assets/storyboard_sheet.en.png): Chinese and English 4-shot contact sheets
- [`rig_card.md`](rig_card.md): Camera Rig (`handheld-selfie-irl`) + Style (`cinematic-genre-adapt`) DNA card and 3-state setup anchor prompt
- [`storyboard.md`](storyboard.md) · [`prompts.json`](prompts.json): Clean-Plate first-frame & `hailuo` motion prompts + Post-HUD popup timeline
- [`drift_report.md`](drift_report.md): 8-gate anti-drift verification report (**PASS**)

## Reproduce

```bash
node scripts/rig_spec.mjs --rig handheld-selfie-irl --style cinematic-genre-adapt --host "青云小师兄" --lang zh-en --out examples/wuxia-sword-flight-live/rig_card.md
node scripts/shot_compiler.mjs --template wuxia-sword-flight-live --duration 15 --engine hailuo --platform douyin --lang zh-en --out examples/wuxia-sword-flight-live/storyboard.md
node scripts/shot_compiler.mjs --template wuxia-sword-flight-live --duration 15 --engine hailuo --platform douyin --json --out examples/wuxia-sword-flight-live/prompts.json
node scripts/drift_check.mjs --pack examples/wuxia-sword-flight-live/prompts.json --engine hailuo --lang zh-en --out examples/wuxia-sword-flight-live/drift_report.md
```
