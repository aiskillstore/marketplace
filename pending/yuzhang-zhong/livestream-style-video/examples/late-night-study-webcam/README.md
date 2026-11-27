# 04 · Late-Night Desk Webcam Study Stream Tabby Cat Chaos / 深夜赶工固定摄像头橘猫踩键盘（陪伴慢直播反转）

15-second (`9:16`, 4-shot) **Livestream POV** package compiled with `--template late-night-study-webcam --engine wan --platform x`.

| 9:16 Animated Preview (Post-HUD) | 4-Shot Storyboard Contact Sheet |
| :---: | :---: |
| <a href="assets/late_night_study_webcam.mp4"><img src="assets/late_night_study_webcam.gif" width="185" alt="Late-Night Desk Webcam Study Stream Tabby Cat Chaos 9:16 preview" /></a> | <img src="assets/storyboard_sheet.zh.png" width="540" alt="Late-Night Desk Webcam Study Stream Tabby Cat Chaos 4-shot contact sheet" /> |

## Package contents

- [`assets/late_night_study_webcam.mp4`](assets/late_night_study_webcam.mp4): offline 9:16 preview video (`H.264 MP4 + synthesized live audio + x HUD`)
- [`assets/storyboard_sheet.zh.png`](assets/storyboard_sheet.zh.png) · [`en`](assets/storyboard_sheet.en.png): Chinese and English 4-shot contact sheets
- [`rig_card.md`](rig_card.md): Camera Rig (`desktop-webcam`) + Style (`realistic-irl`) DNA card and 3-state setup anchor prompt
- [`storyboard.md`](storyboard.md) · [`prompts.json`](prompts.json): Clean-Plate first-frame & `wan` motion prompts + Post-HUD popup timeline
- [`drift_report.md`](drift_report.md): 8-gate anti-drift verification report (**PASS**)

## Reproduce

```bash
node scripts/rig_spec.mjs --rig desktop-webcam --style realistic-irl --host "dev_mika" --lang zh-en --out examples/late-night-study-webcam/rig_card.md
node scripts/shot_compiler.mjs --template late-night-study-webcam --duration 15 --engine wan --platform x --lang zh-en --out examples/late-night-study-webcam/storyboard.md
node scripts/shot_compiler.mjs --template late-night-study-webcam --duration 15 --engine wan --platform x --json --out examples/late-night-study-webcam/prompts.json
node scripts/drift_check.mjs --pack examples/late-night-study-webcam/prompts.json --engine wan --lang zh-en --out examples/late-night-study-webcam/drift_report.md
```
