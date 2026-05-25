# Infer V2 模块参考

推理服务管理（新版 API）。提供推理服务的创建、查询、启停、更新、删除等完整生命周期管理，支持专属池、自定义规格等高级功能。

## 功能索引

| 功能描述 | 对应函数 | 位置 |
|---------|---------|------|
| **服务 CRUD** | | |
| 创建推理服务 | `ma_inference_service_create` | `infer_v2_module/create_service.py` |
| 快速创建推理服务 | `quick_create_v2_service` | `infer_v2_module/create_service.py` |
| 查询推理服务详情 | `ma_inference_service_get` | `infer_v2_module/get_service.py` |
| 快速查询推理服务 | `quick_get_v2_service` | `infer_v2_module/get_service.py` |
| 列出推理服务 | `ma_inference_service_list` | `infer_v2_module/list_services.py` |
| 快速列出推理服务 | `quick_list_v2_services` | `infer_v2_module/list_services.py` |
| 启动推理服务 | `ma_inference_service_start` | `infer_v2_module/start_service.py` |
| 停止推理服务 | `ma_inference_service_stop` | `infer_v2_module/stop_service.py` |
| 中断推理服务 | `ma_inference_service_interrupt` | `infer_v2_module/interrupt_service.py` |
| 更新推理服务 | `ma_inference_service_update` | `infer_v2_module/update_service.py` |
| 快速更新推理服务 | `quick_update_v2_service` | `infer_v2_module/update_service.py` |
| 删除推理服务 | `ma_inference_service_delete` | `infer_v2_module/delete_service.py` |
| 快速删除推理服务 | `quick_delete_v2_service` | `infer_v2_module/delete_service.py` |
| **批量操作** | | |
| 批量删除推理服务 | `ma_inference_service_batch_delete` | `infer_v2_module/batch_delete.py` |
| 快速批量删除推理服务 | `quick_batch_delete_v2` | `infer_v2_module/batch_delete.py` |
| **服务版本管理** | | |
| 切换服务版本 | `ma_inference_service_switch_version` | `infer_v2_module/switch_version.py` |
| 快速切换服务版本 | `quick_switch_v2_version` | `infer_v2_module/switch_version.py` |
| 获取服务版本详情 | `ma_inference_service_get_version` | `infer_v2_module/get_version.py` |
| 快速获取服务版本详情 | `quick_get_v2_version` | `infer_v2_module/get_version.py` |
| **监控与诊断** | | |
| 服务健康检查 | `ma_inference_service_health` | `infer_v2_module/health.py` |
| 快速服务健康检查 | `quick_health_v2_service` | `infer_v2_module/health.py` |
| 获取服务事件 | `ma_inference_service_get_events` | `infer_v2_module/get_events.py` |
| 快速获取服务事件 | `quick_get_v2_events` | `infer_v2_module/get_events.py` |
| 分析服务事件 | `ma_inference_service_analyze_events` | `infer_v2_module/analyze_events.py` |
| 快速分析服务事件 | `quick_analyze_v2_events` | `infer_v2_module/analyze_events.py` |
| **服务 Exec 登录** | | |
| 获取服务 exec 登录信息 | `ma_inference_service_get_exec` | `infer_v2_module/get_exec.py` |
| 快速获取服务 exec 登录信息 | `quick_get_v2_exec` | `infer_v2_module/get_exec.py` |
| **专属池与规格管理** | | |
| 获取专属池列表 | `ma_inference_service_get_pools` | `infer_v2_module/get_pool.py` |
| 快速获取专属池列表 | `quick_get_v2_pools` | `infer_v2_module/get_pool.py` |
| 获取专属池规格 | `ma_inference_service_get_flavors` | `infer_v2_module/get_flavor.py` |
| 快速获取专属池规格 | `quick_get_v2_flavors` | `infer_v2_module/get_flavor.py` |
| 建议适合的自定义规格 | `suggest_flavor_for_custom_spec` | `infer_v2_module/get_flavor.py` |
| **区域一致性** | | |
| 检测当前区域 | `ma_region_detect_current` | `infer_v2_module/detect_region.py` |
| 快速检测当前区域 | `quick_detect_v2_region` | `infer_v2_module/detect_region.py` |
| 创建区域一致性服务 | `ma_inference_service_create_with_region_consistency` | `infer_v2_module/create_with_region.py` |
| 快速创建区域一致性服务 | `quick_create_v2_with_region` | `infer_v2_module/create_with_region.py` |

---