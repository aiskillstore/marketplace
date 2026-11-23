# 可复用时间线编辑计划

`scripts/timeline_ops.py` 读取已解码且与本次保存绑定的明文 JSON，输出新的隔离目录。它使用 Python 3.11 及以上版本的标准库。先完成完整备份和副本绑定，再生成计划。写回由 `draft_workspace.py` 负责。

```text
python timeline_ops.py inspect --input baseline.json
python timeline_ops.py apply --input baseline.json --plan plan.json --output new-edit-directory
python timeline_ops.py validate --input new-edit-directory/draft_content.json
```

`apply` 的输出目录必须尚不存在。成功后包含 `draft_content.json`、`report.json`，新增音效的原始文件另复制到 `assets/`。输入文件保持原状。失败可能留下未完成的输出目录，应查明错误后使用另一个新目录。脚本不打开剪映、不回写草稿，也不探测素材库。

候选计划由 `scripts/plan_candidates.py` 分两步生成：`propose` 输出带证据和风险标记的 `review.json` 以及零删减 `plan.json`；`approve-plan --accept <候选ID> --confirm-reviewed` 才输出实际删时计划。可选 `--transcript` 将哈希绑定的词级转写按源范围映射到时间线，并与能量区间取并集保护语音；候选和批准必须使用同一份转写。它仍不代替剧情理解、识别准确性复核或听感判断。批准时会再次调用本页的计划校验，完整命令见 [本地执行与恢复](jianying-workflow.md#分析综合编辑与预览)。

所有 `*_us` 字段为整数微秒，范围采用左闭右开。计划中的剪点、桥接、翻转、音效目标和 duck 时间均对应输入时间线。输出报告中的时间对应精剪后时间线。脚本依据实际 source/target 范围操作，不按目标帧率统一取整。`boundary_tolerance_us` 默认 4，最高 100，仅把相近剪点吸附到已有主视频片段边界。源素材内的镜头切换应根据实际帧时间填写。

`inspect` 返回轨道 ID、片段 ID、source/target、素材路径、字幕及关键帧属性。用这些 ID 精确指定计划，字幕轨的行数和语言顺序均可不同。

```json
{
  "schema_version": 1,
  "timeline_id": "TIMELINE-ID",
  "input_sha256": "CURRENT-INPUT-FILE-SHA256",
  "primary_video_track_id": "VIDEO-TRACK-ID",
  "boundary_tolerance_us": 4,
  "cuts": [{"start_us": 4200000, "end_us": 4800000}],
  "speech": {
    "coverage_us": [0, 12000000],
    "intervals": [
      {"id": "line-a", "start_us": 1000000, "end_us": 3800000},
      {"id": "line-b", "start_us": 5100000, "end_us": 7800000}
    ],
    "remove_ids": []
  },
  "remove_caption_ids": [],
  "shorten_caption_ids": [],
  "drop_transition_ids": [],
  "audio_roles": {"VOICE-SEGMENT-ID": "dialogue"},
  "audio_edge_fades_us": {"dialogue": 10000, "ambience": 40000},
  "music": {"segment_ids": ["MUSIC-SEGMENT-ID"]},
  "beat_events": [],
  "bridges": [],
  "flips": [],
  "sfx": [],
  "merge_contiguous": true
}
```

`beat_events` 是可选的关键点记录数组，不改变现有 `schema_version`，也不会自行创建剪点或音效。每项必须包含唯一非空字符串 `id`、下述 `kind` 和输入时间线整数微秒 `target_us`；目标不能超出输入时长或落在删除区间内。

新增 SFX 计划：beat 加 `sound_action`（`sfx/original/bgm_change/silence`），新增 `sfx` 行加 `event_id`（实际 beat ID）、可选 `event_class`、由 `sfx-library prepare` 生成的 `selection_evidence` 文件。`apply` 核对选段 SHA、起止、attack、目标与 beat 偏差≤80ms并自动关联生成的 segment ID；禁止编造不存在的 `sfx_segment_id`。旧 schema=1 计划仍可 apply，原 covered/verified 计数仅保留兼容语义；新增 `realized_sfx_event_count` 表示真正关联的主音效数量，实际听感由专项 review 记录。

3.3 的多击选段仍使用同一 `sfx` 行结构。双击/多击的源绝对时码、击体、选段终点和淡出声明保存在 `selection.json`，专项审核同时核对；撤层时改用具体 `original/bgm_change/silence` 动作并移除对应 `sfx` 行。详见 [逐项反馈与有限修正](feedback-refinement.md)。

`kind` 的统一词表为 `hook`、`info`、`conflict`、`anxiety`、`decision`、`reveal`、`impact`、`emotional_reaction`、`prop`、`door`、`phone`、`tail`。每个事件只记录一个主声音变化，`cue` 说明该变化，`screen_change`、`dialogue_anchor`、`character_state` 和 `reason` 分别记录画面、对白、人物状态和取舍依据。

可选字段还包括 `sfx_segment_id`、非负整数 `attack_offset_us`、布尔值 `duck` 和 `verified`。`sfx_segment_id` 只记录关联 ID，不会自动创建或修改音效。输出报告的 `beat_events` 保留原字段，另以 `input_target_us` 保存输入时码、以 `target_us` 保存删后时码；未填写 `verified` 时按 `false` 输出。`verified` 为 `false` 时必须在交付报告中说明只完成了波形/画面定位或其他有限核验。

时间、ID 和哈希均需替换成当前输入的实值。`speech.coverage_us` 必须覆盖完整输入时长。`intervals` 应来自本次素材的分离人声或视频内嵌音频分析，并通过字幕、原声和必要的试听补充；混合音乐/音效的能量候选不能直接当作完整对白覆盖。它允许重叠说话。经实际分析确认无对白的时间线可用空数组。脚本只核对这些声明中的边界，无法单靠字幕或能量证明没有截字。

剪点需有序、互不重叠。删整句时，把每条语言轨被完整移除的字幕片段 ID 放入 `remove_caption_ids`，并将对应实声 ID 放入 `speech.remove_ids`。这些区间必须完全落在删除范围内。

同一字幕内有独立可删的无词停顿时，把实声按确认的语段分别写入 `speech.intervals`，完整保护前后词句。确认字幕文字全都保留、缩后仍读得完，再把每条受影响的静态字幕片段 ID 列入 `shorten_caption_ids`。输出只缩显示区间，文字、样式、原 ID 和轨道保留，剪口两侧仍是一条字幕。逐字计时、动画和未验证的模板需单独处理。未明确列出的字幕仍受保护，实声删减规则照常检查。

`audio_roles` 的值可为 `dialogue`、`ambience`、`sfx`、`other`。只有显式配置 `audio_edge_fades_us` 的角色会在新音频剪边增加淡化。裁剪音频时，原有标准线性淡化会先按原位置折入音量关键帧，再处理新剪边，避免把旧淡入重新施加到片段中部。曲线相乘使用有限采样，仍需核验混音。

配乐必须按 `music.segment_ids` 显式分类。它在画面删口处保持一个连续源片段，从尾部缩短并映射原音量关键帧。跨删口的原音量值不同时，脚本会指出具体片段并拒绝，应重新选择剪点或显式重做该段自动化。片段原始增益保持，已有 duck 通过原曲线保留。`music.energy_reasons` 以原音乐段 ID 为键，记录该段的能量分区依据；新增 BGM 使用对应 `sfx` 行的 `purpose`。

```json
{
  "music": {
    "segment_ids": ["MUSIC-A", "MUSIC-B"],
    "energy_reasons": {"MUSIC-A": "开场冲突", "MUSIC-B": "揭晓升能"},
    "crossfades": [
      {"left_id": "MUSIC-A", "right_id": "MUSIC-B", "mode": "equal_power", "steps": 16}
    ],
    "ducks": [
      {"start_us": 7000000, "end_us": 8000000, "factor": 0.6,
       "attack_us": 140000, "release_us": 260000, "segment_ids": ["MUSIC-B"]}
    ]
  }
}
```

交叠必须已存在，且只有先后两首配乐参与。脚本在这段交叠内生成 sin/cos 等功率音量关键帧，并撤掉对应的旧淡出/淡入，保留外侧首尾淡化。`steps` 为 4–128，默认 16。新 duck 使用 `min(原曲线, nominal × factor)` 上限，nominal 取原曲线最大值，已有低音量不会再乘一次。省略 duck 的 `segment_ids` 会作用于本计划全部配乐。`music.ducks` 只作用于 baseline 中已有且列入 `music.segment_ids` 的音乐段。通过 `sfx` 新增的 BGM 需要用分段或局部 `fader_db` 实现对白让位。零 attack/release 按 1 微秒阶跃表达，通常应提供经过试听选择的缓变时长。

报告将删后实际保留的每个原音乐段和新增 `mix_role=bgm` 段视为一个 BGM 能量区，自动输出 `bgm_zone_count` 和 `bgm_zones`，包含源范围、推子语义、路径、可解析文件哈希和能量理由。`music_ducks` 记录输入/输出区间、factor、attack/release 和 `planned_depth_db`；后者是计划增益上限，不是渲染实测 duck 深度。

画面桥接和翻转使用以下条目。

```json
{
  "bridges": [
    {"start_us": 4100000, "end_us": 4900000,
     "donor_segment_id": "INPUT-VIDEO-SEGMENT-ID", "source_start_us": 8200000}
  ],
  "flips": [
    {"start_us": 9000000, "end_us": 11000000, "horizontal": true}
  ]
}
```

两类条目均可提供 `track_id`，默认主视频轨。桥接的源长度等于其删后保留时长，保持正常速度。它只改画面，供体需已静音、已分离声音或本身没有声音。翻转设置明确的最终 horizontal 状态，并在状态改变时反转静态水平位移。旋转或动画片段须通过原生流程处理。翻转前应核对人物、方向、道具及文字。

当前支持静态重构图：`bridges[].reframe` 调整供体，或顶层 `reframes` 对输入区间内当前画面重构图。两者不改变声音、字幕和时长。

```json
{"bridges":[{"start_us":4100000,"end_us":4600000,"donor_segment_id":"供体ID","source_start_us":8200000,"reframe":{"scale_multiplier":1.22,"offset_x":0.0,"offset_y":-0.03}}],
 "reframes":[{"start_us":4800000,"end_us":6000000,"reframe":{"scale_multiplier":1.22,"offset_x":0.0,"offset_y":-0.03},"rationale":"右侧保持更紧景别至真实换镜"}]}
```

倍率乘已有 x/y scale，增量加已有 transform；允许倍率1.05–1.50、位移[-0.25,0.25]，拒绝未知字段、旋转、动画关键帧。接口存在不等于自动裁切安全：按 [闪跳修复](seam-repair.md) 检查头手/道具、实际源尺寸和最终1080清晰度。普通 `bridges/flips` 旧格式继续可用；以前被静默忽略的 scale/transform 等未支持字段现在明确拒绝。

`merge_contiguous` 默认开启。仅当目标首尾相连、源位置连续、素材及播放参数相同、没有关键帧或淡化等时间效果时合并。合并可避免每个小片段独立 seek 导致回跳。相同路径下使用不同效果或不同源范围的片段保留独立。

新增音效使用实际文件和选段峰值。`mix_role` 可为 `bgm`、`sfx` 或 `other`。提供 `fader_db` 时，脚本按 `target_peak_dbfs = source_peak_dbfs + fader_db` 计算并校验。新 BGM 的 `fader_db` 必须在 -9 至 -5 dB，新动作拟音必须在 -5 至 -2 dB。

```json
{
  "sfx_template_segment_id": "EXISTING-PLAIN-AUDIO-SEGMENT-ID",
  "sfx": [
    {"path": "D:/chosen-effects/punch.wav", "sha256": "ACTUAL-ASSET-SHA256",
     "mix_role": "sfx", "fader_db": -3.0,
     "source_start_us": 40000, "source_duration_us": 250000,
     "attack_offset_us": 105000, "target_us": 6400000,
     "source_peak_dbfs": -1.0, "target_peak_dbfs": -4.0,
     "fade_in_us": 0, "fade_out_us": 40000,
     "track_name": "动作音效", "purpose": "拳套命中肩部"}
  ]
}
```

首版接受整数 PCM WAV，包括 8/16/24/32 位。其他格式先在独立目录转换为 WAV，再测量和绑定其哈希。`attack_offset_us` 从所选源范围的开头计算，`target_us` 对齐实际画面接触点。源范围必须可读，音效不能越过输出时长。脚本测量所选范围所有声道的实际峰值，再算独立片段增益。`source_peak_dbfs` 可省略，提供时须与实测相差不超过 0.15dB。目标峰值需处于 -120 至 0dBFS。源文件与输出资产均校验哈希，片段和轨道保持可编辑。应核验多声音叠加后的成片峰值和听感。

支持范围为普通正向 1 倍速视频/音频、完整移动的多语言字幕、标准线性音量关键帧和静态翻转。裁剪受影响片段时会检查动画、复合素材、反放、速度曲线和未知时间效果，并给出具体 ID 拒绝处理。受影响转场必须先显式列入 `drop_transition_ids`，不能暗中删除。`validate` 核验结构、引用和时序，无法替代实际预览、逐帧接点和听感检查。

成功报告包括 `input_sha256`、`plan_sha256`、`output_sha256`、输出 JSON 的绝对路径 `output`，以及 `seams_us`。`seams_us` 包含所有新剪口和桥接/翻转范围的删后首尾，可直接交给媒体 QC 工具抽帧。另记录合并详情、`beat_events`、`planned_event_count`、`covered_event_count`、`verified_event_count`、`sfx_count` 和 `bgm_segment_count`。`covered_event_count` 只统计具有 `cue`、关联音效或 duck 声明的事件，不证明实际听感；`verified_event_count` 统计显式验收的事件。

每个 `sfx` 结果记录输入/输出 attack 时码、输出起止、源入点、源时长、attack 偏移、淡化、用途、轨道名、SHA-256、源/目标峰值、`fader_db` 和 `mix_role`。这些字段直接交给 `qc --edit-report` 做混合输出开窗测量。完成原生保存后，应对实际草稿另行回读核验。
