# Camera Prompt Patch Matrix

Use these surgical rewrites when `lint_camera_prompt.py` reports warnings:

## 1. Raw `zoom` vs `dolly` (`C02`)
- **Fail:** `Zoom in fast on the detective's face, cinematic.`
- **Pass:** `Starting from a medium shot on a stabilized gimbal, slow dolly in toward the detective at a steady measured pace, preserving natural background parallax and keeping her eyes centered, settling into an eye-level close-up.`

## 2. Multi-Axis Collision (`C03`)
- **Fail:** `Camera orbits around the car while panning left, tilting up, and zooming in dramatically.`
- **Pass:** `Steady 90-degree left arc orbit at constant distance around the silver coupe, keeping the vehicle body anchored center-frame with a level horizon, settling cleanly on a three-quarter front hero angle.`

## 3. Unanchored Start & Float Ending (`C05` / `C06`)
- **Fail:** `Epic tracking shot through neon alley.`
- **Pass:** `Starting on an eye-level wide shot behind the runner, smooth low tracking shot moving forward at constant walking pace down the rain-slick neon alley, keeping the runner's silhouette locked center-left and settling as she stops under the flickering signboard.`
