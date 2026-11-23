---
name: dramacut
description: 在 Windows 10 的剪映专业版草稿副本中精剪海外短剧。用于定位拖沓气口和冗余镜头，按剧情安排卡点配乐与音效，并交付可继续编辑的副本。Fine-cut local Jianying Pro short-drama drafts with dialogue-gap candidates, beat-aligned music and sound effects, and an editable copy.
license: MIT-0
compatibility: Windows 10, Python 3.11+, Jianying Pro, a compatible jy-draftc.exe and jyexport backend, FFmpeg and ffprobe.
metadata:
  author: "zhuxiaoweb"
  author_email: "zhuxiaoweb@163.com"
  display_name: "DramaCut"
  version: "3.5.1"
  workflow_version: "3.5.1"
---

# DramaCut · 海外 TikTok 短剧精剪

本技能以最快的可理解剪辑为默认目标。海外 TikTok 小短剧优先让观众持续获得冲突、因果、选择、反应、线索或悬念，几乎不保留只展示动作过程、装饰氛围或重复情绪的镜头。BGM 是小短剧的情绪主层，冲突、焦虑、追问、追击、身份疑点和反转必须使用有瞬态、有起拍、有能量变化的片段，不能用平淡铺底曲代替情绪设计。剧情关键点和人物内心波动要有明显的声音变化。具体硬门、推子音量、duck、音效事件和跨电脑资源审计见 [BGM 与音效控制协议](references/audio-control.md)。

用户手动重剪过的集数是本项目最高优先级的风格基线。先比较用户改前和改后的剪口，提炼其删掉的多余气口、重复动作链、等待、无信息反应和过渡镜头，再把同一判断应用到目标范围其余未动段落。不要把旧精剪当作不可动的成片。

先删多余动作链和解释性从句，再重选更短的源画面子段，按场景能量重排 BGM，并在实际剧情转折落主音效。

音效执行读 [音效候选与真实落点](references/sfx-library.md) 和 [原生独奏 / A-B](references/audio-audition.md)；快剪后每个新增接点读 [闪跳修复](references/seam-repair.md)。包内自带 24 个原创设计音及 30 个带来源许可的碰撞/脚步/设备候选。BGM 目录仍由用户手选，内置 SFX 不代替 BGM。禁止均匀按“开头/中点/片尾”自动放三声、固定截文件头 0.5 秒、用非空 cue 文字冒充实际覆盖。

处理人工反馈、单薄/消音感音色、多击选段或温馨段撤提示音时，读 [逐项反馈与有限修正](references/feedback-refinement.md)。明确的备注选择优先于状态按钮；已通过项只在原始反馈、实际展示媒体和局部播放图均未变时继承，不能把旧 pass 直接复制到新版本。补镜/重构图除两端接点外，`run` 自动枚举内部与出口的连续帧检查。`assisted` 模式由执行者实际审阅；`autonomous` 模式由 Codex 对生成的帧证据逐项判断并记录方法和限制。新增工具不改变开场 BGM 选择与原事务顺序。

交付剪映里能打开、能继续编辑的精剪副本。用户给草稿名与目标集数即可开始。已有认可的精剪副本时，接着本次读取到的最新保存版修改。项目内有已精剪集时，参考其节奏、字幕、声音和片尾做法。

## 默认本地执行

在任意工作目录，用随技能安装的 [fine_cut.py](scripts/fine_cut.py) 执行。标准整流程优先用 `run` 合并定位、副本、分析、候选、预览、验收和回写：

```powershell
python "<技能目录>/scripts/fine_cut.py" run --draft "<精确原稿名>" --copy "<唯一精剪副本名>" --episodes "9-16" --workspace "<新的任务目录>"
```

