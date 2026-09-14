# 图像画质评估

## 能力用途

用于图像画质评估，对输入图片进行主客观画质和美学评分，适用于质量监控、低质图筛查、内容审核、推荐排序和训练数据清洗。

## 参数填写规则

- 提交一张公网可访问图片 URL，按 tool_version 选择标准版或专业版画质评估。 可选参数仅在用户明确指定，或可从用户意图准确确定时填写；不得伪造。不能准确确定时省略，确为正确完成任务所必需时先向用户澄清。
- 文档派生的 Cloud 公共请求字段只在用户明确提供时传递；不得由 Agent 生成、推断或补写。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli image evaluate-image-quality`
- 生命周期：同步
- 返回方式：直接返回 Cloud 业务结果。

### 使用指南

- 数组参数（`--standard-evaluate-items`）传多个值时用逗号分隔并整体加引号，例如 `--standard-evaluate-items "url1,url2"`。
- 单个值中的文件名或 URL 不能包含逗号（`,`），否则会被 CLI 当成多个元素拆开。遇到这种情况时，先向用户澄清，请其提供不含逗号的文件名或对应 URL 后再调用。

### 调用示例

```bash
MEDIAKIT_RUNTIME=<当前宿主> \
  mediakit-cli image evaluate-image-quality \
  --image-url <image_url>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `image_url` | `--image-url` | string | 是 | - | - | image_url 是待评估的图像 URL，支持公网 HTTP/HTTPS URL、本地文件路径和火山引擎对象存储 tos:// 三种输入协议，支持 png、jpeg、webp 和 heic 图像格式，单张图片不得超过 10 MB，图像输入分辨率的长边不得超过 7680 px，短边不得超过 4320 px。 |
