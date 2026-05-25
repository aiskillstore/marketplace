# Train 模块参考

ModelArts 训练任务管理。

## 功能索引

| 功能描述 | 对应函数 | 位置 |
|--------|---------|------|
| **训练任务 CRUD** | | |
| 创建训练任务 | `ma_train_job_create` | `scripts/train_module/job_create.py` |
| 创建简单训练任务 | `create_simple_training_job` | `scripts/train_module/job_create.py` |
| 创建脚本训练任务 | `create_script_training_job` | `scripts/train_module/job_create.py` |
| 创建调试训练任务 | `create_debug_training_job` | `scripts/train_module/job_create.py` |
| 列出训练任务 | `ma_train_job_list` | `scripts/train_module/job_list.py` |
| 列出训练任务（简化） | `list_training_jobs_simple` | `scripts/train_module/job_list.py` |
| 列出调试训练任务 | `list_debug_training_jobs` | `scripts/train_module/job_list.py` |
| 列出运行中任务 | `list_running_training_jobs` | `scripts/train_module/job_list.py` |
| 列出等待中任务 | `list_pending_training_jobs` | `scripts/train_module/job_list.py` |
| 列出已完成任务 | `list_completed_training_jobs` | `scripts/train_module/job_list.py` |
| 获取训练任务详情 | `ma_show_training_job_details` | `scripts/train_module/job_get_details.py` |
| 停止训练任务 | `ma_train_job_stop` | `scripts/train_module/job_stop.py` |
| 停止训练任务（简化） | `stop_training_job_simple` | `scripts/train_module/job_stop.py` |
| 停止所有等待中任务 | `stop_pending_training_jobs` | `scripts/train_module/job_stop.py` |
| 删除训练任务 | `ma_train_job_delete` | `scripts/train_module/job_delete.py` |
| 删除训练任务（简化） | `delete_training_job_simple` | `scripts/train_module/job_delete.py` |
| 删除所有已完成任务 | `delete_completed_training_jobs` | `scripts/train_module/job_delete.py` |
| 更新训练任务描述 | `ma_train_job_update_description` | `scripts/train_module/job_update.py` |
| **规格查询** | | |
| 获取训练任务规格列表 | `ma_train_job_get_flavors` | `scripts/train_module/job_get_flavors.py` |
| 列出训练任务规格（简化） | `list_training_job_flavors` | `scripts/train_module/job_get_flavors.py` |
| **工具函数** | | |
| 构建训练任务配置 | `build_training_job_config` | `scripts/train_module/common.py` |
| 验证训练任务参数 | `validate_training_job_params` | `scripts/train_module/common.py` |
| 解析训练任务响应 | `parse_training_job_response` | `scripts/train_module/common.py` |

---