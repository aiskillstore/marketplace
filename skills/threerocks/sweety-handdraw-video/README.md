# sweety-handdraw-video

安装一个 Skill，按主题或文章制作完整手绘讲解视频。

- 使用入口：[SKILL.md](SKILL.md)
- 项目说明、安装与样片：[GitHub README](https://github.com/threerocks/sweety-handdraw-video)
- 开始时的可选设置：[画风、手臂、声音、广告、水印与字幕](references/production-options.md)
- 编写任务：[运行格式](references/runtime-contract.md)
- 字幕与收尾：[模型设计规则](references/subtitle-design.md)
- 内置依赖和冲突处理：[依赖路由](references/dependencies.md)

旁白支持兼容的本机 VoiceStudio 服务，或已安装并明确配置的 VoxCPM2；已核对的导出音频可以离线复用。音色仅保留逼真男声、逼真女声、甜美学姐、Iapetus、知性女讲师、故事解说。前两款提供对应成片节选，生产需本机原始参考；其余四款提供合成参考和同文试听，使用方法见[本地声音运行](references/local-runtime.md)。生成新图片还需图像工具、Bun 和 ExifTool；Python 与 FFmpeg 负责本地合成。内置的参考指南不需要另行安装为 Skills。

### v1.2：整篇声音优先

整篇生成/录制并核对旁白后锁定母带，画面和字幕读取母带时间戳。生产构建拒绝逐页音频拼接、固定换图静音、裁换气和变速；验证母带与时间戳哈希，并逐样本检查主体旁白保持完整。详见 `references/continuous-narration.md`。

### v1.2：指定原片音色与纯旁白修复

原片音色不再以合成试听继续克隆。导入参考与逐字稿绑定哈希，VoxCPM2 默认同时使用原参考和准确逐字稿；本机已验收的主力音色保存在个人声音目录中，不进入公共包。参考清理、同文对照、正文短样和完整旁白分别验收；没有附加配乐不代表旁白内部没有杂音。

字幕默认白字黑边，禁止重复字幕；编辑用字幕独立放在 `outputs/editing/`。公开预设与展示素材改用 GitHub Release 链接，见[托管与缓存](references/hosted-assets.md)。当前女声暂用，保留原片参考，后续继续调整；不是最终听感验收。

### v1.2.1：美术指导检查加强

每次出图前必须读取内置美术指导，并准备非空简报与实际提示词、绑定内容哈希；生成后填写真实看图结论。缺记录、空文件、提示词或图片改变均停止生产。详见 SKILL.md 的强制流程。

### v1.2.3：音色目录收敛

选择器、源码与引导统一为上述六项。个人或任务内的旧条目不会加回目录，旧名称也不会覆盖当前名称。当前逼真女声仍为暂用状态。
