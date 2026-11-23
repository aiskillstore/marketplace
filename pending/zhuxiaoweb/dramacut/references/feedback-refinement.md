# 用逐项反馈做有限修正

适用：已有人工意见，要在认可版本上改音色、BGM 或闪跳；不是每次精剪都增加一轮用户审批。按本次画面和混音比较音色、主击和尾音。

## 从听感描述变成可执行选择

| 明确反馈 | 下一步操作 | 对照验收 |
| --- | --- | --- |
| “单薄、轻柔”，明确希望两下低鼓 | 搜低鼓/双击；测波形确认两次真实主击；找至少两个不同音色候选 | 同一画面、同一锚点，分别准备候选并比较原生 full/without/solo；不能只提高旧纯音增益 |
| “像消音哔声” | 先撤该窄带提示，比较无提示音版本与非持续纯音候选 | 关键字没有被提示音误读为消音；不能仅测峰值便通过 |
| “凸显疑点” | 比较有离散敲击/短停顿的候选与现有 BGM 留白 | 提示在疑点可理解之后，后一句清楚；不固定使用某种鼓 |
| “温馨/接受/自主选择”而提示音怪 | 先比较撤 SFX、原声+BGM；必要时从本任务用户选定目录比较短 BGM 区 | BGM 单独标 `mix_role=bgm`，比较入口、对白、尾音；不为 SFX 数量重新塞提示音 |

名字只作检索。`sfx-library measure --tone-profile` 可补充低/中/高频能量，帮助判断候选是否有低频主体；它不能证明应景或手机可听。相同 SHA、源范围和主击不能算两个候选；不同名字但音色近似时仍按同一家族比较，再找另一音色。可以用两个独立新选段的 conditioning 帮助隔离音色差异，并保留原始电平记录；匹配峰值不等于匹配听感响度。

`decision/warmth` 不表示必须加提示音。撤声时，将 beat 的主声音动作改为实际采用的 `original/bgm_change/silence`，记录具体原声、音乐段或留白区间；移除对应 `sfx` 行，不能把已撤音效计入覆盖。必要时在 quality review 的 `sfx_density_exception` 写具体剧情依据，不为了凑数加回。

## 多次主击与尾音分开控制

先实际听辨全部要保留的源主击，再指定哪次对齐剧情锚点。附加主击可早于或晚于对齐主击；工具取最早主击的前导，尾音从最后主击算起。显著起音候选是波形线索，不能自动当成已监听确认。

```powershell
python "<skill>/scripts/fine_cut.py" sfx-library prepare --input "<双击.wav>" --output "<新选段目录>" --confirmed-attack-us 120000 --salient-attack-us 440000 --target-us 12800000 --pre-ms 30 --tail-ms 350 --fade-out-ms 100 --attack-body-ms 80 --fader-db -3 --purpose "划清界限的关键字后，保留两次低鼓主击" --event-id boundary --event-class decision
```

此例选源 90–790 ms，第二击 440 ms 后保留 350 ms 尾音，最后 100 ms 由计划淡出。`selected.wav` 本身不再烘焙这次淡出，避免 apply 重复淡化。`--selection-end-us` 可明确限制源终点；短到截掉任一声明主击或其 `attack-body-ms`、淡出提前压到末击主体时拒绝。80/350/100 ms 是可调试剪起点，不能替代真实素材的击体/衰减判断。旧单主击调用的默认时长、淡出与计划字段保持原样。

主击完整不等于保留整段长尾：先保留末击，再缩尾/淡出，重听下一句。每个候选仍在独立新目录执行 `prepare`，使用相同 `event_id` 和输入时间线 `target_us`，最终只把选中项加入计划。`selection.json` 记录声明的主击、击体、选段终点与淡出，审核同时校验这些字段，不能只审第一击。

## 反馈状态与备注同时读

```powershell
python "<skill>/scripts/fine_cut.py" feedback-review normalize --feedback "<review-response.json>" --output "<新的normalized.json>"
```

