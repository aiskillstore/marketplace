---
name: byted-mediakit-audio
version: "0.2.1"
license: "MIT"
description: "面向音频文件或视频中的音轨，处理语音边界定位、音频媒资信息探测、音频转码与码流封装适配、人声与背景声分离等目标。若对象和目标族已明确属于音频内容理解、音频转码、音频格式治理或音轨分离，但具体做法不确定，可先加载本 Skill 探索。"
permissions:
  - shell
metadata:
  requires:
    bins: ["mediakit-cli"]
  cliHelp: "mediakit-cli audio --help"
  product: mediakit-cli/skills
  domain: audio
  capability_count: 4
---
# audio MediaKit Skill

## 使用规则

1. 先读取 `../byted-mediakit-shared/SKILL.md`，执行统一前置检查；该 Skill 缺失时停止并提示安装。
2. 只从下表选择 `audio` 域工具；相似能力按各工具“能力描述”和参数边界区分。
3. 执行前按需读取对应 reference；参数与结果说明来自同一份已审核文案，完整机器合同以当前 CLI `--schema` 为准。
4. 缺少必填参数、鉴权环境变量或真实输入资源时，向用户索取；通用可选字段只能透传用户明确提供的值，其他可选字段可由明确意图准确确定，但不得伪造。
5. 执行时设置 `MEDIAKIT_SURFACE=skill`，指定调用来源是 Skill。
6. 执行时把 `MEDIAKIT_RUNTIME` 设置为当前 Agent 宿主，避免 CLI 无法可靠识别父级 Agent。

## 澄清与跨域路由

若只说有音频而未说明业务目标，应先澄清。音频裁剪、拼接、调速、淡入淡出、混音、从视频抽取音轨或音视频合流等编辑合成诉求应路由到 editing；字幕生成、提取字幕、语音转字幕、视频理解、视频增强等应路由到 video。

## 工具列表

| 工具 | 说明 | 支持模式 | 命令 | 参考 |
| --- | --- | --- | --- | --- |
| detect-voice-activity | 用于语音端点识别。自动定位音频或视频文件中有效语音的起止时间。将人声和静音、背景噪声等无效片段区分开来。返回包含所有有效人声片段起止时间戳的列表。 | Cloud | `mediakit-cli audio detect-voice-activity` | [reference/detect-voice-activity.md](reference/detect-voice-activity.md) |
| probe-audio-metadata | 探测输入音频 URL，输出标准化媒资元信息，用于获取音频元信息。 | Cloud / Local | `mediakit-cli audio probe-audio-metadata` | [reference/probe-audio-metadata.md](reference/probe-audio-metadata.md) |
| separate-voice | 用于人声背景声分离，可将音频或视频文件中的人声与背景音精准分离，输出为两个独立的音频文件。 | Cloud | `mediakit-cli audio separate-voice` | [reference/separate-voice.md](reference/separate-voice.md) |
| transcode-audio | 音频转码将一个音频码流转换为另一个音频码流，通常涉及编码格式、编码参数和封装格式的转换，用于适应不同业务场景、播放终端和网络环境。 | Cloud | `mediakit-cli audio transcode-audio` | [reference/transcode-audio.md](reference/transcode-audio.md) |
