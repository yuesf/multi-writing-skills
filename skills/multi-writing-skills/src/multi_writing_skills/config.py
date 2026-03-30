"""
配置管理
"""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings


def is_openclaw_env() -> bool:
    """检测是否在 openclaw 环境中运行"""
    openclaw_dir = Path.home() / ".openclaw"
    return openclaw_dir.exists() and openclaw_dir.is_dir()


def load_openclaw_env() -> dict[str, str]:
    """从 ~/.openclaw/.env 加载环境变量"""
    env_file = Path.home() / ".openclaw" / ".env"
    env_vars = {}
    if env_file.exists():
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
    return env_vars


class WeChatConfig(BaseModel):
    """微信公众号配置"""

    app_id: str = ""
    app_secret: str = ""


class ZhihuConfig(BaseModel):
    """知乎配置"""

    cookie: str = ""


class ToutiaoConfig(BaseModel):
    """今日头条配置"""

    cookie: str = ""


class AIConfig(BaseModel):
    """AI 配置"""

    provider: str = "openai"
    api_key: str = ""
    base_url: str = ""
    model: str = "gpt-4"


class Settings(BaseSettings):
    """应用配置"""

    # 配置文件路径
    config_dir: Path = Path.home() / ".multi-writing-skills"

    # 平台配置
    wechat: WeChatConfig = WeChatConfig()
    zhihu: ZhihuConfig = ZhihuConfig()
    toutiao: ToutiaoConfig = ToutiaoConfig()

    # AI 配置
    ai: AIConfig = AIConfig()

    # Markdown 转换配置
    api_endpoint: str = ""  # API 模式的端点
    default_theme: str = "default"

    class Config:
        env_prefix = "WRITING_PUBLISHER_"
        env_nested_delimiter = "_"

    def get_config_file(self) -> Path:
        """获取配置文件路径"""
        return self.config_dir / "config.yaml"

    def load(self) -> None:
        """从文件和环境变量加载配置"""
        # 如果在 openclaw 环境中，先加载 ~/.openclaw/.env
        openclaw_env = {}
        if is_openclaw_env():
            openclaw_env = load_openclaw_env()

        # 先从配置文件加载
        config_file = self.get_config_file()
        if config_file.exists():
            with open(config_file, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                if "wechat" in data:
                    self.wechat = WeChatConfig(**data["wechat"])
                if "zhihu" in data:
                    self.zhihu = ZhihuConfig(**data["zhihu"])
                if "toutiao" in data:
                    self.toutiao = ToutiaoConfig(**data["toutiao"])
                if "ai" in data:
                    self.ai = AIConfig(**data["ai"])
                if "api_endpoint" in data:
                    self.api_endpoint = data["api_endpoint"]
                if "default_theme" in data:
                    self.default_theme = data["default_theme"]

        # 环境变量优先级更高（先检查 openclaw 环境变量，再检查系统环境变量）
        # 微信公众号配置
        wechat_app_id = openclaw_env.get("WECHAT_APP_ID") or os.environ.get("WECHAT_APP_ID")
        if wechat_app_id is not None:
            self.wechat.app_id = wechat_app_id

        wechat_app_secret = openclaw_env.get("WECHAT_APP_SECRET") or os.environ.get("WECHAT_APP_SECRET")
        if wechat_app_secret is not None:
            self.wechat.app_secret = wechat_app_secret

        # 知乎配置
        zhihu_cookie = openclaw_env.get("ZHIHU_COOKIE") or os.environ.get("ZHIHU_COOKIE")
        if zhihu_cookie is not None:
            self.zhihu.cookie = zhihu_cookie

        # 今日头条配置
        toutiao_cookie = openclaw_env.get("TOUTIAO_COOKIE") or os.environ.get("TOUTIAO_COOKIE")
        if toutiao_cookie is not None:
            self.toutiao.cookie = toutiao_cookie

        # AI 配置
        ai_provider = openclaw_env.get("AI_PROVIDER") or os.environ.get("AI_PROVIDER")
        if ai_provider is not None:
            self.ai.provider = ai_provider

        ai_api_key = openclaw_env.get("AI_API_KEY") or os.environ.get("AI_API_KEY")
        if ai_api_key is not None:
            self.ai.api_key = ai_api_key

        ai_base_url = openclaw_env.get("AI_BASE_URL") or os.environ.get("AI_BASE_URL")
        if ai_base_url is not None:
            self.ai.base_url = ai_base_url

        ai_model = openclaw_env.get("AI_MODEL") or os.environ.get("AI_MODEL")
        if ai_model is not None:
            self.ai.model = ai_model

    def save(self) -> None:
        """保存配置到文件"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.get_config_file()

        data = {
            "wechat": self.wechat.model_dump(),
            "zhihu": self.zhihu.model_dump(),
            "toutiao": self.toutiao.model_dump(),
            "ai": self.ai.model_dump(),
            "api_endpoint": self.api_endpoint,
            "default_theme": self.default_theme,
        }

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def is_wechat_configured(self) -> bool:
        return bool(self.wechat.app_id and self.wechat.app_secret)

    def is_zhihu_configured(self) -> bool:
        return bool(self.zhihu.cookie)

    def is_toutiao_configured(self) -> bool:
        return bool(self.toutiao.cookie)


# 全局配置实例
settings = Settings()