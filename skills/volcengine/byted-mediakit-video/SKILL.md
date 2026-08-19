---
name: byted-mediakit-video
version: "1.0.0"
license: "MIT"
description: "视频处理，涵盖视频画质增强、视频理解、字幕擦除等能力。包含能力：analyze-video-highlights, analyze-video-storyline, asr-subtitles, enhance-video, enhance-video-generative, erase-video-subtitle, erase-video-subtitle-pro, generate-highlights-microdrama, generate-highlights-minigame, matte-greenscreen-video, matte-portrait-video, probe-video-metadata, segment-scenes, video-ocr。当用户需要使用 video 域的 MediaKit CLI 能力时触发。"
permissions:
  - shell
metadata:
  requires:
    bins: ["mediakit-cli"]
  cliHelp: "mediakit-cli video --help"
  product: mediakit-cli/skills
  domain: video
  capability_count: 14
---
# Video Skills

## 前置说明

开始前必须先读取 `./reference/shared.md` 的内容，其中包含前置检查、异步任务机制、结果查询等说明。

## 工具列表

| 工具 | 说明 | 参数声明 | 参考文档 |
|------|------|----------|----------|
| analyze-video-highlights | 智能捕捉视频"情绪波峰"与"关键动作"，输出精准时间戳、高光打分、OCR 文本和画面描述等元数据，供下游进行更灵活的二次开发。 支持短剧（Miniseries）和小游戏（Game）两种分析模型。 使用限制：单次最多 100 个视频，累计时长不超过 300 分钟。 | `video_urls:array<string>, model:string, mode:string, minigame_info?:object{name?:string, play_definition?:string, highlight_definition?:string}, callback_args?:string, client_token?:string` | [reference/analyze-video-highlights.md](reference/analyze-video-highlights.md) |
| analyze-video-storyline | 智能解析影视剧内容，生成结构化剧情线，供智能剪辑、内容检索与互动播放等场景使用。 基于大模型视频理解能力，对输入的单个或多个长视频（如电影、电视剧）进行分析，提取并组织成一份完整的故事线。 该故事线由一系列按时间顺序排列的剧情片段（Clips）和基于片段聚合的高光故事线（Highlights）组成。 使用限制：单次最多 30 个视频，单个视频时长不超过 2.5 小时。 | `video_urls:array<string>, enable_snapshot?:boolean, callback_args?:string, client_token?:string` | [reference/analyze-video-storyline.md](reference/analyze-video-storyline.md) |
| asr-subtitles | 对输入视频或音频进行语音识别，输出带时间戳的字幕片段。 支持格式：主流音视频格式（如mp4、mov、mp3、m4a、wav等）。 输入：video_url和audio_url二选一。 | `video_url?:string, audio_url?:string, content_type?:string, language?:string, enable_speaker_info?:boolean, enable_confidence?:boolean, callback_args?:string, client_token?:string` | [reference/asr-subtitles.md](reference/asr-subtitles.md) |
| enhance-video | 画质增强：针对 AIGC / UGC / 短剧 / 教育 / 游戏 / 老片修复等场景，提供画质提升 + 超分增强一站式解决方案。依托 AI MediaKit 智能媒体处理引擎，融合视频内容理解、画质指标智能决策、多维度增强原子算法，实现画质的全面优化。 支持格式：主流视频格式如mp4、flv、ts、avi、mov、wmv、mkv。 使用限制：单文件大小不超过100G。 | `video_url:string, scene?:string, tool_version?:string, resolution?:string, resolution_limit?:integer, fps?:number, callback_args?:string, client_token?:string` | [reference/enhance-video.md](reference/enhance-video.md) |
| enhance-video-generative | 生成式视频增强修复（generative_video_restoration）是基于扩散大模型（Diffusion-based Large Model）的生成式视频修复技术。不仅可以还原被破坏的像素，更借助大规模预训练积累的丰富视觉先验，主动补全细节、理解语义，生成真实、自然、高保真的视频内容。 | `video_url:string, resolution?:string, bitrate_level?:string, fps?:number, callback_args?:string, client_token?:string` | [reference/enhance-video-generative.md](reference/enhance-video-generative.md) |
| erase-video-subtitle | 智能检测并擦除视频画面中已有的硬字幕，保留原始背景。 支持格式：主流视频格式如mp4、flv、ts、avi、mov、wmv、mkv。 | `video_url:string, callback_args?:string, client_token?:string` | [reference/erase-video-subtitle.md](reference/erase-video-subtitle.md) |
| erase-video-subtitle-pro | 针对视频中的字幕，实现高质量的无痕擦除，最大程度的还原视频画面。 支持格式：主流视频格式如mp4、flv、ts、avi、mov、wmv、mkv。 | `video_url:string, mode?:string, output_encode_mode?:string, erase_ratio_location?:array<object{top_left_x:number, top_left_y:number, bottom_right_x:number, bottom_right_y:number}>, callback_args?:string, client_token?:string` | [reference/erase-video-subtitle-pro.md](reference/erase-video-subtitle-pro.md) |
| generate-highlights-microdrama | 深度理解短剧角色、剧情与故事线，自动提取高光片段并混剪成投流视频。 支持故事线混剪模式（StorylineCuts），可选"短剧三要素"视觉模板，输出高光集锦、单集预告等。 支持输出详细分镜信息（storyboard）。 使用限制：单次最多 100 个视频，累计时长不超过 300 分钟。 | `video_urls:array<string>, mode?:string, enable_generate_video?:boolean, enable_return_poster?:boolean, edit_param?:object{mode:string, template_edit?:object{template?:string, title?:string, hint?:string}}, highlight_cuts_param?:object{enable_storyboard?:boolean, min_duration?:number, max_duration?:number, max_number?:integer, cut_mode?:string}, opening_hook_param?:object{enable_opening_hook?:boolean, min_duration?:number, max_duration?:number, min_clip_duration?:number, min_score?:number}, callback_args?:string, client_token?:string` | [reference/generate-highlights-microdrama.md](reference/generate-highlights-microdrama.md) |
| generate-highlights-minigame | 识别小游戏录屏视频中的核心玩法与高光事件（如连击、通关、极限操作等）， 快速生成用于买量的视频素材。支持提供游戏名称、玩法描述、高光定义以辅助模型更精准识别。 使用限制：本期仅支持单视频输入。 | `video_urls:array<string>, mode?:string, enable_generate_video?:boolean, minigame_info?:object{name?:string, play_definition?:string, highlight_definition?:string}, callback_args?:string, client_token?:string` | [reference/generate-highlights-minigame.md](reference/generate-highlights-minigame.md) |
| matte-greenscreen-video | 对以绿幕或纯色为背景的视频进行抠图，自动识别主体（人物、物品、动物等），同时移除背景，生成背景透明的视频。 输出视频格式为 WEBM（默认）或 MOV，分辨率与原片对齐。 支持的格式：主流视频格式如 mp4、flv、ts、avi、mov、mkv、wmv。 | `video_url:string, format?:string, callback_args?:string, client_token?:string` | [reference/matte-greenscreen-video.md](reference/matte-greenscreen-video.md) |
| matte-portrait-video | 自动识别人物主体，同时移除背景，生成背景透明的视频，适用于背景替换等场景。 输出格式为 WEBM（默认）或 MOV，分辨率与原片对齐。 支持的格式：主流视频格式如 mp4、flv、ts、avi、mov、mkv、wmv。 | `video_url:string, format?:string, callback_args?:string, client_token?:string` | [reference/matte-portrait-video.md](reference/matte-portrait-video.md) |
| probe-video-metadata | 对输入视频 URL 进行探测，输出标准化媒资元信息，覆盖容器层（format_meta）、视频流层（video_stream_meta）与音频流层（audio_stream_meta）。 字段分类参考 ffprobe，并对 VOD 原始返回做精简与统一，便于上层做分辨率/帧率/码率/编码等策略判断。 使用限制：仅支持公网 HTTP/HTTPS URL；输入视频分辨率最高支持 4K。 | `video_url:string, callback_args?:string, client_token?:string` | [reference/probe-video-metadata.md](reference/probe-video-metadata.md) |
| segment-scenes | 依据视频转场与画面变化自动切分场景，输出切片时间轴和（可选）切片文件。 支持格式：MP4、FLV、ASF、RM、RMVB、MPEG、MOV、AVI、MPEGTS、M4S、WMV、3GP、TS、MPG、WEBM、MKV、WM、MPE、VOB、DAT、MP4V、M4V、F4V、MXF、QT 等主流视频格式。 使用限制：单个视频时长不超过 2 小时。 | `video_url:string, enable_clip_fade?:boolean, segment_threshold?:number, min_duration?:number, max_duration?:number, callback_args?:string, client_token?:string` | [reference/segment-scenes.md](reference/segment-scenes.md) |
| video-ocr | 识别视频画面中的字幕/文字内容，输出带时间戳的字幕片段。 支持格式：主流视频格式如 mp4、flv、ts、avi、mov、wmv、mkv。 | `video_url:string, mode?:string, callback_args?:string, client_token?:string` | [reference/video-ocr.md](reference/video-ocr.md) |
