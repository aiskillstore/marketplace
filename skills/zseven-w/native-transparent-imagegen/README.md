# native-transparent-imagegen

[简体中文](README.md) | [English](README.en.md)

[![团子与胡桃原生透明 Alpha 案例](assets/tuanzi-hutao-native-alpha-example.png)](../../examples/native-transparent-imagegen-tuanzi-hutao.md)

原生生成并验证带 Alpha 通道的透明 PNG/WebP。它面向贴纸、Sprite、角色素材、商品
素材，以及毛发、头发、玻璃、烟雾等不应依赖事后抠图的细边缘对象。

这个 Skill 不提供“万能透明提示词”，也不把棋盘格当成透明。它逐张生成、检查未经
修改的原始文件、最多有限重试，并在仍为 RGB 时明确失败；不会调用抠图、色键、分割
或本地写入 Alpha 来伪造成功。

## 真透明和“看起来透明”不是一回事

| 输出 | 文件证据 | 本 Skill 的结论 |
|---|---|---|
| 模型原生透明 | PNG/WebP 编码 Alpha，存在完全透明与可见像素 | 进入细边缘视觉检查 |
| 假棋盘格 | RGB 文件，只是把灰白方格画进画面 | 直接失败 |
| 事后抠图 | 原图不透明，后来通过分割、色键或蒙版生成 Alpha | 不属于原生透明生成 |

预览器显示黑底、白底或棋盘格都不能证明文件透明。必须读取模型返回的原始文件并检查
Alpha；Prompt 正确、工具返回成功或文件扩展名是 `.png` 都不算验收。

## Skill 会强制什么

1. **边界。** 只处理“新生成且必须原生透明”的素材；给现有不透明图片去背景应进入
   明确的背景提取编辑流程。
2. **串行。** Prompt-only 的内置生图入口默认逐张生成，避免并发路径掩盖单张失败。
3. **原始字节。** 验证前不缩放、不压缩、不合成、不改 Alpha。
4. **硬校验。** 每张检查格式、尺寸、SHA-256、Alpha 通道、Alpha 极值、完全透明像素
   和四角透明度。
5. **有限重试。** 每个素材默认最多三次原生生成；仍失败就停，不用抠图“救回来”。
6. **视觉 QA。** 元数据通过后，仍要在明暗对比背景下检查毛尖、白边、黑边、低 Alpha
   色雾、错误阴影和裁切。
7. **证据分层。** `generated`、`alpha-validated`、`edge-inspected`、`user-accepted` 和
   `published` 始终是不同状态。

## 团子与胡桃第一版毛发案例

展示图是内置 ImageGen 返回的原始 PNG，参考了权利人直接提供的团子与胡桃第一版
角色动作页。毛发和蓬松尾巴让它比硬边图标更能暴露“事后抠图”与原生 Alpha 的差别。

| 字段 | 实测值 |
|---|---|
| 尺寸 | 1536×1024 |
| 格式 / 模式 | PNG / RGBA |
| Alpha 极值 | 0–254 |
| 完全透明像素 | 854,016（54.2969%） |
| 四角 Alpha | 0 / 0 / 0 / 0 |
| SHA-256 | `066d5b134cbc267a52bbca681afc742b7c64cc2313e1cd77ff3fce5180a8fbb8` |
| 后处理 | 无 |
| 来源标记 | 原始 C2PA / GPT Image 标记保留 |

仓库保留了原始生成媒体来源标记，不清洗元数据。该文件技术 Alpha 门通过，但毛发
外围仍有宽范围低 Alpha 氛围晕染，因此它用于展示
“原生 Alpha 确实存在”，不冒充完美干净的生产级抠边。完整三次尝试、Prompt 和失败
边界见[案例记录](../../examples/native-transparent-imagegen-tuanzi-hutao.md)。

## 安装

```sh
git clone https://github.com/ZSeven-W/craft-skills.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R craft-skills/skills/native-transparent-imagegen \
  "${CODEX_HOME:-$HOME/.codex}/skills/"

python3 -m pip install -r \
  "${CODEX_HOME:-$HOME/.codex}/skills/native-transparent-imagegen/scripts/requirements.txt"
```

## 调用示例

```text
使用 $native-transparent-imagegen，参考附件中我有权使用的角色设定，生成一张透明
PNG 贴纸。必须是模型原生 Alpha，不允许抠图、色键、分割或绘制棋盘格。

逐张生成并验证未经修改的原文件；如果三次仍没有真实 Alpha，就报告失败。
```

如果显式使用支持输出控制的 API，可请求：

```json
{
  "background": "transparent",
  "output_format": "png"
}
```

API 参数仍不能代替最终文件检查。

## 验证原图

```sh
python3 \
  "${CODEX_HOME:-$HOME/.codex}/skills/native-transparent-imagegen/scripts/validate_alpha.py" \
  --require-transparent-corners \
  /path/to/original-output.png
```

脚本只读，不会修改输入。通过时会报告 `encoded_alpha: true`、Alpha 极值、透明像素、
四角值和 SHA-256；RGB 棋盘格会以 `missing-alpha-channel` 和非零退出码失败。

## 进一步阅读

- [Agent 工作流与触发边界](SKILL.md)
- [中文完整使用指南](../../docs/native-transparent-imagegen.zh-CN.md)
- [English guide](../../docs/native-transparent-imagegen.md)
- [团子与胡桃第一版毛发案例记录](../../examples/native-transparent-imagegen-tuanzi-hutao.md)
- [返回 Craft Skills 集合](../../README.md)

**状态：v0.1 实验版。** 原生透明能力与宿主工具链仍可能变化。展示图由 Fini Yang
明确授权用于本 Skill 案例，保留角色与画面权利，不进入 Apache-2.0 许可；详见
[THIRD_PARTY_NOTICES](../../THIRD_PARTY_NOTICES.md)。
