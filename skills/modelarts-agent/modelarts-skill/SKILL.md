---
name: modelarts-skill
description: "Huawei Cloud ModelArts platform integration. Modular design, OBS as primary storage support, environment variable authentication, includes pool plugin management and node configuration template queries."
version: "1.0.0"
---

# ModelArts Skill

Huawei Cloud ModelArts platform integration skill, featuring modular design, OBS as Notebook primary storage, and environment variable auto-authentication.

---

## 🔐 Security Model (CRITICAL)

All credentials handled internally, never returned to LLM:

```
┌─────────────────────────────────────────────────────────────┐
│                     LLM / OpenClaw                          │
│  ❌  NEVER sees: AK, SK, Security Token, raw credentials     │
│  ✅  ONLY sees: Masked status, API results, resource IDs     │
└─────────────────────────────────────────────────────────────┘
                            ↕ (Safe data only)
┌─────────────────────────────────────────────────────────────┐
│              auth_manager.py (Secure Vault)                 │
│  🔒  Credentials stored in memory only                       │
│  ✅  Only masked data exposed externally                      │
└─────────────────────────────────────────────────────────────┘
                            ↕ (Secure session)
┌─────────────────────────────────────────────────────────────┐
│              Module Functions (Secure SDK Wrapper)          │
│  Unified pattern: access.sdk().execute(api_func, ...)        │
│  Returns: Standard format API responses only                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Authentication Methods

| Mode | How It Works |
|------|-------------|
| **Notebook Mode** | Auto-detects ModelArts environment, zero configuration |
| **Local Mode** | Reads `MODELARTS_AK/SK/PROJECT_ID/REGION` environment variables |

---

## 📚 Module Routing

Use keywords to find the corresponding reference file for function index and locations.

| Keyword | Reference File |
|---------|----------------|---------------|--------|
| **notebook, jupyter, image, obs, flavor, cluster, auth** | [`references/notebook.md`](references/notebook.md) |
| **pool, resource pool, dedicated pool, node, workload, os network, plugin** | [`references/pool.md`](references/pool.md) |
| **node pool, nodepool, scale node, node group, plugin, config template** | [`references/node_pool.md`](references/node_pool.md) |
| **train, training job, 训练任务** | [`references/train.md`](references/train.md) |
| **infer1.0, inference, service, 旧版推理服务,旧版在线服务** | [`references/infer_v1.md`](references/infer_v1.md) |
| **infer2.0, inference, service, 新版推理服务，在线服务,新版在线服务** | [`references/infer_v2.md`](references/infer_v2.md) |
| **management, workspace, authmode, authorization, quota, tag, scheduled event** | [`references/management.md`](references/management.md) | 
| **swr, image repo, 镜像仓库** | [`references/swr.md`](references/swr.md) |
| **vpc, virtual private, subnet, security group, 虚拟私有云** | [`references/vpc.md`](references/vpc.md) | 
| **kms, key management, 密钥管理** | [`references/kms.md`](references/kms.md) |
| **liteserver, dev server, hyper cluster, hyperinstance, eip, roce** | [`references/liteserver.md`](references/liteserver.md) | 
| **common, auth, api helper, format result, decorator** | [`references/common.md`](references/common.md) |

---

## 📦 Module Architecture

```
modelarts/
├── scripts/
│   ├── common_module/          # 跨模块共享基础设施
│   │   ├── __init__.py
│   │   ├── _bootstrap.py       # 统一引导
│   │   ├── auth.py             # 认证管理
│   │   ├── api_helper.py       # API 调用封装
│   │   └── result.py           # 返回格式统一
│   │
│   ├── notebook_module/        # Notebook & 镜像管理
│   ├── pool_module/            # 资源池管理
│   ├── node_pool_module/       # 节点池管理
│   ├── train_module/           # 训练任务管理
│   ├── infer_v1_module/        # 旧版推理服务管理
│   ├── infer_v2_module/        # 新版推理服务管理
│   ├── management_module/      # 平台管理: 工作空间/授权/配额/事件
│   ├── swr_module/             # SWR 镜像仓库
│   ├── vpc_module/             # VPC 虚拟私有云
│   ├── kms_module/             # KMS 密钥管理服务
│   ├── liteserver_module/      # Lite Server 轻量计算节点管理 (含 HPS/超节点完整支持)
│   └── __pycache__/
│
└── references/
    ├── notebook.md
    ├── pool.md
    ├── node_pool.md
    ├── train.md
    ├── infer_v1.md
    ├── infer_v2.md
    ├── management.md
    ├── swr.md
    ├── vpc.md
    ├── kms.md
    └── common.md
