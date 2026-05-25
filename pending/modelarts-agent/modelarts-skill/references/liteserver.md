# Lite Server 模块参考

## 功能索引

### Dev Server 基础操作

| 功能描述 | 对应函数 | 位置 | API参考 |
|---------|---------|------|---------|
| 创建 Lite Server 实例 | `ma_liteserver_create` | `scripts/liteserver_module/create_dev_server.py` | CreateDevServer |
| 查询 Lite Server 实例列表 | `ma_liteserver_list` | `scripts/liteserver_module/list_dev_servers.py` | ListDevServers |
| 获取 Lite Server 实例详情 | `ma_liteserver_get` | `scripts/liteserver_module/get_dev_server.py` | ShowDevServer |
| 更新 Lite Server 实例名称 | `ma_liteserver_update` | `scripts/liteserver_module/update_dev_server.py` | UpdateDevServer |
| 停止 Lite Server 实例 | `ma_liteserver_stop` | `scripts/liteserver_module/stop_dev_server.py` | StopDevServer |
| 启动 Lite Server 实例 | `ma_liteserver_start` | `scripts/liteserver_module/start_dev_server.py` | StartDevServer |
| 删除 Lite Server 实例 | `ma_liteserver_delete` | `scripts/liteserver_module/delete_dev_server.py` | DeleteDevServer |
| 重启 Lite Server 实例 | `ma_liteserver_reboot` | `scripts/liteserver_module/reboot_dev_server.py` | RebootDevServer |
| 重装 Lite Server 操作系统 | `ma_liteserver_reinstall_os` | `scripts/liteserver_module/reinstall_dev_server_os.py` | ReinstallDevServerOS |
| 切换 Lite Server 操作系统 | `ma_liteserver_change_os` | `scripts/liteserver_module/change_dev_server_os.py` | ChangeDevServerOS |
| 同步 Lite Server 状态 | `ma_liteserver_sync` | `scripts/liteserver_module/sync_dev_servers.py` | SyncDevServers |
| 查询所有 Lite Server 实例 | `ma_liteserver_list_all` | `scripts/liteserver_module/list_all_dev_servers.py` | ListAllDevServers |
| 获取 Lite Server 操作状态 | `ma_liteserver_get_operation` | `scripts/liteserver_module/get_dev_server_operation.py` | GetDevServerOperation |

### Hyper Cluster 管理

| 功能描述 | 对应函数 | 位置 | API参考 |
|---------|---------|------|---------|
| 创建 Hyper Cluster | `ma_liteserver_create_hyper_cluster` | `scripts/liteserver_module/create_hyper_cluster.py` | CreateHyperCluster |
| 查询 Hyper Cluster 列表 | `ma_liteserver_list_hyper_clusters` | `scripts/liteserver_module/list_hyper_clusters.py` | ListHyperCluster |
| 获取 Hyper Cluster 详情 | `ma_liteserver_get_hyper_cluster` | `scripts/liteserver_module/get_hyper_cluster.py` | GetHyperCluster |
| 删除 Hyper Cluster | `ma_liteserver_delete_hyper_cluster` | `scripts/liteserver_module/delete_hyper_cluster.py` | DeleteHyperCluster |
| 查询 Hyper Cluster 容量 | `ma_liteserver_list_hyper_clusters_capacity` | `scripts/liteserver_module/list_hyper_clusters_capacity.py` | ListHyperinstanceClustersCapacity |

### Hyperinstance 管理

