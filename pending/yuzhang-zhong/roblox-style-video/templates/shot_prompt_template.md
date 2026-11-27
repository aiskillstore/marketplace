# Shot Prompt Card / 单镜头提示词卡: Shot <NN>

## Shot Overview / 镜头概览

- **Time Window / 时间段**: `<0.0s–3.5s>`
- **Beat Role / 叙事功能**: `<Hook / Escalation / Payoff>`
- **Target Engine / 目标模型**: `<Kling / Seedance / Hailuo / Wan / Sora / Runway>`
- **Motion Intensity / 运动幅度建议**: `<Low (3/10) / Medium (5/10) / High-Slapstick (7/10)>`

## 1. First-Frame Image Prompt / 首帧静态图提示词 (I2V Anchor)

```text
[Subject Geometry Lock] + [Outfit & UGC Accessories] + [2D Face Decal Expression] + [Starting Pose] + [Miniature 3D Environment & Lighting] + [9:16 Composition & Lens]
```

## 2. Video Motion Prompt / 图生视频动态提示词 (I2V / T2V)

### English Prompt

```text
[Engine Camera Tag] + [Subject Anchor] + [Single Primary Action with Rigid Hinge Physics] + [Secondary Accessory/Light Motion] + [Geometry Lock Tail]
```

### 中文提示词

```text
[运镜指令] + [主体锚点与材质锁定] + [单一核心刚体动作] + [配饰/光影次级动态] + [防漂移几何尾缀]
```

## 3. Negative Prompt / 负向提示词

```text
human fingers, five-fingered hand, realistic human face, 3D nose, skin pores, Lego top studs, Minecraft voxel blocks, rubbery limbs, noodle arms, foot sliding, morphing clothes, text watermark
```
