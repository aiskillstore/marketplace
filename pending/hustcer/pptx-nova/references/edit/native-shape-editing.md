# 原生形状编辑：连接线、组合与资源归属

仅在编辑连接线、组合、OLE、嵌入模型或复制相关对象时读取。先走
`inspect-and-edit.md` / `edit-contract.md` 的 inspect → contract → dry-run → apply
路径，再按本页补充证据。以本次运行的 schema 和结果为准，不从版本号推断支持。

## 连接点与坐标

按需读取完整操作合同：

```bash
xdoc schema --mode ops --ops add-connector,set-connector,set-shape,ungroup-shapes --minimal
```

- `site` 是目标原生几何中的 0-based 连接点索引，**不是**通用的上/右/下/左编号，
  也不固定在 `0..3`。schema 的数值上限不代表该对象有那么多站点。根据目标 preset
  或 custom geometry 的实际站点及 dry-run 确认；未披露站点时不能凭外框猜绑定。
- 创建端点必须给齐 `x`、`y`，或给齐 `shape`、`site`。绑定优先于同时提供的坐标；
  坐标不会覆盖绑定点。更新端点允许只改一个坐标分量，以实际绑定/回读结果确认行为。
- 原生绑定会考虑 adjustments、旋转、翻转和祖先 group 变换，再换算到连接线父级
  坐标系。不要自己再加一遍组偏移或重复缩放。`set-shape` 改动绑定对象的几何后，
  同时检查关联线的两端、引用和路由；坐标轴对齐的外框不能证明端点正确。
- 这是端点绑定能力，不是避障布线器。非法站点、不可解析几何或越界坐标被拒绝时，
  保留报告并修正已授权的目标；不要默默解除绑定、改成自由线或靠 raw XML 绕过拒绝。

对已核实连接点的矩形，可写：

```json
{
  "op": "add-connector",
  "slide": 0,
  "name": "Decision link",
  "kind": "straight",
  "begin": { "shape": { "name": "Decision" }, "site": 3 },
  "end": { "x": "8in", "y": "3in" }
}
```

示例的 `site: 3` 只适用于已核实的目标，不能套到箭头、三角形等其他 preset。
部分 preset 的非空 adjustment 列表可能触发 `preset-adjustments`；先按
`../runtime/troubleshooting.md` 诊断，禁止为消除 finding 丢弃作者的 adjustment 值。

## 组合与取消组合

`ungroup-shapes` 应保留子对象在幻灯片上的几何、祖先命名空间和嵌套坐标系。
不均匀缩放叠加旋转可能产生无法表示的 shear、非整数 EMU 或越界坐标；当前运行时
会拒绝这些变换。包含不能安全提升的 `AlternateContent`、不透明模型场景或不支持
方向的 graphic frame 也可能被拒绝。保留 group，或在任务允许时选择另一种编辑方式；
不要用四舍五入、删除扩展、扁平化截图来强行完成取消组合。

apply 后重新 inspect 实际 IDs/层级，不复用旧 group 下的选择假设。核对：

- 子对象在 slide 坐标系中的位置、尺寸、旋转/翻转，以及连接线端点。
- 未触达兄弟 group 的外框和 child coordinate frame 没有变化。
- 文本 autofit 与几何是同一次编辑的结果；失败后从原始输入重做完整 patch，
  不把失败前的中间变换当作已提交状态。

## 复制与资源隔离

优先让 `duplicate-shape` / `duplicate-slide` / 原生 `slide-copy` 分配身份和关系。
从 apply 的 `createdObjects` 和新 inspect 获取 ID；OLE host、嵌套 preview、group
子对象都参与身份分配，不假定一个可见对象只占一个 ID。

- 同页复制 SmartArt frame（包括包含它的 group）会为复制体分离 diagramData 及其
  relationship sidecar；layout/style/color/cache 可共享。保留模型 ID 和不透明内容，
  不把复制能力解释为任意 SmartArt 结构编辑能力。
- 页级 notes、chart、workbook、classic palette 与导航规则见
  `template-following.md`。不要将页级隔离保证外推到任意同页 chart shape 复制。
- 复制后需要独立编辑的对象，应在一次性候选上修改其中一份并回读其他副本，
  同时检查关系归属；只比较图片无法证明隔离。

## OLE 与嵌入模型

OLE host 与显示 preview 的变换应在创建、移动、缩放和组坐标变化后保持一致。
核对实际可见预览及其独立 ID，并保留嵌入 payload、preview 图像、crop 和其他
变换。缩略图元数据不是预览的显示外框，不能据此再缩放一次。

删除 OLE/图片会按最后一个显式 slide 引用清理相关关系；共享引用、图表 workbook、
导入 payload 和不明归属内容可能保留。不要为了缩小文件手动删除剩余 part 或把
所有剩余媒体都判为泄漏；检查新悬空引用和完整包语义证据。

嵌入 3D model 与 Shape/Text 3D 是不同合同。先发现
`model-3d/host-geometry-editing`；当前 `partial` 条目的 `operations` 可为空，而
`recommendation.operations: ["set-shape"]` 明确指向已有 host 的有限几何编辑。
不要让 `model-3d/create-edit: unsupported` 覆盖这个独立子集，也不要据此修改场景、
相机、材质、动画或创建新模型。

按 inspect 得到的 host selector，用 `set-shape` 的位置/尺寸字段先 dry-run。
object-mode 可以移动和缩放 host，poster 跟随 host 中心并保持 cached canvas scale；
这不是模型重新渲染。window-mode 可平移，但需要新 raster 的 resize 会拒绝。
含糊 carrier、不合法或不匹配的 raster 几何、模型 ungroup 也会拒绝，不用 raw XML 绕过。
apply 后核对 host 与 group-local 几何，并比较 opaque scene、嵌入 payload、cached raster
字节和关系归属。不能用 `threeDFacts` 或二维 PNG 认证模型保真；要求 Office 外观或模型
交互时另取 PowerPoint 原生证据。

## 验证

先保存 source/candidate 的 inspect、dry-run/apply、changed-scope vision-diff 和
semantic diff；检查新增语义问题、绑定、payload/关系归属及未授权对象的几何。
对结构风险补 OPC/XML/compat 检查；预览复核之后运行可用的 PowerPoint clean-open。
失败或拒绝是可保留的诊断结果，不应发布一个绕过保护的候选。