```

---

## ✅ Design Features

1. **Modular Design** - One file per function, clean structure, easy to maintain
2. **OBS as Primary Storage** - Notebook can use OBS buckets directly as root filesystem
3. **OBS Bucket Management** - Built-in create/delete/list OBS bucket functions
4. **Environment Variable Auth** - Zero configuration for local/CI environments
5. **Unified API Pattern** - All functions use consistent calling pattern
6. **Clean Deliverables** - No temp scripts, no debug code, no redundant files
7. **Node Pool Management** - Independent node pool lifecycle management
8. **Plugin Management** - Resource pool plugin listing and creation (ListPoolPlugins, CreatePoolPlugin)
9. **Node Configuration Template Query** - Query node configuration template details (ShowNodeConfigTemplate)
10. **Common Infrastructure** - Extracted shared infrastructure, improved code reuse
11. **Training Job Management** - Full lifecycle: create/list/stop/delete training jobs
12. **Inference Service Management** - Old v1 API: create/list/start/stop/update/delete inference services
13. **Workspace & Authorization** - Workspace CRUD, auth mode, IAM authorization, quotas, scheduled events
14. **SWR Image Repository** - Query training images from SWR
15. **VPC Virtual Private Cloud** - Query VPCs, Subnets, Security Groups from Huawei Cloud VPC service
16. **KMS Key Management Service** - Query SSH keypairs from Huawei Cloud KMS
17. **Lite Server Management** - Full lifecycle management of lightweight compute nodes (51 APIs covering Chapter 22)
18. **Hyper Cluster Management** - Create, list, delete hyper clusters for high-performance computing
19. **Hyperinstance Operations** - Scale, start, stop, and manage hyper instances
20. **Batch Operations** - Bulk actions on multiple Lite Server instances (start/stop/reboot/changeOS/reinstallOS/delete)
21. **Job Management** - Create, list, delete jobs on Lite Server instances

---

## 🎯 Quick Reference by Use Case

| What You Want To Do | Go To Module |
|---------------------|-------------|
| Start/Stop/Create/Delete Notebook | notebook_module |
| Save Notebook to Image | notebook_module |
| Attach/Detach OBS Storage | notebook_module |
| Create/Delete OBS Buckets | notebook_module |
| Create/Delete Dedicated Resource Pool | pool_module |
| Batch Node Operations (Reboot/Delete/Lock/Resize) | pool_module |
| Scale Node Pool Size | node_pool_module |
| Create Additional Node Pools (different flavors) | node_pool_module |
| List Resource Pool Plugins (ListPoolPlugins) | node_pool_module |
| Create Plugin in Resource Pool (CreatePoolPlugin) | node_pool_module |
| Query Node Configuration Template (ShowNodeConfigTemplate) | node_pool_module |
| Create/Stop/Delete Training Job | train_module |
| List Training Jobs (running/pending/completed) | train_module |
| Create/Start/Stop/Delete Inference Service | infer_v1_module |
| List/Get Inference Service Details | infer_v1_module |
| List Models (custom/subscription) | infer_v1_module |
| Create/Start/Stop/Delete Inference Service (新版) | infer_v2_module |
| List/Get Inference Service Details (新版) | infer_v2_module |
| Query Dedicated Pools & Flavors (新版) | infer_v2_module |
| Get Service Exec Login Info (新版) | infer_v2_module |
| Batch Delete Inference Services (新版) | infer_v2_module |
| Service Version Management (新版) | infer_v2_module |
| Service Events & Health Monitoring (新版) | infer_v2_module |
| Region Detection & Consistency (新版) | infer_v2_module |
| Create/Update/Delete Workspace | management_module |
| Manage Authorization (add/delete/list) | management_module |
| Query/Update Auth Mode | management_module |
| List Quotas & Scheduled Events | management_module |
| Query SWR Training Images | swr_module |
| Query VPC/Subnet/SecurityGroup | vpc_module |
| Query SSH Keypairs | kms_module |
| Create/Start/Stop Lite Server Instances | liteserver_module |
| Manage Hyper Clusters & Hyperinstances | liteserver_module |
| Batch Operations on Lite Servers | liteserver_module |
| Attach/Detach Volumes & EIPs | liteserver_module |
| Query Flavors & Images for Lite Server | liteserver_module |
| Create/Manage Jobs on Lite Server | liteserver_module |
| Infrastructure / Internal Tools | common_module |
