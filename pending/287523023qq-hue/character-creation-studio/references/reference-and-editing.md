# 参考图分工与局部编辑

## 分工声明
| 参考图 | 只负责 | 明确不引入 |
|---|---|---|
| 图1 | 脸与发型（身份） | 姿势、背景 |
| 图2 | 服装 | 脸、发色、体型 |
| 图3 | 材质/色调/画风 | 身份、构图 |
| 图4 | 构图或姿势 | 脸、服装 |

冲突时：用户明确要求 > 身份参考 > 其他参考 > 推测。画风参考永不接管身份。反推图片时只描述可见内容，结果称"重建提示词"，不称原始提示词。

## 编辑指令模板
```
Use Image 1 as the base. Keep the face, hair, body proportions, outfit and composition unchanged.
Change only <部位> to <结构、材质、连接方式>.
Image 2 is a reference for <指定元素> only; do not copy its face, pose or background.
Match lighting, occlusion and edges to the original. Keep the same aspect ratio.
```

## 规则
- 一次编辑只改一个目标。
- 连续编辑超过 2–3 轮出现累积漂移时，回到母版重新派生。
- "换衣服/摘眼镜/干发"只改该状态，不连带改发色、脸型。