| `queue_id` | `--queue-id` | string | 否 | - | - | 任务提交的目标队列 ID。如不传，默认使用系统自动创建的队列 ID。可将不同业务或优先级的任务提交到不同队列，以实现按队列对应的项目分账。队列可创建和管理，系统会自动为队列分配队列 ID。 仅在用户明确提供该值时传递；不得由 Agent 生成、推断或补写。 |
| `standard_evaluate_items` | `--standard-evaluate-items` | array<string> | 否 | ["vqscore","noise","aesthetic","blur"] | 元素枚举: ["vqscore","advcolor","blockiness","noise","aesthetic","blur","cg","contrast","texture","brightness","overexposure","hue","saturation","green","cmartifacts"] | standard_evaluate_items 为非必填参数，仅当 tool_version 为 standard 时生效，用于指定需要返回的标准版评估维度。standard_evaluate_items 可选 15 个评估维度：vqscore（图片主观质量，值越高表示质量越好）、advcolor（图片整体色彩质量）、blockiness（块效应（马赛克）严重程度）、noise（图片噪声强度）、aesthetic（综合大众美学的质量评分）、blur（模糊度）、cg（是否为非自然场景，如游戏、录屏）、contrast（对比度）、texture（纹理丰富程度）、brightness（平均亮度）、overexposure（过曝光程度）、hue（色调均衡程度）、saturation（饱和度均衡程度）、green（偏绿或绿幕检测）、cmartifacts（压缩失真检测）。standard_evaluate_items 为空时默认返回 vqscore、noise、aesthetic、blur 四个维度。 CLI 传参时可使用逗号分隔多个值，或重复传递该 flag；不要传 JSON 数组字符串。 |
| `tool_version` | `--tool-version` | string | 否 | "standard" | 枚举: ["standard","professional"] | tool_version 用于选择画质评估所用的模型版本，为非必填参数，支持 standard 和 professional，默认为 standard。standard 提供 15 种基础画质评估维度，可通过 standard_evaluate_items 灵活选择部分或全部维度，在成本和功能灵活性上达到较好的平衡。professional 基于大模型进行评估，直接返回一组固定的综合性评分，提供更优的综合评估效果，适用于对图像品质要求较高的场景，且不支持自定义评估维度。 |

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `advcolor` | number | 否 | Cloud | standard 的 advcolor 表示图片整体色彩质量，值越高表示色彩质量越高，取值范围为 0 到 100：[0, 50] 表示色彩质量差，[50, 60] 表示中，[60, 100] 表示好。 |
| `aesthetic` | number | 否 | Cloud | standard 的 aesthetic 表示综合大众美学的质量评分，值越高表示更具美感，取值范围为 0 到 100。 |
| `aesthetics` | number | 否 | Cloud | professional 的 aesthetics 表示美学评分，评分越高，图像越“好看”，构图、色彩、风格越协调，取值范围为 0 到 100，支持两位小数。 |
| `artifacts` | number | 否 | Cloud | professional 的 artifacts 表示伪影评分，即图像是否存在压缩、AI 生成痕迹、畸变等；评分越高，伪影越少，图像越自然，取值范围为 0 到 100，支持两位小数。 |
| `blockiness` | number | 否 | Cloud | standard 的 blockiness 表示图片的块效应严重程度，值越高图片块效应越强，[0, 50] 表示差，[50, 60] 表示中，[60, 100] 表示好，-1 表示检测图像为非常规图像（如游戏、特效图等）。 |
| `blur` | number | 否 | Cloud | standard 和 professional 的 blur 都表示模糊评分，即图像是否清晰；评分越高，图像越清晰和锐利，取值范围为 0 到 100，支持两位小数。 |
| `brightness` | number | 否 | Cloud | standard 的 brightness 表示平均亮度，值越高表示越亮，取值范围为 0 到 255。 |
| `cg` | number | 否 | Cloud | standard 的 cg 取值范围为 0 到 100，数值接近 0 表示自然场景，接近 100 表示非自然场景（游戏、录屏等）。 |
| `cmartifacts` | number | 否 | Cloud | standard 的 cmartifacts 表示压缩失真强度，分数越高表示压缩失真越显著、画质越差，取值范围为 0 到 100：[0, 30) 表示无或轻微压缩失真，[30, 60) 表示存在压缩失真，[60, 100] 表示存在明显噪声。 |
| `contrast` | number | 否 | Cloud | standard 的 contrast 表示对比度程度，值越低表示对比度越低，取值范围为 0 到 100。 |
| `green` | number | 否 | Cloud | standard 的 green 表示图像绿色区域面积大小；数值越大，绿色区域面积越大，是绿幕的概率越大，取值范围为 0 到 255。 |
| `hue` | number | 否 | Cloud | standard 的 hue 表示色调的均衡程度，值越高表示色调越均衡，取值范围为 0 到 100。 |
| `noise` | number | 否 | Cloud | standard 和 professional 的 noise 都表示噪声评分，即图像中是否存在颗粒感或随机噪声；评分越高，图像越干净，取值范围为 0 到 100，支持两位小数。 |
| `overall` | number | 否 | Cloud | professional 的 overall 表示综合以上指标的总评分，评分越高，图像画质越好，取值范围为 0 到 100，支持两位小数。 |
| `overexposure` | number | 否 | Cloud | standard 的 overexposure 表示过曝光面积大小程度，值越高越可能存在过曝光，取值范围为 0 到 100。 |
| `saturation` | number | 否 | Cloud | standard 的 saturation 表示饱和度的均衡程度，值越高表示饱和度越均衡，取值范围为 0 到 100。 |
| `texture` | number | 否 | Cloud | standard 的 texture 表示纹理的丰富程度，值越高表示纹理越丰富，取值范围为 0 到 255。 |
| `tool_version` | string | 否 | Cloud | result.tool_version 在 standard 结果中固定为 standard，在 professional 结果中固定为 professional。 |
| `vqscore` | number | 否 | Cloud | standard 的 vqscore 表示图片主观质量，值越高表示质量越好，取值范围为 0 到 100。 |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli image evaluate-image-quality --help
mediakit-cli image evaluate-image-quality --schema
```
