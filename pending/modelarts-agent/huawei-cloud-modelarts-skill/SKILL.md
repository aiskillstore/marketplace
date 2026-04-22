---
name: huawei-cloud-modelarts-skill
description: 提供 ModelArts 全栈基础资源管理能力
---

## 基本信息
- 技能名称：huawei-cloud-modelarts-skill
- 版本：1.0.0
- 认证方式：ModelArts 运行环境临时安全凭证
- 安全等级：高

## 功能说明
提供 ModelArts 全栈基础资源管理能力：
- 资源概览查询
- 训练作业管理
- 模型管理
- 推理服务管理
- Notebook 管理

## 安全特性
- 自动脱敏：AK/SK、网络信息、密钥全部屏蔽
- 无缓存、无存储、无持久化
- 异常不暴露内部结构
- 全程内存运行

## 支持 Action
| action | 说明 |
|--------|------|
| list_resource_overview | 查询资源概览 |
| list_training_jobs | 查询训练作业 |
| create_training_job | 创建训练作业 |
| list_models | 查询模型 |
| list_services | 查询推理服务 |
| list_notebooks | 查询 Notebook |

## 调用示例
```json
{
  "action": "list_resource_overview",
  "params": {}
}
