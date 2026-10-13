# 运行格式与命令

任务目录包含 `job.json`、模型编写的 `design.json`、`design/art-direction.json`、`inputs/`、`work/` 和 `outputs/`。`review.json` 由 verify 初始化，执行者实际检查后填写。脚本不代替模型写内容、选路线或设计素材。

## 最小字段示例

以下只是格式说明；须先生成、检查、清理图片，写入有效美术记录并锁定完整旁白和时间戳后才能运行。

```json
{
  "version": 1,
  "title": "本次主题",
  "design_file": "design.json",
  "art_direction": {"record": "design/art-direction.json"},
  "canvas": {"width": 1920, "height": 1080, "fps": 30},
  "cover": {"source": "inputs/cover.png", "seconds": 1.0},
  "hand": {"preset": "navy", "pen_text": ""},
  "voice_studio": {"voice": "iapetus"},
  "narration": {"source": "inputs/narration/master.wav", "alignment": "inputs/narration/alignment.json"},
  "audio": {"end_hold_seconds": 0.45},
  "pages": [{"beats": [{
    "id": "opening",
    "text": "与音频逐字对应的讲解。",
    "actions": [
      {"type": "text", "text": "本段短标题", "x": 120, "y": 60, "size": 80},
      {"type": "illustration", "source": "inputs/object.png", "x": 200, "y": 230,
       "width": 680, "height": 580, "weight": 3,
       "parts": [{"id": "single_object", "polygon": [[0,0],[1,0],[1,1],[0,1]]}]}
    ]
  }]}]
}
```

单一部位示例只适用于一个简单物体。人物必须根据实际图像划出头、颈、躯干、左右臂、下半身等有语义的部位，不能用整图一个矩形敷衍。

## 设计和图片记录

`design.json` 必须有 `narrative_route.decision/reason/director_review`。默认路线 decision 为 `default_life_concept`；其他路线还要有 `director_plan`，记录 omniailab 的具体导演规划。完整内容字段见 [创作与分镜](story-design.md)。

美术记录格式：

```json
{
  "dependency_sha256": "随包美术指导 GUIDE.md 的实际 SHA-256",
  "images": [{
    "source": "../inputs/object.png",
    "sha256": "清理后文件的实际 SHA-256",
    "method": "generated_under_guidance",
    "brief_file": "briefs/object.md",
    "brief_sha256": "出图前简报文件的实际 SHA-256",
    "prompt_file": "prompts/object.txt",
    "prompt_sha256": "本次实际完整提示词文件的 SHA-256",
    "status": "pass",
    "evidence": "实际查看后的主体、接触、构图、边缘和可绘制性判断"
  }]
}
```

所有路径相对记录文件。封面、正文源图、自定义手均要覆盖；包内六款手有自己的记录。合成封面 method 为 `composed_with_verified_layers`，保存可编辑文字图层说明。图集用 `approved_crops` 数组列出已查看的像素裁切，每项是 `[left,top,right,bottom]`；未批准格子不能参与成片。更换图像后旧哈希失效，必须重新检查。提示词文件存在不是“指导已经执行”的充分证据。

## 绘制和时序

- `text`：`text/x/y/size/color/weight`，一行一项。每个字形在独立区域内描线，后字不会提前露出。默认近似字形路径，不保证规范书法笔顺。图层按各字真实边界计算，并保留至少5px空白；禁止用字号估算高度。
- `marker`：`style` 为 `highlight/underline/circle/box`，使用 `width/height/color/line_width`。
- `illustration`：`source/x/y/width/height`，可设像素裁切 `crop`。保持比例缩入框。
- `parts`：有序数组，唯一 `id` 与归一化 `polygon` 坐标。坐标相对裁切后的图。区域重叠时先声明者拥有像素；所有可见像素必须有归属。模型看图后确定边界，避免切碎手指、轮廓或道具。轮廓按数组顺序完成全部部位，再按同一顺序填色。笔划间抬笔。
- 前景手臂、持物或其他遮挡可用 `exclude_polygons` 给出归一化排除多边形数组；从头部或躯干排除的像素必须由后续正确部位接管。不要因为手臂横过胸前就让它在躯干阶段提前显现。
- 复杂遮挡可用部位的 `exclude_hsv:[[hue_min,hue_max,saturation_min,value_min]]` 排除透过发丝等空隙可见的背景颜色（色相0—360，饱和度/亮度0—1）。排除的像素必须由后续正确部位接管，需实际看图验证，不能仅以颜色自动推断语义。
- `weight` 只分配对应音频窗口里的绘制时间，不是秒数。所有元素可设 `z`；底纹默认位于文字下面。

跨多句的一个完整画面可以使用页面 `visual_groups`，每组为 `{"start_beat":0,"end_beat":2,"lead":0.54,"hold":0.72,"actions":[...]}`，索引从0开始。此时 beats 中的 actions 可以为空或省略。起止索引必须有序且在该页范围内，lead 非负，hold 至少0.45秒；多个组不能造成主笔事件重叠。不要给每句机械安排一幅新图。

生产任务必须使用 `narration.source/alignment` 指定完整旁白母带和对应时间戳，字段见[连续旁白约定](continuous-narration.md)。`audio.end_hold_seconds` 只控制整篇声音结束后的画面停留；生产任务拒绝非零 `sentence_pause_seconds/page_pause_seconds`、`pace` 非1和 `trim_silence:true`。绘制窗口太短则简化画面或合并绘制窗口，不能截短呼吸、插入空白或拉慢旁白来容纳画面。封面只接受1秒，前半秒静止、后半秒渐隐，正文和旁白从1秒后开始。

