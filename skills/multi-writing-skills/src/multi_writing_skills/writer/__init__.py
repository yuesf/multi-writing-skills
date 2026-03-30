"""
AI 写作助手

支持多种写作风格的 AI 写作辅助工具。
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import httpx
import yaml


class WritingStyle(str, Enum):
    """写作风格"""

    DAN_KOE = "dan-koe"  # Dan Koe 风格：简洁、直接、实用
    TECHNICAL = "technical"  # 技术风格：严谨、详细、专业
    CASUAL = "casual"  # 随意风格：轻松、亲切、口语化
    FORMAL = "formal"  # 正式风格：严肃、规范、学术
    STORYTELLING = "storytelling"  # 故事风格：叙事、引人入胜


@dataclass
class StyleConfig:
    """风格配置"""

    name: str
    description: str
    system_prompt: str
    tone: str
    example: str


# 预设写作风格
BUILTIN_STYLES: dict[str, StyleConfig] = {
    "dan-koe": StyleConfig(
        name="Dan Koe 风格",
        description="简洁、直接、实用，适合个人成长和效率类文章",
        system_prompt="""你是一个擅长 Dan Koe 风格写作的专家。你的写作特点是：

1. 简洁有力：每句话都有价值，不写废话
2. 直接表达：开门见山，直奔主题
3. 实用优先：提供可操作的建议和方法
4. 个人视角：用第一人称分享经验和见解
5. 结构清晰：使用列表、小标题等提高可读性

请用这种风格改写用户的内容。""",
        tone="专业但亲切，直接但不生硬",
        example="很多人想提高效率，但不知道从何开始。其实方法很简单：先做最重要的事。",
    ),
    "technical": StyleConfig(
        name="技术风格",
        description="严谨、详细、专业，适合技术教程和深度文章",
        system_prompt="""你是一个技术写作专家。你的写作特点是：

1. 严谨准确：使用准确的技术术语
2. 逻辑清晰：按步骤、层次展开
3. 代码示例：提供可运行的代码片段
4. 注重细节：解释"为什么"而不只是"怎么做"
5. 结构化：使用清晰的章节和小标题

请用这种风格改写用户的内容。""",
        tone="专业、客观、深入",
        example="首先，我们需要理解核心概念。然后，通过代码示例演示具体实现。",
    ),
    "casual": StyleConfig(
        name="随意风格",
        description="轻松、亲切、口语化，适合生活类和个人博客",
        system_prompt="""你是一个擅长轻松写作的专家。你的写作特点是：

1. 口语化：像和朋友聊天一样
2. 亲切感：用"我们"、"你"拉近距离
3. 轻松幽默：适当加入轻松元素
4. 真实感：分享真实经历和感受
5. 互动性：经常提问，引发思考

请用这种风格改写用户的内容。""",
        tone="轻松、亲切、有趣",
        example="说实话，我也曾遇到过这个问题。后来发现，其实解决起来没那么难。",
    ),
    "formal": StyleConfig(
        name="正式风格",
        description="严肃、规范、学术，适合专业论文和正式报告",
        system_prompt="""你是一个正式写作专家。你的写作特点是：

1. 规范用语：使用标准的书面语
2. 客观中立：避免主观情感表达
3. 逻辑严密：论证有理有据
4. 引用出处：标注信息来源
5. 格式规范：符合学术或商务写作规范

请用这种风格改写用户的内容。""",
        tone="正式、专业、客观",
        example="根据研究表明，该方法在实践中具有较高的可行性。",
    ),
    "storytelling": StyleConfig(
        name="故事风格",
        description="叙事、引人入胜，适合情感类和案例分享",
        system_prompt="""你是一个故事写作专家。你的写作特点是：

1. 场景感：描述具体的时间、地点、人物
2. 情节性：有起承转合
3. 情感共鸣：引发读者的情感反应
4. 人物刻画：生动描述人物特点
5. 意义升华：从故事中提炼经验和道理

请用这种风格改写用户的内容。""",
        tone="生动、感人、有感染力",
        example="那是一个平凡的下午，我收到了改变人生的那封邮件...",
    ),
}


class AIWriter:
    """AI 写作助手"""

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

    def get_style(self, style_name: str) -> Optional[StyleConfig]:
        """获取写作风格配置"""
        return BUILTIN_STYLES.get(style_name)

    def list_styles(self) -> list[dict]:
        """列出所有可用的写作风格"""
        return [
            {
                "name": name,
                "display_name": config.name,
                "description": config.description,
            }
            for name, config in BUILTIN_STYLES.items()
        ]

    async def write(
        self,
        topic: str,
        style: str = "dan-koe",
        length: str = "medium",
        context: Optional[str] = None,
    ) -> str:
        """
        根据主题生成文章

        Args:
            topic: 写作主题
            style: 写作风格
            length: 文章长度 (short/medium/long)
            context: 额外上下文

        Returns:
            生成的文章内容
        """
        style_config = self.get_style(style)
        if not style_config:
            raise ValueError(f"未知的写作风格: {style}")

        length_guide = {
            "short": "300-500字",
            "medium": "800-1200字",
            "long": "2000-3000字",
        }

        prompt = f"""{style_config.system_prompt}

主题：{topic}

要求：
- 文章长度：{length_guide.get(length, "800-1200字")}
- 写作风格：{style_config.tone}
{f"- 补充信息：{context}" if context else ""}

请直接输出文章内容，使用 Markdown 格式。"""

        return await self._call_ai(prompt)

    async def rewrite(
        self,
        content: str,
        style: str = "dan-koe",
        keep_structure: bool = True,
    ) -> str:
        """
        用指定风格改写内容

        Args:
            content: 原始内容
            style: 目标写作风格
            keep_structure: 是否保留原有结构

        Returns:
            改写后的内容
        """
        style_config = self.get_style(style)
        if not style_config:
            raise ValueError(f"未知的写作风格: {style}")

        prompt = f"""{style_config.system_prompt}

原始内容：
{content}

要求：
- 保持原文的核心观点和信息
{'- 保留原有的文章结构' if keep_structure else '- 可以重新组织文章结构'}
- 使用目标写作风格进行改写

请直接输出改写后的内容，使用 Markdown 格式。"""

        return await self._call_ai(prompt)

    async def generate_cover_prompt(
        self,
        title: str,
        content: Optional[str] = None,
    ) -> str:
        """
        生成封面图片的提示词

        Args:
            title: 文章标题
            content: 文章内容（可选）

        Returns:
            图片生成提示词
        """
        prompt = f"""请根据以下文章信息，生成一个适合作为封面图片的英文提示词。

标题：{title}
{f"内容摘要：{content[:500]}..." if content else ""}

要求：
1. 提示词用英文描述
2. 适合生成简洁、专业的封面图
3. 避免文字和复杂场景
4. 突出主题，视觉冲击力强

请只输出提示词，不要其他内容。"""

        return await self._call_ai(prompt)

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
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            },
        )

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def close(self) -> None:
        """关闭客户端连接"""
        await self._client.aclose()