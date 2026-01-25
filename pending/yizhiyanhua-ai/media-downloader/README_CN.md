# 🎬 智能媒体下载器

> 根据你的描述自动搜索和下载图片、视频片段，支持视频自动剪辑。

[🇬🇧 English](./README.md)

---

## 🚀 我能帮你做什么？

| 你说... | 我会... |
|---------|---------|
| "下载一些可爱的猫咪图片" | 搜索并下载 5 张猫咪图片 |
| "找一段海浪的视频，15秒左右" | 下载一段 15 秒的海浪视频 |
| "下载一段 30 秒的烹饪视频" | 下载并剪辑烹饪视频 |
| "下载这个 YouTube 视频的 1:30-2:00" | 下载并自动剪辑指定片段 |

---

## ✨ 功能特点

- 🖼️ **图片下载** - 从专业图库搜索高清图片
- 🎬 **视频素材** - 获取免费商用视频片段
- 📺 **YouTube 下载** - 支持下载和剪辑
- ✂️ **智能剪辑** - 自动裁剪到你需要的长度
- 🌍 **中英双语** - 支持中文和英文指令

---

## ⚡ 一句话安装

在 Claude Code 中对 Claude 说：

> **"帮我安装 https://github.com/yizhiyanhua-ai/media-downloader.git 这个 skill 和它的所有依赖"**

Claude 会自动完成：
- 下载 skill 到正确位置
- 安装 yt-dlp、ffmpeg 等依赖工具
- 检查安装状态

你只需要在 Claude 询问时点击「允许」就行了！

---

## 🔑 配置 API Key（下载图片需要）

> 💡 **注意**：如果你只需要下载 YouTube 视频，可以跳过这一步！

图片下载需要一个免费的 API Key（就像图库网站的「会员卡」）：

1. 打开 **https://www.pexels.com**，点击 **Join** 注册（支持 Google/Apple 一键注册）
2. 注册后访问 **https://www.pexels.com/api/**，点击 **Your API Key**
3. 复制显示的密钥，然后对 Claude 说：**"帮我把 Pexels API Key 保存到环境变量"**

完成后对 Claude 说 **"检查一下 media-downloader 的状态"** 确认一切正常。

---

## 📋 更多图库 API Key（可选）

> 💡 **为什么需要 API Key？**
>
> 简单来说，API Key 就像是图库网站给你的「会员卡」。有了它，你就能搜索和下载高清图片和视频。
>
> **好消息**：注册完全免费，下载的素材也可以免费商用！

上面的快速安装只配置了 Pexels。如果你想要更多图片来源，可以再注册这些：

### 🟢 Pixabay（更多素材选择）

1. 打开 **https://pixabay.com**
2. 点击右上角 **Join** 注册
3. 注册后访问 **https://pixabay.com/api/docs/**
4. 页面上会直接显示你的 API Key（绿色框里）
5. 对 Claude 说：**"帮我把 Pixabay API Key 保存到环境变量"**，然后粘贴你的 Key

### 🔵 Unsplash（艺术感更强的图片）

1. 打开 **https://unsplash.com/developers**
2. 点击 **Register as a developer**
3. 创建一个 Application（随便填个名字就行）
4. 找到 **Access Key** 并复制
5. 对 Claude 说：**"帮我把 Unsplash API Key 保存到环境变量"**

### 🔧 遇到问题？

对 Claude 说：**"检查一下 media-downloader 的状态"**

Claude 会告诉你哪些工具已安装、哪些 API Key 已配置。缺什么就补什么！

---

## 💬 使用示例

> ⚠️ **重要提示**：使用前请先对 Claude 说 **"检查一下 media-downloader 的状态"**，确保所有依赖工具已安装完成！

### 下载图片

```
"帮我下载 5 张星空的图片"
"下载 10 张咖啡店的照片"
"找一些适合做壁纸的风景图"
```

### 下载视频素材

> 💡 **推荐**：如果你需要下载视频，**优先使用 YouTube**！YouTube 视频内容丰富、质量高，而且不需要额外的 API Key。

```
"下载这个视频：https://youtube.com/watch?v=xxx"
"下载这个 YouTube 视频的第 2 分钟到第 3 分钟"
"只下载这个视频的音频"
```

如果你需要从素材库下载短视频片段：

```
"下载一段城市夜景的视频，30秒以内"
"找一段 15 秒的海浪视频"
"找一些适合做背景的自然风光视频"
```

---

## 📁 下载位置

所有文件默认保存在：

```
~/.claude/skills/media-downloader/downloads/
```

### 自定义下载目录

你可以使用 `-o` 或 `--output` 参数指定下载位置：

```bash
# 下载图片到指定文件夹
media_cli.py image "猫咪" -o ~/Pictures/cats

# 下载视频到桌面
media_cli.py video "日落" -o ~/Desktop

# 下载 YouTube 视频到当前目录
media_cli.py youtube "URL" -o .
```

或者直接告诉我你想保存到哪里：

```
"下载 5 张猫咪图片到桌面"
"把视频保存到 ~/Videos/project 文件夹"
```

---

## ❓ 常见问题

### Q: 为什么搜索图片没有结果？
A: 请确认已配置 API Key。运行 `status` 命令检查配置状态。

### Q: YouTube 视频下载失败？
A: YouTube 下载不需要 API Key，但需要安装 yt-dlp。运行 `pip install yt-dlp` 安装。

### Q: 视频剪辑功能不工作？
A: 需要安装 ffmpeg。macOS 用户运行 `brew install ffmpeg`。

### Q: 这些图片/视频可以商用吗？
A: Pexels、Pixabay、Unsplash 的素材都可以免费商用，无需署名（但署名是一种礼貌）。

---

## 🛠️ CLI 命令参考

供高级用户直接使用命令行：

```bash
# 检查配置状态
media_cli.py status

# 下载图片
media_cli.py image "关键词" -n 数量 -o 输出目录

# 下载视频素材
media_cli.py video "关键词" -d 最大时长 -n 数量

# 下载 YouTube 视频
media_cli.py youtube "URL" --start 开始秒数 --end 结束秒数

# 搜索媒体（不下载）
media_cli.py search "关键词" --type image/video/all

# 剪辑本地视频
media_cli.py trim 输入文件 --start 开始 --end 结束
```

---

## 📦 支持的素材来源

| 来源 | 类型 | 特点 |
|------|------|------|
| Pexels | 图片 + 视频 | 高质量，更新快 |
| Pixabay | 图片 + 视频 | 数量多，种类全 |
| Unsplash | 图片 | 艺术感强，适合壁纸 |
| YouTube | 视频 | 内容丰富，支持剪辑 |

---

## 📄 许可证

MIT License

---

🎬 **开始使用吧！直接告诉我你想要什么图片或视频！**
