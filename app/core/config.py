"""应用配置管理"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Tushare配置
    tushare_token: str

    # 应用配置
    log_level: str = "INFO"
    cache_ttl: int = 3600

    # 数据库配置（后期使用）
    database_url: str = "sqlite+aiosqlite:///./data/invest_agent.db"


# 全局配置实例
settings = Settings()
