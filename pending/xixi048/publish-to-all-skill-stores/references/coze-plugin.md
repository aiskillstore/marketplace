# 扣子插件商店（API 插件上架）——实测全流程

> 与「扣子技能商店」（卖 SKILL.md，2026-05 起申请制）是**两条不同的线**。
> 本文件是 **API 插件（OpenAPI → 云插件）** 路线：国内唯一个人开发者可上架自有 HTTP API 的渠道。
> 验证基准：2026-10-28，feeling-search 感觉检索插件 `7701395462196281387` 实测全流程通过（audit_status:1 审核中）。

## 路线总览

```
资源库 → +资源 → 插件（旧版 UI 菜单才可用）
  → 导入（URL 和原始数据 → 贴 OpenAPI YAML）→ 三个工具自动生成
  → 启用开关（每工具）→ 试运行（必须调试通过）
  → 编辑示例（每个工具保存一次"运行示例"，勾选复选框！）
  → 发布（版本号）→ 插件商店 → 上架插件 → 选插件 → 填表 → 提交审核
```

## 硬性门槛（实测顺序）

1. **发布要求全部工具试运行通过**（错误码 702093011「请确认插件中的工具已全部试运行通过」）。
   - 有一个工具过不了就**在工具列表把它「启用」开关关掉**即可发布（下线工具不参与校验，且可保留在草稿里）。
2. **上架要求自定义头像**（默认头像直接拒：「上架插件需要自定义插件头像」）。
   - 头像在 **插件页 → 名称旁小铅笔 → 编辑插件配置 → 插件头像**，改完要点确认保存（update_plugin_meta）。
   - **改头像后要重新发布新版本**，商店才读得到新头像。
3. **上架要求每个工具都有「运行示例」**（错误码 788664015）。
   - 陷阱：在「编辑示例」弹窗里跑完调试后，**必须勾选「保存调试结果为工具使用示例」复选框再点完成**。
     只点完成会以 `save_example:false` 落库（表面成功，商店不认）。
   - 复选框是 Semi UI 隐藏 input，自动化要 `document.querySelector('.semi-modal .semi-checkbox input').click()`（JS click 可靠，label 文本点击不可靠）。
   - 示例保存后**再发布一个新版本**，商店校验拉的是最近发布版本的配置。
4. 上架表单还需：关于插件（预填）、使用场景（必填富文本，0/5000）、分类（默认「图像」）。

## 自动化要点（受控浏览器 / CDP）

- 新版 UI（code.coze.cn）的「+资源 → 插件」点不动；用 **「回到旧版」→ www.coze.cn/space/<id>/library**，菜单在固定坐标可用。
- 发布接口可直接在页面上下文 fetch 调用（带 cookie）：
  `POST /api/plugin_api/publish_plugin` body `{plugin_id, privacy_status:false, privacy_info:"", version_name:"v0.0.4", version_desc:"…"}`
  —— 绕开 UI 弹窗点击不稳定的问题。
- 上架入口：`www.coze.cn/store/plugin` → 右上「上架插件」→ 弹窗两个 Semi Select
  （工作空间 / 选择插件，选项 y≈442）→ 确认 → 插件信息表单（两个 contenteditable 富文本：关于插件 / 使用场景）。
- 提交成功回执：`POST /api/marketplace/product/listing` → `{"code":0,"data":{"audit_status":1}}`，页面出现「审核中」。
- 调试报错先抓 `debug_api` 的响应体，`reason` 字段写得很直白（如 "Please enable this tool before debugging."）。

## 计费类端点的取舍（重要决策）

- analyze 这类**按次付费（402）端点无法通过试运行** → 不停用就整个插件发不出去。
- 三选一：
  1. 停用付费工具，只上免费端点（**本次采用**：dictionary + links 免费，description 里写明 analyze 是站外付费 API）；
  2. 服务端给 Coze 加带日上限的免费额度（需要改生产代码，先问用户）；
  3. 把个人 X-FS-Quota 塞进插件 Header——**禁止**：上架后等于把额度白送全部扣子用户。
- 素材：`<repo>/distribution/coze/feeling-search-plugin.yaml`（OpenAPI 3.0）可直接粘进「URL 和原始数据」导入，三个工具全自动生成。

## 成果记录（feeling-search，2026-10-28）

- 插件：感觉检索 `plugin/7701395462196281387`（个人空间 7536771673367445558）
- 版本 v0.0.4；上线工具 dictionary / links（免费），analyze 停用（402 付费）
- 上架分类「图像」，使用场景已填；`audit_status:1` 审核中
- 头像：紫渐变放大镜+「感」字 512px（`distribution/coze/assets-icon-512.png`，浏览器渲染 SVG 生成）
