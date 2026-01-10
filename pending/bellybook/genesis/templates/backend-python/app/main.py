"""
[INPUT]: 依赖 app/config 的 settings，依赖 app/db/session 的 test_connection，依赖 app/router 的 api_router
[OUTPUT]: 对外提供 app FastAPI 应用实例
[POS]: 应用主入口，FastAPI 应用配置与启动
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.db.session import test_connection
from app.router import api_router


# ============================================================================
#  生命周期管理
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期事件"""
    # 启动时
    print("应用启动 - 测试数据库连接...")
    await test_connection()
    yield
    # 关闭时
    print("应用关闭")


# ============================================================================
#  FastAPI 应用
# ============================================================================

app = FastAPI(
    title="python1",
    description="""
    FastAPI 后端服务

    python1 API 文档
    """,
    version="1.0.0",
    contact={"name": "开发团队"},
    lifespan=lifespan,
    openapi_url=(
        f"/openapi.json"
        if settings.ENVIRONMENT == "dev"
        else None
    ),
    docs_url="/docs" if settings.ENVIRONMENT == "dev" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "dev" else None,
)


# ============================================================================
#  中间件配置
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 允许所有来源
    allow_credentials=True,    # 允许携带凭证
    allow_methods=["*"],       # 允许所有 HTTP 方法
    allow_headers=["*"],       # 允许所有请求头
)


# ============================================================================
#  路由挂载
# ============================================================================

app.include_router(api_router)
