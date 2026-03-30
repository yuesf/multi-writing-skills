"""
MiniMax 图片生成 Provider
"""

from typing import Optional

import httpx

from . import ImageGenerateResult, ImageProvider


class MiniMaxProvider(ImageProvider):
    """MiniMax 图片生成"""

    BASE_URL = "https://api.minimaxi.com/v1/image_generation"

    def __init__(
        self,
        api_key: str,
        model: str = "image-01",
    ) -> None:
        self.api_key = api_key
        self.model = model
        self._client = httpx.AsyncClient(timeout=120.0)

    @property
    def name(self) -> str:
        return "minimax"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: Optional[str] = None,
    ) -> ImageGenerateResult:
        """
        使用 MiniMax 生成图片
        """
        try:
            # 解析尺寸
            aspect_ratio_map = {
                "1:1": "1:1",
                "16:9": "16:9",
                "9:16": "9:16",
                "1024x1024": "1:1",
                "1024x1792": "9:16",
                "1792x1024": "16:9",
            }
            aspect_ratio = aspect_ratio_map.get(size, "1:1")

            response = await self._client.post(
                self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "n": 1,
                },
            )

            response.raise_for_status()
            data = response.json()

            if data.get("data") and data["data"].get("image_urls"):
                image_urls = data["data"]["image_urls"]
                if image_urls and len(image_urls) > 0:
                    return ImageGenerateResult(
                        success=True,
                        image_url=image_urls[0],
                        message="生成成功",
                    )

            return ImageGenerateResult(
                success=False,
                message=f"生成失败: {data}",
            )

        except httpx.HTTPStatusError as e:
            return ImageGenerateResult(
                success=False,
                message=f"API 错误: {e.response.status_code}",
            )
        except Exception as e:
            return ImageGenerateResult(
                success=False,
                message=f"生成异常: {str(e)}",
            )

    async def close(self) -> None:
        await self._client.aclose()
