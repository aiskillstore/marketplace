# Common 模块参考

跨模块共享的公共工具与基础设施。

## 功能索引

| 功能描述 | 对应函数 | 位置 |
|---------|---------|------|
| **认证管理** | | |
| 认证装饰器（所有模块通用） | `authenticated_api_call` | `scripts/common_module/api_helper.py` |
| 认证检查（获取 SDK access 对象） | `ensure_authentication` | `scripts/common_module/auth.py` |
| **API 调用封装** | | |
| 基础 API 调用（构造 session + 路径） | `make_api_call` | `scripts/common_module/api_helper.py` |
| 简化 API 调用（推荐使用） | `simple_api_call` | `scripts/common_module/api_helper.py` |
| API 调用包装（带路径变量替换） | `access_api_call` | 各模块内的 `common.py` |
| **返回格式统一** | | |
| 格式化 API 返回结果 | `format_api_result` | `scripts/common_module/result.py` |

---