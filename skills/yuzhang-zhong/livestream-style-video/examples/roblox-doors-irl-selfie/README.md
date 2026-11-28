# 07 · Roblox DOORS Corridor Handheld Selfie-Stick Live Scare / Roblox 惊悚走廊自拍杆直拍 · 身后白眼突脸（Roblox IRL 样本）

15-second (`9:16`, 4-shot) **Livestream POV** package compiled with `--template roblox-doors-irl-selfie --engine sora --platform instagram`.

| 9:16 Animated Preview (Post-HUD) | 4-Shot Storyboard Contact Sheet |
| :---: | :---: |
| <a href="assets/roblox_doors_irl_selfie.mp4"><img src="assets/roblox_doors_irl_selfie.gif" width="185" alt="Roblox DOORS Corridor Handheld Selfie-Stick Live Scare 9:16 preview" /></a> | <img src="assets/storyboard_sheet.zh.png" width="540" alt="Roblox DOORS Corridor Handheld Selfie-Stick Live Scare 4-shot contact sheet" /> |

## Package contents

- [`assets/roblox_doors_irl_selfie.mp4`](assets/roblox_doors_irl_selfie.mp4): offline 9:16 preview video (`H.264 MP4 + synthesized live audio + instagram HUD`)
- [`assets/storyboard_sheet.zh.png`](assets/storyboard_sheet.zh.png) · [`en`](assets/storyboard_sheet.en.png): Chinese and English 4-shot contact sheets
- [`rig_card.md`](rig_card.md): Camera Rig (`handheld-selfie-irl`) + Style (`roblox-blocky`) DNA card and 3-state setup anchor prompt
- [`storyboard.md`](storyboard.md) · [`prompts.json`](prompts.json): Clean-Plate first-frame & `sora` motion prompts + Post-HUD popup timeline
- [`drift_report.md`](drift_report.md): 8-gate anti-drift verification report (**PASS**)

## Reproduce

```bash
node scripts/rig_spec.mjs --rig handheld-selfie-irl --style roblox-blocky --host "momo_rblx" --lang zh-en --out examples/roblox-doors-irl-selfie/rig_card.md
node scripts/shot_compiler.mjs --template roblox-doors-irl-selfie --duration 15 --engine sora --platform instagram --lang zh-en --out examples/roblox-doors-irl-selfie/storyboard.md
node scripts/shot_compiler.mjs --template roblox-doors-irl-selfie --duration 15 --engine sora --platform instagram --json --out examples/roblox-doors-irl-selfie/prompts.json
node scripts/drift_check.mjs --pack examples/roblox-doors-irl-selfie/prompts.json --engine sora --lang zh-en --out examples/roblox-doors-irl-selfie/drift_report.md
```