`run` 启动时默认弹出 Windows 文件夹选择框，由用户选择本次本地 BGM 文件夹；随后让用户选择是否中途配合“回看与专项审阅”。选择“需要配合”使用 `assisted` 模式，保留接点/区间审阅 HTML 和人工记录模板；选择“不需要配合”使用 `autonomous` 模式，不生成审阅 HTML，由 Codex 查看关键帧和范围帧，检查原生渲染的 full/without/solo 音频及波形/频段、技术 QC，再填写哈希绑定的自动审阅 JSON，然后继续后续提交和交付。自动模式必须由 Codex 实际检查证据；脚本只生成证据模板，不会自动判语义通过。不得把机器结果写成人工试听或正常速度观看。证据不足、判断需修改或技术门禁未过时仍须修复后重审。首次可用 `--review-mode assisted|autonomous` 预先指定，3.5.1 续跑时显式重复同一个选项。已明确 BGM 目录可用 `--music-dir "<绝对路径>"` 免除文件夹弹窗；配乐目录保存在 `run.json`，同一任务续跑沿用。取消选择时返回 `music_selection_required` 或 `review_mode_required`。

首次没有批准计划时停在 `awaiting_plan`；Codex 按授权范围检查候选并批准计划，再用同一目录加 `--plan` 续跑。`assisted` 模式在提交前 QC 后停在 `awaiting_commit`，等待人工专项记录；`autonomous` 模式返回 `awaiting_agent_review` 和 `automated-review.template.json`。Codex 需实际查看模板引用的关键帧/接点/区间图片、QC 以及 SFX 的 native full/without/solo 音频证据，记录结论、理由、置信度、使用方法和限制，另存为 `automated-review.json`，再加 `--review "实际集名=自动审阅.json" --commit` 续跑。若当前执行器不能感知音频，只可填写 `analysis_method=spectral_and_metadata`，明确这是基于声音特征和素材/节拍信息的推断，不得声称听过；存在明确风险或不确定项时先修复或保留待审。协作模式下执行者实际看画面、听独奏/A-B并填写后，加 `--review "实际集名=审阅.json" --commit` 续跑；未审完返回 `awaiting_quality_review`。候选计划审批仍然保留。完整参数、断点规则和失败恢复见 [本地执行与恢复](references/jianying-workflow.md#一键编排与断点续跑)。

只需只读预检或分步控制时，用 `start --draft "<精确草稿名>" --episodes "9-16" --workspace "<新的隔离目录>"`，再按工作流逐步执行。`doctor`、`list`、`probe`、`inspect` 用于具体诊断。
- “在剪映草稿或副本里精剪”“回看一遍”默认走本地预览和可编辑副本交付。开场用脚本读写文件和渲染，精剪任务无须加载原生导出技能或初始化桌面控制。
- 用户明确要求某个界面动作时，或必要能力经适用的本地排查仍无法完成、且界面确实能补上时，才走 [界面备用](references/jianying-workflow.md#必要时才用界面)。范围只到该动作，Windows-MCP 最后考虑。副本占用时照常做只读工作，按实际需要处理保存与锁。

## 每次由用户手动选配乐文件夹

- 每个新精剪任务都请用户亲自选择**本次的本地可选配乐文件夹**。优先打开 [Windows 文件夹选择器](scripts/select_music_folder.ps1)，由用户确认目录。用户在本次请求或本次回复中已明确选定可访问的本地目录时，使用该选择。同一任务的续跑或下一集沿用本次选择。
- 选择器无法显示时，接受用户手动提供本次的绝对目录。取消或不可访问时请用户重选。等待期间继续定位、备份、梳理剧情与审查素材等独立工作。
- 只从本次所选目录挑选新配乐。历史路径、最近使用的目录和案例曲目不构成本次选择。按场景挑曲和剪配乐由剪辑执行，用户只需选文件夹。

## 执行顺序

1. 读 [剪辑标准](references/editorial-standard.md)、[快节奏二次精剪](references/fast-cut-pass.md) 和 [BGM 与音效控制协议](references/audio-control.md)。先做速度闸门，再做对白气口、动作和声音检查。先列 beat matrix，再为高能场景比较候选 BGM、确定能量区和音效事件。按剧情因果、开头钩子、推进速度和情绪来定取舍。声音参与叙事。主动修明显闪跳、单帧残留和有证据的镜像穿帮。
2. 定位精确草稿和集数，备份并绑定独立副本。**每一轮重新读取当前保存版**。把用户手调的节奏、曲目、音量与字幕作为基线，在本轮明确要求和有实际依据的范围内改动。主时间线和根级镜像由随附事务工具处理。
3. 按 [首版节奏与情绪音效检查](references/editorial-standard.md#首版节奏与情绪音效检查) 和 [BGM 与音效控制协议](references/audio-control.md) 逐场核实接话、句内停顿和动作的有效段，建立 beat matrix。每个关键点明确画面变化、对白/留白、BGM变化、duck 或音效主 attack。可用 `propose` 整理能量和字幕候选，可选 `transcribe` 提供词级转写并在两阶段命令中以同一 `--transcript` 文件保护语音；零删减安全计划不是剪辑结果，计划批准仍由 Codex 按授权检查明确选中的候选。30 至 60 秒集默认至少 3 个独立可感知音效事件，BGM 默认拆成 2 至 3 个能量区并至少完成一次升能、换拍或撤拍。再按 [时间线编辑与回写](references/timeline-editing.md) 隔离执行。
4. 完成一次编辑后，必须对本轮未动的场次再做一遍二次狠剪。重新扫描重复动作链、无信息等待、已被对白说明的反应、备用角度和多余细节镜头。一次预览覆盖全部改动并检查 BGM、duck、beat、音效 attack 与接点。`assisted` 模式由执行者按正常速度审完整对话/动作并逐帧检查接点；`autonomous` 模式由 Codex 查看关键帧总览、接点帧和补镜/重构图入口/内部/出口帧，并检查 full/without/solo 音频渲染及可用的波形/频段证据，不把帧采样或声学测量描述为真人播放、试听。若模式内的审阅发现问题，回到选曲/事件矩阵或编辑，修复后只重做受影响的集或片段。温馨段撤掉不合适提示音或用户明确选无 SFX 时，记录具体原声/BGM/留白方案，必要时填既有 `sfx_density_exception`，不为凑数加回。同一副本串行写入，哈希一致的有效产物可复用。
   - 新 SFX：每个 `event_id` 绑定实际画面/关键字，至少两个候选分别用 `sfx-library prepare` 以相同事件和输入锚点生成选段，实际比较后只将选中项加入计划；`audio-audition` 原生渲染有/无此层/独奏，听后记录。双击/多击先确认全部主击，保留末击主体后再缩尾或淡出。30–60 秒冲突+反转先排查 4–8 个独立事件机会，剧情不支持时写原因；不为了凑数在普通切镜加声。
   - 新接点：`seam-review scan` 全部检查，同源同参数跳时优先查同人同景别姿势跳变。先找真实动作接点，再用同场 0.25–0.60 秒有效补镜；必要时用已支持的 `bridges.reframe` / `reframes` 静态收紧景别。除两端外，还要逐帧检查补镜/重构图的内部与出口，并在 `picture_ranges` 记录入口/内部/出口及正常速度审阅。禁止短到 1–3 帧的插镜、无依据翻转和装饰转场掩盖问题。
5. 按 [验收要求](references/jianying-workflow.md#验收与交付) 执行 `commit → verify → readback → 最终 preview → 最终 qc`。`readback` 从实际副本解出最终 JSON，只在非路径结构完全一致时重绑编辑报告，并补齐副本内素材哈希；最终预览和 QC 必须使用该回读版本。首版核对台词、气口、动作、BGM 分区、推子 `fader_db`、对白 duck、音效落点与渲染峰值。提交前扫描待提交 JSON 的媒体路径，禁止把 `work/`、`analyze/`、`timeline_audio/` 或临时预览目录写回草稿。客观测量、模型看帧、实际监听和原生播放分别记录。
6. 报告副本名、已完成集数、重点变化和实际验收范围。报告至少记录删掉的多余气口、动作链、细节镜头和过渡镜头类别，保留的关键反应依据，BGM 候选比较、能量分区、文件哈希、源入点、`fader_db` 和 duck 理由，`planned_event_count`、`covered_event_count`、`sfx_count`、每个音效的 attack 和实际落点，以及删前删后时长。用户要求成片或字幕文件时，再按其交付规格导出。按剧情、节奏、画面和声音验收，避免重复检测和整批重渲染。
