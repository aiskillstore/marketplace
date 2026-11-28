# Livestream Camera Rigs and Optics / 八大直播机位光学与物理锚点规范

The single biggest difference between a "movie clip" and a "livestream clip" is **physical camera truth**: viewers subconsciously recognize *where the camera is mounted*, *what lens focal length it uses*, and *how the rig vibrates when the host moves or touches the desk*.

## 1. Eight Canonical Livestream Camera Rigs / 八大标准直播机位总表

| Rig ID | Mount & Focal Length | Depth of Field | Physical Motion Signature | Best Scenarios |
| --- | --- | --- | --- | --- |
| `desktop-webcam` | Monitor-top (`5–8°` down) or desk ring-light stand, `24–28mm` | Deep `f/4.5` (room shelves & RGB strips stay readable) | 100% locked horizon; high-frequency micro-shake **only** on desk slams | Chatting, late-night study, coding, reaction, drama storytime |
| `handheld-selfie-irl` | Extended arm / pocket gimbal (`55–70cm`), `18–20mm` ultra-wide front cam | Deep `f/4`, slight close-range nose/hand perspective | Coupled to footsteps & arm fatigue; `6–12°` roll on sudden turns; auto-exposure shift indoors/outdoors | Street food, travel, outdoor dares, wuxia/fantasy IRL adaptations |
| `pip-facecam-rig` | **Track A**: active game/world cam; **Track B**: locked `28mm` RGB webcam | Track A variable; Track B `f/4` studio sharp | Dual-track independent plates composited cleanly; PiP box never warps | Roblox obby, horror gaming, speedruns, live commentary reactions |
| `overhead-showcase-rig` | `35mm` C-stand / desk clamp (`30–45°` or counter level) | Continuous `AF-C` shifting from host (`f/4`) to `18cm` macro item (`f/2.8`) | Locked stand; **palm-backed influencer autofocus gesture** triggers crisp focus pull | Unboxing, beauty swatches, tech gadgets, blind-box drops, cooking |
| `chest-head-pov` | Chest harness or head strap, `16mm` action-cam wide | Deep `f/5.6` from `25cm` foreground hands to hallway end | Breathing rise/fall, crisp footstep thuds, flashlight cone coupled to torso | Urban exploration, haunted corridors, craftsmanship, parkour POV |
| `pk-cohost-split` | Two independent locked `28mm` studio webcams in `50/50` split | Both rooms `f/4.5` with contrasting warm vs. cool RGB keys | Independent locked frames; hosts lean toward the center split seam | Co-stream debates, talent PK battles, Pro vs. Noob mystery box duels |
| `cctv-obs-fixed` | Ceiling corner (`25–30°` down), `20mm` wide security/room cam | Infinite `f/8` covering full room floor-to-door | 100% bolted static frame; zero pan/zoom—subjects enter/exit frame | 24/7 pet cams, convenience store night shift, candid fail comedy |
| `drone-follow-live` | Handheld follow-gimbal or low follow-drone (`2–3m` distance), `24mm` | `f/4` live broadcast auto-exposure | `0.2s` human cameraman framing lag when subject sprints or pivots | Sports challenges, street interviews, large-scale outdoor stunts |

## 2. The Fourth-Wall Eye-Line Triangle (`0° / 15° / 8°` 直播眼神三角)

Never write `"the character acts naturally"` without specifying eye-line geometry—diffusion models will default to an off-camera movie gaze (`30–45°` away with zero viewer awareness). Lock one of three livestream eye-lines per beat:

1. **`0° Direct Primary Lens Address (`主镜0°怼脸直视`)**:
   - Eyes lock straight into the optical center of the webcam or front selfie camera. Circular ring-light or screen catchlights sit centered on the pupils.
2. **`15° Off-Axis Chat-Monitor Glance (`桌面15°偏轴扫弹幕`)**:
   - Used in `desktop-webcam`, `pip-facecam-rig`, and `overhead-showcase-rig`. The host's eyes (and slight `5–10°` head yaw) flick toward a secondary monitor or iPad just off-frame, pause `0.3–0.5s` while cool screen glow shifts across glasses/cheeks, then snap back to `0°` to reply.
3. **`8° Downward Phone-Screen Read (`手持8°下瞥弹幕区`)**:
   - Used in `handheld-selfie-irl`. Because live comments scroll along the lower half of the smartphone screen just beneath the front camera bezel, the host's eyes dip `8°` downward when reading surging comments, then flick back up to `0°` lens.

## 3. Microphone & Studio Prop Continuity Lock

Cross-shot diffusion cuts frequently flip boom microphones from screen-left to screen-right. Always declare exact screen-space side ownership in every shot prompt:
- `boom-left`: `"matte-black condenser boom microphone arm entering from the lower-left frame edge with foam pop filter"`
- `lavalier`: `"compact clip-on wireless lavalier microphone transmitter clipped to collar"`
- `headset-mic`: `"over-ear RGB headset with curved boom mic positioned at left cheek"`
