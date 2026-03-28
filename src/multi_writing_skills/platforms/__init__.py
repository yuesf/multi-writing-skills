"""
平台适配器

支持微信公众号、知乎、今日头条等多平台发布。
"""

from .base import Platform, PlatformType, PlatformRegistry, PublishRequest, PublishResult, ImageUploadResult, registry
from .wechat import WeChatPlatform
from .zhihu import ZhihuPlatform
from .toutiao import ToutiaoPlatform

__all__ = [
    "Platform",
    "PlatformType",
    "PlatformRegistry",
    "PublishRequest",
    "PublishResult",
    "ImageUploadResult",
    "WeChatPlatform",
    "ZhihuPlatform",
    "ToutiaoPlatform",
    "registry",
]