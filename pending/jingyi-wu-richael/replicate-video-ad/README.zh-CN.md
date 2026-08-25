# 视频带货复刻 Skill

[English](README.md) | 简体中文

这是一个面向 Codex 的视频复刻 skill：把参考视频转化为基于证据的镜头分析，以及可直接用于生产的电商剧情广告复刻提示词。

它会保留原视频的节奏、构图、叙事机制、商品植入、证明过程和转化逻辑，同时替换人物身份、品牌信息、未经证实的产品主张与平台界面。

## 可以产出什么

- 最高 2 fps 的高密度抽帧、分镜接触表和关键帧故事板
- 带时间轴的镜头表，覆盖画面动作、对白或字幕、剧情功能与商品露出
- 对 Hook、升级、反转、商品桥接、效果证明、情绪回报与 CTA 的拆解
- 把原视频结构迁移到另一产品的可复制主提示词
- 对白与声音方向、后期字幕文案、负面约束和分段生成方案
- 明确区分原片可观察事实、改编决策与仍需确认的产品主张

## 环境要求

- Codex，或其他支持文件夹式 skill 的 Agent 环境
- Python 3.10+
- `ffmpeg` 和 `ffprobe`
- 可选：使用视频 URL 时安装 `yt-dlp`
- 可选：先使用 `watch` skill 完成视频下载、字幕与画面获取

内置抽帧脚本只依赖 Python 标准库，并在需要时调用上述外部程序。

## 安装

将仓库克隆到 Codex 的 skills 目录：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Jingyi-Wu-Richael/replicate-video-ad.git \
  ~/.codex/skills/replicate-video-ad
```

重启 Codex 或新建一个任务，让 Codex 重新发现该 skill。

## 使用方式

显式调用 skill，并附上本地视频：

```text
使用 $replicate-video-ad 拆解这个参考视频，并把它的剧情结构改编成我的护肤产品广告。
```

也可以提供公开视频链接：

```text
使用 $replicate-video-ad 拆解这个视频，为【产品名】生成一套 30 秒抖音剧情带货复刻提示词：【URL】
```

当产品信息不完整时，skill 会保留 `【品牌】`、`【产品名】`、`【核心卖点】` 等占位符，不会自行编造产品主张。

## 内置抽帧工具

已有本地视频时，可以直接运行确定性的抽帧脚本：

```bash
python3 scripts/extract_video.py "/path/to/reference.mp4" \
  --out-dir "/path/to/new-output-directory" \
  --fps 2 --max-frames 120 --width 768
```

增加 `--extract-audio` 参数，可生成单声道 16 kHz MP3，交给可用的转写流程处理。

输出目录必须为空或尚未创建。脚本通常会生成：

```text
storyboard.jpg
frames.zip
frame_manifest.json
frame_manifest.csv
contact_sheets/
frames/
audio.mp3             # 仅在使用 --extract-audio 时生成
```

## 仓库结构

```text
replicate-video-ad/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── ad-framework.md
│   └── output-template.md
└── scripts/
    └── extract_video.py
```

## 复刻边界

这个 skill 复刻的是结构与转化机制，不是身份。它会避开可识别的人脸、声音、水印、账号名、平台 UI，以及未经支持的产品主张。只有在原生字幕、许可转写或画面内嵌字幕提供依据时，才会写入具体对白。

默认分析方式是“高密度抽帧”，不是导出视频编码中的每一帧。
