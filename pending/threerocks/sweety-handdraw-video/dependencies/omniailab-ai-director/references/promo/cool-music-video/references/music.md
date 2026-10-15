---
name: omniailab-promo-cool-music-video-music
description: 「复古潮流拼贴音乐执行」—— 酷感音乐短片（15 秒横屏） 方向细则：音乐是镜头、人物动作和文字动效的上游，不是最后补一段“有氛围音乐”。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 复古潮流拼贴音乐执行

音乐是镜头、人物动作和文字动效的上游，不是最后补一段“有氛围音乐”。15 秒必须像一首完成度高的微型歌曲：有开场身份、连续 vocal 内容、可记住的 Hook、至少一次 flow 或编曲变化、Hook 回归和明确结束。缺少音乐信息时只让用户选择“原创歌曲 / 纯器乐 BGM / 上传参考音乐”；选择后不再确认歌词、Hook 或屏幕词。

用户选择原创歌曲但没有指定曲风时，默认写 **K-pop hip-hop / K-hip-hop / trap-rap performance track**，让复古拼贴、高时装人物表演和大字包装拥有清楚的说唱推进与旋律 Hook。用户明确指定 dark-pop、post-punk、boom-bap 或其他方向时服从用户，但仍保留完整的 15 秒歌曲结构。不得写“模仿某位真实艺人”；只描述节奏、旋律、声线、编曲与表演特征。

## 15 秒八小节结构

默认 4/4、128 BPM；8 小节约等于 15 秒。K-pop hip-hop 默认使用 128 BPM double-time grid / 64 BPM half-time body feel，既能快速切镜又保留说唱落点。按以下时间线写入 `Music Prompt`，并把每一段绑定到镜头、动作和字体：

1. **Bar 1｜0.0–1.875s｜Intro tag**：用制作人式 vocal tag、吸气、短采样或 4–6 音主 motif 建立身份；低频不要一开始就铺满。
2. **Bars 2–3｜1.875–5.625s｜Rap A**：两条连续 rap lyric，一条使用紧凑 straight-sixteenth pocket，下一条改为切分或 triplet cadence；两条语义相连，不是孤立口号。
3. **Bar 4｜5.625–7.5s｜Pre-hook lift**：减少 808 或 kick，用上行旋律、和声抬升、反拍 clap 或半拍停顿把 rap 推向 Hook。
4. **Bars 5–6｜7.5–11.25s｜Melodic / chant Hook**：两句短 Hook，采用问答关系、清晰音程和多层人声；第二句回应第一句，不能只是同一句机械复制。
5. **Bar 7｜11.25–13.125s｜Beat switch / response**：只改变一个关键支点，例如抽掉 kick、切换 808 节奏、短暂半拍或加入 crowd response；保持同一歌曲，不突然换成无关曲风。
6. **Bar 8｜13.125–15.0s｜Final Hook tag**：Hook 关键词、主 motif、人物动作和终字同拍回归；最后一拍用 bass hit、短 vocal tail、磁带 stop 或干净 hard stop 完整收束，不淡出、不悬空循环。

镜头可以在一个小节内切两次，但不可破坏这六个音乐功能。用户音乐明显不是 128 BPM 时，按真实 BPM 重算段落；不要为了套模板伪造节拍。

## K-pop hip-hop / Rap 编曲骨架

- **Groove**：默认 128 BPM double-time / 64 BPM half-time；也可根据气质选择 94–108 BPM boom-bap pocket 或 136–148 BPM modern trap grid。不要所有项目固定同一 BPM。
- **Drums**：短而重的 kick 留出 vocal 空间；half-time 主 snare/clap 落在第三拍，可加极轻 ghost clap；hi-hat 以 1/8 或 1/16 为底，只在句尾、转场或 ad-lib 前做 1/32 roll，不要全程滚奏。
- **808 / bass**：使用 3–4 个根音形成可听见的低频走向，至少一次短滑音或八度回答；kick 与 808 交错，不要持续同一个低音把歌词盖住。
- **Main motif**：4–6 音、可哼唱、有起伏的问答动机；优先小调五声音阶或自然小调，Hook 前可用一个半音趋近音制造 K-pop 式张力。第一句先跳进，第二句下行回答并落回主音或五度，不写没有方向的随机音符。
- **Section contrast**：Rap 段保持低音和干鼓的负空间；pre-hook 抽掉一个低频层并抬高旋律；Hook 增加和声、宽度和打击层；beat switch 只替换一个节奏支点；最终 Hook 回收主 motif。
- **Sound palette**：从短 brass stab、金属 pluck、失真电钢琴、切片人声、磁带倒放、复印机式 percussion 中选 2–3 种，不把所有音色同时堆满。声音要锐利、时尚、可表演，不做廉价 EDM preset 或无旋律噪声墙。

## Rap flow 与歌词

原创 rap / K-pop hip-hop 默认写 **5–7 行实际可表演歌词**，不是只写两三个屏幕口号。建议格式：

```text
Rap A1: "[8–12 个可听音节，建立人物/冲突]"
Rap A2: "[8–12 个可听音节，语义推进并与 A1 内押或尾押]"
Pre-hook: "[4–7 个音节，上行或留悬念]"
Hook 1: "[3–6 个音节，最强记忆词]"
Hook 2: "[3–6 个音节，回答 Hook 1]"
Response / ad-lib: "[2–5 个音节，可选]"
Final tag: "[3–6 个音节，回收主 Hook]"
```

