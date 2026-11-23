# 本地执行与恢复

## 开场合并预检

统一入口为 `<技能目录>/scripts/fine_cut.py`，需要 Python 3.11+。若 `python` 不在 PATH 而 Windows Python 启动器可用，使用 `py -3`。路径和名字取实际值。`--config`、`--metrics` 放在子命令之前。

```powershell
python "<技能目录>/scripts/fine_cut.py" --metrics "<任务目录>/timing.jsonl" start --draft "<精确草稿名>" --episodes "9-16" --workspace "<新的隔离目录>"
```

`start` 定位精确登记名，返回实际集名、路径、身份、本地能力和下一步。可给集号范围或多个实际标签，例如 `--episodes "9-11" "第13集"`。集号必须唯一对应实际标签。缺集或歧义按 `list --draft "<精确草稿名>"` 给出的标签处理。

`start` 在隔离工作目录读出稳定保存版，首次或后端变化时以目标项目的一集验证编解码回环。后续仍读取本轮保存文件，已验证的同一 codec 和运行库可跳过重复回环。当前运行库不兼容时，入口会尝试有限的本机候选。实际预览仍需验证渲染组合。

用 `episodes` 确定后续真实集名，用 `copy_open` 判断当前草稿的写入条件。有 `inspection.json` 时，直接用 `episodes[].json` 做只读分析。结果为 `partial` 时，先做已读出的集数，再查 `episode_errors`。遇到 `needs_local_action` 时，按 `next` 和已有候选处理，继续可做的阶段。

## 一键编排与断点续跑

标准整流程可用 `run` 串起 `start → clone/snapshot → analyze/propose → apply → preview/qc → commit/verify → readback → 最终 preview/qc`。首次只需精确原稿、唯一副本名、集数和新的任务目录：

```powershell
python "<技能目录>/scripts/fine_cut.py" run --draft "<精确原稿名>" --copy "<唯一精剪副本名>" --episodes "9-16" --workspace "<新的任务目录>"
```

`run` 启动时会通过 `powershell.exe -NoProfile -STA -File scripts/select_music_folder.ps1` 打开系统文件夹选择框，让用户亲自选择本次本地 BGM 文件夹；随后通过 `select_review_mode.ps1` 选择 `assisted`（用户中途配合回看与专项审阅）或 `autonomous`（Codex 自动审阅，不生成人工审阅 HTML）。同一任务沿用已选配乐目录。3.5.1 续跑时显式重复本次的 `--review-mode`，避免状态保存后的类型差异导致重新选择。自动模式生成哈希绑定的 `seam_review.json`、区间帧页、关键帧联系表、原生音频证据和 `automated-review.template.json`，但不生成 `review.html`、人工 decisions 或 listening 模板；脚本只生成证据，不自动作语义判断。Codex 必须检查图像和音频证据，填写逐项结论、理由、置信度、分析方法和限制，再以 `--review` 交给 `automated-review validate` 门禁。不能把机器测量写成已试听/正常速度观看；没有音频感知能力时如实使用 `spectral_and_metadata` 并说明局限，有未解决的明确风险不能提交。目录失效、取消或选择器不可用时分别返回 `music_selection_required` 或 `review_mode_required`；也可用 `--music-dir` 和 `--review-mode` 预先指定。每个新任务使用新工作区并重新选择，不复用历史目录。

