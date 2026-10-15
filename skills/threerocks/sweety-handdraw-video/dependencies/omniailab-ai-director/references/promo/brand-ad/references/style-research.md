---
name: omniailab-promo-brand-ad-style-research
description: 「品牌广告与 TVC 风格 Research」—— 品牌广告与 TVC（官方） 方向细则：在 brand-ad 需要补充风格、产品氛围、叙事世界或 Campaign 差异参考时读取。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 品牌广告与 TVC 风格 Research

在 `brand-ad` 需要补充风格、产品氛围、叙事世界或 Campaign 差异参考时读取。默认使用“缺口判断 → 定向搜索 → 用户选图 → 分析 → 下游引用”骨架；复杂 TVC 只有在明确的策略问题仍未解决时才追加研究轮次，并把结果合入同一份品牌方向锁。

**交互预算：**第一轮搜索的正常路径停顿三次：先确认是否搜索，再从 3 张推荐候选中选择方向，最后在常规生成前确认创意与分镜。选择不搜索时跳过搜索与选图；用户已明确要求搜索、明确拒绝搜索、明确只用已有参考或授权代选时，跳过对应的重复确认。追加研究不得重复询问已确认事项。

## 1. 快速门禁

- 路线选定后默认主动提出 Research，并在搜索前用一次 confirmation card 让用户决定，不静默搜索，也不让用户自己外出找图。只有用户已明确要求搜索、明确拒绝搜索，或明确只使用已上传参考时才跳过该问题。
- confirmation card 使用清楚的二选一语义：“是否先搜索一轮风格参考图？搜索后会提供 3 张推荐候选供你选择主方向，后续风格、运镜和品牌区分会更稳，但会多一个选图环节，整体链路与耗时更长；不搜索会更快，但仅根据当前 brief 或已有参考推导风格，稳定性和品牌区分度可能较弱。”选项为“搜索参考图”和“不搜索，直接制作”。
- 用户选择搜索后才执行；选择不搜索时记录 `research_mode: skipped_by_user` 并继续创意，不重复劝说。用户已明确要求搜索或明确拒绝时，不再重复询问。
- 用户已给参考但没有明确排除搜索时，把问题改为“是否再搜索一轮补充风格参考”；选择搜索后只围绕现有参考未覆盖的关键维度编 query，选择不搜索时直接使用现有参考。
- 用户没有可用风格参考且没有明确风格时，不追加“高级 / 科技 / 电影感”等抽象偏好问题；第一轮搜索后只展示 3 个差异明确的推荐方向。推荐方向是 soft inspiration，不是创意执行锁。
- 三个推荐方向不能只写风格形容词：每个方向先绑定一个与当前路线匹配的 reference path，并读取该 ref 的适用边界和执行方法，再编译成用户可见选项。可用的方向与 ref 示例为：感官 / 物理隐喻 → [sensory-visual-prompting.md](sensory-visual-prompting.md)；品牌 Hero 情绪推进 → [brand-hero-emotional-structure.md](brand-hero-emotional-structure.md)；未来系统视觉 → [future-system-montage.md](future-system-montage.md)。不适配当前路线的 ref 不得为了凑满三项而强行使用。
- 品类、目标时长和画幅已足以编 query 时，不为“高级还是科技”、成片形态、旁白、CTA 或其他非搜索阻塞项增加问题。
- Research 只补风格与品类氛围。产品型号、包装、Logo、文字、卖点和指标仍只信用户素材或官方来源。
- 明确的新品牌/原创概念没有 Logo 或包装时，直接以“概念片”边界搜索；概念字标、概念包装和不可作为官方标识的说明并入生成前确认，不先单独询问是否继续。

## 2. 定向搜索，生成 3 张推荐候选

从已核验的品类、品牌定位、已选路线、平台/画幅和卖点编译 **3 个互有差异但都符合 brief 的英文 query**。各方向必须在空间、光线、材质或镜头语法上有实质差异，不只是换颜色。每个 query 使用：

```text
{specific product category} {direction-specific art direction} commercial editorial style frame {concrete light/material/composition mechanism}
```

使用一次批量图片搜索，保持原搜索覆盖度：每个方向提交一个具体英文 query，每个方向最多保留三张候选，并优先保留短边至少 1200 像素的清晰图片。