## 手、字体和字幕

六款手臂及仅画笔的 `hand.preset` 标识见 `assets/hands/catalog.json`。未选时使用模型根据内容准备的默认方案。`pen_text` 最多16个字符，这是格式上限。保留用户原文，按正常视频尺寸检查可读性；必要时调整笔杆排版，不擅自缩写广告名称。`pen_text_color` 可选。自定义手设置 `source/nib/wrist/label_segment/label_height`，提供实测锚点，源图前臂须延伸到底边；运行时自动限制最小尺度，使裁切边留在画外。新手图须同样经过美术指导和隐私清理。

`font` 为 `{"path":"/actual/font.ttc","index":2}`。字幕按[字幕与片尾设计](subtitle-design.md)由模型独立决定。`captions` 支持 `font:{path,index}/font_size/color/bottom_margin/max_width_ratio/max_lines/stroke_width/stroke_color`，`background:null` 不生成底板；可选 `background:{color,opacity}` 轻度底板；不继承顶层手写字体。优先单行，最多两行。beat 可增加 `caption_cues:[{"text":"完整短句。","start":0,"end":2.5}]`，秒数相对母带对应 beat 的开始时间；生产字幕时间写在 alignment 对应 beat 中，所有文本拼接须与 beat 文本逐字一致；不需要为字幕重新生成或切割语音。字幕作为静态排字显示，不执行主笔描写。`paper` 为十六进制颜色。默认管线适合白底或透明底的清晰线稿，不保证复杂深色背景自动分离成功。

可用 `ending:{"fade_seconds":0.6}` 指定片尾渐隐到纸色；渐隐须完全位于最后一句结束后的停留区间内。`audio.end_hold_seconds` 默认0.45秒、范围0.2—0.8秒，默认不渐隐。总尾部静音不得超过1.2秒；详见[声音与收尾硬约束](audio-and-ending.md)。

## 命令

替换实际路径后运行：

```bash
python3 /path/to/skill/scripts/voice_studio.py /path/to/job --transcribe
python3 /path/to/skill/scripts/handdraw_video.py doctor /path/to/job
python3 /path/to/skill/scripts/handdraw_video.py build /path/to/job
python3 /path/to/skill/scripts/handdraw_video.py verify /path/to/job --assets-only
python3 /path/to/skill/scripts/handdraw_video.py render /path/to/job --preview --duration 15
python3 /path/to/skill/scripts/handdraw_video.py render /path/to/job
python3 /path/to/skill/scripts/handdraw_video.py verify /path/to/job
```

`doctor`中的 `ready` 表示已有任务输入可合成；`voice_studio.available` 单独表示新旁白服务是否可用，二者不能混用。

先实际查看短段再导出整片。verify 完整解码并生成成片抽帧，只代表工程检查。按 [检查与返工](quality-gates.md) 填写检查证据后，才运行 `finalize`。它会拒绝未检查记录、哈希过期和运行测试夹具。

输出 `film.mp4/cover.png/captions.srt/script.txt/verification.json/verification.txt`。另存中文名时保留原件与哈希。脚本、图片、音频、设计或布局变化均需重渲染和复核。`runtime_fixture:true` 仅供包内离线测试，永远不能生成成片交付回执。

## 画风与绘制计划门槛

生产任务必须完成[画风选择与可绘制约定](style-and-drawing.md)。`job.json` 增加 `drawing_plan`、`drawing_review`；每个插画 action 增加 `drawing_plan_id`，需要独立轮廓时增加 `outline_mask`。旧任务不能直接绕过新门槛。

## v1.2 可选制作设置

开始时按[可选制作设置](production-options.md)收集偏好。`hand.preset` 新增 `pen-only`，只显示完整画笔，不套用前臂长度规则。`hand.pen_text` 上限为16个字符。字幕可设 `background:{"color":"#243039","opacity":0.76}` 并配白字；空背景仍可用。上述新约定替代旧示例中的20字符与固定无背景。

`watermark:{"text":"用户原文，可换行","opacity":0.24}` 添加低对比、缓慢浮动水印；不配置或空文字不加。默认1080p约27px，可指定 `font/color/font_size`，不透明度上限0.35。固定封面静止阶段不漂移，从1秒正文开始显示，位置始终在画内并避开底部字幕。

`ending.caption_hold_seconds` 可延长最后一句的阅读停留；必须小于或等于末句后停留减去渐隐的时间。字幕文字不变，SRT和实际画面一起延长。

## v1.3 整篇声音主时间线

旧生产任务先按连续旁白约定迁移，不能仅把旧分段文件拼接后声称已解决语调断裂。`runtime_fixture:true` 保留分段合成只为离线测试，永远不能作为交付路径。

字幕交付使用单一烧录层。`timeline.captions` 固定为 `{"presentation":"burned","owner":"caption_events"}`；额外字幕事件、字幕轨和成片同目录的字幕文件均拒绝交付。

v1.2.1 起简报和提示词必须非空且与绑定哈希一致。调用图像工具前运行 `python scripts/art_direction.py bind-evidence design/art-direction.json`；该命令不会把图片标记为通过。封面、正文、角色、道具、自定义手部和所有候选/编辑遵守同一流程。