保留原条目及原文件 SHA，另给出 action：

- `pending` 但写“不应景/太单薄/像消音” → `needs_changes`，不是未反馈。
- `pass` 但明确“用户手调基线更好” → `restore_baseline`，不是候选通过。
- 明确“本轮候选更好” → `retain_candidate`。
- `使用：具体曲名` → `apply_named_choice`；执行该选择并做技术复核，不重复询问已给出的选择。
- 其他备注保持 `interpret_notes`。工具只识别有限明确语句，不猜开放语言。执行者读原文后可给 `--action-map`：`{"actions":{"条目key":{"action":"compare_without_sfx","reason":"原文允许调整或直接去掉；先比较去层版本"}}}`。允许 action 见脚本 `ACTIONS`，选择曲目还可记 `choice`。

冲突备注、否定说明、未决 pending 和缺少依据的按钮状态都不会被自动解释成新通过。意见涉及精确取舍而无法从上下文解决时才问用户；先做不依赖该选择的独立工作。

## 只继承确实未变的那一项

制作下一轮复核页前，用 `bind` 对**用户当时看到的版本**建证据，再用 `check` 比较新版本。不能先改完，再把新内容绑定成旧的通过项。

原反馈须有 `episodes[].episode/edited_sha256`，或条目自带 `reviewed_input_sha256`。同一集的版本声明必须唯一；条目与集级同时给出哈希时必须相同。bind 严格核对该版本，不允许给后来修改的 JSON 套旧通过意见。调用者从原审核页清单填写真正展示的 `review_media`，工具记录其 SHA 并检测后续变化；工具不能反推用户实际播放了哪个文件。缺版本或媒体绑定时重审该项，不能补造通过证据。

spec JSON：

```json
{"items":[{"key":"picture-19-33050000","kind":"picture","input":"C:/isolated/accepted.json","copy_root":"D:/draft-copy","start_us":32000000,"end_us":38000000,"review_media":["C:/review/accepted-picture.mp4"]}]}
```

```powershell
python "<skill>/scripts/fine_cut.py" feedback-review bind --normalized "<normalized.json>" --spec "<accepted-spec.json>" --output "<新的binding.json>"
python "<skill>/scripts/fine_cut.py" feedback-review check --binding "<binding.json>" --spec "<current-spec.json>" --output "<新的reuse.json>"
```

current-spec 沿用同一 key/kind/window，input 指向本轮孤立 JSON。窗口覆盖真正展示给审核者的完整上下文。音效/BGM 用视听上下文，画面用 picture；整集只在原反馈明确通过且全范围未变时才能继承。

检查比较素材字节、所有重叠片段的完整时序、增益、自动化、引用效果、画布/FPS与全局配置；忽略段/轨自己的随机 ID 和等价媒体迁移。picture 排除音轨及明确的音频字段；未知字段保守保留，可能要求多审，不会推测它无影响。无法解析资源路径、引用循环、冲突 ID 直接拒绝继承；可重做该项复核，无须改写真实草稿来迎合工具。完整重叠片段和全局项比较可能使窗口外改动也触发重审。

反馈文件、规范化文件及当时展示媒体的 SHA 必须仍一致。输出只证明**该项该范围**可以复用旧判断，不会填写 `quality-review` 的 listened/normal_speed 布尔值，也不会把执行者写成监听者。最终仍由既有 `review-check` 检查当前版本的专项记录。

后轮反馈里来自 `prior_*` 或 `inheritance.inherited` 的旧 pass 不作为本轮新通过；沿原始绑定再次 check，不能只搬运状态按钮建立新证据。

复核页折叠“未变且已过”项，修改项给前后对照。画面已过仅继承画面；当前试听短片必须带当前混音，不能回放已否定的旧音效。整集 optional pending 继续 pending，不因若干局部通过而冒称整集通过。明确选中候选只需落实并复核受影响段，保留原反馈来源。
