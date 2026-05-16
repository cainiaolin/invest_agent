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
    deepseek_base_url: Optional[str] = Field(default="https://api.deepseek.com", description="DeepSeek Base URL")
    glm_api_key: Optional[str] = Field(default=None, description="智谱AI API密钥")
    glm_base_url: Optional[str] = Field(default="https://open.bigmodel.cn/api/paas/v4", description="智谱AI Base URL")
    glm_model: Optional[str] = Field(default="glm-4-flash", description="智谱AI模型")

    # AI模式配置
    ai_mode_enabled: bool = Field(default=True, description="是否启用AI模式")
    knowledge_base_path: str = Field(default="knowledge", description="知识库路径")

    # Agent个性化搜索配置
    buffet_search_horizon: int = Field(default=30, description="巴菲特搜索时间范围（天）")
    graham_search_horizon: int = Field(default=90, description="格雷厄姆搜索时间范围（天）")
    fisher_search_horizon: int = Field(default=60, description="费雪搜索时间范围（天）")
    lynch_search_horizon: int = Field(default=14, description="林奇搜索时间范围（天）")
    soros_search_horizon: int = Field(default=7, description="索罗斯搜索时间范围（天）")
    dalio_search_horizon: int = Field(default=30, description="达利欧搜索时间范围（天）")


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