| 功能描述 | 对应函数 | 位置 | API参考 |
|---------|---------|------|---------|
| 查询 Hyperinstance 列表 | `ma_liteserver_list_hyperinstances` | `scripts/liteserver_module/list_hyperinstances.py` | ListHyperinstances |
| 获取 Hyperinstance 详情 | `ma_liteserver_get_hyperinstance` | `scripts/liteserver_module/get_hyperinstance.py` | GetHyperinstance |
| 删除 Hyperinstance | `ma_liteserver_delete_hyperinstance` | `scripts/liteserver_module/delete_hyperinstance.py` | DeleteHyperinstance |
| 启动 Hyperinstance | `ma_liteserver_start_hyperinstance` | `scripts/liteserver_module/start_hyperinstance.py` | StartHyperinstance |
| 停止 Hyperinstance | `ma_liteserver_stop_hyperinstance` | `scripts/liteserver_module/stop_hyperinstance.py` | StopHyperinstance |
| 切换 Hyperinstance 操作系统 | `ma_liteserver_change_hyper_os` | `scripts/liteserver_module/change_hyper_os.py` | ChangeHyperinstanceOS |
| 查询所有 Hyperinstance | `ma_liteserver_list_all_hyperinstances` | `scripts/liteserver_module/list_all_hyperinstances.py` | ListAllHyperinstances |
| 扩容 Hyperinstance | `ma_liteserver_scale_up_hyperinstance` | `scripts/liteserver_module/scale_up_hyperinstance.py` | ScaleUpHyperinstance |
| 缩容 Hyperinstance | `ma_liteserver_scale_down_hyperinstance` | `scripts/liteserver_module/scale_down_hyperinstance.py` | ScaleDownHyperinstance |
| 获取扩缩容评估 | `ma_liteserver_get_scale_evaluations` | `scripts/liteserver_module/get_scale_evaluations.py` | GetScaleEvaluationsDevServer |

### 标签管理

| 功能描述 | 对应函数 | 位置 | API参考 |
|---------|---------|------|---------|
| 创建 Hyperinstance 标签 | `ma_liteserver_create_hyper_tags` | `scripts/liteserver_module/create_hyper_tags.py` | CreateHyperinstanceTags |
| 删除 Hyperinstance 标签 | `ma_liteserver_delete_hyper_tags` | `scripts/liteserver_module/delete_hyper_tags.py` | DeleteHyperinstanceTags |
| 查询 Hyperinstance 标签 | `ma_liteserver_query_hyper_tags` | `scripts/liteserver_module/query_hyper_tags.py` | QueryHyperinstanceTags |

### 存储管理

| 功能描述 | 对应函数 | 位置 | API参考 |
|---------|---------|------|---------|
| 挂载存储卷到 Lite Server | `ma_liteserver_attach_volume` | `scripts/liteserver_module/attach_volume.py` | AttachDevServerVolume |
| 从 Lite Server 卸载存储卷 | `ma_liteserver_detach_volume` | `scripts/liteserver_module/detach_volume.py` | DetachDevServerVolume |
| 绑定弹性公网IP到 Lite Server | `ma_liteserver_bind_eip` | `scripts/liteserver_module/bind_eip.py` | BindDevServerPublicIP |
| 查询 Lite Server 弹性公网IP列表 | `ma_liteserver_list_eips` | `scripts/liteserver_module/list_eips.py` | ListDevServerPublicIP |

### 规格与镜像

| 功能描述 | 对应函数 | 位置 | API参考 |
|---------|---------|------|---------|
| 查询 Lite Server 规格列表 | `ma_liteserver_list_flavors` | `scripts/liteserver_module/list_flavors.py` | ListDevServerFlavors |
| 查询 Lite Server 资源规格列表 | `ma_liteserver_list_resource_flavors` | `scripts/liteserver_module/list_resource_flavors.py` | ListDevServerResourceflavors |
| 获取 Lite Server 镜像详情 | `ma_liteserver_get_image` | `scripts/liteserver_module/get_image.py` | GetDevServerImage |
| 查询 Lite Server 镜像列表 | `ma_liteserver_list_images` | `scripts/liteserver_module/list_images.py` | ListDevServerImages |

### 网络管理

| 功能描述 | 对应函数 | 位置 | API参考 |
|---------|---------|------|---------|
| 创建 RoCE 网络 | `ma_liteserver_create_roce_network` | `scripts/liteserver_module/create_roce_network.py` | CreateRoceNetwork |

### 批量操作

| 功能描述 | 对应函数 | 位置 | API参考 |
|---------|---------|------|---------|
| 批量操作 Lite Server 实例 | `ma_liteserver_batch_action` | `scripts/liteserver_module/batch_action.py` | BatchDevServersAction |

### 作业管理

