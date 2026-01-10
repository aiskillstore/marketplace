# FastAPI + UV + SQLModel 初始化指南

## 一、项目初始化

### 1. 使用 uv 初始化项目

```bash
uv init --python 3.13
uv venv --python 3.13
```

### 2. 添加依赖

```bash
uv add fastapi "fastapi[standard]" python-dotenv pydantic-settings sqlmodel asyncpg greenlet
```

### 3. 删除初始化自带的 main.py

```bash
rm main.py
```

### 4. 创建 .env.dev 文件

> 不要上传到仓库，添加到 .gitignore

```env
ENVIRONMENT=dev

# Postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=YourUsername
POSTGRES_PASSWORD=YourPassword
```

### 5. 创建目录结构

```
app/
├── __init__.py
├── main.py
├── config.py
│
├── db/
│   ├── __init__.py
│   └── session.py
│
├── models/
│   └── __init__.py
│
├── schemas/
│   ├── __init__.py
│   └── base_resp.py
│
├── router/
│   ├── __init__.py
│   ├── login.py
│   └── user.py
│
└── utils/
    ├── __init__.py
    └── log.py
```

---

## 二、初始化代码配置

> 注释使用中文

### 1. app/config.py

```python
from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"
    
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    API_V1_STR: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

    @computed_field
    def DataBaseURI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()

if __name__ == "__main__":
    print(settings.DataBaseURI)
```

### 2. app/db/session.py

```python
import multiprocessing
from typing import AsyncGenerator, Annotated
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

cpu_count = multiprocessing.cpu_count()
workers = cpu_count * 2
max_db_conn = 2400
pool_size = max_db_conn // (workers * 2)
max_overflow = pool_size

async_engine: AsyncEngine = create_async_engine(
    str(settings.DataBaseURI),
    pool_size=pool_size,
    max_overflow=max_overflow,
    pool_pre_ping=True,  # 使用前验证连接
    echo=False,  # 调试时设为 True
)


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
    # 异常交给外部处理 fastapi
    try:
        async with async_session() as session:
            yield session
    except Exception as e:
        raise e


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
```

### 3. app/schemas/base_resp.py

```python
from pydantic import BaseModel, Field
from typing import Optional, Any, Generic, TypeVar
from app.utils.log import logger

T = TypeVar('T')


class BaseResp(BaseModel, Generic[T]):
    """统一响应模型
    
    所有 API 响应的基础模型，提供统一的响应格式。
    支持泛型，可指定 data 字段的具体类型。
    """
    code: int = Field(200, description="状态码，200表示成功，其他值表示错误")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    extra: Optional[dict[str, Any]] = Field(None, description="额外数据")

    @classmethod
    def success(
        cls, 
        data: Any = None, 
        message: str = "success", 
        extra: Optional[dict[str, Any]] = None
    ) -> "BaseResp":
        """成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            extra: 额外数据
            
        Returns:
            BaseResp: 成功响应对象
        """
        return cls(message=message, data=data, extra=extra)

    @classmethod
    def error(
        cls, 
        code: int = 400, 
        message: str = "error", 
        extra: Optional[dict[str, Any]] = None
    ) -> "BaseResp":
        """错误响应
        
        Args:
            code: 错误状态码
            message: 错误消息
            extra: 额外数据
            
        Returns:
            BaseResp: 错误响应对象
        """
        logger.error(f"错误响应: {message}")
        return cls(code=code, message=message, data=None, extra=extra)
```

### 4. app/utils/log.py

```python
"""日志模块

提供统一的日志记录功能。
"""
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### 5. app/router/login.py

```python
"""登录模块路由

处理用户登录相关的接口。
"""
from fastapi import APIRouter
from app.schemas.base_resp import BaseResp
from app.db.session import SessionDep

router = APIRouter()


@router.get("/request_sms_code", summary="发送登录验证码")
async def request_sms_code(session: SessionDep):
    return BaseResp.success(
        message="发送登录验证码",
        data={"code": "null"}
    )
```

### 6. app/router/user.py

```python
"""用户模块路由

处理用户信息相关的接口。
"""
from fastapi import APIRouter
from app.schemas.base_resp import BaseResp
from app.db.session import SessionDep

router = APIRouter()


@router.get("/get_user_info", summary="获取用户信息")
async def get_user_info(session: SessionDep):
    return BaseResp.success(
        message="获取用户信息",
        data={"name": "张三", "age": 18}
    )
```

### 7. app/router/__init__.py

```python
"""路由模块

统一管理所有 API 路由。
"""
from fastapi import APIRouter
from app.config import settings
from app.schemas.base_resp import BaseResp
from . import login, user

api_router = APIRouter()

base_router = APIRouter(prefix=settings.API_V1_STR)
base_router.include_router(user.router, prefix="/user", tags=["user"])
base_router.include_router(login.router, prefix="/login", tags=["login"])

api_router.include_router(base_router)


@api_router.get("/")
async def root() -> BaseResp:
    return BaseResp.error(message="请检查 path - root")
```

### 8. app/main.py

```python
"""应用主入口

FastAPI 应用配置与启动。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.db.session import test_connection
from app.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期事件"""
    # 启动时
    print("应用启动 - 测试数据库连接...")
    await test_connection()
    yield
    # 关闭时
    print("应用关闭")


app = FastAPI(
    title="应用标题",
    description="""
    API 文档

    XXX 团队
    """,
    version="1.0.0",
    contact={"name": "XXX 开发团队"},
    lifespan=lifespan,
    openapi_url=(
        f"/openapi.json"
        if settings.ENVIRONMENT == "dev"
        else None
    ),
    docs_url="/docs" if settings.ENVIRONMENT == "dev" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "dev" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,  # 允许携带凭证
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

app.include_router(api_router)
```

### 9. app/__init__.py

```python
"""应用根模块

FastAPI 后端应用。
"""
```

### 10. app/db/__init__.py

```python
"""数据库模块

提供数据库连接与会话管理。
"""
```

### 11. app/models/__init__.py

```python
"""数据模型模块

定义 SQLModel 数据库模型。
"""
```

### 12. app/schemas/__init__.py

```python
"""数据模式模块

定义 Pydantic 请求/响应模型。
"""
```

### 13. app/utils/__init__.py

```python
"""工具模块

提供通用工具函数。
"""
```

---

## 三、脚本配置

### local-run.sh

```bash
#!/bin/bash

set -a  
source .env.dev
set +a  

uv run fastapi dev app/main.py --host 127.0.0.1 --port 1234
```

赋予执行权限：

```bash
chmod +x local-run.sh
```

---

## 四、初始化完成检查

- [ ] 所有文件无乱码
- [ ] `./local-run.sh` 启动成功
- [ ] 访问 http://127.0.0.1:1234/docs 看到 Swagger 文档
- [ ] 数据库连接测试通过
- [ ] 构建 L1/L2/L3 文档，实现分形初始化

完成后等待下一步指令。
