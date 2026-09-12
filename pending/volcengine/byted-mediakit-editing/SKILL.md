---
name: byted-mediakit-editing
version: "0.2.1"
license: "MIT"
description: "面向音频、视频或图片素材组成成片的编辑制作目标，适用于时间线裁剪与拼接、速度和音量调整、视频滤镜、运镜特效、转场、画面裁切旋转翻转、画面叠加、字幕压制、动图截取、淡入淡出、音视频提取与合流、音频混合、文字滚屏成片、图转视频以及多画面空间组合等操作。若用户要给视频添加滤镜效果，或对象和目标族已明确是对现有素材做剪辑、合成、叠加、混合或成片编排，但具体做法不确定，可先加载本 Skill 探索。"
permissions:
  - shell
metadata:
  requires:
    bins: ["mediakit-cli"]
  cliHelp: "mediakit-cli editing --help"
  product: mediakit-cli/skills
  domain: editing
  capability_count: 23
---
# editing MediaKit Skill

## 使用规则

1. 先读取 `../byted-mediakit-shared/SKILL.md`，执行统一前置检查；该 Skill 缺失时停止并提示安装。
2. 只从下表选择 `editing` 域工具；相似能力按各工具“能力描述”和参数边界区分。
3. 执行前按需读取对应 reference；参数与结果说明来自同一份已审核文案，完整机器合同以当前 CLI `--schema` 为准。
4. 缺少必填参数、鉴权环境变量或真实输入资源时，向用户索取；通用可选字段只能透传用户明确提供的值，其他可选字段可由明确意图准确确定，但不得伪造。
5. 执行时设置 `MEDIAKIT_SURFACE=skill`，指定调用来源是 Skill。
6. 执行时把 `MEDIAKIT_RUNTIME` 设置为当前 Agent 宿主，避免 CLI 无法可靠识别父级 Agent。

## 澄清与跨域路由

若只给出媒体类型而未说明要剪、合、叠、调、加滤镜还是分析，应先澄清。纯图像增强、抠图、OCR、图片水印或图片尺寸优化应路由到 image；视频画质增强、内容理解、从视频提取字幕、语音转字幕、字幕擦除、暗水印、人像或绿幕抠像等视频智能处理应路由到 video；音频转码、语音端点检测、人声背景分离等非剪辑目标应路由到 audio。滤镜效果包括春日/晚霞/鲜亮/白皙/食物等，具体参数以工具 reference 为准。

## 工具列表

