"""
OpenAI DALL-E 图片生成 Provider
"""

from typing import Optional

import httpx

from . import ImageGenerateResult, ImageProvider


class OpenAIProvider(ImageProvider):
    """OpenAI DALL-E 图片生成"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "",
        model: str = "dall-e-3",
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
        self.model = model
        self._client = httpx.AsyncClient(timeout=120.0)

    @property
    def name(self) -> str:
        return "openai"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: Optional[str] = None,
    ) -> ImageGenerateResult:
        """
        使用 DALL-E 生成图片

        Args:
            prompt: 图片描述
            size: 尺寸 (256x256, 512x512, 1024x1024, 1792x1024, 1024x1792)
            style: 风格 (vivid, natural)

        Returns:
            ImageGenerateResult
        """
        try:
            response = await self._client.post(
                f"{self.base_url}/images/generations",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "n": 1,
                    "size": size,
                    "style": style or "vivid",
                    "response_format": "url",
                },
            )

            response.raise_for_status()
            data = response.json()

            if "data" in data and len(data["data"]) > 0:
                image_url = data["data"][0]["url"]
                return ImageGenerateResult(
                    success=True,
                    image_url=image_url,
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