| 功能描述 | 对应函数 | 位置 | API参考 |
|---------|---------|------|---------|
| 获取 Lite Server 作业详情 | `ma_liteserver_get_job` | `scripts/liteserver_module/get_job.py` | GetDevServerJob |
| 查询 Lite Server 作业列表 | `ma_liteserver_list_jobs` | `scripts/liteserver_module/list_jobs.py` | ListDevServerJobs |
| 删除 Lite Server 作业 | `ma_liteserver_delete_jobs` | `scripts/liteserver_module/delete_jobs.py` | DeleteDevServerJobs |
| 创建 Lite Server 作业 | `ma_liteserver_create_job` | `scripts/liteserver_module/create_job.py` | CreateDevServerJob |
| 查询 Lite Server 作业模板列表 | `ma_liteserver_list_job_templates` | `scripts/liteserver_module/list_job_templates.py` | ListDevServerJobTemplates |
| 获取 Lite Server 作业模板详情 | `ma_liteserver_get_job_template` | `scripts/liteserver_module/get_job_template.py` | GetDevServerJobTemplate |

### 插件与软件

| 功能描述 | 对应函数 | 位置 | API参考 |
|---------|---------|------|---------|
| 查询插件列表 | `ma_liteserver_list_plugins` | `scripts/liteserver_module/list_plugins.py` | ListPlugins |
| 查看软件信息 | `ma_liteserver_show_software` | `scripts/liteserver_module/show_software.py` | ShowSoftware |
| 获取作业服务信息 | `ma_liteserver_get_job_service` | `scripts/liteserver_module/get_job_service.py` | GetDevServerJobService |

### 拓扑与工具

| 功能描述 | 对应函数 | 位置 | API参考 |
|---------|---------|------|---------|
| 获取拓扑信息 | `ma_liteserver_get_topologies` | `scripts/liteserver_module/get_topologies.py` | GetTopologies |
| 获取 Lite Server 技能信息 | `ma_get_liteserver_skill_info` | `scripts/liteserver_module/__init__.py` | 模块信息函数 |

---

## 接口详细说明

### charging_info 计费参数（create_dev_server 必填）

创建 HPS 超节点包周期资源时，`charging_info` 参数结构：

```python
charging_info = {
    "charge_mode": "PRE_PAID",   # 包周期 / COMMON: 按量
    "period_type": "month",      # month: 月 / year: 年（PRE_PAID时必填）
    "period_num": 1              # 周期数量，1-9（PRE_PAID时必填）
}
```

### HPS 创建关键参数

创建 HPS 超节点时，`network` 中需包含：

```python
network = {
    "vpc_id": "vpc-id",              # VPC ID（必填）
    "subnet_id": "subnet-id",         # 子网 ID（必填）
    "security_group_id": "sg-id",     # 安全组 ID（必填）
    "hps_cluster_id": "cluster-id"    # Hyper Cluster ID（创建 HPS 时必填）
}
```

### 标签管理接口 URI

| 操作 | URI |
|------|-----|
| 创建标签 | `POST /v1/{project_id}/dev-servers/hyperinstance/{id}/tags/create` |
| 查询标签 | `GET /v1/{project_id}/dev-servers/hyperinstance/{id}/tags` |
| 删除标签 | `POST /v1/{project_id}/dev-servers/hyperinstance/{id}/tags/delete` |

> 接口返回 200 时 body 为空，`None` 响应会被自动处理为成功。

### ScaleUpHyperinstance 参数

```python
ma_liteserver_scale_up_hyperinstance(
    hyperinstance_id="...",       # 超节点ID（必填）
    flavor="kat3ne-16-800t...",   # 目标规格（必填）
    image_id="uuid...",           # 镜像ID（必填）
    root_volume={"type": "GPSSD", "size": 200},  # 系统盘（可选）
    data_volume={"type": "GPSSD", "size": 500, "count": 1},  # 数据盘（可选）
    key_pair_name="key-name",     # 密钥对（HPS 扩容必填，仅支持密钥对）
    userdata="base64..."          # 自定义数据（可选）
)
```

### list_hyper_clusters_capacity 参数

```python
ma_liteserver_list_hyper_clusters_capacity(
    hyper_cluster_id="cluster-id"  # Hyper Cluster ID（必填）
)
```
