"""
智谱 AI（Zhipu）图片生成 Provider
支持 CogView-3 模型，国内直连
"""

from typing import Optional

import httpx

from . import ImageGenerateResult, ImageProvider


class ZhipuProvider(ImageProvider):
    """智谱 AI 图片生成"""

    BASE_URL = "https://open.bigapi.cn/v1/images/generations"

    def __init__(
        self,
        api_key: str,
        model: str = "cogview-3",
    ) -> None:
        self.api_key = api_key
        self.model = model
        self._client = httpx.AsyncClient(timeout=120.0)

    @property
    def name(self) -> str:
        return "zhipu"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: Optional[str] = None,
    ) -> ImageGenerateResult:
        """
        使用智谱 CogView-3 生成图片
        """
        try:
            # 解析尺寸
            size_map = {
                "1024x1024": "1024x1024",
                "720x1280": "720x1280",
                "1280x720": "1280x720",
                "1024x1792": "1024x1792",
                "1792x1024": "1792x1024",
            }
            model_size = size_map.get(size, "1024x1024")

            response = await self._client.post(
                self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "size": model_size,
                    "n": 1,
                    "style": style or "auto",
                },
            )

            response.raise_for_status()
            data = response.json()

            if "data" in data and len(data["data"]) > 0:
                image_url = data["data"][0].get("url") or data["data"][0].get("b64_json")
                if image_url:
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
