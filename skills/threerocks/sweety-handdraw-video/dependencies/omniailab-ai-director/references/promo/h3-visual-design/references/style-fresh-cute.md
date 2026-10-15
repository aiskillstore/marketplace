---
name: omniailab-promo-h3-visual-design-style-fresh-cute
description: 「清新可爱风｜手绘综艺片头执行规则」—— 动态视觉设计（字体包装／追踪视觉／手绘融合） 方向细则：只在用户选择“清新可爱风”，或素材明确要求手绘综艺片头、粉笔/蜡笔动画、人物定格、涂鸦互动、旅行回忆录时读取。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 清新可爱风｜手绘综艺片头执行规则

只在用户选择“清新可爱风”，或素材明确要求手绘综艺片头、粉笔/蜡笔动画、人物定格、涂鸦互动、旅行回忆录时读取。本风格的核心是让真实画面、人物抠像、手绘线条、纸面拼贴和怪趣字体互相转化，不把“可爱”简化成一套低饱和圆体贴纸。

房地产、精致室内、展览、画廊、商业空间或建筑漫游优先执行 `7.1 建筑与精致室内适配`；该分支覆盖手绘综艺片头的高字重、强描边、人物定格、彩色涂鸦和快速换色。

## 导航

- 第 1–2 节：建立色盘、字体角色和手绘媒介。
- 第 3–4 节：选择动画动作并编排 15 秒片头。
- 第 5–7 节：判断原片权限、时长与特殊品类。
- 第 8–10 节：生成 Prompt、检查边界并读取参考锚点。

## 1. 固定视觉 DNA

生成 Prompt 前写：

```text
FRESH_DRAWN_DNA = {
  medium: live_action_cutout + chalk_crayon_line + paper_photo_collage + flat_illustration,
  palette_spine: chalk_white + one_deep_ink + rotating_source_based_accent_pairs,
  type_cast: quirky_chunky_display + chalk_marker_display + stable_humanist_utility,
  transition_spine: real_edge → growing_line → subject_outline → illustrated_carrier → color_wipe → final_title,
  motion_character: handmade_stepped_redraw + clean_readable_holds
}
```

### 颜色脚本

- 从原片取一个贯穿色，再建立 5–7 色的全片母盘；每个状态只显示其中 3–4 个颜色角色。
- 固定墨色使用粉笔白 `#FFF8E9`，搭配深可可 `#382822`、深墨绿 `#173F36` 或钴蓝 `#1649B8` 中的一种。
- 明亮组合按内容轮换：天空蓝/草绿/信号黄；木色/杏橙/西瓜红；钴蓝/叶绿/珊瑚粉。一个状态只使用一组组合，下一状态由继承的线条或色块换色。
- 实拍人物和环境保持原色；高饱和色主要落在描边、手绘景片、标题挤压面和转场形状上。
- 13–15 秒至少有三种颜色关系：实拍自然色 + 粉笔白、亮色人物定格、终版多色标题；同一深墨色负责全片稳定。

### 字体角色

```text
TYPE CAST:
- Display A: [master id]；2–6 个汉字或 1–3 个英文词；怪趣不等宽粗黑/圆尖混合综艺字，白色或亮色正面，2%–4% 手绘描边，3%–7% 单向扁平错位挤压面；承担人物名、主标题和最终片头字。
- Display B: [different secondary id]；4–12 个汉字或一条短英文 phrase；粉笔、蜡笔或记号笔骨架，笔画粗细和边缘纹理可见；承担心情句、动作句和手绘大字。
- Utility: [different verified labels]；中等字重人文黑体/圆体或稳定手写细字；承担准确小标题、相片日期、地点、真实注释和录制框标签。
- Marks: 无文字手绘线、箭头、花、叶、云、翅膀、动物轮廓、脚印、路径、圆框和内容图标；全部来自画面中的人物、物件、地点或动作。
```

