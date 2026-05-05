"""应用配置管理"""

from typing import Optional
from pydantic import BaseModel, Field
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

    # LLM配置
    llm_provider: str = Field(default="openai", description="LLM提供商")
    llm_model: str = Field(default="gpt-4o", description="LLM模型")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API密钥")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API密钥")
    deepseek_api_key: Optional[str] = Field(default=None, description="DeepSeek API密钥")
    glm_api_key: Optional[str] = Field(default=None, description="智谱AI API密钥")

    # AI模式配置
    ai_mode_enabled: bool = Field(default=True, description="是否启用AI模式")
    knowledge_base_path: str = Field(default="knowledge", description="知识库路径")


class LLMConfig(BaseModel):
    """LLM配置模型"""
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000


# 全局配置实例
settings = Settings()
