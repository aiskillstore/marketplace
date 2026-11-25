# 提示词模板（GPT Image 为主，MJ 可选）

## 1. 结构
```
[CHARACTER ANCHOR — 不可变，跨所有图逐字复用]
<名称>, <年龄印象>, <物种/种族与体型、身高印象>,
face: <脸型、眼形与颜色、鼻、嘴、肤色、痣疤等标记>,
hair: <颜色、长度、质地、分缝与走向>,
outfit: <内层 / 主体 / 连接件 / 配件，逐件写材质与颜色>,
signature: <核心道具结构>, <不对称记忆点（双写：角色侧（画面侧），例：角色左耳（画面右侧））>

[SHOT VARIABLE — 本次可变]
<景别与角度>, <姿态/动作>, <表情>, <背景>, <光线>, <画幅>

[STYLE]
Style: <style-library 中的固定风格描述>

[CONSTRAINTS]
no text, no watermark, <本次需要的限制>
```
锚点块一旦确认就不改写；身份跑偏时**加强锚点或改用参考图/编辑**，不是加更多风格词。锚点块里的画面侧标注（如「画面右侧」）以正面视角为基准：出侧面/背面图时该标注不逐字复用，只保留角色侧、由执行者按当前视角换算画面位置（见 lock-record.md 左右口径）。

## 2. GPT Image 使用要点
- 用自然语言完整描述，不依赖"和参考图一样"这类空指；参考图可见的特征也要写成文字。
- 有参考图时逐条写分工："Image 1: identity (face, hair) only. Image 2: outfit only — do not copy its face, pose or background."
- 编辑任务写明保留项与唯一修改项；要求保持原构图与画幅。
- 多张设定板（三视图等）可在一张图内完成，但要写清面板顺序、朝向角度与统一尺度。
- 参数（尺寸、质量）按当前工具实际支持填写，不确定就不写。
- 编译前扫一遍 Style 行与锚点、母版规格有没有直接冲突（如风格词含 real human 而种族非人、含戏剧光而母版禁用戏剧光）；有冲突按 SKILL.md 步骤 ④ 的编译冲突规则处理，不许原样硬塞。

## 3. 母版提示词示例结构
```
[ANCHOR]
Full body, front view, neutral relaxed expression, mouth closed, arms slightly away from body,
even soft studio lighting, plain light gray seamless background, no text.
Style: <...>
```

## 4. MJ（可选，探索审美）
MJ 只负责找方向：用锚点块的精简英文 + 风格描述出探索图；参数仅在确认当前版本支持后填写。选中后把 MJ 图作为**风格/造型参考**交给 GPT Image 重建母版，锚点以文字为准。

当前版本常用参数（填写前先核对所用界面/版本是否支持，不支持就不写）：
- `--ar W:H` 画幅，如全身母版 `--ar 2:3`
- `--v <版本号>` 模型版本，如 `--v 6.1`
- `--style raw` 减少 MJ 自带美化，探索阶段更接近提示词本身
- `--chaos 0–100` 探索发散度，找方向时可开 10–25；定方向后归 0
- `--sref <图>` 风格参考（把探索图或风格图当画风来源，不接管身份）
- `--cref <图> --cw 0–100` 角色参考（仅探索阶段借脸找感觉；正式母版必须回 GPT Image 以文字锚点为准重建）

## 5. 精简交付模板
```
角色定位：一句话
核心锚点：1–3 个
English prompt：<anchor + variable + style>
```
