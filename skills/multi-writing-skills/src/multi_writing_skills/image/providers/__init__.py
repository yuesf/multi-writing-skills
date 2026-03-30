"""
图片生成 Provider 基类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ImageGenerateResult:
    """图片生成结果"""

    success: bool
    image_url: Optional[str] = None
    local_path: Optional[str] = None
    message: Optional[str] = None


class ImageProvider(ABC):
    """图片生成 Provider 基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider 名称"""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: Optional[str] = None,
    ) -> ImageGenerateResult:
        """
        生成图片

        Args:
            prompt: 图片描述
            size: 图片尺寸
            style: 风格

        Returns:
            ImageGenerateResult
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """检查是否已配置"""
        pass