"""
Google Gemini 图片生成 Provider
"""

from typing import Optional

import httpx

from . import ImageGenerateResult, ImageProvider


class GeminiProvider(ImageProvider):
    """Google Gemini 图片生成"""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp") -> None:
        self.api_key = api_key
        self.model = model
        self._client = httpx.AsyncClient(timeout=120.0)

    @property
    def name(self) -> str:
        return "gemini"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: Optional[str] = None,
    ) -> ImageGenerateResult:
        """
        使用 Gemini 生成图片

        注意：Gemini 的图片生成能力可能需要特定的模型版本
        """
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

            response = await self._client.post(
                url,
                headers={"Content-Type": "application/json"},
                params={"key": self.api_key},
                json={
                    "contents": [
                        {
                            "parts": [
                                {"text": f"Generate an image: {prompt}"},
                            ]
                        }
                    ],
                    "generationConfig": {
                        "responseModalities": ["image", "text"],
                    },
                },
            )

            response.raise_for_status()
            data = response.json()

            # 解析响应，提取图片
            if "candidates" in data:
                for candidate in data["candidates"]:
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "inlineData" in part:
                                # Base64 图片数据
                                import base64
                                import tempfile

                                image_data = base64.b64decode(part["inlineData"]["data"])
                                temp_file = tempfile.NamedTemporaryFile(
                                    suffix=".png", delete=False
                                )
                                temp_file.write(image_data)
                                temp_file.close()

                                return ImageGenerateResult(
                                    success=True,
                                    local_path=temp_file.name,
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