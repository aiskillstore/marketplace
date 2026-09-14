[![中文](https://img.shields.io/badge/%E4%B8%AD%E6%96%87-a02128?style=for-the-badge)](README.md)
[![English](https://img.shields.io/badge/English-ece9e7?style=for-the-badge&labelColor=ece9e7&color=8a8785)](README.en.md)

# video-sync

把 [video-shots](../video-shots/) 的拉片数据和原片合成一条**能直接看的视频**：
一边是画面，一边是这一镜的分镜信息，**镜头切了信息跟着切**，镜头表自动滚动并高亮当前这一镜。

## 版式只看宽高比

| 原片 | 版式 | |
| --- | --- | --- |
| 横版（宽 > 高）、方版 | **画面在上，信息在下** | `vstack` |
| 竖版（高 > 宽） | **画面在左，信息在右** | `hstack` |

竖版的样子——输出是 1580×1080 的近似 3:2，不是把竖片硬塞进 16:9 两边填黑：

<img src="assets/output-portrait.png" width="620" alt="左右版式">

两个方向都保证**画面原样缩放、不裁不拉**，面板补足剩下的画布。所有边长取偶数（h264 的要求），
面板最短边不低于 260px（再小字就放不下）。

默认**只缩不放**。但面板是跟着画面区算的，原片太小面板也跟着小——640×360 的片子面板只有
640×288，四列谁也读不了。这种时候 `--scale 2` 把画面区放到 1280×720、面板放到 1280×576，
宽高比一分不动。详见 [`references/layout.md`](references/layout.md)。

## 只截三张图，动的部分交给 ffmpeg

面板上会变的只有两样：**滚到哪**、**哪一行亮**。所以既不逐帧截图，也不一个镜头截一张：

```
量一次  每行的位置、列表视窗、整张表的高（浏览器量，脚本推不出来）
截三张  底板（表头+进度条）、整张表压暗的长图、整张表全亮的长图
合成    暗底长图裁一个视窗 → 滚动；亮条长图裁一行 → 高亮
```

53 镜的片子截图从 53 次降到 3 次（12 秒），换来的是**真正的连续动画**。

**当前镜头钉在第二行**：第 1、2 镜列表不动（高亮往下挪一行），**第 3 镜起每切一次往上滚一行**。
切点处滚 0.45 秒到位就停住——长镜头里一直爬只会晃眼。高亮条和视窗同一段缓动，一起滑过去。

行高**由内容决定**（描述长的行就高）。高亮条因此按行高分层：`crop` 的高度改不动，
所以出现几种行高就建几层，没轮到的挪到画面外。

四个踩过的坑写在 [`references/layout.md`](references/layout.md) 里：
`drawbox` 的表达式只在初始化时算一次（动不了）；把整片拼成一条大表达式，
ffmpeg 的解析器在一百来项上直接配置失败（所以改用 `sendcmd`，每镜一条小命令）；
裁窗口的 x 要和盖回去的 x 是同一个值（不然整张表右移一个缩进、右边的字被啃掉）；
没轮到的高亮条要停到**整块面板**之外（只躲开视窗的话会露在进度条上）。

## 布局你随便改

面板是一张 HTML 页面，**长相全在 [`scripts/panel.css`](scripts/panel.css) 里**——
改它就能改版式，不用碰脚本，也不用重新想截图逻辑。改完重跑 `panels` 就是新版面。

| | |
| --- | --- |
| <img src="assets/panel-landscape.png" width="440"> | <img src="assets/panel-portrait.png" width="200"> |
| 横版面板：表头 + 四格（镜号时间景别运镜 / 画面 / 画面描述 / 节奏分析） | 竖版面板：同样四格，窄而高 |

`panels` 还会顺手写一张 `panels/panel.html`——**浏览器打开就能预览**，地址后加 `#S07` 换镜头。
两种版式共用同一份 DOM，靠 `.panel` 上的 `.landscape` / `.portrait` 切 grid，
不写第二份模板也就不会改了一边忘了另一边。约定见 [`references/panel-style.md`](references/panel-style.md)。

字号跟着面板尺寸走（`base = clamp(12, min(宽/38, 高/26), 26)`），所以 CSS 里**一律用 rem**——
导出的是视频，屏幕上舒服的 13px 在手机上播就是一团糊。

## 用法

```bash
# 0. 先有 video-shots 的产出：shots.json（+ frames/ 当缩略图）

# 1. 只算几何，不动视频（几秒出结果，先确认尺寸再往下走）
node scripts/video-sync.mjs plan shots.json --video clip.mp4

# 2. 渲面板：三张图 + 一张可预览的 panel.html
node scripts/video-sync.mjs panels shots.json --video clip.mp4 --frames frames --lang zh

# 3. 合成（音轨照搬原片）
node scripts/video-sync.mjs compose shots.json --video clip.mp4 -o out.mp4

# 或者一条龙
node scripts/video-sync.mjs export shots.json --video clip.mp4 --frames frames -o out.mp4
```

调版式：`--panel <比例>`（横版是面板高÷画面高，默认 0.8；竖版是面板宽÷画面宽，默认 1.6）、
`--scale <倍数>`（画面区放大几倍，默认 1 = 只缩不放；小素材靠它把面板撑开）、
`--width` / `--height`（画面区上限）、`--crf`（质量）、`--ease`（切点缓动秒数）、
`--anchor`（当前镜头钉第几行，默认 1 = 第二行）、`--lang zh|en`。

依赖：`node` >= 18（只用标准库）+ `ffmpeg` / `ffprobe` + 一个无头浏览器
（Chrome / Chromium / Edge，`--chrome` 可指路径）。**零 npm 依赖、零 API key。**

## 验收不能只看「没报错」

合成完至少抽三帧，看**画面属于哪一镜、面板上的镜号是不是同一个、高亮行有没有跟着走**：

```bash
for t in 5 30 60; do ffmpeg -v error -y -ss $t -i out.mp4 -frames:v 1 -q:v 3 /tmp/check-$t.jpg; done
```

对不上通常是 shots.json 和原片不是同一条。

## 自测

```bash
node scripts/selftest.mjs
# ✅ 122 项断言全部通过
```

不碰 ffmpeg、不开浏览器，查的是：几何（横/方/竖、偶数边长、上下限、旋钮、读不出宽高就报错）、
面板页面的数据契约（词表与节奏角色下发中文名而不是枚举键、缩略图有才给、`<script>` 转义）、
动画命令（每条都必须短、长镜头滚完就夹住、`--ease` 生效）、
ffmpeg 参数（vstack/hstack、`setsar=1`、三张静态图都要 `-loop`、无声片不接音轨、原片必须是 0 号输入）。

## 和 video-shots 的关系

```
video-shots  →  shots.json + frames/  →  video-sync  →  out.mp4
（拉片：镜头拆解与标注）                  （合成：画面 + 信息）
```

**两个 skill 各自独立**：四张词表在这边**自带一份**，不跨目录 import——skill 要能整个拷走。
代价是 `video-shots` 那边加了新词，这边也要加一次，否则显示成枚举键。

## 成片长这样

287.4 秒的英文片段 + 46 镜分镜信息，1280×1296（原片 640×360，`--scale 2` 放大）。
镜头切了信息跟着切，列表往上滚、高亮跟着滑：

<video src="https://github.com/eternityspring/reelbench-skills/raw/main/demo-sync/demo-en-sync.mp4" controls muted playsinline width="760"></video>

播放器没出来就直接下载：[`demo-sync/demo-en-sync.mp4`](../../demo-sync/demo-en-sync.mp4)
