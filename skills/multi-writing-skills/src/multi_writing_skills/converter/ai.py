"""
AI 模式转换器

使用 AI 模型进行 Markdown 转换和优化。
"""

from typing import Optional

import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel


class AIConfig(BaseModel):
    """AI 配置"""

    provider: str = "openai"
    api_key: str = ""
    base_url: str = ""
    model: str = "gpt-4"


class AIConverter:
    """AI 模式转换器"""

    DEFAULT_PROMPT = """你是一个专业的 Markdown 到 HTML 转换专家。
请将以下 Markdown 内容转换为适合微信公众号发布的 HTML 格式。

要求：
1. 保留原文结构和语义
2. 使用语义化的 HTML 标签
3. 代码块使用 <pre><code> 标签
4. 图片保留原始链接
5. 表格使用标准的 <table> 标签
6. 不添加额外的样式，保持简洁

Markdown 内容：
{markdown}

请直接输出转换后的 HTML 内容，不要添加任何解释。"""

    def __init__(self, config: AIConfig) -> None:
        self.config = config
        self._client = httpx.AsyncClient(timeout=120.0)

    async def convert(self, markdown: str, prompt: Optional[str] = None) -> str:
        """
        使用 AI 进行转换

        Args:
            markdown: Markdown 内容
            prompt: 自定义提示词

        Returns:
            转换后的 HTML
        """
        system_prompt = prompt or self.DEFAULT_PROMPT.format(markdown=markdown)

        # 根据不同的 Provider 调用不同的 API
        if self.config.provider == "openai":
            return await self._call_openai(system_prompt, markdown)
        elif self.config.provider == "anthropic":
            return await self._call_anthropic(system_prompt, markdown)
        elif self.config.provider == "gemini":
            return await self._call_gemini(system_prompt, markdown)
        else:
            # 默认使用 OpenAI 兼容格式
            return await self._call_openai(system_prompt, markdown)

    async def _call_openai(self, system_prompt: str, user_content: str) -> str:
        """调用 OpenAI API"""
        base_url = self.config.base_url or "https://api.openai.com/v1"

        response = await self._client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                "temperature": 0.3,
            },
        )

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _call_anthropic(self, system_prompt: str, user_content: str) -> str:
        """调用 Anthropic API"""
        response = await self._client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": self.config.model or "claude-3-opus-20240229",
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_content}],
            },
        )

        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]

    async def _call_gemini(self, system_prompt: str, user_content: str) -> str:
        """调用 Gemini API"""
        response = await self._client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model or 'gemini-pro'}:generateContent",
            headers={"Content-Type": "application/json"},
            params={"key": self.config.api_key},
            json={
                "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_content}"}]}],
            },
        )

        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def close(self) -> None:
        """关闭客户端连接"""
        await self._client.aclose()


async def convert_with_ai(
    markdown: str,
    api_key: str,
    provider: str = "openai",
    base_url: str = "",
    model: str = "gpt-4",
    prompt: Optional[str] = None,
) -> str:
    """
    使用 AI 转换 Markdown

    Args:
        markdown: Markdown 内容
        api_key: API 密钥
        provider: AI 提供商 (openai/anthropic/gemini)
        base_url: API 基础 URL
        model: 模型名称
        prompt: 自定义提示词

    Returns:
        转换后的 HTML
    """
    config = AIConfig(
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        model=model,
    )
    converter = AIConverter(config)
    try:
        return await converter.convert(markdown, prompt)
    finally:
        await converter.close()