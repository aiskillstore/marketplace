# Pool 模块参考

专属资源池管理。

> ⚠️ **注意**：所有函数的 `pool_name` 参数，实际传的是 **Pool ID**（格式：`pool-xxx-xxx-xxx-xxx`），不是用户自定义的显示名。

## 功能索引

| 功能描述 | 对应函数 | 位置 |
|---------|---------|------|
| **资源池 CRUD** | | |
| 列出所有专属资源池 | `list_pools` | `scripts/pool_module/list_pools.py` |
| 获取资源池详情 | `get_pool` | `scripts/pool_module/get_pool.py` |
| 创建专属资源池 | `create_pool` | `scripts/pool_module/create_pool.py` |
| 更新资源池配置 | `update_pool` | `scripts/pool_module/update_pool.py` |
| 删除资源池 | `delete_pool` | `scripts/pool_module/delete_pool.py` |
| **节点批量操作** | | |
| 列出资源池节点 | `list_pool_nodes` | `scripts/pool_module/list_pool_nodes.py` |
| 批量删除节点 | `batch_delete_nodes` | `scripts/pool_module/batch_delete_nodes.py` |
| 批量重启节点 | `batch_reboot_nodes` | `scripts/pool_module/batch_reboot_nodes.py` |
| 批量锁定节点 | `batch_lock_nodes` | `scripts/pool_module/batch_lock_nodes.py` |
| 批量解锁节点 | `batch_unlock_nodes` | `scripts/pool_module/batch_unlock_nodes.py` |
| 批量更新节点配置 | `batch_update_nodes` | `scripts/pool_module/batch_update_nodes.py` |
| 批量重置节点 | `batch_reset_nodes` | `scripts/pool_module/batch_reset_nodes.py` |
| 批量调整节点规格 | `batch_resize_nodes` | `scripts/pool_module/batch_resize_nodes.py` |
| 批量迁移节点 | `batch_migrate_nodes` | `scripts/pool_module/batch_migrate_nodes.py` |
| 批量绑定节点 | `batch_bind_nodes` | `scripts/pool_module/batch_bind_nodes.py` |
| **工作负载管理** | | |
| 列出资源池工作负载 | `list_pool_workloads` | `scripts/pool_module/list_pool_workloads.py` |
| 资源池工作负载统计 | `pool_workload_statistics` | `scripts/pool_module/pool_workload_statistics.py` |
| **资源规格** | | |
| 列出可用资源规格 | `list_resource_flavors` | `scripts/pool_module/list_resource_flavors.py` |
| **监控与统计** | | |
| 资源池统计信息 | `pool_statistics` | `scripts/pool_module/pool_statistics.py` |
| 资源池监控指标 | `pool_monitor` | `scripts/pool_module/pool_monitor.py` |
| 资源池运行时指标 | `get_pool_runtime_metrics` | `scripts/pool_module/get_pool_runtime_metrics.py` |
| **OS 网络管理** | | |
| 列出专属OS网络 | `list_os_networks` | `scripts/pool_module/list_os_networks.py` |
| 获取OS网络详情 | `get_os_network` | `scripts/pool_module/get_os_network.py` |
| 创建OS网络 | `create_os_network` | `scripts/pool_module/create_os_network.py` |
| 删除OS网络 | `delete_os_network` | `scripts/pool_module/delete_os_network.py` |
| 更新OS网络配置 | `patch_os_network` | `scripts/pool_module/patch_os_network.py` |
| **OS 配置与事件** | | |
| 获取OS配置 | `get_os_config` | `scripts/pool_module/get_os_config.py` |
| 列出OS事件 | `list_os_events` | `scripts/pool_module/list_os_events.py` |
| **插件模板管理** | | |
| 列出插件模板 | `list_plugin_templates` | `scripts/pool_module/list_plugin_templates.py` |
| 获取插件模板详情 | `get_plugin_template` | `scripts/pool_module/get_plugin_template.py` |

---