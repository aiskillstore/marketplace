# 轻抖文案提取 API

仅在执行失败、需要理解接口兼容逻辑或维护脚本时读取。

## 限制

- 默认任务并发路数：1。
- 创建任务后需要轮询获取结果。

## 创建任务

- 请求：`POST https://www.qingdou.vip/web/api/commitGetTextTask`
- Header：`x-api-key: {API Key}`、`Content-Type: application/json`
- Body：`userInputList`

用户提供的文档出现两种 Body 形式：

```json
{"userInputList":"完整分享文案或视频链接"}
```

```json
{"userInputList":[{"numberIndex":0,"url":"完整分享文案或视频链接"}]}
```

脚本优先使用字符串形式；仅在业务状态 `4001` 时改用数组形式重试。

成功状态为 `status.code = 1001`。文档中的 `result` 既出现过数字 `batchId`，也出现过包含 `batchId` 的对象；脚本兼容两种形式。

## 获取结果

- 请求：`GET https://www.qingdou.vip/web/api/getTaskResult?batchId={batchId}`
- Header：`x-api-key: {API Key}`
- `batchStatus = 0` 或 `1`：处理中。
- `batchStatus = 2`：批任务结束。

成功条目包含：

- `originLink`：原始链接；
- `platformName`：平台；
- `awemeId`：视频 ID；
- `status`：条目状态；
- `videoTitle`：视频标题；
- `videoContent`：识别文字；
- `videoCover`：封面链接；
- `videoTime`：视频时长。

用户提供的返回样例没有作者字段。脚本兼容 `authorName`、`author_name`、`authorNickname`、`nickname`、`userName`、`accountName`，以及 `author`、`user`、`owner` 对象中的对应字段。没有明确字段时归入 `_未识别作者`。

## 状态码

### 接口状态

| 状态 | 含义 |
| --- | --- |
| `1001` | 请求成功 |
| `4001` | 参数错误 |
| `4100` | API Key 异常 |

### 条目状态

| 状态 | 含义 |
| --- | --- |
| `0` | 处理中 |
| `1000` | 文案提取成功 |
| `1001` | 获取视频唯一状态码失败 |
| `1010` | 链接获取失败 |
| `1011` | QPS 上限 |
| `1100` | 视频链接为空 |
| `1101` | 视频结果获取失败 |
| `1110` | 文案提取错误 |
| `1111` | 其他错误 |
| `1112` | 视频过大或视频不是 MP4 |
| `1113` | 用户资源不足 |
| `1114` | 视频时长获取失败或时长为 0 |
| `1115` | 获取链接信息失败 |
| `1116` | 预扣费异常 |
| `1117` | 获取视频链接异常 |
| `1118` | 超时失败 |
