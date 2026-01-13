"""
[INPUT]: 依赖 app/schemas/base_resp 的 BaseResp，依赖 app/db/session 的 SessionDep
[OUTPUT]: 对外提供 router 用户路由
[POS]: 用户模块路由，处理用户信息相关接口
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

from fastapi import APIRouter

from app.schemas.base_resp import BaseResp
from app.db.session import SessionDep


router = APIRouter()


# ============================================================================
#  用户接口
# ============================================================================

@router.get("/get_user_info", summary="获取用户信息")
async def get_user_info(session: SessionDep):
    return BaseResp.success(
        message="获取用户信息",
        data={"name": "张三", "age": 18}
    )
