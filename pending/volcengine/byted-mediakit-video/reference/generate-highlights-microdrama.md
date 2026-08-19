# 高光智剪-短剧

## 能力描述
深度理解短剧角色、剧情与故事线，自动提取高光片段并混剪成投流视频。
支持故事线混剪模式（StorylineCuts），可选"短剧三要素"视觉模板，输出高光集锦、单集预告等。
支持输出详细分镜信息（storyboard）。
使用限制：单次最多 100 个视频，累计时长不超过 300 分钟。

## 执行方式

| 项目 | 说明 |
|------|------|
| Domain | `video` |
| Tool | `generate-highlights-microdrama` |
| 是否异步 | `是` |
| 是否支持 local | `否` |
| 模式说明 | cloud only；可通过 `--cloud` 强制当前调用 |
| 幂等行为 | 如命令支持 `client_token` 与 `callback_args`，重试时复用同一组值；强制重跑时更换新的 `client_token` |

## 参数
| 参数 | CLI flag | 类型 | 必填 | 默认值 | 说明 |
|------|----------|------|------|--------|------|
| video_urls | `--video-urls` | array<string> | 是 | - | 输入视频列表。待处理的短剧原片视频 URL 列表，支持 1-100 个视频。子项说明：视频 URL，CLI 传参时请使用 JSON 字符串，并用单引号包裹整个值。 CLI 传参时请使用 JSON 字符串，并用单引号包裹整个值 |
| mode | `--mode` | string | 否 | StorylineCuts | 短剧高光智剪模式，本期固定为 StorylineCuts（故事线混剪模式） |
| enable_generate_video | `--enable-generate-video` | boolean | 否 | true | 是否生成混剪成片视频。true（默认）= 同时输出混剪视频与分镜信息；false = 仅输出高光分镜信息，不生成混剪视频，此时底层请求不会携带 Edit 字段，且传入的 edit_param 将被忽略 |
| enable_return_poster | `--enable-return-poster` | boolean | 否 | false | 是否在结果中返回混剪视频封面图 URL。false（默认）= 不返回封面图；true = 若底层存在封面则返回 poster_url |
| edit_param | `--edit-param` | object | 否 | - | 成片剪辑参数配置。CLI 传参时请使用 JSON 字符串，并用单引号包裹整个值 |
| highlight_cuts_param | `--highlight-cuts-param` | object | 否 | - | 高光混剪参数配置。CLI 传参时请使用 JSON 字符串，并用单引号包裹整个值 |
| opening_hook_param | `--opening-hook-param` | object | 否 | - | 精彩前置功能参数配置（可选）。CLI 传参时请使用 JSON 字符串，并用单引号包裹整个值 |
| callback_args | `--callback-args` | string | 否 | - | 可选，回调参数 |
| client_token | `--client-token` | string | 否 | - | 可选，用于幂等，默认幂等，用户可根据需求进行调整 |

## 调用示例
```bash
mediakit-cli video generate-highlights-microdrama \
  --video-urls '["https://example.com/video_url"]' \
  --mode StorylineCuts \
  --enable-generate-video \
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

- 当前命令：`mediakit-cli video generate-highlights-microdrama`
- 推荐查询：`mediakit-cli shared query-task --task-id <task_id>`