可爱/综艺子路由可以额外使用气泡、箭头、星芒、手绘线、笑脸、胶带角和夸张感叹框；它们必须从真实动作或物件边缘生长，和圆润/怪趣字、亮色描边、相片卡一起使用。复古拼贴海报不自动继承这组糖果色装饰。

- Display A/B/Utility 使用不同白名单文案；中英文分别补充信息，不逐条互译，也不把同一句换字体复用。
- 字体多样性来自固定角色的粗细、材质和空间分工；每个状态继续复用同一 TYPE CAST，不临时换一套字体。
- 汉字先保持完整偏旁和方形重心，再进行描边抖动、错位挤压或轻微角度差；英文保持完整拼写和清楚基线。

## 2. 手绘媒介与画面层级

先写 `HAND_DRAWN_SOURCE_MAP`：逐镜记录一个真实动作、一个可追踪轮廓、一处负空间、一件可画成图标的真实物件，以及该手绘元素在下一镜的去向。

- `Live layer`：保留真实人物、产品或环境，提供动作、光线和情绪锚点。
- `Cutout layer`：人物/物件只抠一份，使用一种专色描边；可在前景、中景和后景交换一次，不复制五官和肢体。
- `Doodle layer`：沿真实轮廓、手势、行走路线、流水、树线或物件边缘逐段生长；线条随后变成相框、地形、翅膀、气泡或下一镜擦屏边。
- `Photo/card layer`：使用同一素材的真实裁切、相片、圆形局部或双格回忆卡；卡片边缘允许粉笔框、胶片孔、手撕纸或录制角标中的一种。
- `Illustration layer`：用平涂、蜡笔或粉笔画出素材中已存在的人物、动物、植物和物件；完整插画状态保持发型、服装、动作、数量和身份线索。

13–15 秒至少使用 Live、Cutout、Doodle、Photo/Illustration 中三层，并发生一次前后景遮挡和一次媒介转换。装饰必须服务当前内容：人物抬手可长出翅膀/动作弧，走路可留下路径/脚印，树线可延伸成山丘/相框，真实动物可转成插画伙伴。

## 3. 动画动作库

每个状态只选一个主动作；其他层同步落位或稳定。一个动作写清 `真实触发 → 手绘生成 → 完整构图 → 继承到下一状态`。

- `Line grow`：线头从真实边缘出发，0.25–0.70 秒沿一个方向画完；到达终点后才出现文字或图标，随后一段线变成下一镜边框。
- `Stepped redraw`：手绘线以 6–10 fps 的逐帧重画感轻微变化，偏移不超过线宽的 30%；持续 0.4–0.9 秒后冻结成干净轮廓，人物实拍仍保持正常帧率。
- `Freeze-frame cast`：动作重音处冻结 0.45–0.90 秒；人物抠像向前错层 2%–4%，专色轮廓写入，Display A 分语义组落位，插画伙伴或真实物件从背后探出。
- `Photo-page swap`：一张真实相片沿画边推入，第二张由同一纸边翻开或擦出；0.30–0.60 秒完成，卡片稳定 0.8–1.2 秒。
- `Live-to-drawn`：真实轮廓先被完整描出，颜色随后从接触点铺开，在 0.40–0.90 秒内形成局部或完整插画；下一触发点让同一色块擦回实拍或进入新镜。
- `Doodle morph`：翅膀、花、叶、动物轮廓、路径或手写圈在 2–4 张明确关键形之间变化，最终成为相框、地形或转场遮罩。
- `Color-shape wipe`：由前一镜已有的叶片、山丘、气泡、纸面或笔画扩张覆盖 70%–100% 画面，0.20–0.45 秒后揭开下一状态；形状与颜色必须在前镜先出现。
- `Title assembly`：Display A 的字组、Display B 的弧形/手写短句、人物抠像和 2–4 个 Marks 依次到位，0.55–0.95 秒完成，终版稳定 1.0–1.4 秒。

基础动作不再统一使用“短弧滑入 + 106% 回弹”。回弹只在内容本身具有跳跃、碰撞或惊喜重音时使用一次；其余状态分别使用写入、描边、翻页、错层、转绘、形变或擦屏。

