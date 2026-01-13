"""
[INPUT]: 依赖 app/schemas/base_resp 的 BaseResp，依赖 app/db/session 的 SessionDep
[OUTPUT]: 对外提供 router 登录路由
[POS]: 登录模块路由，处理用户登录相关接口
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

from fastapi import APIRouter

from app.schemas.base_resp import BaseResp
from app.db.session import SessionDep


router = APIRouter()


# ============================================================================
#  登录接口
# ============================================================================

@router.get("/request_sms_code", summary="发送登录验证码")
async def request_sms_code(session: SessionDep):
    return BaseResp.success(
        message="发送登录验证码",
        data={"code": "null"}
    )
