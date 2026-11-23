# 音效候选库与真实落点

这里的库是 SFX，不能作为 BGM 目录，也不能用它取消用户选择 BGM 的开场步骤。`scripts/sfx_library.py` 只读索引与测量源文件，`prepare` 只在新的隔离目录写选段，不写剪映草稿；继续用现有 `apply → preview → qc → commit → verify → readback` 回写。

## 可带走的默认包

`assets/sfx/manifest.json` 收录 24 个原创程序合成短音，总 WAV 约 0.82 MiB；授权 CC0-1.0，完整来源与使用边界写在每项的 `provenance / use / avoid / license`。包含轻/重冲击、中频冲击、轻/快/重划过、反向蓄势、升压、意识轻敲、线索微亮、电子通知、心沉、双脉冲、暗/亮揭晓、反转急扣、片尾疑点、决定轻扣、关心、记忆入口、坚定收束。

这是可用的设计音起点，不是已主观试听的“最优网络热梗包”。不含真实敲门、脚步、衣物、纸张、玻璃、拳击、枪声或人的喘息；不得把合成重音冒充这些拟音。真实物件/动作优先保留现场声，缺失时搜索用户库、剪映库或有明确可复用许可的真实拟音。

另有 `assets/sfx-foley/manifest.json`：从 Kenney Impact Sounds / Interface Sounds 官方下载包选出的 30 个 CC0 候选，涵盖地毯/硬地/木地单步，木/玻璃/金属/软物碰撞、打击补强，以及点击、确认、错误、疑问、拨音、开关。随包保留两份原许可、官方下载页、压缩包/成员 SHA、取得日期和 PCM 转码记录。它们是按动作材质筛出的候选，不能称为“已知 TikTok 热门”或断言全为现场录音。玻璃碰撞不等于碎玻璃，开关不等于开门。先保留原声，再按实际画面试听选择。

复现/验包：

```powershell
python "<技能目录>/scripts/build_starter_sfx.py" --verify
python "<技能目录>/scripts/fine_cut.py" sfx-library verify-pack --root "<技能目录>/assets/sfx-foley"
```

`build_starter_sfx.py --verify` 重新生成同样的字节作 SHA-256 比较；不会覆盖不同内容的旧文件。`verify-pack` 检查 manifest 中的 WAV 路径、数量、哈希与来源字段，也拒绝目录中未登记的 WAV；不证明许可真实性或听感。音效素材必须随最终副本登记到 `Resources/Imported`，不能依赖技能在另台电脑上的路径。

外部补库与已取得素材的出处见 [来源目录](external-sfx-sources.md)。

## 找音效的具体顺序

先给真实剧情事件写一个 `event_id`、输入时码、画面动作/对白关键字、要让观众理解的变化。先辨类型，再搜候选；不要按“2.5 秒、中点、片尾”均匀铺三声。

| 事件类型 | 查找对象 | 不适用 |
| --- | --- | --- |
| `impact` | 可见接触的真实原声/拟音；设计冲击只作补强 | 普通切镜、无动作人脸 |
| `motion` | 确有快速运动时的短划过 | 同景别人脸跳切的遮掩 |
| `prop / door / phone` | 对应实物/动作的真实声或明确手机通知 | 泛低音替代纸张、门、脚步 |
| `recognition` | 证据、人名或意识变得清楚的一拍 | 每次眨眼/看到道具 |
| `reveal / dread` | 真相成立、攻守改变、意识到代价 | 关键信息尚未可辨时抢先揭底 |
| `decision / warmth` | 承诺、拒绝、接受关心、立场改变 | 每句对白末尾 |
| `riser / tail` | 危险/揭晓前短蓄势；具体未解片尾 | 整集循环或充当 BGM |

每个主事件先比较至少两个作用相同的短候选；`use/avoid` 和原声决定能否选，标签仅用于缩小搜索。连续同一情绪链可只有一个声音动作，两个脉冲仍是一个事件。场内另有独立动作或意识转变才另加，不靠机械数量堆音。

“单薄/像消音/温馨处怪声”等明确反馈的查找对象与撤层对照见 [逐项反馈与有限修正](feedback-refinement.md)。`decision/warmth` 不表示必须加提示音；BGM 变化或留白可承担声音动作，具体记录原因并重新核对事件矩阵，不把撤掉的音效计入覆盖。

```powershell
python "<技能目录>/scripts/fine_cut.py" sfx-library index --root "<技能目录>/assets/sfx" --root "<技能目录>/assets/sfx-foley" --root "<本次获准音效目录>" --output "<任务>/sfx-index.json"
python "<技能目录>/scripts/sfx_library.py" search --catalogue "<任务>/sfx-index.json" --event-class recognition --query "线索" --count 4
python "<技能目录>/scripts/sfx_library.py" measure --input "<候选.wav>" --output "<任务>/candidate-measure.json"
```

`index` 可传 `--cache <旧索引>`，只对完整 SHA-256 相同的文件复用测量，不改动、不复制源库。不能把历史许可或过去的试听判断当成本次剧情适配。长于 30 秒的输入默认只分析前 30 秒并标 `possibly_truncated`，不宣称测了完整文件；要测其他位置先明确取候选子段，或增加 `measure --max-seconds`。

