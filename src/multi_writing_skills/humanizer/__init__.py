"""
AI 去痕模块

去除 AI 写作痕迹，使文章更加自然人性化。
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import httpx


class Intensity(str, Enum):
    """处理强度"""

    LIGHT = "light"  # 轻度：保留大部分原文
    MEDIUM = "medium"  # 中度：适度调整
    HEAVY = "heavy"  # 重度：大幅改写


@dataclass
class HumanizeResult:
    """去痕结果"""

    original: str
    humanized: str
    changes: list[str]


class Humanizer:
    """AI 去痕处理器"""

    SYSTEM_PROMPT = """你是一个专业的文本人性化专家。你的任务是重写 AI 生成的内容，使其更加自然、人性化。

AI 写作的常见特征包括：
1. 过于规整的句式结构
2. 频繁使用"首先"、"其次"、"最后"等过渡词
3. 缺乏个人观点和情感
4. 过度使用被动语态
5. 句子长度过于均匀
6. 缺少口语化表达
7. 过于完美的逻辑结构

人性化改写的策略：
1. 变化句式长度和结构
2. 添加个人观点和感受
3. 使用更口语化的表达
4. 加入适当的语气词
5. 打破过于规整的结构
6. 添加一些"不完美"但更真实的表达
7. 保留核心信息，调整表达方式

请根据指定的强度进行改写。"""

    INTENSITY_GUIDES = {
        "light": """轻度改写：保持原文大部分内容，只做轻微调整。
- 调整个别句式
- 添加少量口语化表达
- 保持原有结构不变""",
        "medium": """中度改写：适度调整，保留核心内容。
- 重新组织部分段落
- 添加个人观点
- 调整句式多样性
- 加入一些口语化表达""",
        "heavy": """重度改写：大幅调整，使文章焕然一新。
- 重新组织文章结构
- 大量使用口语化表达
- 添加个人经历和感受
- 打破原有的规整模式
- 让文章更有"人味" """,
    }

    def __init__(
        self,
        api_key: str,
        provider: str = "openai",
        base_url: str = "",
        model: str = "gpt-4",
    ) -> None:
        self.api_key = api_key
        self.provider = provider
        self.base_url = base_url
        self.model = model
        self._client = httpx.AsyncClient(timeout=120.0)

    async def humanize(
        self,
        content: str,
        intensity: str = "medium",
        style_hint: Optional[str] = None,
    ) -> HumanizeResult:
        """
        对内容进行去痕处理

        Args:
            content: 原始内容
            intensity: 处理强度 (light/medium/heavy)
            style_hint: 风格提示

        Returns:
            HumanizeResult 包含处理结果
        """
        intensity_guide = self.INTENSITY_GUIDES.get(intensity, self.INTENSITY_GUIDES["medium"])

        prompt = f"""{self.SYSTEM_PROMPT}

改写强度：{intensity}
{intensity_guide}

{f"风格提示：{style_hint}" if style_hint else ""}

原文内容：
{content}

请对上述内容进行人性化改写，使其读起来更像是真人写的内容。
直接输出改写后的内容，使用 Markdown 格式。"""

        humanized = await self._call_ai(prompt)

        # 分析变化
        changes = await self._analyze_changes(content, humanized)

        return HumanizeResult(
            original=content,
            humanized=humanized,
            changes=changes,
        )

    async def _analyze_changes(self, original: str, humanized: str) -> list[str]:
        """分析改写的变化"""
        prompt = f"""对比原文和改写后的内容，列出主要的变化点。

原文：
{original[:1000]}

改写后：
{humanized[:1000]}

请用简洁的语言列出 3-5 个主要变化点，每点一句话。格式：
1. xxx
2. xxx
..."""

        try:
            result = await self._call_ai(prompt)
            # 解析变化点
            changes = []
            for line in result.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    # 移除序号
                    change = line.lstrip("0123456789.-) ")
                    if change:
                        changes.append(change)
            return changes[:5]
        except Exception:
            return ["内容已人性化改写"]

    async def _call_ai(self, prompt: str) -> str:
        """调用 AI API"""
        base_url = self.base_url or "https://api.openai.com/v1"

        response = await self._client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.8,
            },
        )

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def close(self) -> None:
        """关闭客户端连接"""
        await self._client.aclose()


async def humanize_content(
    content: str,
    api_key: str,
    intensity: str = "medium",
    provider: str = "openai",
    base_url: str = "",
    model: str = "gpt-4",
) -> HumanizeResult:
    """
    快捷函数：对内容进行去痕处理

    Args:
        content: 原始内容
        api_key: API 密钥
        intensity: 处理强度
        provider: AI 提供商
        base_url: API 基础 URL
        model: 模型名称

    Returns:
        HumanizeResult
    """
    humanizer = Humanizer(
        api_key=api_key,
        provider=provider,
        base_url=base_url,
        model=model,
    )
    try:
        return await humanizer.humanize(content, intensity)
    finally:
        await humanizer.close()