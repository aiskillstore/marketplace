"""
[INPUT]: 依赖 app/config 的 settings，依赖 sqlalchemy/sqlmodel 的异步能力
[OUTPUT]: 对外提供 async_engine, get_async_session, SessionDep, test_connection
[POS]: 数据库会话管理器，所有数据库操作的入口
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

import multiprocessing
from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings


# ============================================================================
#  连接池配置
# ============================================================================

cpu_count = multiprocessing.cpu_count()
workers = cpu_count * 2
max_db_conn = 2400
pool_size = max_db_conn // (workers * 2)
max_overflow = pool_size


# ============================================================================
#  异步引擎
# ============================================================================

async_engine: AsyncEngine = create_async_engine(
    str(settings.DataBaseURI),
    pool_size=pool_size,
    max_overflow=max_overflow,
    pool_pre_ping=True,  # 使用前验证连接
    echo=False,          # 调试时设为 True
)


# ============================================================================
#  数据库操作
# ============================================================================

async def test_connection():
    """测试数据库连接是否成功"""
    try:
        async with AsyncSession(bind=async_engine) as session:
            statement = text("SELECT 'hello'")
            result = await session.exec(statement)
            print(result.all())
            print("数据库连接测试成功")
    except Exception as e:
        print(f"数据库连接测试失败: {str(e)}")
        raise Exception(f"数据库连接测试失败: {str(e)}")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话

    Yields:
        AsyncGenerator[AsyncSession, None]: 数据库会话生成器
    """
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    try:
        async with async_session() as session:
            yield session
    except Exception as e:
        raise e


# ============================================================================
#  依赖注入
# ============================================================================

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
