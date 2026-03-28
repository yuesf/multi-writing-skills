"""
图片处理模块
"""

from pathlib import Path
from typing import Optional

from PIL import Image


class ImageProcessor:
    """图片处理器"""

    @staticmethod
    def resize(
        image_path: str,
        output_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        max_size: Optional[int] = None,
    ) -> str:
        """
        调整图片大小

        Args:
            image_path: 原图路径
            output_path: 输出路径
            width: 目标宽度
            height: 目标高度
            max_size: 最大边长（保持比例）

        Returns:
            输出文件路径
        """
        img = Image.open(image_path)

        if max_size:
            # 按最长边缩放，保持比例
            ratio = min(max_size / img.width, max_size / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        elif width and height:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        elif width:
            ratio = width / img.width
            new_size = (width, int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        elif height:
            ratio = height / img.height
            new_size = (int(img.width * ratio), height)
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        img.save(output_path, quality=95)
        return output_path

    @staticmethod
    def optimize(image_path: str, output_path: str, quality: int = 85) -> str:
        """
        优化图片大小

        Args:
            image_path: 原图路径
            output_path: 输出路径
            quality: 质量 (1-100)

        Returns:
            输出文件路径
        """
        img = Image.open(image_path)

        # 转换为 RGB（如果需要）
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.save(output_path, "JPEG", quality=quality, optimize=True)
        return output_path

    @staticmethod
    def get_info(image_path: str) -> dict:
        """
        获取图片信息

        Args:
            image_path: 图片路径

        Returns:
            图片信息字典
        """
        img = Image.open(image_path)
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode,
            "size_bytes": Path(image_path).stat().st_size,
        }