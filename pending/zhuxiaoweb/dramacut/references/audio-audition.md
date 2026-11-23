# 原生音效独奏与 A/B

在计划 `apply → preview` 后，用 `audio_audition.py` 为新增 `mix_role=sfx` 逐事件生成同窗的 **full / without / solo** 三版。它只读孤立 JSON、已解码的预览副本与哈希证书；不回写草稿，不改原音频文件，也不把测量写成已试听。

```powershell
python "<skill>/scripts/audio_audition.py" --input "<edited/draft_content.json>" --preview "<preview目录>" --edit-report "<edited/report.json>" --output "<新试听目录>" --ffmpeg "<ffmpeg.exe>" --codec "<jy-draftc.exe>" --runtime "<匹配引擎目录>"
```

加 `--segment-id "<report.sfx中的segment_id>"` 只验受影响事件。参数可重复。BGM 不冒充 SFX。仅检查此次 `report.sfx` 中的新增 SFX；继承音效需另建立对应事件报告，不凭轨道名自动猜测。

默认窗口模式会忽略窗外效果，窗内不支持的时间结构仍拒绝。遇到原时间线非等长 source/target 或相交的复杂画面效果时，显式加 `--full-timeline`：保持完整原生时序/效果，将 full/without/solo 三版**整集渲染完成后再裁试听窗**，不改 source duration 绕过限制。

`--batch-independent-events` 必须同时加 `--full-timeline`。工具先检查完整时间线，而不只检查选中音效：上下文必须互不重叠、其他选音不落入试听窗、选音为独立整数 PCM WAV、时间结构普通可编辑，未证明的素材组和全局/轨道/片段自动化及动态处理均拒绝。保守结构预检通过后才复用三次整集渲染；不假定不同原生渲染与编码路径完全等价，仍须审实际输出。拒绝时回到逐事件 `--full-timeline`，不强行批量。预设子草稿的播放/config路径与占位解析逐项绑定；缺UI封面不代表可忽略播放资源。

每个窗从主 attack 前 0.8 秒到后至少 1.2 秒，长尾另加 0.3 秒。三版均通过相同原生引擎与设置渲染；without 只静音这一层，solo 静音其他音轨及视频内嵌音频。为避免字幕截断造成无关拒绝，诊断副本去掉字幕轨；正式时间线不变。裁切保留原始声源、线性推子曲线、淡化位置；复杂变速、反放、非线性音量或未知时间效果会明确拒绝，不降级猜测。

打开 `audition.html`，用同样的设备音量比较三版，并结合正式有字幕预览确认具体动作/词语：

- solo 主 attack RMS 低于 −36 dBFS：先查选段是否含真实 attack，检查实际来源，而不是直接拉高推子。
- solo 比 without 的 attack 窗 RMS 低于 18 dB：可能被遮蔽。听 A/B，必要时换更清晰音效、缩短尾音或给 BGM 局部 duck。该差值不是声学掩蔽的证明。
- full 中辨认不到事件、或事件虽响却不合画面：不能通过。回到事件锚点和至少两个候选的比较，不按固定秒数均匀撒音效。
- 同时检查关键名字、否定词与下一句是否清楚，总峰值有余量。峰值相同不代表 RMS、密度和听感相同。

`audition.json` 绑定输入 JSON、report、preview 证书、已解析预览 JSON、原始媒体/后端依赖、所有三版产物的 SHA-256。`verify_manifest(path)` 可用于提交门禁复核。`listening.template.json` 默认 `listened=false`、其余审阅项 false；实际看片听音之后逐条填 anchor、decision 与 notes。没有音频感知能力时保留 pending 并报告有限核验范围，不能批量改为 true。

该工具提供真实渲染的音效分轨与 A/B，不能自动判断音效是否应景、观众是否能感知、或主 attack 是否正好命中眼神/动作。非本工具生成的“独奏统计”和 `cue` 文本不能代替试听证据。故障保留 `failure.json` 和原生 render log，修复后只重做受影响事件到新目录。

## 与提交记录对接

工具提示 attack 过低或可能被遮蔽时，先修选段/音色/局部 duck 并重渲受影响事件。实际 A/B 确认是故意极轻的声音才在 quality review 的 `measurement_exception_reason` 写具体理由；不能只把 decision 改成 pass 消除提示。

`listening.template.json` 是可选逐事件笔记；run 的提交门实际消费 `quality-review.json`。从 run 给出的 `quality-review.template.json` 另存后，填写 `audition_manifests`（指向本工具 `audition.json`），并把真实判断写入 `sfx[]` 的 `attack_checked / scene_relevance_checked / dialogue_clear / listened_solo / listened_ab / decision / anchor / candidates_compared / reason`。第二候选的准备方式和记录格式见 [音效候选与真实落点](sfx-library.md#attack-与选段必须分开)：两候选都需 `prepare`，使用相同的 `event_id` 和输入时间线 `target_us`，并将最终选用者包含在 `candidates_compared` 中。只填写 listening 笔记不会让 run 通过；不要把波形候选或工具输出当成实际听过。没有监听能力时保持 pending，报告有限核验范围。

分步流程也可用 `fine_cut.py review-check --input <JSON> --edit-report <report> --qc <QC> --seam-scan <scan> --template <新模板>` 生成相同模板，填后用 `--review <记录>` 校验。纯音频、零新SFX/零接点无需伪造这些记录。