没有 `--plan` 时，完成分析和候选生成后返回 `awaiting_plan`，不会自动删减。按 [候选审阅](#分析综合编辑与预览) 生成每集批准计划，再用**同一任务目录**续跑。单集可直接给路径，多集逐集给 `实际集名=计划路径`：

```powershell
python "<技能目录>/scripts/fine_cut.py" run --draft "<精确原稿名>" --copy "<唯一精剪副本名>" --episodes "9-16" --workspace "<同一任务目录>" --plan "第9集=<第9集批准计划.json>" --plan "第10集=<第10集批准计划.json>"
```

全部计划齐全后，`assisted` 模式完成提交前预览/QC并返回 `awaiting_commit`，为每集输出 `seam-review/review.html`、`decisions.template.json`、`quality-review.template.json`；`autonomous` 模式不生成这些人工审阅页面/模板，而是输出分组关键帧 PNG、区间 `range_review.json`、full/without/solo 音频渲染及 `automated-review.template.json`。Codex 需检查这些证据，把完整记录另存为 `automated-review.json`；`run` 用当前输入、编辑报告、QC、接点、区间、候选素材和音频文件哈希验证它。新增视频接点和补镜/重构图仍逐项观察；新增 SFX 仍要求两份真实候选 selection evidence，并检查 attack、锚点、混音测量和与剧情节拍的匹配。自动审阅不得声称人工试听或正常速度观看；不具备音频感知时需标明依据是素材/节拍元数据与频谱/RMS等测量。自动审阅未完成或技术 QC 未过时不能提交。协作模式仍由执行者填写 `quality review`，其中 `seam_decisions`、`picture_ranges`、`audition_manifests` 和候选比较按原规则绑定；不得批量把待审布尔值设 true。

续跑保留全部 `--plan` 并重复本次的 `--review-mode`，逐集加 `--review "实际集名=quality-review.json" --commit`；仅 `--commit` 且专项记录不完整返回 `awaiting_quality_review`，不会回写。有新增 SFX 但扫描为 `required_review_count=0` 时，保留 `seam_decisions=null`，无需伪造接点记录；没有新增 SFX、SFX 声明、视频接点或补镜/重构图区间的轮次不要求伪造专项记录。已有认可副本时用 `--reuse-copy` 跳过 clone；源草稿仍须可定位。提交前核对每集的 `precommit.technical_status` 和 `issues`。协作模式在没有新增音效、接点或画面检查区间时会跳过专项分支，需先处理提交前 QC 中的未解问题。默认 `commit --register-media`，确认本轮没有新媒体需要登记时才用 `--no-register-media`。`--software` 可同时用于提交前后预览的软件编码，`--size` 控制预览尺寸。

`run.json` 保存每阶段输入签名、脚本和配置版本、结果及产物 SHA-256；续跑只复用完全匹配且未变化的阶段。换基线、改已执行计划、改脚本后需要新任务目录。已提交工作区不能去掉 `--commit` 或移除已执行计划来伪装成未提交状态。失败会保留 `current_stage` 和现场；先按具体阶段诊断，不删除事务证据或强制覆盖。新一轮剪辑使用新任务目录。

`run` 会强制完成本次 BGM 文件夹选择，并按已选审阅模式处理证据。它不代替剪辑执行按场景选曲、剧情判断和候选计划批准。`completed` 表示当前模式要求的审阅记录已通过且最终技术 QC passed；autonomous 模式明确不代表人工试听或正常速度真人审片。最终技术 QC 有未解项返回 `completed_needs_review`。旧工作区包含脚本指纹，升级后需新工作区，不修改旧事务记录或强行重绑签名。可选 `--transcript` 目前限单集任务。

## 本地诊断与恢复

本地配置默认保存到 `$CODEX_HOME/state/tiktok-drama-fine-cut/backend.json`，未设置时用用户目录下 `.codex/state/...`。可用 `--config <机器配置>` 指定。换机重新发现本地后端，不共享机器配置或配乐目录。`doctor` 只检查安装线索、索引和固定深度的产品目录。按缺失能力缩小诊断范围，正常开场无需重复执行这些命令。

```powershell
python "<技能目录>/scripts/fine_cut.py" doctor --search-root "<安装父目录>"
python "<技能目录>/scripts/fine_cut.py" list --draft "<精确草稿名>"
python "<技能目录>/scripts/fine_cut.py" probe --draft "<精确草稿名>" --episodes "<实际集名>" --workspace "<新的探测目录>"
```

- 索引或依赖缺失时，按发现结果补 `--index`、`--codec`、`--runtime`、`--support-dir`、`--app-dir`、`--cache-dir`、`--ffmpeg` 或 `--ffprobe`，再验证受影响能力。索引可用时可继续核对草稿和集号，渲染暂缺时可继续备份和分析。
- 新机器可用 `start --search-root "<交付助手安装目录或父目录>"` 补充发现范围。独立交付助手包可包含 `engine/bin/jy-draftc.exe`、`source/jyexport` 和 `引擎数据/<版本>`。codec 要用已通过回环的运行库。`--app-dir` 指向实际剪映安装目录，供素材解析使用。
- 同名或集号歧义时澄清实际项目或标签。保存期间文件发生变化时，从稳定保存版重取该集。副本锁的处理见下节。
- `clone` 自定义目标需要已有父目录。`commit` 遇到快照变化或已存在事务时，从本轮事务状态选择重新取样、`verify` 或 `recover`。素材或效果报错时先定位具体路径、源范围或字段，按受影响的操作处理。

## 用户选择音乐与音效来源

选曲、推子、duck、音效事件底线和资源可移植性按 [BGM 与音效控制协议](audio-control.md) 执行。

每个新精剪任务让用户手选本地配乐目录。本次已明确选定有效目录时直接用，本任务续修沿用本次选择。

```powershell
powershell.exe -NoProfile -STA -File "<技能目录>/scripts/select_music_folder.ps1"
```

脚本打开用户自己操作的系统文件夹选择窗口。异步等待并读取 UTF-8 JSON 的 `status`，确认返回 `selected` 且目录可访问后选曲。取消或不可交互时接受用户手动提供本次绝对目录，期间继续定位、备份与分析。

音效优先用本任务指定的库，再查包内 `assets/sfx`、`assets/sfx-foley`、剪映库或已核准本地素材。实测索引和真实 attack 选段按 [音效库](sfx-library.md)，外部补库见 [来源目录](external-sfx-sources.md)。`.lnk` 仅解析目标目录。按真实路径和哈希缓存本批索引，核拟用段，避免每轮重扫数千文件。缺少合适素材时先用音乐进退、原声、对白或留白完成能做的情绪点，并在事件矩阵中写明原因。只复制实际使用资产到副本或隔离目录，分享包保留通用流程。

已有人工反馈、需要撤层对照或继承局部通过项时，按 [逐项反馈与有限修正](feedback-refinement.md) 绑定原始意见、实际展示媒体和局部播放图。未知备注或变更项保留待审，不搬运旧 pass；工具不自动填写任何主观试听或正常速度观看声明。

## 副本和本轮基线

新项目用 `clone` 完整备份、复制项目内资源，建立独立草稿/项目身份并登记。已有认可副本时继续当前副本。

```powershell
python "<技能目录>/scripts/fine_cut.py" clone --source "<原稿名>" --copy "<唯一精剪副本名>" --workspace "<新建副本事务目录>"
python "<技能目录>/scripts/fine_cut.py" snapshot --source "<原稿名>" --copy "<副本名>" --episodes "<实际集名1>" "<实际集名2>" --workspace "<本轮新快照目录>"
```

用户明确指定继续编辑的已有副本，而原稿已不在索引时，`snapshot` 可省略 `--source`。仍须用副本精确登记名和实际集名，核对路径、身份、锁和本轮哈希。快照记录仅绑定该副本，不能据此证明它与已缺失原稿之间的对应关系。新建副本仍用带 `--source` 的 `clone`。

`snapshot.json` 和输出给出准确文件名。以 `baseline/<时间线ID>.json` 为本轮基线，不用旧聊天里的 `edited` 或剪点覆盖它。主时间线、根级活动镜像、历史 `.bak`、项目清单和元数据按角色处理，详见 [时间线编辑与回写](timeline-editing.md)。

`.locked` 暂缓离线写入，稳定保存文件仍可读取。先继续剧情与素材分析。

```powershell
python "<技能目录>/scripts/fine_cut.py" inspect --draft "<副本名>" --episodes "<实际集名>" --workspace "<新的只读分析目录>"
```

`start` 已有本轮可用的只读结果时，直接用它分析。单独刷新时用 `inspect`，结果标记 `analysis_only`、`copy_open`。准备写入时，若副本仍占用，请用户保存并回到剪映主页，再按最新文件取写入快照。若保存内容有变化，比较受影响集并保留用户调整。

## 分析、综合编辑与预览

先读 [剪辑标准](editorial-standard.md)、[快节奏二次精剪](fast-cut-pass.md) 和 [BGM 与音效控制协议](audio-control.md)。逐集列事件、信息增量、钩子、情绪和要保动作，用本轮人声、字幕、画面互证。每个高能场景先建立候选 BGM 评分表，再确定能量区和音效事件。若存在用户手改集数，先做改前/改后回归，测量时长、视频片段数量、源画面重选、字幕删除对和 BGM/SFX 重排，再把重复出现的判断推广到其余集数。

```powershell
python "<技能目录>/scripts/fine_cut.py" analyze --input "<隔离集JSON>" --copy-root "<副本目录>" --workspace "<新分析目录>"
python "<技能目录>/scripts/fine_cut.py" inspect-json --input "<隔离集JSON>"
python "<技能目录>/scripts/fine_cut.py" propose --input "<隔离集JSON>" --analysis "<新分析目录/analysis.json>" --transcript "<可选转写目录/transcript.json>" --output "<新候选目录>"
```

`propose` 把能量低谷和字幕间隔整理成 `review.json`，并生成一个 `cuts=[]` 的零删减安全 `plan.json`。候选不是自动剪辑结论，不能直接代表剧情取舍。逐条看画面、听原声、核字幕和因果后，只批准明确接受的候选 ID：

```powershell
python "<技能目录>/scripts/fine_cut.py" approve-plan --input "<隔离集JSON>" --analysis "<新分析目录/analysis.json>" --transcript "<候选阶段使用的同一份transcript.json>" --review "<新候选目录/review.json>" --accept "cut-0001" --confirm-reviewed --output "<新的批准计划.json>"
```

`approve-plan` 再次核对输入、分析、review 和可选转写哈希，检查候选不重叠、声明语音不被截断、字幕保护及静态字幕缩短条件。候选阶段用了转写时，批准阶段必须提供同一份文件；未使用转写的候选不能在批准时临时换入。未经 `--confirm-reviewed` 不会生成执行计划；整字幕被覆盖时拒绝自动删除，需按原计划格式显式重作。音乐段只按 `music/extract_music` 材料类型预分类，仍须剪辑者复核。批准计划通过校验后，仍要走预览和完整验收。

需要词级时间戳时，可用可选 `transcribe` 适配层，不会静默安装 ASR 依赖：

```powershell
python "<技能目录>/scripts/fine_cut.py" transcribe --input "<源媒体文件>" --transcript "<已有Whisper风格词级JSON>" --workspace "<新转写目录>"
python "<技能目录>/scripts/fine_cut.py" transcribe --input "<源媒体文件>" --command "<本机ASR程序及参数，包含 {input} 和 {output} 占位符>" --workspace "<新转写目录>"
```

外部命令必须实际生成含 `segments[].words[]` 或顶层 `words[]` 的 JSON，每个词含 `start`、`end` 和 `word`/`text`（秒）。只有整段文字而没有词级时间戳会被拒绝。输出的 `transcript.json` 统一为整数微秒并绑定源媒体、原始结果 SHA-256。

把该文件传给 `propose/approve-plan --transcript` 后，工具按素材路径和实际文件哈希定位源媒体，再按 source range 和恒定速率把每个词映射到时间线中的每次出现。词级区间与能量区间取并集参与语音保护。跨源段边界的词、反放/曲线变速等不支持段不会被截断或猜测映射，而是在 review 的 `partial_word_ids`、`unsupported_word_ids`、`unused_word_ids` 和 `unsupported_segment_ids` 中留证。ASR 识别准确性和这些未映射词仍需原声复核。

`analyze` 解析资源并解码已有分离人声；没有独立人声音轨时，也会直接解码普通视频段的内嵌音频。已分离、静音或纯照片画面不会重复测量。`voice_measurements` 逐段记录 `separated_human` 或 `embedded_video` 来源、测量状态和失败原因，`voice_source_counts` 汇总已测来源；无音流或解码失败的段落进入 `unmeasured_audio_segments`，不阻断其他段分析。内嵌声音可能混合音乐和音效，能量仍不是 ASR 或语音证明，必须结合原声和画面复核。

`prepared.json` 和 `timeline_audio/` 只用于分析与预览，不能直接作为 commit 输入。写回前从本轮 baseline 或原始保存版恢复草稿内分离音频的 placeholder 路径。查 `gap_candidates` 中的字幕间隔，也查 `energy_dip_candidates` 中前后有人声能量的低谷。后者包含同一字幕内的候选，方便定位短停顿和句内空等。用带轨道 ID 的字幕、源画面时段、能量和实际语境定剪点。复杂变速、低电平软音节和混合声场也需核实。源 24 fps 等帧率与 60 fps 时间线可能不同，接点查真实源帧。

先按 [首版检查](editorial-standard.md#首版节奏与情绪音效检查) 把实际剪口和关键声音落点放在同一场次的工作记录里。记录输入时码、为什么剪或留、音效服务的变化、源入点和实际起音。随后按 [计划格式](plan-schema.md) 一次隔离执行。计划按输入时间轴写，验收按删后输出时码核对，避免后续删时错移音效。复杂结构只阻止受影响操作，继续其他可完成步骤。

```powershell
python "<技能目录>/scripts/fine_cut.py" apply --input "<本轮基线JSON>" --plan "<本集计划JSON>" --output "<新的编辑输出目录>"
python "<技能目录>/scripts/fine_cut.py" preview --input "<编辑输出/draft_content.json>" --copy-root "<副本目录>" --workspace "<本版本新预览目录>"
python "<技能目录>/scripts/fine_cut.py" qc --input "<编辑输出/draft_content.json>" --preview "<预览目录>" --edit-report "<编辑输出/report.json>" --frames-dir "<新的接点图目录>" --report "<QC.json>"
```

预览默认取输入帧率。早期构思可显式降帧，单帧验收用实际目标帧率。`qc` 核对绑定、声画、时长、峰值和单帧黑画面，列全局短镜候选并抽新剪口帧，包括片尾。运动、粒子和有意暗场可触发检测，逐帧判断实际原因。

## 提效与断点

- 本地读取和分集分析可并行。渲染先小并发并观察 CPU、磁盘和失败率，同一副本只一个写者。
- 每集先整合计划再渲染。问题先查实际源点、帧率和解码边界，只重渲受影响集。已有分析在核对本轮快照与相关媒体、引用和时码后可沿用。编辑仍以本轮快照为输入。
- 硬件编码失败时先查该集的 `render.log`。日志指向编码器时，在新预览目录试 `preview --software`。缺素材或效果时先处理对应来源。先复用已有预览和接点证据。
- `preview --reuse` 只复用输入、设置、媒体和后端依赖及产物哈希完全相同且证据完整的预览。有变化就用新目录。库识别和波形按文件哈希与源范围复用。
- `--metrics <本任务timing.jsonl>` 记录阶段耗时。团队评估提效时，分别记技术执行、剪辑判断和等待用户的时间，以同集的成片质量和返工为准。

## 验收与交付

首版先核因果与跨集钩子、关键道具、双语字幕、残帧与镜像。按实际预览完成 [节奏与情绪音效回查](editorial-standard.md#首版节奏与情绪音效检查)，包括未动过的候选和主要转折点。核对 BGM 分区数、候选比较、`fader_db`、对白 duck、音效事件覆盖率和实际可感知性。声场分类按材料和段 ID 核实。混音回查人声优先、对白段和无对白段 BGM RMS、局部峰值和整体余量，已保护的峰值同时检查相邻语句和停顿。确认的问题直接修到本轮，只重验受影响的段或集。

新 BGM 和音效放到副本 `Resources/Imported` 或本轮资源子目录并校验。`register_media` 会在 `commit --register-media` 时把新媒体复制到副本 `Resources/Imported` 并改写引用。提交前扫描待提交 JSON，禁止残留 `work/`、`analyze/`、`timeline_audio/`、`effects_audio/`、`preset_audio/` 或临时预览目录的绝对路径；原有分离对白和背景声恢复为草稿内的 draft-relative placeholder 引用。最终 JSON 按快照返回文件名放入独立提交目录，按需登记新增媒体。

```powershell
python "<技能目录>/scripts/fine_cut.py" commit --workspace "<本轮快照目录>" --edited "<最终JSON目录>" --register-media
python "<技能目录>/scripts/fine_cut.py" verify --workspace "<本轮快照目录>"
python "<技能目录>/scripts/fine_cut.py" readback --workspace "<本轮快照目录>" --episode "<实际集名>" --report "<本集编辑输出/report.json>" --output "<新的最终回读目录>"
python "<技能目录>/scripts/fine_cut.py" preview --input "<最终回读目录>/<时间线ID>.json" --copy-root "<副本目录>" --workspace "<新的最终预览目录>"
python "<技能目录>/scripts/fine_cut.py" qc --input "<最终回读目录>/<时间线ID>.json" --preview "<最终预览目录>" --edit-report "<最终回读目录/report.json>" --frames-dir "<新的最终接点图目录>" --report "<最终QC.json>"
```

回写带原始哈希和锁保护、编码回环、事务日志和失败恢复。`readback` 再次执行精确提交验证，从实际副本解码最终 JSON，并输出 `readback.json`。提供原编辑报告时，只有原编辑输出哈希仍匹配且最终结构除活动媒体路径外完全一致，才会另写重绑后的 `report.json`；同时从副本实际素材补齐路径、解析路径和 SHA-256。任何其他差异都必须回到编辑与提交阶段排查，不能强行重绑。每集使用独立回读目录；不需要报告时可省略 `--report`。

提交后的最终 `preview/qc` 必须使用上述回读 JSON 和重绑报告，不拿提交前隔离预览冒充最终副本证据。遇到错误保留现场和具体失败记录。

有音频输入能力时试听拟用段和关键混音过渡。只有波形和电平时完成可验证部分，并明确未主观试听。需要原生播放证据时，另行记录本轮实际播放结果。

## 必要时才用界面

用户明确要求实际界面动作，例如“打开副本让我在剪映编辑器看”，按该要求处理。其他情况先按本地诊断继续，只有交付缺少某个必要能力、已排查适用的本地路径且界面确实能补上时，才在该步骤考虑界面。优先可用的专用接口或轻量界面工具，Windows-MCP 最后使用。记录具体步骤、缺口、已验证的本地处理和界面结果。完成该动作后继续批处理。相同截图故障无新增证据时停止重试，继续独立工作。

纯导出、四版或 SRT 按用户规格走对应交付流程。