- 搜索预算为主 Agent 的内部计时预算；到时使用当前最佳结果，不为凑数量扩展 query。
- 禁止单独使用 `moodboard`、`aesthetic`、`cinematic`、`4k`、“高级感”或“氛围感”作为 query。
- 预筛时不使用 media analysis。剔除重复、低分辨率、拼贴/缩略图、纯 Logo/字卡、无关品类和只靠明星/他牌身份成立的图。
- 每张候选默认同时提供可迁移风格和可承载产品的空间/氛围；只有品牌视觉过程或未来系统蒙太奇路线可使用不出现产品空间的纯视觉系统图。
- 跨 query 去重并过滤后保留 3 张差异明确的候选，并按推荐顺序编号 `brand_direction_01..03`；同轮可靠候选不足 3 张时展示当前全部有效项，不补弱相关图。整批为空时才允许改写一次 query。

## 3. 一屏展示，选择主方向

1. 把 3 张候选作为独立媒体节点写入画布，稳定编号 `brand_direction_01..03`；不创建 Research 文档。
2. 用一张确认卡提供恰好 3 个用户可见选项；每个选项包含“方向名 + 对应 reference + 一句可见差异 + 适用原因”，并关联对应画布 ref。每个选项的 reference 必须已读取并记录其贡献与禁止迁移内容。请用户选择 1 个主方向并回复“选好了”；只有用户明确要求混合时才允许追加第 2 张。
3. 用户回复后读取选择结果，把所有已选节点的真实路径写入参考集合。选择为空时只提醒至少选择一张或明确改为不使用 Research，不重新搜索。
4. 用户已明确授权主 Agent 代选时，选择与品牌事实和路线最匹配的一张或多张，记录 `selection_mode: delegated`，跳过这次选择停顿。

## 4. 只分析已选图

只对全部已选图执行一次批量媒体分析，逐张提取：成像与镜头质感、构图/机位/负空间、光比/高光/阴影、色彩结构、空间层次、材质和产品摆位，以及可转成运镜/转场/节奏的动态暗示。同时逐张记录不得迁移的人脸、人物身份、产品外观、Logo、包装、文字和案例专属道具。不分析未选候选，不猜测无来源 HEX，不重复读图。

收敛为一个 `Style Reference Capsule`，记录已选方向图片的真实路径、对应 reference 路径、可贡献内容、禁止迁移内容、选择方式、6–8 个可观察风格词、一句可执行风格描述、起点—路径—终点及节奏，以及 1–2 个由材质或动作触发的转场机制。

风格词必须可观察，例如 `precise hard rim light`、`low-saturation mineral palette`、`macro condensation texture`、`slow axial dolly with abrupt hero stop`；禁止只写 `premium`、`cinematic`、`stylish`、`high-end`。

## 5. 直接进入创意确认与 H3

1. 把品牌/产品事实与 `Style Reference Capsule` 组合为 `Brand Direction Lock`：2–3 个带 `evidence` 和 `status: verified | creative_interpretation` 的品牌特质，以及唯一 `visual_thesis`、`camera_grammar`、`rhythm_curve`、`transition_profile` 和“开场钩子 → 品牌/产品证明 → 视觉揭示 → 品牌收束”的 `script_spine`。参考图不能反推新的品牌故事、口号或卖点。
2. 不为 Research 结果新增一次确认。立即把已选图、`Brand Direction Lock`、时间码分镜、文字与声音放进本 Skill 原有的生成前确认；用户确认后直接生成。
3. 每个镜头写新的品牌或产品信息，并用主体动作、材质反应、环境反馈或空间关系推进；不能只换景别、重复产品慢转或用泛化运镜填时长。
4. 进入 H3 生成时，把 `selected_direction_refs[*].path` 全部按顺序作为真实参考，逐张映射为对应 `@图片N`，并写清各自风格贡献与禁止迁移内容；同时写入收敛后的风格词、运镜和转场。未选候选图、纯文字风格词或画布缩略图不得替代真实 path。

## 6. 复杂 TVC 的追加研究

- 只有在第一轮后仍存在一个已命名、会改变脚本或视觉系统的缺口时追加研究，例如受众文化语境、品类视觉符号、角色世界、竞品差异或系列 Campaign 统一性。
- 每轮只回答一个问题，保留来源与结论，并说明它改变 `Brand Direction Lock`、脚本、分镜或连续性圣经中的哪一项；不能用更多图片替代决策。
- 新结论与已确认事实冲突时暂停并请求用户选择；没有冲突时并入既有的生成前或里程碑确认，不额外堆叠审核环节。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
