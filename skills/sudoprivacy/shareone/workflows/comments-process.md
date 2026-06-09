# 处理 ShareOne 评论

当用户明确要求“处理这些评论”、“根据评论改一下页面”、“修改这个 ShareOne 链接的内容”时读取本文件。只查看评论时不要读取本文件。

ShareOne 页面评论包含状态机字段 `status`：`open` / `in_progress` / `resolved` / `dismissed`，以及作者字段 `author_role`：`visitor` / `owner` / `agent`。

## 1. 获取 share_id 与评论

从 ShareOne 链接 `https://shareone.app/s/<share_id>` 提取 `<share_id>`。

建议先获取未处理评论：

```bash
node scripts/shareone_api_request.js "/api/v1/shares/<SHARE_ID>/comments?status=unresolved"
```

评论数据中可能包含 `replies`。必须将父评论及其所有回复作为一个 thread 整体阅读，综合理解最终共识。回复不需要单独走流程，只对父评论操作状态。

## 2. 标准闭环流程

对每条要处理的父评论，严格按以下顺序执行。

### 步骤 1：认领

必须在动手之前做：

```bash
node scripts/shareone_api_request.js "/api/v1/shares/<SHARE_ID>/comments/<COMMENT_ID>/status" \
  --method PUT \
  --data '{"status": "in_progress"}'
```

访问者会立刻在页面侧栏看到“处理中”徽标和顶部“AI 正在处理 N 条评论...”横幅。跳过这一步会让用户感受不到 AI 在干活。

### 步骤 2：取源

```bash
node scripts/shareone_api_request.js "/api/v1/shares/<SHARE_ID>/download"
```

返回：

```json
{ "content": "...", "filename": "...", "content_type": "..." }
```

### 步骤 3：精准应用修改

- 综合理解整个 thread（父评论 + 所有 replies）的最终意图，必要时先和用户确认。
- 绝对不要用全局 `replace()` 或正则批量替换，会误伤其他同名文案。
- 基于 DOM 结构精确定位：利用 `highlighter_data.startMeta.parentTagName`、`parentIndex`、`textOffset`，结合 `quote`（被选中原文）定位准确节点。
- 理解结构性意图：评论可能是“把这部分挪到底部 / 删掉这个区块 / 加个图标”，先定位再做结构变更。
- 如果在当前源文件里无论如何都找不到对应位置，不要瞎改，直接走 dismissed 流程，并用 note 告诉用户：“源文件结构已变更，无法定位你这条关于 XXX 的评论”。

### 步骤 4：重新发布

使用 `publish-text-page.md` 的 PUT 更新流程重新发布改后的文件，保留同一 `share_id`。

### 步骤 5：写回复并关闭评论

先在该父评论下发一条 AI 回复，明确告诉访问者改了什么：

```bash
node scripts/shareone_api_request.js "/api/v1/shares/<SHARE_ID>/comments" \
  --method POST \
  --data '{"parent_id":"<COMMENT_ID>","quote":"<父评论的 quote>","highlighter_data":"<父评论的 highlighter_data>","content":"已按你的建议把标题改成 ...，并调整了 ...","author_role":"agent"}'
```

`author_role: "agent"` 只在 owner 鉴权下生效，访问者会在侧栏看到 AI 徽标和蓝色背景的回复。

然后关闭父评论：

```bash
node scripts/shareone_api_request.js "/api/v1/shares/<SHARE_ID>/comments/<COMMENT_ID>/status" \
  --method PUT \
  --data '{"status": "resolved", "note": "已采纳，见最新版本"}'
```

`note` 会作为绿色“AI 已处理: ...”高亮区块显示在评论卡片底部，给访问者明确交代。

## 3. 无法处理或无关评论

对于无法处理或无关的评论，必须 dismiss，不要无视：

```bash
node scripts/shareone_api_request.js "/api/v1/shares/<SHARE_ID>/comments/<COMMENT_ID>/status" \
  --method PUT \
  --data '{"status": "dismissed", "note": "页面中没有此元素，可能指的是另一份分享"}'
```

## 4. 兼容旧接口

旧接口仍然可用，但新代码不要使用：

```http
PUT /api/v1/shares/<SHARE_ID>/comments/<COMMENT_ID>/resolve
{ "resolved": true/false }
```

它等价于把 `status` 切到 `resolved` 或 `open`，但不会附带 `note`，访问者拿不到 AI 的解释。新代码一律使用 `/status` 接口。

## 5. 关键准则速查

| 准则 | 为什么 |
| --- | --- |
| 动手前先 `in_progress` | 让访问者看到“AI 在干活” |
| 改完一定要 `POST` 一条 `author_role=agent` 的回复 | 闭环的“答复”部分，没有它就只是状态变化、不是对话 |
| `resolution_note` 要写人话 | “已把按钮改成主色” 比 “Applied.” 有用 |
| 不能处理就 `dismissed` + note | 不要让评论永远卡在 `open` |
| 只对父评论改状态，回复不单独操作 | 状态语义属于 thread 整体 |
| `unresolved` = `open + in_progress` | 拉单子默认用 `?status=unresolved` |
