# 画风选择与可绘制约定

## 选择弹窗

每个新任务先确定画风路径。明确编号、明确三个选项之一、明确自定义描述、明确委托模型，都可记录后直接执行，不重复询问；否则通过[制作选项窗口](production-options.md)展示图文选择，最多等待60秒。超时采用模型事先根据内容拟定的方案，记录 `timeout_default` 并继续。这里是本地 HTML 选择界面，不是原生系统对话框。

```bash
python3 scripts/style_choice.py prepare JOB --catalog-source /path/to/hand-drawn
python3 scripts/production_options.py JOB --defaults JOB/options/defaults.json
```

用当前可用的打开网页工具展示输出的 `PRODUCTION_OPTIONS_URL`。窗口逐个展示编号、原始画风名、真实效果图，可搜索和放大。末尾必须是：

1. **不主动选择，由模型自动匹配**：`catalog_auto`，根据内容从本次快照库中选最合适的一种，记录理由与完整配方。
2. **不选择列表中的，模型推理产出**：`inferred`，根据内容独立推理线条、色板、明暗、材质、背景；不加载或借用画风库配方，不用某个编号悄悄兜底。
3. **自定义描述风格**：`custom`，用户描述是画风依据，不受画风库和内容偏好替换；内容只决定画什么。描述不足时只补足可执行细节，存在冲突时指出冲突。

直接点某张卡为 `catalog`。以上四条路径都受同一绘制约定约束。

用户明确指出某个安装路径时，以该路径的实际目录为准；不要混进另一个版本的编号。否则默认使用本包固定依赖。目录从 `STYLES.md` 动态提取，不手写固定数量；快照保存完整配方和哈希。预览优先真实本地图，其次包内缩略图，最后使用上游清单的图片地址；不可用时修复图片后再让用户选择，不能用臆造图片冒充效果图。更换目录来源需要重新准备快照。

弹窗只监听 127.0.0.1，仅保存该任务的选择文件。不自动生图、启动付费任务或发布。完成选择后停止本次服务。

## 风格决策文件

`style/selection.json` 由窗口保存。用户在聊天中明确选择/委托时可手工记录，`confirmation` 用 `explicit_user_request` 或 `user_delegated`；等待结束后用 `timeout_default`，说明实际等待时间和模型默认方案，不制造用户确认记录。

```json
{"mode":"inferred","confirmation":"explicit_user_request","evidence":"用户明确选择不选择列表中的，模型推理产出"}
```

模型随后写 `style/resolved.json`：

```json
{
  "status":"resolved",
  "mode":"inferred",
  "selection_sha256":"selection.json 的实际 SHA-256",
  "style_name":"本片实际画风名称",
  "rationale":"为什么采用此画法",
  "content_fit":"与本片具体内容的对应关系",
  "style_spec":{"line":"可分辨的独立轮廓","palette":"具体配色","shading":"具体明暗","texture":"具体质感","background":"背景处理"}
}
```

库内两模式还须 `catalog_id` 和快照中的 `recipe_sha256`；库内自动匹配须 `content_fit`。独立推理禁止这些库内字段。自定义还须 `style_basis`，逐字保留用户描述。先运行 `python3 scripts/style_choice.py verify JOB`。

库内配方的锚点、多阶段生成等既有要求仍然适用。对于原本没有黑轮廓的纸雕、像素、水粉、扁平等画风，提前设计可独立追踪的轮廓层或对齐轮廓遮罩，不能假装深色色块就是全部轮廓。保留所选风格的外观；若当前工具无法兼顾，要在生图前说明具体冲突，不能偷偷换画风。

## 出图前的可绘制计划

每次调用图像生成或编辑前，先写计划并运行：

```bash
python3 scripts/drawing_contract.py JOB JOB/design/drawing-plan.json
```

输入含 `illustrations` 数组，每项有唯一 `id`，并包含：

- `composition`：实际主体、动作、遮挡和留白安排。
- `drawability_reason`：为什么这些部分能独立描线和上色，线条复杂度是否适合口播时长。
- `outline_strategy`：`visible_source_ink` 或 `explicit_mask`；后者在 action 提供同尺寸的灰度 `outline_mask`，白色为轮廓、黑色为填色。
- `subjects`：每个对象的 `id` 与 `kind`（human/animal/object/environment）。人物须覆盖 `head / neck / torso / left_arm / right_arm / lower_body`；不可见部分放入 `omitted_roles` 并说明裁切或遮挡，不能借此略过实际可见部位。左右指画面左右；不同观察角度保持解释一致。
- `parts`：按实际绘制顺序，每项写 `id / subject / role / stroke_groups`。`stroke_groups` 是独立笔画的简述数组，例如头部的外形弧线、左眼、右眼、鼻、嘴；不能一句“整个头连续画完”替代。
- `outline_order`、`fill_order`：均为同一有序 part id 数组。
- `spatial_order`：通常 `top_to_bottom_left_to_right`；构图/遮挡例外记录 `order_exception`。人物默认头、脖子、躯干、左臂、右臂、下半身，非默认在该 subject 写 `order_exception`。

校验通过生成同名 `.preflight.json`，绑定风格和计划哈希。计划改变后须重新预检；若图已生成，先重新评估受影响部分，不能把新计划伪称为旧图的出图前证据。

## 成图后的核对与执行

实际看图后，为 action 写 `drawing_plan_id`、按计划同顺序的 `parts` 多边形及必要排除区域，所有可见像素只能归属一个部位。多边形随实际解剖与遮挡，不用从上到下的等高横条代替语义部位。

`job.json` 指定 `drawing_plan` 和 `drawing_review`。使用 `outline_mask` 时，审核中还须 `outline_mask_sha256`，且遮罩尺寸必须与裁切前的完整原图一致。后者结构：

```json
{"style_sha256":"resolved.json 的实际哈希","plan_sha256":"实际计划哈希","illustrations":[{
  "plan_id":"figure-01","status":"pass","source_sha256":"实际图像哈希","crop":null,
  "anatomy_and_occlusion":"看到了什么、哪些部位被遮挡",
  "part_boundaries":"各区域如何对应实际部位",
  "stroke_breaks":"哪里起笔、转折、收笔与抬笔",
  "outline_then_fill":"轮廓是否齐全且可独立追踪",
  "spatial_order":"确认部位顺序或说明构图例外"
}]}
```

`art_direction.record` 的顶层也须写入相同 `style_sha256`，绑定封面和生成素材到本次画风。换画风后不得沿用旧的图片审核。

所有插画整幅轮廓完成后才能填色，两阶段按同一部位顺序。黑白线稿可以没有填色阶段，但不可反过来省略轮廓。笔画只能沿连续像素前进，断开的笔画必须抬笔，不能用最近点跳连；颜色只在笔刷经过范围出现。短到看不出起落、画面必须疯狂跳笔才能赶上口播时，减少非必要线条或重新分镜，不能靠缩短抬笔假装自然。

构建、渲染、验证会拒绝缺少风格/计划/审核的生产任务，并校验实际路径。检查不能自动证明模型标对了人体或遵守了画风；代表段必须实际检查轮廓末帧、填色起始、关键部位切换和连续动作。旧任务没有这些证据时需按真实来源重新评估，不批量补写“通过”。运行测试 fixture 仅用于工程回归，禁止最终交付。