Rap A1 与 A2 必须是同一段话的连续意思，并写出至少一组内押和一组尾押；优先强辅音、清楚元音和自然英语语序，不为了押韵生成无意义短句。A1 的重音可以靠近正拍，A2 至少有一次提前落在 snare 前或跨过小节线，形成 push-pull。两条 rap 至少切换一次 cadence：straight sixteenth → triplet、短短长 → 长短短，或密集音节 → 半拍停顿。句尾保留极短呼吸，不把所有音节塞成机器枪。

歌词量与屏幕文字是两回事：演唱/说唱可以有 5–7 行，画面仍只从歌词和情节中提取 3–6 个最有视觉价值的英文词组。不要把全部歌词逐字做成字幕。

## Hook 与旋律好听的硬规则

- Hook 使用“主句 + 回应句”，两个短句的节奏轮廓不同但共享一个核心音程或关键词。
- 主旋律必须有明确最高音、方向和落点；不能只在同一个音高反复念，也不能每拍随机换音。
- Rap 以节奏为主，pre-hook 让音高范围扩大，Hook 再进入 chant-singing 或 melodic rap；这三段必须听得出角色变化。
- 最终 Hook 增加一层低八度 double、三度/五度和声或左右声道短 ad-lib，但主唱仍在中心，不能被和声盖住。
- 混音保持 vocal 靠前、辅音清楚、短而干的空间；rap 用单声道主轨和少量 rhyme-word doubles，Hook 才展开宽度。低频不要遮住嘴型对应的辅音。

## 其他音乐路线

- **Dark-pop / Cyber-grunge**：116–124 BPM；小调或多利亚调性感，失真但可唱的 motif，干 kick、宽但不过度的 bass；仍安排 rap-like rhythmic verse 或连续 lyric phrase，Hook 加低八度与和声，中段半拍抽空。
- **Boom-bap / Underground Rap**：94–108 BPM；swing 设为轻微而非松垮，kick/snare 留出头部点拍，采样切片与 bass line 形成问答；两条 verse flow 不能完全同节奏。
- **Post-punk / Breakbeat**：124–132 BPM；干燥鼓、单音贝斯、短吉他或金属 motif，反拍切分和一次鼓组 fill；人声可以冷静宣告，但仍需连续语句和记忆性 refrain。
- **Instrumental BGM**：明确写 `instrumental only, no vocals, no lyrics`；仍需 4–6 音主 motif、低频根音、鼓组层次、一次中段变化、Hook 等价的器乐回归和最终落点，不得从头到尾一层循环。

## 性别、声线与表演

声线必须跟随人物参考：明显男性主角用 `male / masculine timbre`，明显女性主角用 `female / feminine timbre`，多人按实际角色分配，无法判断时才用 `neutral timbre`。不得把男性角色默认写成女声，也不得在 15 秒中途无理由换声线。

写清 vocal delivery：低沉/明亮、贴耳/外放、松弛/攻击性、咬字位置、气息和 ad-lib 方式。Rap 不是“站着读单词”：嘴型、下颌、肩膀、手势、跨步、转身和急停要跟 syllable stress、rhyme word、snare、808 与 breath gap 同步。

## 音乐到画面的映射

- intro tag / motif → 第一镜建立人物与主字族；Rap A 重音 → 人物主动运动和短促硬切；cadence switch → 改变镜头距离、方向或分屏结构。
- pre-hook lift → 人物突然静止、镜头悬停或文字恢复清晰；Hook 1/2 → Hero type 的主句/回应句依次压屏；beat switch → 场景、景别和版式同时变换。
- kick/808 → 跨步、落地、肩背转向、广角推近或字形纵拉；snare/clap → 文字放大、套印归位、肩膀下压或闪白硬切。
- hi-hat roll → 字边微震、跳帧和字符细碎重组；rhyme word double → 同词 Print plate 叠层；final tag → 终字压屏并 hard cut。

## 失败模式

出现以下任一情况必须重写后再生成指令：只有 2–4 个孤立口号；rap 没有连续语义、内押/尾押或 cadence 变化；Hook 没有问答、最高音和落点；主旋律只重复同一音高；鼓组从头到尾不变；808 只有一个持续根音；K-pop 只写成“大制作、很抓耳”却没有段落对比；人声性别与角色不符；歌词过密到没有呼吸；结尾淡出、悬空或被硬截断。

## 资料依据

- [Sound On Sound — How To Make It In K-Pop](https://www.soundonsound.com/techniques/how-make-it-k-pop)：行业制作人强调更多段落、更多 Hook、段落重组、快速旋律节奏和非常规/半音旋律设计。
- [Berklee — BTS and Beyond: What K-Pop Does Differently](https://www.berklee.edu/global-initiatives/news/bts-and-beyond-what-k-pop-does-differently)：K-pop 是多类型融合，包含 K-hip-hop、K-R&B 与高密度 Hook、表演和影像协同。
- [Kyle Adams — On the Metrical Techniques of Flow in Rap Music](https://doi.org/10.30535/mto.15.5.1)：rap flow 的关键包括重读音节、押韵音节和句法在拍号中的位置，以及这些参数如何形成新的节奏层。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