## 4. 15 秒手绘综艺片头

```text
STATE 1｜0.0–2.5s｜PHOTO COLD OPEN
从真实画边翻出一至两张相片/局部卡；粉笔线把相片边缘接成标题基线，Display B 写出第一条完整心情或场景句。实拍底、纸面和粉笔白先建立。

STATE 2｜2.5–5.3s｜FREEZE-FRAME CAST
在真实动作重音处定格人物/物件；一层专色轮廓沿主体写完，Display A 以怪趣粗字建立人物/主题 Hero。一个内容相关的插画伙伴、物件或地形从主体背后进入，主体穿过文字一次。

STATE 3｜5.3–8.5s｜DRAWN INTERACTION
同一轮廓长出翅膀、花叶、路径、动物线稿或动作弧；局部实拍转成平涂/蜡笔插画，再由线条拉回真实主体。Display B 使用另一条真实文案，跟随负空间或动作方向写入。

STATE 4｜8.5–11.8s｜COLLAGE / COLOR CHANGE
前一状态的手绘元素扩成色块擦屏；进入新的亮色组合和双格/圆形相片拼贴。Utility 锁定真实地点、时间或内容标签；一条线跨卡片连接因果或行程，不做无关装饰。

STATE 5｜11.8–15.0s｜VARIETY TITLE RESOLVE
相框边、人物描边和手绘路径汇成终版片头：Display A 主标题、不同 Display B 短句、稳定 Utility、中心主体和 2–4 个内容 Marks 共同落位。只在标题完成时给一次短促彩纸/叶片/线尾响应，稳定 1.0–1.4 秒。
```

五个状态继承同一条线、同一深墨色、同一 TYPE CAST 和同一主体身份。每段像同一本手绘旅行册/综艺片头的连续页面，不写成五套独立模板。

## 5. 原片权限

### 锁定原片，只做包装

- 保持原片镜头、动作、声音、调色和剪辑；只新增相片裁切、单份人物抠像、粉笔线、平涂 Marks 和文字。
- 人脸、身体和环境保持实拍；`Live-to-drawn` 只覆盖轮廓外侧、衣物局部或背景载体，并在 0.9 秒内回到实拍。
- 手绘动物、植物、物件和地点只能来自原片或用户资料；抽象情绪使用线条、色块和无文字符号表达。

### 根据视频二创 / 架空重建

- 保持人物/产品身份、服装、数量、关键动作和地点线索；允许 0.4–1.0 秒完整插画状态，并明确从哪条真实轮廓进入、从哪块颜色回到实拍。
- 可重排负空间、相片卡和人物抠像，但每个新图形仍由真实内容触发；不自动改成商品广告舞台。

## 6. 时长适配

- `4–5 秒`：相片/真实边缘写线 → 人物定格 + Display A → 手绘标题终版，共 2 个状态。
- `6–8 秒`：相片开场 → 定格抠像/描边 → 局部转插画 → 标题，共 3 个状态。
- `9–12 秒`：保留 PHOTO、CAST、DRAWN、TITLE 四状态，至少一次换色和一次媒介转换。
- `13–15 秒`：完整执行五状态，至少三种媒介、三种颜色关系和三种固定字体角色。

## 7. 特殊品类覆盖

### 7.1 建筑与精致室内适配

- 把“可爱”转译成轻盈、亲和、低饱和专色和柔和缓动；Display A 使用中等字重几何/人文无衬线或现代宋体，Display B 只用一个克制手写角色，Utility 使用真实空间信息。
- 保留原空间色盘，只取一个低饱和专色配暖白/深灰；从柱线、墙缝、画框、门窗、桌边、百叶、圆灯或光影生成一条真实空间轴和一个载体。
- 使用 `SPATIAL_MOTIF_MAP` 和 `DISCOVER → ATTACH → TRACK → OCCLUDE → TRANSFER → SETTLE`；全片一个 master title、一次 55%–85% Hero、2–3 条空间关系文案和 3–5 个真实标签。
- 字体使用单色实心、局部半透明建筑面或 1%–2% 软阴影；艺术品、家具、墙面比例和原相机运动保持主角。

