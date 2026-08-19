# 精细化字幕擦除

## 能力描述
针对视频中的字幕，实现高质量的无痕擦除，最大程度的还原视频画面。
支持格式：主流视频格式如mp4、flv、ts、avi、mov、wmv、mkv。

## 执行方式

| 项目 | 说明 |
|------|------|
| Domain | `video` |
| Tool | `erase-video-subtitle-pro` |
| 是否异步 | `是` |
| 是否支持 local | `否` |
| 模式说明 | cloud only；可通过 `--cloud` 强制当前调用。 |
| 幂等行为 | 如命令支持 `client_token` 与 `callback_args`，重试时复用同一组值；强制重跑时更换新的 `client_token`。 |

## 参数
| 参数 | CLI flag | 类型 | 必填 | 默认值 | 说明 |
|------|----------|------|------|--------|------|
| video_url | `--video-url` | string | 是 | - | 输入视频。String 类型，支持http://xxx或https://xxx格式 URL |
| mode | `--mode` | string | 否 | Subtitle | 字幕擦除模式，取值如下：Subtitle：擦除OCR检测为字幕的文本。在此模式下，系统将启用 OCR 识别，并依据检测结果进行擦除操作，仅擦除下面50%画面的字幕。 Text：擦除OCR检测为字幕及其他的文本（如人物介绍等），不包含场景文字（如宫殿门牌匾等）。 |
| output_encode_mode | `--output-encode-mode` | string | 否 | Quality | 输出视频编码模式，支持以下两种取值：Quality（默认值）：画质优先模式。此模式下，系统会采用较高的目标码率进行编码，以确保高画质。这通常会导致输出文件的码率显著高于源文件，文件体积也相应增大。 Size：大小优先模式。在保证一定画质的前提下，使输出码率尽量向源视频码率对齐。 |
| erase_ratio_location | `--erase-ratio-location` | array<object{top_left_x:number, top_left_y:number, bottom_right_x:number, bottom_right_y:number}> | 否 | - | 擦除框数组。添加擦除框后，系统仅擦除框内文本。 子项说明：擦除框位置信息 CLI 传参时请使用 JSON 字符串，并用单引号包裹整个值，例如 `--erase-ratio-location '[{"top_left_x": 1.0, "top_left_y": 1.0, "bottom_right_x": 1.0, "bottom_right_y": 1.0}]'`。 |
| erase_ratio_location[].top_left_x | `--erase_ratio_location[].top_left_x` | number | 是 | - | 框选区域左上角相对于视频左上角在X轴上的偏移比例，取值范围为[0,1]，其中 0 表示无偏移（与视频左边缘对齐），1 表示完全偏移（与视频右边缘对齐）。 |
| erase_ratio_location[].top_left_y | `--erase_ratio_location[].top_left_y` | number | 是 | - | 框选区域左上角相对于视频左上角在 Y 轴上的偏移比例，取值范围为 [0,1]，其中 0 表示无偏移（与视频上边缘对齐），1 表示完全偏移（与视频下边缘对齐）。 |
| erase_ratio_location[].bottom_right_x | `--erase_ratio_location[].bottom_right_x` | number | 是 | - | 框选区域右下角相对于视频左上角在 X 轴上的偏移比例，取值范围为 [0,1]，其中 0 表示无偏移（与视频左边缘对齐），1 表示完全偏移（与视频右边缘对齐）。 |
| erase_ratio_location[].bottom_right_y | `--erase_ratio_location[].bottom_right_y` | number | 是 | - | 框选区域右下角相对于视频左上角在 Y 轴上的偏移比例，取值范围为 [0,1]，其中 0 表示无偏移（与视频上边缘对齐），1 表示完全偏移（与视频下边缘对齐）。 |
| callback_args | `--callback-args` | string | 否 | - | 可选，回调参数 |
| client_token | `--client-token` | string | 否 | - | 可选，用于幂等，默认幂等，用户可根据需求进行调整 |

## 调用示例
```bash
mediakit-cli video erase-video-subtitle-pro \
  --video-url https://example.com/video_url \
  --mode Subtitle \
  --output-encode-mode Quality \
  --erase-ratio-location '[{"top_left_x": 1.0, "top_left_y": 1.0, "bottom_right_x": 1.0, "bottom_right_y": 1.0}]' \
  --callback-args sample-callback-args \
  --client-token demo-client-token
```

## 输出格式
```json
{
  "task_id": "task_demo_001",
  "request_id": "req_demo_001"
}
```

## 任务结果查询
提交成功后会返回 `task_id`，再执行 `mediakit-cli shared query-task --task-id <task_id>` 查询。

- 当前命令：`mediakit-cli video erase-video-subtitle-pro`
- 推荐查询：`mediakit-cli shared query-task --task-id <task_id>`
