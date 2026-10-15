# 托管素材与安装体积

v1.2 的公开手部 PNG、合成音色参考/试听 WAV、21 张画风预览以及 README 展示图片与视频放在本仓库 GitHub Release 附件，代码包只保留清单和校验值。原片女声录音、提取的人声、用户个人音色目录不公开上传。

`assets/hosted-manifest.json` 固定每个素材的 URL、字节数和 SHA-256。默认缓存为 `~/.cache/sweety-handdraw-video`，可用 `HANDDRAW_ASSET_CACHE` 指定；缓存以内容哈希隔离。首次使用需要网络，校验成功才写入缓存；`HANDDRAW_OFFLINE=1` 仅复用有效缓存，缺失或损坏会明确报错。不会退回另一张图或另一种声音。

```bash
python scripts/hosted_assets.py --all
HANDDRAW_OFFLINE=1 python scripts/hosted_assets.py assets/hands/pen-only.png
```

画风配方沿用上游 `hand-drawn-styles` 提交 `4132988b8596bfa36321c970a4472d4e3bb25d96`，该版本本身已经是轻量文本版本。移除的是本项目额外打包的 21 张预览图。上游五张运行参考图补充 GitHub 镜像；其中三张含来源或模拟相机字段，已清理并逐像素确认无变化，清单另存上游字节校验值以便追溯。镜像使用清理后的大小与 SHA-256，原地址不可用或校验不匹配时尝试镜像。配方、锚点像素与生产验收规则没有简化。

2026-10-13 检查到指定 Netlify 团队额度耗尽，项目与部署暂停；用户确认先使用 GitHub。后续迁移到 Netlify 时，必须取得当前生产站点完整文件，合并独立的 `sweety-handdraw-video/` 目录，禁止用新增素材覆盖整个已有站点。上传后逐项匿名下载比对大小和 SHA-256，通过后再更新链接；保留 GitHub 镜像便于回退。本次未执行 Netlify 部署。

第三方导演和动效依赖的运行代码、字体与资源仍按锁定版本保留。减小当前代码包不等于清理 Git 历史；没有改写历史提交。