## attack 与选段必须分开

测量保留全声道绝对峰值，使用 5 ms RMS 窗口估计 onset、最多 5 个上升沿候选、全局峰值位置、尾音截止和 RMS/crest。反相立体声不会被简单混成零；文件最大峰值不自动等于叙事命中点。渐强/反向素材的主攻击常在后部，不能只取文件头 0.5 秒，也不能把 onset、peak 或固定 100 ms 当成已确认 attack。

可选 `measure --tone-profile` 增加按声道计算的 2048 点 Hann FFT 频段能量（每声道最多 64 窗，不混成单声道），帮助比较低频主体和中频瞬态等信号特征；不分类鼓种，不证明音色应景、真实听感或手机可听。双击/多击用 `prepare --salient-attack-us` 逐次声明已听辨主击，从最早主击保留前导、从末击保留尾音。可给 `--selection-end-us / --fade-out-ms / --attack-body-ms`，末击或其声明主体被截短、淡出提前压入主体时拒绝；完整例子和撤层对照见 [逐项反馈与有限修正](feedback-refinement.md)。

用试听和画面/字词，确认一个**源绝对时码**。`prepare` 必须显式给 `--confirmed-attack-us`，按该点保留短前导和自然尾音，生成整数 PCM WAV 与可直接插入现有计划 `sfx` 数组的 `plan_sfx_row`：

```powershell
python "<技能目录>/scripts/sfx_library.py" prepare --input "<已选源.wav>" --output "<任务>/sfx-event-04" --confirmed-attack-us 420000 --target-us 12800000 --purpose "文件金额可读后，角色意识到被欺骗" --event-id e04 --event-class recognition --pre-ms 30 --tail-ms 500 --fader-db -3
```

`target_us` 是画面接触/关键字/意识变化的输入时码；工具输出 `attack_offset_us = confirmed_attack_us - selected_start_us`，随后 `apply` 用它对齐。把 `plan_sfx_row` 原样加入计划，其中已支持 `event_id/event_class/selection_evidence`；beat 必须存在且 `sound_action=sfx`。后端检查 selection 的哈希、选段和目标，主响声与 beat 偏差不超过80 ms。确认输出 `target_us - attack_offset_us ≥ 0`，尾音不越过本集/下一句；高音短提示通常留 80–250 ms，情绪 stinger 可先留 250–700 ms，按真实素材调整。

每个比较候选都在**不同的新输出目录**执行一次 `prepare`，使用相同的 `event_id` 与输入时间线 `target_us`，分别确认源 attack、前导和尾音。第二候选只用于实际比较，不要把它的 `plan_sfx_row` 加入计划。删时后报告里的 `target_us` 是输出时码，不能拿来代替这里的输入锚点。

quality review 用下述结构引用两份实际 `selection.json`，必须包含最终选中项。校验会检查原始文件和选段哈希、源范围/attack、事件与输入锚点；多击声明还检查所有主击偏移、击体、选段终点与淡出记录。同一文件的重复路径不算两个候选，不同源文件或不同源范围/attack 可以。工具仍不能证明比较时真的听过或语义应景。

```json
"candidates_compared": [
  {"selection_evidence": "D:/task/candidate-a/selection.json"},
  {"selection_evidence": "D:/task/candidate-b/selection.json"}
]
```

## 小声音的修法与验收

若源本身很轻（例如选段峰值 -23 dBFS），推子 -3 dB 会得到 -26 dBFS，不能称为“明显”。先比较另一个干净候选。确需增益时，`prepare --normalize-peak-dbfs -6` 只在新 WAV 上进行确定增益并记 `conditioning_gain_db`，不改用户原素材；增益超过 +18 dB 拒绝并要求换更干净候选。新源峰值加推子仍重新计算，响度与密度不同的音效不能只看峰值选。

不要为了让声效明显而把所有 cue 推到一样响。关键对白前后 80 ms 内先留辅音/尾音空间，音效易被 BGM 遮住时先对该事件局部 duck 或换更有中频瞬态的音色，再调整 cue。低频重音在手机上不一定可辨，优先比较中频冲击/轻敲；不能用持续提高低音峰值解决。

每个事件至少留这组验收：输入/输出 anchor、真实源 attack、选段 SHA、推子、SFX 独奏 attack 附近 160 ms RMS 与峰值、原混音和加音效混音在同一窗口的差异、对白是否清楚、主观 A/B 状态。能量差只证明信号变化，不能证明“应景”。`qc --edit-report` 只有混合窗口，不足以证明某 cue 可听；必须补独奏或有/无这一层 A/B。无法主观监听就记录 `not_listened` 并保留审听结果待填，禁止写“听感通过”。

外部来源只收录可追溯的官方下载页、许可页、作者、取得日期与具体文件 SHA；不从热门短视频/影视声音中随意抽取受保护片段。网络热度是检索提示，不是可复制授权。本包里的原创默认素材解决无网络、无许可明确素材时的短提示音缺口；真实拟音仍按事件需要选。
