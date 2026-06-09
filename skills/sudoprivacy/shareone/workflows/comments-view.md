# 查看 ShareOne 评论

当用户只是要求查看、拉取、总结评论时读取本文件。不要修改源文件，不要认领评论，不要关闭评论。

## 1. 获取 share_id

从用户提供的 ShareOne 链接 `https://shareone.app/s/<share_id>` 中提取 `<share_id>`。

## 2. 查看未处理评论

调用：

```bash
node scripts/shareone_api_request.js "/api/v1/shares/<SHARE_ID>/comments?status=unresolved"
```

`status` 可选值：

- `all`
- `open`
- `in_progress`
- `resolved`
- `dismissed`
- `unresolved`，等价于 `open + in_progress`

## 3. 评论理解规则

- 只展示评论内容，绝对不要自作主张开始修改源文件。
- 等用户明确要求“处理这些评论”、“根据评论改一下页面”等，再进入 `comments-process.md`。
- 评论数据中可能包含 `replies`。必须将父评论及其所有回复作为一个 thread 整体阅读，综合理解最终共识。
- 不要把每条回复当成独立修改指令。
- 所有回复继承父评论的锚点，也就是 `highlighter_data` 和 `quote`。

## 4. 轻量摘要

如果只想看“现在还有没有未处理的事”，用摘要接口：

```bash
node scripts/shareone_api_request.js "/api/v1/shares/<SHARE_ID>/comments/summary"
# -> { total, open, in_progress, resolved, dismissed, last_activity_at }
```

返回 `open == 0` 时无需拉全量评论。
