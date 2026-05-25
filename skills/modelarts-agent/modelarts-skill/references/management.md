# Management 模块参考

ModelArts 平台管理功能：工作空间、授权、配额、标签、计划事件、授权模式。

## 功能索引

| 功能描述 | 对应函数 | 位置 |
|--------|---------|------|
| **工作空间** | | |
| 列出工作空间 | `ma_workspace_list` | `scripts/management_module/workspace.py` |
| 创建工作空间 | `ma_workspace_create` | `scripts/management_module/workspace.py` |
| 查询工作空间详情 | `ma_workspace_show` | `scripts/management_module/workspace.py` |
| 更新工作空间 | `ma_workspace_update` | `scripts/management_module/workspace.py` |
| 删除工作空间 | `ma_workspace_delete` | `scripts/management_module/workspace.py` |
| 查询工作空间配额 | `ma_workspace_show_quotas` | `scripts/management_module/workspace.py` |
| 更新工作空间配额 | `ma_workspace_update_quotas` | `scripts/management_module/workspace.py` |
| 验证工作空间权限 | `ma_workspace_validate_auth` | `scripts/management_module/workspace.py` |
| **授权模式** | | |
| 查询当前授权模式 | `ma_authmode_show` | `scripts/management_module/authmode.py` |
| 更新授权模式 | `ma_authmode_update` | `scripts/management_module/authmode.py` |
| **授权管理** | | |
| 列出所有授权 | `ma_authorization_list` | `scripts/management_module/authorization.py` |
| 添加授权 | `ma_authorization_add` | `scripts/management_module/authorization.py` |
| 删除授权 | `ma_authorization_delete` | `scripts/management_module/authorization.py` |
| 创建 IAM 委托授权 | `ma_authorization_agency_create` | `scripts/management_module/authorization.py` |
| **配额** | | |
| 列出项目资源配额 | `ma_quota_list` | `scripts/management_module/quota.py` |
| **标签** | | |
| 列出资源池所有标签 | `ma_tag_list_pool` | `scripts/management_module/tag.py` |
| 获取指定资源池标签 | `ma_tag_get_pool` | `scripts/management_module/tag.py` |
| **计划事件** | | |
| 列出计划事件 | `ma_scheduled_event_list` | `scripts/management_module/scheduled_event.py` |
| 接受/授权计划事件 | `ma_scheduled_event_accept` | `scripts/management_module/scheduled_event.py` |

---