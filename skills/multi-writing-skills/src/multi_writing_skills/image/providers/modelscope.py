"""
ModelScope 图片生成 Provider
"""

from typing import Optional

import httpx

from . import ImageGenerateResult, ImageProvider


class ModelScopeProvider(ImageProvider):
    """ModelScope 图片生成"""

    BASE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"

    def __init__(
        self,
        api_key: str,
        model: str = "wanx-v1",
    ) -> None:
        self.api_key = api_key
        self.model = model
        self._client = httpx.AsyncClient(timeout=120.0)

    @property
    def name(self) -> str:
        return "modelscope"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: Optional[str] = None,
    ) -> ImageGenerateResult:
        """
        使用 ModelScope (通义万相) 生成图片
        """
        try:
            # 解析尺寸
            size_map = {
                "1024x1024": "1024*1024",
                "720x1280": "720*1280",
                "1280x720": "1280*720",
            }
            model_size = size_map.get(size, "1024*1024")

            response = await self._client.post(
                self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "X-DashScope-Async": "enable",
                },
                json={
                    "model": self.model,
                    "input": {
                        "prompt": prompt,
                    },
                    "parameters": {
                        "size": model_size,
                        "n": 1,
                        "style": style or "<auto>",
                    },
                },
            )

            response.raise_for_status()
            data = response.json()

            # 获取任务 ID，轮询结果
            if "output" in data and "task_id" in data["output"]:
                task_id = data["output"]["task_id"]
                return await self._poll_result(task_id)

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

    async def _poll_result(self, task_id: str) -> ImageGenerateResult:
        """轮询获取结果"""
        import asyncio

        url = f"{self.BASE_URL}/{task_id}"

        for _ in range(60):  # 最多等待 60 次
            await asyncio.sleep(2)

            response = await self._client.get(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )

            data = response.json()

            if data["output"].get("task_status") == "SUCCEEDED":
                results = data["output"].get("results", [])
                if results and "url" in results[0]:
                    return ImageGenerateResult(
                        success=True,
                        image_url=results[0]["url"],
                        message="生成成功",
                    )

            elif data["output"].get("task_status") == "FAILED":
                return ImageGenerateResult(
                    success=False,
                    message=f"任务失败: {data['output'].get('message', '未知错误')}",
                )

        return ImageGenerateResult(
            success=False,
            message="生成超时",
        )

    async def close(self) -> None:
        await self._client.aclose()