| 工具 | 说明 | 支持模式 | 命令 | 参考 |
| --- | --- | --- | --- | --- |
| add-image-to-video | 支持将指定图片（如 Logo、水印等）叠加到视频画面上。 | Cloud / Local | `mediakit-cli editing add-image-to-video` | [reference/add-image-to-video.md](reference/add-image-to-video.md) |
| add-subtitle-to-video | 将字幕文件或文本内容按自定义样式压制到视频画面中，生成带内嵌字幕的新视频。 | Cloud / Local | `mediakit-cli editing add-subtitle-to-video` | [reference/add-subtitle-to-video.md](reference/add-subtitle-to-video.md) |
| adjust-audio-speed | 用于音频调速，可调整音频播放倍速，实现快放或慢放效果。 | Cloud / Local | `mediakit-cli editing adjust-audio-speed` | [reference/adjust-audio-speed.md](reference/adjust-audio-speed.md) |
| adjust-video-speed | 用于视频调速，通过调整播放倍速产生快放或慢放效果。 | Cloud / Local | `mediakit-cli editing adjust-video-speed` | [reference/adjust-video-speed.md](reference/adjust-video-speed.md) |
| adjust-video-volume | 用于调整输入视频的音量大小，也可实现静音。 | Cloud / Local | `mediakit-cli editing adjust-video-volume` | [reference/adjust-video-volume.md](reference/adjust-video-volume.md) |
| apply-camera-motion | 对输入视频在指定时间段内添加一种运镜特效，常用于素材二次创作、营销片头、短剧动效等场景。 | Cloud | `mediakit-cli editing apply-camera-motion` | [reference/apply-camera-motion.md](reference/apply-camera-motion.md) |
| apply-video-filter | 为指定视频添加滤镜效果。 | Cloud | `mediakit-cli editing apply-video-filter` | [reference/apply-video-filter.md](reference/apply-video-filter.md) |
| concat-audio | 拼接多个音频片段。 | Cloud / Local | `mediakit-cli editing concat-audio` | [reference/concat-audio.md](reference/concat-audio.md) |
| concat-video | 将多个视频按顺序拼接成一个完整的视频文件，并支持在拼接处添加转场效果。 | Cloud / Local | `mediakit-cli editing concat-video` | [reference/concat-video.md](reference/concat-video.md) |
| crop-video | 按指定的矩形区域裁剪视频画面，裁剪结果仅保留指定的需要区域。 | Cloud | `mediakit-cli editing crop-video` | [reference/crop-video.md](reference/crop-video.md) |
| extract-animated-image | 从视频中按指定开始时间和结束时间截取一段画面，生成 GIF 或 WebP 动图，常用于制作封面动图、营销素材和短预览。 | Cloud | `mediakit-cli editing extract-animated-image` | [reference/extract-animated-image.md](reference/extract-animated-image.md) |
| extract-audio | 从输入视频文件中分离音轨，生成独立的音频文件。 | Cloud / Local | `mediakit-cli editing extract-audio` | [reference/extract-audio.md](reference/extract-audio.md) |
| fade-audio | 对输入音频的起止位置实现淡入或淡出效果，输出处理后的音频文件。 | Cloud / Local | `mediakit-cli editing fade-audio` | [reference/fade-audio.md](reference/fade-audio.md) |
| fade-video-audio | 在片头或片尾对输入视频音轨执行淡入或淡出处理，用于弱化音轨突兀的起止，提升成片听感。输出处理后的视频文件。 | Cloud / Local | `mediakit-cli editing fade-video-audio` | [reference/fade-video-audio.md](reference/fade-video-audio.md) |
| flip-video | 用于视频画面翻转，对指定视频进行上下或左右镜像翻转。 | Cloud / Local | `mediakit-cli editing flip-video` | [reference/flip-video.md](reference/flip-video.md) |
| image-to-video | 将多张图片按顺序组合成动态视频，可配置转场动画和镜头内动画；仅把现有图片做成带动效的视频，不支持根据参考图生成新的画面内容。 | Cloud | `mediakit-cli editing image-to-video` | [reference/image-to-video.md](reference/image-to-video.md) |
| mix-audio | 将多个音频文件（如背景音乐、音效、人声）进行混音，生成一个新的音频文件。<br>处理耗时：处理耗时与视频时长正相关。视频时长越长，处理耗时越长。平均 RTF（处理耗时/原片时长）为 1。<br>输出音频的时长以最长的音频为准。<br>输出视频格式：mp3 | Cloud / Local | `mediakit-cli editing mix-audio` | [reference/mix-audio.md](reference/mix-audio.md) |
| mux-audio-video | 可将输入的音频流与视频流合并成一个新的视频文件，并可选择保留或替换视频的原有音轨；当音视频时长不一致时，可进行对齐处理。 | Cloud / Local | `mediakit-cli editing mux-audio-video` | [reference/mux-audio-video.md](reference/mux-audio-video.md) |
| rotate-video | 用于视频画面旋转，对指定视频进行整体旋转。 | Cloud | `mediakit-cli editing rotate-video` | [reference/rotate-video.md](reference/rotate-video.md) |
| stitch-video | 将多个视频在空间上按水平或垂直方向拼接成一个完整画面，适用于多视角对比、画面组合等场景。 | Cloud | `mediakit-cli editing stitch-video` | [reference/stitch-video.md](reference/stitch-video.md) |
| text-to-scrolling-video | 将指定文本内容转换为文字滚屏视频，输出视频为固定 9:16 竖版，常用于小说推文、内容讲解和歌词视频等场景。 | Cloud | `mediakit-cli editing text-to-scrolling-video` | [reference/text-to-scrolling-video.md](reference/text-to-scrolling-video.md) |
| trim-audio | 用于音频裁剪，按指定的开始时间和结束时间从输入音频中截取片段。 | Cloud / Local | `mediakit-cli editing trim-audio` | [reference/trim-audio.md](reference/trim-audio.md) |
| trim-video | 用于视频裁剪，可按指定的开始和结束时间从输入视频截取片段。 | Cloud / Local | `mediakit-cli editing trim-video` | [reference/trim-video.md](reference/trim-video.md) |
