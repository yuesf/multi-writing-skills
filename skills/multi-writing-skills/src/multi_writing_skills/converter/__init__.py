"""
Markdown 转换器

支持 API 模式和 AI 模式转换 Markdown 为各平台兼容的 HTML。
支持 wenyan-cli 格式的 CSS 主题。
"""

from pathlib import Path
from typing import Optional

from markdown_it import MarkdownIt
from pydantic import BaseModel

from .wechat_style import WeChatStyleConverter
from .themes import get_theme, list_themes


class ConvertOptions(BaseModel):
    """转换选项"""

    theme: str = "default"
    api_endpoint: Optional[str] = None
    highlight_code: bool = True
    image_host: Optional[str] = None
    platform: str = "default"
    css_path: Optional[str] = None


class ConvertResult(BaseModel):
    """转换结果"""

    title: str
    html: str
    images: list[str] = []


class MarkdownConverter:
    """Markdown 转换器"""

    # mdnice API 端点
    MDNICE_API = "https://api.mdnice.com/api/v1/markdown"

    def __init__(self, options: Optional[ConvertOptions] = None) -> None:
        self.options = options or ConvertOptions()
        self._md = MarkdownIt("gfm-like", {"html": True, "linkify": True})

    def convert(
        self,
        content: str,
        title: Optional[str] = None,
        platform: str = "default",
        theme: str = "default",
        use_api: bool = False,
        api_endpoint: Optional[str] = None,
        css_path: Optional[str] = None,
    ) -> ConvertResult:
        """转换 Markdown 为 HTML

        Args:
            content: Markdown 内容
            title: 文章标题
            platform: 目标平台 (default/wechat)
            theme: 排版主题名称
            use_api: 是否使用 API 模式
            api_endpoint: API 端点
            css_path: CSS 文件路径（兼容 wenyan-cli 格式）
        """
        # 提取标题
        extracted_title = title
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# "):
                extracted_title = line[2:].strip()
                break

        if not extracted_title:
            extracted_title = "无标题文章"

        # 选择转换方式
        if platform == "wechat":
            if use_api:
                # API 模式：调用 mdnice 或自定义 API
                html = self._convert_via_api(content, api_endpoint, theme)
            else:
                # 本地样式转换（支持 CSS 主题）
                converter = WeChatStyleConverter(theme=theme, css_path=css_path)
                html = converter.convert(content, extracted_title)
        else:
            # 基础转换
            html = self._md.render(content)

        # 提取图片
        images = self._extract_images(content)

        return ConvertResult(
            title=extracted_title,
            html=html,
            images=images,
        )

    def _convert_via_api(
        self,
        markdown: str,
        api_endpoint: Optional[str],
        theme: str,
    ) -> str:
        """通过 API 转换 Markdown"""
        import httpx

        endpoint = api_endpoint or self.MDNICE_API

        try:
            # mdnice API 格式
            payload = {
                "content": markdown,
                "theme": theme,
                "mobile": False,
            }

            with httpx.Client(timeout=60.0) as client:
                response = client.post(endpoint, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    # mdnice 返回格式
                    if "data" in data and "content" in data["data"]:
                        return data["data"]["content"]
                    return data.get("content", data.get("html", markdown))

                # 如果 mdnice 失败，回退到本地转换
                converter = WeChatStyleConverter(theme=theme)
                return converter.convert(markdown)

        except Exception:
            # 出错时回退到本地转换
            converter = WeChatStyleConverter(theme=theme)
            return converter.convert(markdown)

    def convert_file(
        self,
        file_path: Path,
        title: Optional[str] = None,
        platform: str = "default",
        theme: str = "default",
        use_api: bool = False,
        api_endpoint: Optional[str] = None,
        css_path: Optional[str] = None,
    ) -> ConvertResult:
        """转换 Markdown 文件"""
        content = file_path.read_text(encoding="utf-8")
        if not title:
            title = file_path.stem
        return self.convert(content, title, platform, theme, use_api, api_endpoint, css_path)

    def _extract_images(self, content: str) -> list[str]:
        """提取 Markdown 中的图片 URL"""
        import re

        pattern = r"!\[.*?\]\((.*?)\)"
        return re.findall(pattern, content)