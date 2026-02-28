---
name: plugin-publisher
description: SkillStore Plugin 发布流程。审核并发布 plugin 到 skillstore.io。包括生成封面图、使用指南、审批发布。
---

# Plugin Publisher

自动化 SkillStore Plugin 发布流程：将待发布的 plugin 审核、生成内容并发布上线。

## 适用场景

- Plugin 提交审核后，需要生成封面图和使用指南
- 需要审批并发布 plugin 到 skillstore.io
- 处理 GitHub Issue 中的 plugin review 请求

## 前置要求

1. **权限**：Admin 权限（skillstore 管理员账户）
2. **工具**：
   - GitHub CLI (`gh`)
   - 飞书消息发送权限
   - 访问 skillstore 管理后台
3. **环境变量**：
   - `GITHUB_TOKEN`：GitHub 访问令牌
   - `SKILLSTORE_ADMIN_URL`：管理后台地址

---

# 完整流程

## 步骤 1：发现待处理 Plugin

### 方式 A：从 GitHub Issue 发现

```bash
# 查看带有 plugin-review 标签的 open issues
gh issue list --repo aiskillstore/marketplace --label "plugin-review" --state open
```

### 方式 B：从飞书群收到请求

当用户在飞书群中提到"发布 plugin"或@你审核 plugin 时，提取 plugin 名称。

## 步骤 2：审核 Plugin 基本信息

打开 GitHub Issue，检查：
- [ ] Plugin 名称是否合适
- [ ] 描述是否有效
- [ ] 是否应该上架

**Issue 位置**：`https://github.com/aiskillstore/marketplace/issues/<issue_number>`

### 决策

| 情况 | 操作 |
|------|------|
| 名称/描述不合规 | `/reject <原因>` 并关闭 Issue |
| 符合要求，继续流程 | 执行步骤 3 |

## 步骤 3：生成内容

在 Issue 下评论：
```
/generate
```

这会触发：
1. 调用 Gemini API 生成封面图
2. 调用 Gemini API 生成使用指南
3. 上传封面图到 Supabase Storage (pending/)
4. 在 Issue 评论中发布预览

**等待生成完成**（通常 30-60 秒），检查生成的：
- [ ] 封面图是否符合主题
- [ ] 使用指南是否准确
- [ ] 快速开始步骤是否完整

### 决策

| 情况 | 操作 |
|------|------|
| 需要修改 | `/regenerate --cover` 或 `/regenerate --guide` |
| 完全重做 | `/regenerate` |
| 可以接受 | 执行步骤 4 |

## 步骤 4：审批发布

在 Issue 下评论：
```
/approve
```

或带修改指南：
```
/approve --guide "修改后的指南内容"
```

这会触发：
1. 移动封面图：pending/ → approved/
2. 更新 plugin 记录：
   - cover_image_url
   - usage_guide
   - quick_start_steps
   - status: 'published'
   - published_at: now()
3. 关闭 Issue（标记 approved）

## 步骤 5：验证发布

确认 plugin 已上线：
1. 访问 `https://skillstore.io/plugins/<plugin_slug>`
2. 确认封面图正常显示
3. 确认使用指南可见

---

# 命令参考

| 命令 | 说明 |
|------|------|
| `/generate` | 生成封面图和使用指南 |
| `/approve` | 批准并发布 |
| `/approve --guide "..."` | 批准并自定义指南 |
| `/regenerate` | 重新生成全部内容 |
| `/regenerate --cover` | 仅重新生成封面 |
| `/regenerate --guide` | 仅重新生成指南 |
| `/reject <原因>` | 拒绝并关闭 |

---

# 常见问题

## Q: 生成失败怎么办？

A: 检查 Issue 评论中的错误信息。常见原因：
- Gemini API 配额不足
- 网络超时
- 图片生成失败

可以重试 `/generate`，或手动上传封面图后用 `/approve`。

## Q: 如何查看已发布的 plugin？

A:
```bash
# 方法 1：直接访问
# https://skillstore.io/plugins/<slug>

# 方法 2：GitHub Issue 已关闭
gh issue list --repo aiskillstore/marketplace --label "approved" --state closed
```

## Q: 需要修改已发布的 plugin 怎么办？

A: 暂时需要通过 Supabase 管理后台或直接修改数据库。未来可能添加更新流程。

---

# 验证检查清单

发布完成后，确认以下全部通过：

- [ ] GitHub Issue 已关闭，标签为 `approved`
- [ ] Plugin 页面可访问：`https://skillstore.io/plugins/<slug>`
- [ ] 封面图正常加载
- [ ] 使用指南可见
- [ ] 快速开始步骤完整
- [ ] 在飞书群通知相关人员发布完成
