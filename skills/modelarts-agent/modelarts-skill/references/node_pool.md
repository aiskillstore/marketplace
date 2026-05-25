# Node Pool 模块参考

资源池内的节点池管理。

> ⚠️ **注意**：所有函数的 `pool_name` 参数，实际传的是 **Pool ID**（格式：`pool-xxx-xxx-xxx-xxx`），不是用户自定义的显示名。

## 功能索引

| 功能描述 | 对应函数 | 位置 |
|------|---------|------|
| **节点池 CRUD** | | |
| 列出资源池下所有节点池 | `list_node_pools` | `scripts/node_pool_module/list_node_pools.py` |
| 获取节点池详情 | `get_node_pool` | `scripts/node_pool_module/get_node_pool.py` |
| 创建新节点池 | `create_node_pool` | `scripts/node_pool_module/create_node_pool.py` |
| 更新节点池配置 | `update_node_pool` | `scripts/node_pool_module/update_node_pool.py` |
| 删除节点池 | `delete_node_pool` | `scripts/node_pool_module/delete_node_pool.py` |
| **便捷操作** | | |
| 节点池扩缩容 | `scale_node_pool` | `scripts/node_pool_module/update_node_pool.py` |
| **节点管理** | | |
| 列出指定节点池下的节点 | `list_node_pool_nodes` | `scripts/node_pool_module/list_node_pool_nodes.py` |
| **插件管理** | | |
| 查询插件列表 | `list_pool_plugins` | `scripts/node_pool_module/list_pool_plugins.py` |
| 创建插件 | `create_pool_plugin` | `scripts/node_pool_module/create_pool_plugin.py` |
| **节点配置模板查询** | | |
| 查询节点配置模板 | `get_config_template` | `scripts/node_pool_module/get_config_template.py` |

---