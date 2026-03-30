"""
API 模式转换器

调用外部 API 服务进行 Markdown 到 HTML 的转换，适用于微信公众号样式优化。
"""

import httpx
from pydantic import BaseModel


class APIConvertOptions(BaseModel):
    """API 转换选项"""

    endpoint: str
    timeout: float = 60.0
    theme: str = "default"


class APIConverter:
    """API 模式转换器"""

    def __init__(self, options: APIConvertOptions) -> None:
        self.options = options
        self._client = httpx.AsyncClient(timeout=options.timeout)

    async def convert(self, markdown: str, title: str = "") -> dict:
        """
        调用 API 进行转换

        Args:
            markdown: Markdown 内容
            title: 文章标题

        Returns:
            转换结果，包含 html, images 等字段
        """
        try:
            response = await self._client.post(
                self.options.endpoint,
                json={
                    "markdown": markdown,
                    "title": title,
                    "theme": self.options.theme,
                },
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API 请求失败: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise RuntimeError(f"API 请求异常: {str(e)}") from e

    async def convert_with_images(self, markdown: str, title: str = "") -> dict:
        """
        转换并处理图片

        Args:
            markdown: Markdown 内容
            title: 文章标题

        Returns:
            转换结果，包含处理后的 html 和图片信息
        """
        result = await self.convert(markdown, title)

        # 如果 API 返回了图片列表，返回原始结果
        if "images" in result:
            return result

        # 否则尝试从 HTML 中提取图片
        import re

        html = result.get("html", "")
        images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)

        result["images"] = images
        return result

    async def close(self) -> None:
        """关闭客户端连接"""
        await self._client.aclose()


# 预设的 API 端点
BUILTIN_ENDPOINTS = {
    "mdnice": "https://api.mdnice.com/api/v1/markdown",
    "wechat": "https://api.weixin.qq.com/cgi-bin/media/upload",  # 示例
}


def get_converter(endpoint: str, theme: str = "default") -> APIConverter:
    """
    获取 API 转换器实例

    Args:
        endpoint: API 端点 URL 或预设名称 (如 "mdnice")
        theme: 主题名称

    Returns:
        APIConverter 实例
    """
    # 检查是否是预设端点
    actual_endpoint = BUILTIN_ENDPOINTS.get(endpoint, endpoint)

    options = APIConvertOptions(endpoint=actual_endpoint, theme=theme)
    return APIConverter(options)