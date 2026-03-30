"""
平台抽象层

定义多平台发布的统一接口。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PlatformType(str, Enum):
    """支持的平台类型"""

    WECHAT = "wechat"
    ZHIHU = "zhihu"
    TOUTIAO = "toutiao"


@dataclass
class PublishRequest:
    """发布请求"""

    title: str
    content: str  # HTML 格式
    cover: Optional[str] = None
    author: Optional[str] = None
    digest: Optional[str] = None
    source_url: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    category: Optional[str] = None
    column_id: Optional[str] = None  # 知乎专栏 ID


@dataclass
class PublishResult:
    """发布结果"""

    success: bool
    platform: str
    media_id: Optional[str] = None
    article_url: Optional[str] = None
    draft_url: Optional[str] = None
    message: Optional[str] = None
    title: Optional[str] = None


@dataclass
class ImageUploadResult:
    """图片上传结果"""

    success: bool
    url: Optional[str] = None
    media_id: Optional[str] = None
    message: Optional[str] = None


class Platform(ABC):
    """平台抽象基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """平台标识"""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """平台显示名称"""
        pass

    @abstractmethod
    async def publish(self, request: PublishRequest) -> PublishResult:
        """
        发布文章

        Args:
            request: 发布请求

        Returns:
            发布结果
        """
        pass

    @abstractmethod
    async def upload_image(self, image_path: str) -> ImageUploadResult:
        """
        上传图片

        Args:
            image_path: 图片路径（本地路径或 URL）

        Returns:
            上传结果
        """
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        验证凭证是否有效

        Returns:
            凭证是否有效
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """
        检查是否已配置凭证

        Returns:
            是否已配置
        """
        pass


class PlatformRegistry:
    """平台注册表"""

    def __init__(self) -> None:
        self._platforms: dict[str, Platform] = {}

    def register(self, platform: Platform) -> None:
        """注册平台"""
        self._platforms[platform.name] = platform

    def get(self, name: str) -> Optional[Platform]:
        """获取平台"""
        return self._platforms.get(name)

    def list_platforms(self) -> list[Platform]:
        """列出所有平台"""
        return list(self._platforms.values())

    def list_configured(self) -> list[Platform]:
        """列出已配置的平台"""
        return [p for p in self._platforms.values() if p.is_configured()]


# 全局注册表
registry = PlatformRegistry()