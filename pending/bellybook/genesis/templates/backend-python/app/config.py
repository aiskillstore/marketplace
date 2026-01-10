"""
[INPUT]: 依赖 pydantic/pydantic_settings 的配置管理能力
[OUTPUT]: 对外提供 settings 全局配置实例
[POS]: 应用配置中心，管理所有环境变量与数据库连接
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================================================
#  Settings - 全局配置
# ============================================================================

class Settings(BaseSettings):
    """应用配置类

    从环境变量加载配置，支持 .env 文件。
    """
    ENVIRONMENT: str = "dev"

    # PostgreSQL 配置
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # API 版本前缀
    API_V1_STR: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

    @computed_field
    def DataBaseURI(self) -> PostgresDsn:
        """构建 PostgreSQL 异步连接 URI"""
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
