# Infer V1 模块参考

推理服务管理（旧版 API）。提供推理服务的创建、查询、启停、更新、删除等完整生命周期管理。

## 功能索引

| 功能描述 | 对应函数 | 位置 |
|---------|---------|------|
| **服务 CRUD** | | |
| 创建推理服务 | `ma_old_inference_service_create` | `scripts/infer_v1_module/create_service.py` |
| 快速创建推理服务 | `quick_create_old_service` | `scripts/infer_v1_module/create_service.py` |
| 查询推理服务详情 | `ma_old_inference_service_get` | `scripts/infer_v1_module/get_service.py` |
| 快速查询推理服务 | `quick_get_old_service` | `scripts/infer_v1_module/get_service.py` |
| 列出推理服务 | `ma_old_inference_service_list` | `scripts/infer_v1_module/list_services.py` |
| 快速列出推理服务 | `quick_list_old_services` | `scripts/infer_v1_module/list_services.py` |
| 启动推理服务 | `ma_old_inference_service_start` | `scripts/infer_v1_module/start_service.py` |
| 停止推理服务 | `ma_old_inference_service_stop` | `scripts/infer_v1_module/stop_service.py` |
| 更新推理服务 | `ma_old_inference_service_update` | `scripts/infer_v1_module/update_service.py` |
| 全量更新推理服务 | `ma_old_inference_service_full_update` | `scripts/infer_v1_module/full_update_service.py` |
| 删除推理服务 | `ma_old_inference_service_delete` | `scripts/infer_v1_module/delete_service.py` |
| **服务属性/配置** | | |
| 更新服务属性 | `ma_old_inference_service_update_property` | `scripts/infer_v1_module/update_service_property.py` |
| 获取服务规格列表 | `ma_old_inference_get_specifications` | `scripts/infer_v1_module/get_service_specifications.py` |
| 获取公共规格 | `ma_old_inference_get_public_specs` | `scripts/infer_v1_module/get_public_spec.py` |
| 获取专属池规格 | `ma_old_inference_get_dedicated_specs` | `scripts/infer_v1_module/get_dedicated_spec.py` |
| 获取专属池信息 | `ma_old_inference_get_dedicated_pool` | `scripts/infer_v1_module/get_dedicated_pool.py` |
| **服务事件** | | |
| 获取服务事件 | `ma_old_inference_service_get_events` | `scripts/infer_v1_module/get_service_events.py` |
| 获取服务内部通道信息 | `ma_old_inference_get_internal_channel_info` | `scripts/infer_v1_module/get_service_internal_channel_info.py` |
| 获取服务数量 | `get_old_service_count` | `scripts/infer_v1_module/get_services_count.py` |
| **模型管理** | | |
| 列出模型 | `ma_old_inference_list_models` | `scripts/infer_v1_module/get_model.py` |
| 列出自定义模型 | `ma_old_inference_list_custom_models` | `scripts/infer_v1_module/get_model.py` |
| 列出订阅模型 | `ma_old_inference_list_subscription_models` | `scripts/infer_v1_module/get_model.py` |
| 获取订阅模型版本 | `get_subscription_model_versions` | `scripts/infer_v1_module/get_model.py` |
| **标签管理** | | |
| 创建服务标签 | `ma_old_inference_service_create_tags` | `scripts/infer_v1_module/create_service_tags.py` |
| 获取服务标签 | `ma_old_inference_service_get_tags` | `scripts/infer_v1_module/get_service_tags.py` |
| 删除服务标签 | `ma_old_inference_service_delete_tags` | `scripts/infer_v1_module/delete_service_tags.py` |
| **认证/工具** | | |
| 获取 API 端点 | `getapiendpoint` | `scripts/infer_v1_module/GetApiEndpoint.py` |
| 获取 Token Headers | `get_token_headers` | `scripts/infer_v1_module/get_token_headers.py` |
| Token 认证请求 | `make_token_auth_request` | `scripts/infer_v1_module/make_token_auth_request.py` |
| 解析 API 响应 | `parse_api_response` | `scripts/infer_v1_module/parse_api_response.py` |

---