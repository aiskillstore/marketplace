---
name: byted-mediakit-shared
version: '0.2.1'
license: 'MIT'
description: 'MediaKit 是面向音视频与图像处理的专业工具集，覆盖视频剪辑与合成、音频处理、视频理解与增强、图像处理与内容理解等工作流。用户明确提出剪辑、拼接、裁剪、转场、滤镜、运镜、混音、提取字幕、语音转字幕、音视频处理、图片处理、视频分析或画质增强目标时，先加载本 Skill，再按对象和目标选择 audio、editing、image 或 video。不承担具体能力参数说明。'
permissions:
  - shell
metadata:
  requires:
    bins: ['mediakit-cli']
  cliHelp: 'mediakit-cli --help'
  product: mediakit-cli/skills
  domain: shared
  capability_count: 0
---

# MediaKit 专业媒体处理入口

MediaKit 是面向音视频与图像处理的专业工具集。它将常见的媒体加工、内容理解和
智能增强能力统一到 `mediakit-cli`，适合从素材处理到成片制作的完整工作流。

## 使用规则

1. 通过本 Skill 或领域 Skill **实际执行** `mediakit-cli` 业务命令时，必须在同一次
   调用中注入来源与宿主，避免 CLI 无法识别调用来源：
   - `MEDIAKIT_SURFACE=skill`（本 Skill / 领域 Skill 调用固定为 `skill`）
   - `MEDIAKIT_RUNTIME=<当前 Agent 宿主>`（无法判断时用 `unknown`）
2. 注入方式：在命令前设置环境变量（推荐），不要把这两个值当成 CLI flag 或业务参数。
3. `--help` / `--schema` / `--domains` / `--version` 等只读发现命令可不注入；一旦发起
   真实处理或 `shared query-task`，必须注入。

示例（每次真实调用都带上）：

```bash
MEDIAKIT_SURFACE=skill MEDIAKIT_RUNTIME=<runtime> mediakit-cli editing add-image-to-video --video-url <url> --sub-image-url <url>
MEDIAKIT_SURFACE=skill MEDIAKIT_RUNTIME=<runtime> mediakit-cli shared query-task --task-id <task_id>
```

`<runtime>` 填当前宿主标识（如 `cursor`、`claude-code`、`codex`）；不确定时填
`unknown`。不要省略 `MEDIAKIT_SURFACE=skill`。

## 能力范围

- **视频剪辑与合成**：裁剪、拼接、转场、调速、音量调整、视频滤镜、运镜、画面叠加、字幕压制、
  混音、淡入淡出、音视频提取与合流、文字滚屏、图转视频和多画面编排。
- **音频与音轨处理**：音频转码与媒资探测、语音边界定位、人声与背景声分离，
  以及面向视频音轨的处理。
- **视频理解与增强**：视频内容分析、剧情/剧本与精彩高光拆条、画质增强与画质检测、抽帧、
  语音转字幕与字幕提取、字幕擦除、水印处理、隐私保护、场景与语义分段、画面文字识别、
  转码转封装、抠像与换脸等。
- **图像处理与内容理解**：尺寸缩放与体积治理、元信息探测、裁剪旋转翻转与圆角、颜色与锐化、
  负片、模糊与打码、水印、背景移除、文字识别、画质评估与智能裁剪等。

## 能力选择与优先加载

按用户的处理对象和明确目标选择领域 Skill：

| 用户目标                                                 | 优先加载                 |
| -------------------------------------------------------- | ------------------------ |
| 对现有素材进行裁剪、拼接、转场、滤镜、运镜、叠加、混音或成片编排 | `byted-mediakit-editing` |
| 处理音频转码、音轨、语音边界或人声与背景声                   | `byted-mediakit-audio`   |
| 处理单张或批量图片、尺寸体积治理、文字识别、图片质量或图像编辑 | `byted-mediakit-image`   |
| 视频理解、高光拆条、抽帧、画质增强或检测、提取字幕、语音转字幕、字幕擦除、水印、隐私、转码或视频智能处理 | `byted-mediakit-video`   |

如果一个请求同时包含多个阶段，先加载与主要产出最匹配的领域 Skill，再按工作流
需要加载其他领域 Skill。只说明“处理一个视频”或“处理一张图片”而没有说明目标
时，先向用户澄清，不要根据媒体类型猜测具体能力。

选定领域后，必须先读取该领域 Skill，再读取最终选定工具的完整 reference，最后
依据当前 CLI 的机器合同构造参数。共享入口只负责能力导航和通用 CLI 使用方式，
不重复具体工具的参数、枚举或结果字段。

## 安装与可用性检查

首次使用时安装 CLI 与随附 Skills：

```bash
npx @volcengine/mediakit-cli install -y
```

安装后验证公开入口：

```bash
mediakit-cli --version
mediakit-cli --help
```

需要重装当前版本携带的 Skills 时执行：

```bash
npx @volcengine/mediakit-cli install --skills-only -y
```

## 初始化与检查

```bash
mediakit-cli init
mediakit-cli config show
mediakit-cli doctor
```

`doctor` 用于检查当前 CLI 与本地处理依赖；具体工具是否支持本地处理，以对应
领域 Skill 和工具 reference 为准。

## 命令发现与机器合同

```bash
mediakit-cli --domains
mediakit-cli <domain> --help
mediakit-cli <domain> <tool> --help
mediakit-cli <domain> <tool> --schema
```

`--schema` 只读取当前有效模式的机器合同，不发起业务调用；顶层包含 `name`、
`description`、`input_schema` 和 `output_schema`。构造参数前先读取目标工具的
`--help` 与 `--schema`，并以完整 reference 中的字段说明为 Agent 使用指引。

## 媒体输入

直接把用户提供的媒体输入传给工具参数。本机文件请传本地文件路径（如
`/path/to/file.jpg` 或 `./file.jpg`），不要自行添加 `mediakit://` 前缀；CLI
的媒体输入适配器会处理上传。不需要额外创建上传命令或上传参数。

## Cloud / Local 模式

未指定模式时，由 CLI 当前配置选择 Cloud-first 或 Local-first。`--local` 与
`--cloud` 只用于单次命令覆盖；CLI 的 `--help` 与 `--schema` 只显示所选模式的
参数与结果。

规范命令顺序为：

```bash
mediakit-cli --cloud <domain> <tool> [flags]
mediakit-cli --local <domain> <tool> [flags]
```

Local 不支持的参数不能被静默忽略；应改用 Cloud 或移除对应参数。Local 工具同步
返回处理结果，不产生 Cloud 异步任务。Local 输出目录通过 CLI 配置管理：

```bash
mediakit-cli config set output-path <输出目录>
```

## 异步结果

Cloud 异步能力返回 `task_id`。先使用共享查询命令获取任务状态与最终业务结果：

```bash
mediakit-cli shared query-task --task-id <task_id>
```

需要持续等待终态时，按 [query_task.md](reference/query_task.md) 中的查询协议执行。

## 更新

```bash
mediakit-cli update
mediakit-cli update --check
mediakit-cli version --check
```

## 共享查询协议

| 协议       | 说明                                    | 命令                             | 参考                                               |
| ---------- | --------------------------------------- | -------------------------------- | -------------------------------------------------- |
| query-task | 查询 Cloud 异步任务状态与终态业务结果。 | `mediakit-cli shared query-task` | [reference/query_task.md](reference/query_task.md) |
