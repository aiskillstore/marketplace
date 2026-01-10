"""
[INPUT]: 依赖 app/config 的 settings，依赖 login/user 子路由
[OUTPUT]: 对外提供 api_router 总路由
[POS]: 路由模块，统一管理所有 API 路由
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

from fastapi import APIRouter

from app.config import settings
from app.schemas.base_resp import BaseResp
from . import login, user


# ============================================================================
#  路由配置
# ============================================================================

api_router = APIRouter()

base_router = APIRouter(prefix=settings.API_V1_STR)
base_router.include_router(user.router, prefix="/user", tags=["user"])
base_router.include_router(login.router, prefix="/login", tags=["login"])

api_router.include_router(base_router)


# ============================================================================
#  根路由
# ============================================================================

@api_router.get("/")
async def root() -> BaseResp:
    return BaseResp.error(message="请检查 path - root")
