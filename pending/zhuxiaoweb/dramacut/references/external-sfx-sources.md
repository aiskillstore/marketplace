# 外部音效来源与候选补库

本包不宣称掌握抖音/TikTok使用频率排行榜。按短剧情节需要整理的工作类型是：物理接触、快速运动、意识轻点、低压/心沉、揭晓、决定/关心、电子通知、记忆入口与片尾疑点。用 [事件表](sfx-library.md) 判断是否适配，网络热梗不是选声依据。

## 已实际取得并随包保存

2026-11-19 从 Kenney 官方下载入口获取 Impact Sounds 1.0 与 Interface Sounds 1.0，压缩包内均有 Creative Commons Zero 许可。筛出30个候选转为整数PCM，未做增益、未声称已试听。来源、原成员/压缩包/转码后 SHA、用途和不适用场景逐项写在 `assets/sfx-foley/manifest.json`；原 `License.txt` 以包名保存。原站下载链接为临时签名链接，复取时从资产页重新获取，不固化过期直链。

- 官方 Impact Sounds：`https://kenney.nl/assets/impact-sounds`
- 官方 Interface Sounds：`https://kenney.nl/assets/interface-sounds`
- CC0 说明：`https://creativecommons.org/publicdomain/zero/1.0/`

30个候选补充脚步、材质碰撞与设备反馈；24个原创合成cue补充情绪和叙事变化。同一声色避免连续覆盖不同情绪。手机听不清低频时优先比较中频轻敲/短冲击，不先增大低音峰值。

## 需要特定拟音时

优先保留原素材的门、衣物、脚步、纸张和接触声。内置无匹配时查用户库/剪映素材，再查可追溯外部条目。Freesound官方FAQ说明素材逐条采用不同许可；搜索结果不能被笼统视为可商用或可打包。查单条作者、原页、许可和实际文件SHA；需要署名的保留署名，不能确认许可的仅列候选链接，不混入skill资产。

- Freesound官方FAQ：`https://freesound.org/help/faq/`
- 检索词：`paper rustle single`、`door latch close`、`cloth movement`、`glass set down`、`phone notification`、`cinematic sting`、`short whoosh`。

“用于视频”与“把原文件装进可分发skill包”分别核对。本次没有收录从剧集、短视频或平台热梗中抽出的声音，也没有打包未核实再分发条件的素材站文件。查询下载失败时保留具体失败，不自动换来源不明镜像。