### 7.2 产品架空展示

- 使用奶油白圆角舞台、一个素材取样专色和柔和接触影；保持产品身份与真实结构，空间上优先做前景卡片 / 中景主体 / 后墙标题的三层关系，让可爱更像综艺片头，不像平贴纸。
- 以干净 3/4 全貌开始，做一次 60° 绕拍与 4–6 cm 轻浮起，再推近一个真实按钮、纹理或边缘；产品本身只落稳一次。
- 让产品真实边缘生成 2–5 个同源手绘点、短线或图标；它们触碰 Display A 后变成相框/基线。Display B 使用不同文案形成一次 75%–110% 片头状态，Utility 锁在一个圆角框角。

## 8. 可直接写入 H3 Prompt 的锁定块

```text
FRESH HAND-DRAWN VARIETY OPENING LOCK:
Build one continuous hand-drawn variety-show opening from live-action cutouts, chalk/crayon lines, paper-photo collage and flat illustration.
COLOR SCRIPT: [source anchor] + chalk white + [deep ink] remain continuous; rotate [accent pair 1] → [accent pair 2] → [final accent pair], with 3–4 visible color roles per state.
TYPE CAST: Display A=[exact master id + quirky chunky/short flat extrusion role]；Display B=[different exact secondary id + chalk/crayon/marker role]；Utility=[different verified labels + stable humanist role].
SOURCE MAP: [real action] generates [line/outline] → becomes [frame/wing/path/illustrated carrier] → expands into [color wipe] → resolves as [final title component].
MEDIA CHOREOGRAPHY: photo cold open → freeze-frame cast → live/drawn interaction → collage/color change → variety title resolve；inherit one line, one deep ink, the same type cast and the same subject identity.
READABILITY: complete text settles after each handmade transition and remains stable for 0.8–1.2 seconds；the final title holds for 1.0–1.4 seconds.
```

## 9. 生成指令前检查

- 配色是否有贯穿色和分状态换色，而不是固定薄荷粉橙或全片彩虹？
- Display A/B/Utility 是否为三种明确角色并使用不同文案？
- 是否至少出现相片/卡片、人物定格、线条生长、局部转绘、内容涂鸦或色块擦屏中的三种媒介？
- 每个手绘元素是否从真实动作/物件/轮廓产生，并成为下一状态的载体？
- 动画是否交替使用写入、翻页、描边、错层、转绘、形变和擦屏，而不是所有文字回弹？
- 锁定原片时是否保持人脸、镜头、声音和调色；完整插画是否只用于已授权二创？
- 建筑/室内是否启用 7.1，保持一个主标题、一条真实空间轴和克制三级字阶？
- 最终片头是否让主体、主标题、次级手写字和手绘图形稳定共存？

## 10. 用户参考锚点：只内化机制

- [现在就出发 2 AE 栏目包装](https://www.xiaohongshu.com/discovery/item/6964c223000000000c0355ce)：内化人物定格抠像、白蓝怪趣立体名字、弧形英文、动物/地形插画、绿色路径与树形擦屏，以及多人物片头汇成终版标题的方式。
- [用综艺的感觉打开夏天回忆录](https://www.xiaohongshu.com/discovery/item/65c35abf000000001100d1ca)：内化相片翻页、粉笔手写、线条生长、蝴蝶翅膀、实拍转插画、双格回忆卡、录制框和手绘英文终版。
- [芒果综艺手绘后期](https://www.xiaohongshu.com/discovery/item/6860ed7200000000230049d9)：内化人物专色描边、夸张表情插画、黄橙漫画色场、反应动物和人物抠像压住后景手写标题的层级。

所有参考只校准媒介、运动、字体角色和颜色关系；生成时使用用户自己的主体、文案、物件与身份，不复制参考中的节目名、Logo、人物、水印或原文字。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
