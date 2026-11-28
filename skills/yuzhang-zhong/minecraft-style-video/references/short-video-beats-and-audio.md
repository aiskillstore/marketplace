# 9:16 Short-Video Beats, Camera Angles, and Minecraft Audio / 竖屏分镜节奏、机位与原版音效卡点

Viral Minecraft short videos on Douyin, Xiaohongshu, TikTok, and YouTube Shorts rely on **snappy block-grid timing**, **high-contrast lighting shifts**, and **instantly recognizable Minecraft sound effects**.

## 1. Three-Zone Retention Structure for 15s (4-Shot) Vertical Shorts

| Shot | Time Window | Retention Role | Voxel Action & Camera Rule |
| :---: | :---: | --- | --- |
| **Shot 01** | `0.0s – 3.8s` | **Hook / 黄金前3秒** | Open mid-action on a high-contrast voxel object (cracking a glowing `16×16×16` Diamond Ore, placing the final Lantern on a cabin, or a Creeper dropping into frame). Never start with an empty landscape pan. |
| **Shot 02** | `3.8s – 7.5s` | **Escalation 1 / 动作推进** | Execute one crisp mechanical hinge action (`swing pickaxe`, `snap hinged chest onto grid`, `place TNT block`). Pair with cubic pixel particles (`destroy_stage` cracks or placement dust). |
| **Shot 03** | `7.5s – 11.3s` | **Escalation 2 / 情绪或光影升级** | Trigger a dramatic visual state change: Creeper/TNT flashing white and swelling, BSL shader lantern light flooding the room, or `8×8` pixel eyes widening into `2×2` hollow squares. |
| **Shot 04** | `11.3s – 15.0s` | **Payoff & Loop / 反转或无缝循环** | Cubic white explosion smoke burst, red-tinted `90°` hurt tilt, cozy sunset diorama pull-back, or synchronized `45°` cubic head turn that matches Shot 01's framing for infinite loop replay. |

## 2. Signature Minecraft Camera framings for 9:16 Vertical Video

1. **Over-the-Shoulder Block Focus (`越肩方块特写`)**:
   - Frame the character's `8×8×8` head and `4×12×4` arm in the lower-left or lower-right third while keeping the target `16×16×16` block (Diamond Ore, Chest, Crafting Table, TNT) dead-center in the 9:16 sweet spot.
2. **45° Isometric Micro-Diorama (`45度微缩等距移轴视角`)**:
   - Ideal for Xiaohongshu/Douyin cozy builds (`cozy-lantern-build`). Use a 50mm tilt-shift depth of field on a `5×5×5` block cutaway chunk floating on a clean studio or twilight backdrop.
3. **Low-Angle Mob Confrontation (`低角度生物压迫仰拍`)**:
   - Place the camera near ground block level (`y = 0.3 blocks`) looking up at a swelling Creeper or a tall `3-block` Enderman with glowing purple pixel eyes.

## 3. Iconic Minecraft Sound Cues (`SFX`) & Visual Feedback Sync

Always pair each shot with its canonical Minecraft sound cue and visual particle counterpart:

| Event | Canonical Minecraft Sound Cue | Visual Particle / State Sync |
| --- | --- | --- |
| **Mining / Breaking Block** | `block.stone.hit` + crisp `block.stone.break` pop | Progressive dark pixel crack overlay (`destroy_stage_0..9`) -> burst of `12–16` small square texel cubes + bobbing miniature item drop |
| **XP / Diamond Pickup** | High-pitched `entity.experience_orb.pickup` (`Ding!`) + `entity.item.pickup` pop | Floating green/yellow square XP orbs curving into the character's torso |
| **Creeper / TNT Fuse** | `entity.creeper.primed` / `entity.tnt.primed` (`Tsssss...` 1.5s hiss) | Mob or TNT block alternates solid white emissive flash at 4Hz while expanding `1.15×` horizontally |
| **Voxel Explosion** | `entity.generic.explode` punchy low-pass boom | Cluster of stepped white/grey cubic smoke blocks expanding outward |
| **Chest / Door / Lantern** | `block.chest.open` wooden creak / `block.lantern.place` metallic clink | Chest top `14×4×14` lid hinges open `75°`; Lantern immediately casts warm `#F59E0B` block light across adjacent `16×16` texels |
| **Player Damage / Knockback** | Classic `entity.player.hurt` (`Oof / Crack!`) | Entire character mesh flashes translucent crimson red for `0.25s` and tilts `15°–90°` sideways |
