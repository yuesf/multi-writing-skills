"""
CLI 入口
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .config import settings
from .platforms import WeChatPlatform, ZhihuPlatform, ToutiaoPlatform, registry

app = typer.Typer(
    name="multi-writing-skills",
    help="多平台 Markdown 发布工具，支持微信公众号、知乎、今日头条",
)
console = Console()


def init_registry() -> None:
    """初始化平台注册表"""
    settings.load()

    # 注册微信平台
    if settings.is_wechat_configured():
        wechat = WeChatPlatform(
            app_id=settings.wechat.app_id,
            app_secret=settings.wechat.app_secret,
        )
        registry.register(wechat)

    # 注册知乎平台
    if settings.is_zhihu_configured():
        zhihu = ZhihuPlatform(cookie=settings.zhihu.cookie)
        registry.register(zhihu)

    # 注册今日头条平台
    if settings.is_toutiao_configured():
        toutiao = ToutiaoPlatform(cookie=settings.toutiao.cookie)
        registry.register(toutiao)


@app.callback()
def main() -> None:
    """初始化"""
    init_registry()


# 配置命令组
config_app = typer.Typer(help="配置管理")
app.add_typer(config_app, name="config")


@config_app.command("init")
def config_init() -> None:
    """初始化配置文件"""
    settings.save()
    console.print(f"[green]配置文件已创建: {settings.get_config_file()}[/green]")


@config_app.command("show")
def config_show() -> None:
    """显示当前配置"""
    settings.load()

    table = Table(title="配置信息")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")

    table.add_row("配置文件", str(settings.get_config_file()))
    table.add_row("微信 AppID", settings.wechat.app_id or "[red]未配置[/red]")
    table.add_row("微信 Secret", "***" if settings.wechat.app_secret else "[red]未配置[/red]")
    table.add_row("知乎", "已配置" if settings.is_zhihu_configured() else "[red]未配置[/red]")
    table.add_row("头条", "已配置" if settings.is_toutiao_configured() else "[red]未配置[/red]")
    table.add_row("AI Provider", settings.ai.provider or "[red]未配置[/red]")
    table.add_row("AI Model", settings.ai.model or "[red]未配置[/red]")
    table.add_row("API 端点", settings.api_endpoint or "[red]未配置[/red]")

    console.print(table)


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="配置键，格式: section.key"),
    value: str = typer.Argument(..., help="配置值"),
) -> None:
    """设置配置项

    示例:
        multi-writing-skills config set wechat.app_id your_app_id
        multi-writing-skills config set wechat.app_secret your_secret
        multi-writing-skills config set ai.api_key your_api_key
    """
    settings.load()

    parts = key.split(".")
    if len(parts) != 2:
        console.print("[red]错误: 配置键格式应为 section.key[/red]")
        raise typer.Exit(1)

    section, subkey = parts

    if section == "wechat":
        if subkey == "app_id":
            settings.wechat.app_id = value
        elif subkey == "app_secret":
            settings.wechat.app_secret = value
        else:
            console.print(f"[red]未知配置项: {key}[/red]")
            raise typer.Exit(1)
    elif section == "zhihu":
        if subkey == "cookie":
            settings.zhihu.cookie = value
        else:
            console.print(f"[red]未知配置项: {key}[/red]")
            raise typer.Exit(1)
    elif section == "toutiao":
        if subkey == "cookie":
            settings.toutiao.cookie = value
        else:
            console.print(f"[red]未知配置项: {key}[/red]")
            raise typer.Exit(1)
    elif section == "ai":
        if subkey == "provider":
            settings.ai.provider = value
        elif subkey == "api_key":
            settings.ai.api_key = value
        elif subkey == "base_url":
            settings.ai.base_url = value
        elif subkey == "model":
            settings.ai.model = value
        else:
            console.print(f"[red]未知配置项: {key}[/red]")
            raise typer.Exit(1)
    else:
        console.print(f"[red]未知配置节: {section}[/red]")
        raise typer.Exit(1)

    settings.save()
    console.print(f"[green]已设置 {key}[/green]")


# 转换命令
@app.command()
def convert(
    file: Path = typer.Argument(..., help="Markdown 或 HTML 文件路径", exists=True),
    platform: str = typer.Option("wechat", "--platform", "-p", help="发布平台 (wechat/zhihu/toutiao)"),
    draft: bool = typer.Option(False, "--draft", "-d", help="发布到草稿箱"),
    preview: bool = typer.Option(False, "--preview", help="预览 HTML 输出"),
    cover: Optional[str] = typer.Option(None, "--cover", "-c", help="封面图片路径"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="作者"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出文件路径"),
    theme: str = typer.Option("default", "--theme", "-t", help="排版主题名称"),
    css: Optional[str] = typer.Option(None, "--css", help="CSS 文件路径或 URL（兼容 wenyan-cli 格式）"),
    use_api: bool = typer.Option(False, "--api", help="使用 mdnice API 模式转换（推荐，排版更精美）"),
    use_ai: bool = typer.Option(False, "--ai", help="使用 AI 模式转换"),
) -> None:
    """转换 Markdown 或直接发布 HTML 到指定平台

    文件格式支持：
    - .md/.markdown: Markdown 文件，会转换为 HTML
    - .html/.htm: HTML 文件，直接使用，不进行转换

    主题支持：
    - 内置主题: default/orange/blue/green/purple/simple
    - CSS 主题: 使用 --css 指定 CSS 文件（兼容 wenyan-cli 格式）

    转换模式说明（仅 Markdown）：
    - 默认模式：使用内置样式转换，速度快，适合离线使用
    - --api 模式：调用 mdnice API，排版更精美，推荐用于正式发布
    - --ai 模式：使用 AI 生成样式，需要配置 AI API Key
    """
    if not file.exists():
        console.print(f"[red]文件不存在: {file}[/red]")
        raise typer.Exit(1)

    # 读取文件内容
    content = file.read_text(encoding="utf-8")
    title = file.stem

    # 判断文件类型
    file_ext = file.suffix.lower()
    is_html = file_ext in (".html", ".htm")

    console.print(f"[cyan]处理文件: {file}[/cyan]")

    # HTML 文件直接使用
    if is_html:
        console.print("[cyan]HTML 文件，直接使用...[/cyan]")
        html_content = content
        # 从 HTML 中提取标题
        import re
        title_match = re.search(r"<h1[^>]*>([^<]+)</h1>", content)
        if title_match:
            title = title_match.group(1)
        else:
            title_match = re.search(r"<title>([^<]+)</title>", content)
            if title_match:
                title = title_match.group(1)
    else:
        # Markdown 文件尝试从内容提取标题（第一个 # 开头的行）
        import re
        # 匹配 # 标题，支持 # Title 或者 ## Title，取第一个
        title_match = re.search(r'^\s*#+\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # 移除标题行，避免正文中重复显示标题
            content = re.sub(r'^\s*#+\s+.+\n?', '', content, count=1, flags=re.MULTILINE)
    else:
        # Markdown 转换
        html_content: str
        first_platform = platform.split(",")[0].strip() if platform else "default"

        # 处理主题：支持 CSS 文件
        actual_theme = theme
        css_path = css
        if css_path:
            console.print(f"[cyan]使用 CSS 主题: {css_path}[/cyan]")

        if use_api:
            from .converter import MarkdownConverter

            console.print("[cyan]使用 mdnice API 模式转换...[/cyan]")
            converter = MarkdownConverter()
            result = converter.convert(
                content, title,
                platform=first_platform,
                theme=theme,
                use_api=True,
                api_endpoint=settings.api_endpoint or None,
            )
            html_content = result.html

        elif use_ai and settings.ai.api_key:
            from .converter.ai import convert_with_ai

            console.print("[cyan]使用 AI 模式转换...[/cyan]")
            html_content = asyncio.run(
                convert_with_ai(
                    content,
                    api_key=settings.ai.api_key,
                    provider=settings.ai.provider,
                    base_url=settings.ai.base_url,
                    model=settings.ai.model,
                )
            )

        else:
            from .converter import MarkdownConverter

            if css_path:
                console.print(f"[cyan]使用 CSS 主题转换: {css_path}[/cyan]")
            else:
                console.print(f"[cyan]使用主题 '{actual_theme}' 转换...[/cyan]")
            converter = MarkdownConverter()
            result = converter.convert(
                content, title,
                platform=first_platform,
                theme=actual_theme,
                css_path=css_path,
            )
            html_content = result.html

    if preview:
        console.print("\n[yellow]预览 HTML:[/yellow]")
        console.print(html_content[:500] + "..." if len(html_content) > 500 else html_content)

    if output:
        output.write_text(html_content, encoding="utf-8")
        console.print(f"[green]已保存到: {output}[/green]")

    if draft:
        # 支持多平台发布
        platforms = platform.split(",")
        for plat_name in platforms:
            plat = registry.get(plat_name.strip())
            if not plat:
                console.print(f"[red]未知平台: {plat_name}[/red]")
                continue

            if not plat.is_configured():
                console.print(f"[red]平台 {plat_name} 未配置，请先运行 config set 设置凭证[/red]")
                continue

            from .platforms import PublishRequest

            request = PublishRequest(
                title=title,
                content=html_content,
                cover=cover,
                author=author,
            )

            result = asyncio.run(plat.publish(request))

            if result.success:
                console.print(f"[green]发布到 {plat.display_name} 成功！[/green]")
                if result.media_id:
                    console.print(f"  Media ID: {result.media_id}")
                if result.article_url:
                    console.print(f"  URL: {result.article_url}")
            else:
                console.print(f"[red]发布到 {plat.display_name} 失败: {result.message}[/red]")


# 发布命令
@app.command()
def publish(
    file: Path = typer.Argument(..., help="HTML 文件路径", exists=True),
    platform: str = typer.Option("wechat", "--platform", "-p", help="发布平台 (wechat/zhihu/toutiao)"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="文章标题（默认从文件名提取）"),
    cover: Optional[str] = typer.Option(None, "--cover", "-c", help="封面图片路径"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="作者"),
) -> None:
    """发布 HTML 文件到指定平台

    直接发布 HTML 文件，不进行任何转换。适用于已准备好的 HTML 内容。
    """
    if not file.exists():
        console.print(f"[red]文件不存在: {file}[/red]")
        raise typer.Exit(1)

    # 读取 HTML 内容
    html_content = file.read_text(encoding="utf-8")

    # 确定标题
    article_title = title or file.stem
    if not title:
        # 尝试从 HTML 中提取标题
        import re
        title_match = re.search(r"<h1[^>]*>([^<]+)</h1>", html_content)
        if title_match:
            article_title = title_match.group(1)
        else:
            title_match = re.search(r"<title>([^<]+)</title>", html_content)
            if title_match:
                article_title = title_match.group(1)

    console.print(f"[cyan]发布 HTML 文件: {file}[/cyan]")
    console.print(f"[cyan]标题: {article_title}[/cyan]")

    # 发布到平台
    platforms = platform.split(",")
    for plat_name in platforms:
        plat = registry.get(plat_name.strip())
        if not plat:
            console.print(f"[red]未知平台: {plat_name}[/red]")
            continue

        if not plat.is_configured():
            console.print(f"[red]平台 {plat_name} 未配置，请先运行 config set 设置凭证[/red]")
            continue

        from .platforms import PublishRequest

        request = PublishRequest(
            title=article_title,
            content=html_content,
            cover=cover,
            author=author,
        )

        result = asyncio.run(plat.publish(request))

        if result.success:
            console.print(f"[green]发布到 {plat.display_name} 成功！[/green]")
            if result.media_id:
                console.print(f"  Media ID: {result.media_id}")
            if result.article_url:
                console.print(f"  URL: {result.article_url}")
        else:
            console.print(f"[red]发布到 {plat.display_name} 失败: {result.message}[/red]")


# 写作命令
@app.command()
def write(
    topic: str = typer.Argument(..., help="写作主题"),
    style: str = typer.Option("dan-koe", "--style", "-s", help="写作风格"),
    length: str = typer.Option("medium", "--length", "-l", help="文章长度 (short/medium/long)"),
    context: Optional[str] = typer.Option(None, "--context", help="额外上下文"),
    cover_prompt: bool = typer.Option(False, "--cover-prompt", help="生成封面提示词"),
) -> None:
    """AI 写作助手"""
    if not settings.ai.api_key:
        console.print("[red]请先配置 AI API Key: multi-writing-skills config set ai.api_key your_key[/red]")
        raise typer.Exit(1)

    from .writer import AIWriter

    writer = AIWriter(
        api_key=settings.ai.api_key,
        provider=settings.ai.provider,
        base_url=settings.ai.base_url,
        model=settings.ai.model,
    )

    try:
        if cover_prompt:
            console.print(f"[cyan]生成封面提示词...[/cyan]")
            prompt = asyncio.run(writer.generate_cover_prompt(topic))
            console.print(f"\n[green]封面提示词:[/green]")
            console.print(prompt)
        else:
            console.print(f"[cyan]使用 {style} 风格写作...[/cyan]")
            article = asyncio.run(
                writer.write(
                    topic=topic,
                    style=style,
                    length=length,
                    context=context,
                )
            )
            console.print(f"\n[green]生成的文章:[/green]")
            console.print(article)
    finally:
        asyncio.run(writer.close())


@app.command()
def rewrite(
    file: Path = typer.Argument(..., help="Markdown 文件路径", exists=True),
    style: str = typer.Option("dan-koe", "--style", "-s", help="目标写作风格"),
    keep_structure: bool = typer.Option(True, "--keep-structure/--no-keep-structure", help="是否保留原有结构"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出文件路径"),
) -> None:
    """使用指定风格改写文章"""
    if not settings.ai.api_key:
        console.print("[red]请先配置 AI API Key[/red]")
        raise typer.Exit(1)

    content = file.read_text(encoding="utf-8")

    from .writer import AIWriter

    writer = AIWriter(
        api_key=settings.ai.api_key,
        provider=settings.ai.provider,
        base_url=settings.ai.base_url,
        model=settings.ai.model,
    )

    try:
        console.print(f"[cyan]使用 {style} 风格改写...[/cyan]")
        rewritten = asyncio.run(
            writer.rewrite(
                content=content,
                style=style,
                keep_structure=keep_structure,
            )
        )

        if output:
            output.write_text(rewritten, encoding="utf-8")
            console.print(f"[green]已保存到: {output}[/green]")
        else:
            console.print(f"\n[green]改写后的文章:[/green]")
            console.print(rewritten)
    finally:
        asyncio.run(writer.close())


# AI 去痕命令
@app.command()
def humanize(
    file: Path = typer.Argument(..., help="Markdown 文件路径", exists=True),
    intensity: str = typer.Option("medium", "--intensity", "-i", help="处理强度 (light/medium/heavy)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出文件路径"),
) -> None:
    """AI 写作去痕"""
    if not settings.ai.api_key:
        console.print("[red]请先配置 AI API Key[/red]")
        raise typer.Exit(1)

    content = file.read_text(encoding="utf-8")

    from .humanizer import Humanizer

    humanizer = Humanizer(
        api_key=settings.ai.api_key,
        provider=settings.ai.provider,
        base_url=settings.ai.base_url,
        model=settings.ai.model,
    )

    try:
        console.print(f"[cyan]执行 AI 去痕 (强度: {intensity})...[/cyan]")
        result = asyncio.run(humanizer.humanize(content, intensity))

        if output:
            output.write_text(result.humanized, encoding="utf-8")
            console.print(f"[green]已保存到: {output}[/green]")
        else:
            console.print(f"\n[green]去痕后的文章:[/green]")
            console.print(result.humanized)

        if result.changes:
            console.print(f"\n[yellow]主要变化:[/yellow]")
            for change in result.changes:
                console.print(f"  - {change}")
    finally:
        asyncio.run(humanizer.close())


# 图片生成命令
@app.command("generate-image")
def generate_image(
    prompt: str = typer.Argument(..., help="图片描述"),
    provider: str = typer.Option("openai", "--provider", "-p", help="图片生成 Provider (openai/gemini/modelscope)"),
    size: str = typer.Option("1024x1024", "--size", "-s", help="图片尺寸"),
    style: Optional[str] = typer.Option(None, "--style", help="图片风格"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出文件路径"),
) -> None:
    """AI 图片生成"""
    if not settings.ai.api_key:
        console.print("[red]请先配置 AI API Key[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]使用 {provider} 生成图片...[/cyan]")

    async def generate() -> tuple[bool, str, Optional[str]]:
        if provider == "openai":
            from .image.providers.openai import OpenAIProvider

            p = OpenAIProvider(api_key=settings.ai.api_key, model="dall-e-3")
            result = await p.generate(prompt, size, style)
            await p.close()
            return result.success, result.message or "", result.image_url

        elif provider == "gemini":
            from .image.providers.gemini import GeminiProvider

            p = GeminiProvider(api_key=settings.ai.api_key)
            result = await p.generate(prompt, size, style)
            await p.close()
            return result.success, result.message or "", result.local_path or result.image_url

        elif provider == "modelscope":
            from .image.providers.modelscope import ModelScopeProvider

            p = ModelScopeProvider(api_key=settings.ai.api_key)
            result = await p.generate(prompt, size, style)
            await p.close()
            return result.success, result.message or "", result.image_url

        else:
            return False, f"未知 Provider: {provider}", None

    success, message, image_url = asyncio.run(generate())

    if success:
        console.print(f"[green]图片生成成功！[/green]")
        if image_url:
            console.print(f"  URL: {image_url}")

        if output and image_url:
            # 下载图片到本地
            import httpx

            async def download() -> None:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(image_url)
                    output.write_bytes(resp.content)

            asyncio.run(download())
            console.print(f"  已保存到: {output}")
    else:
        console.print(f"[red]图片生成失败: {message}[/red]")


# 平台命令组
platform_app = typer.Typer(help="平台管理")
app.add_typer(platform_app, name="platform")


@platform_app.command("list")
def platform_list() -> None:
    """列出所有支持的平台"""
    table = Table(title="支持的平台")
    table.add_column("平台", style="cyan")
    table.add_column("标识", style="yellow")
    table.add_column("状态", style="green")

    platforms_info = [
        ("微信公众号", "wechat", settings.is_wechat_configured()),
        ("知乎", "zhihu", settings.is_zhihu_configured()),
        ("今日头条", "toutiao", settings.is_toutiao_configured()),
    ]

    for name, ident, configured in platforms_info:
        status = "[green]已配置[/green]" if configured else "[red]未配置[/red]"
        table.add_row(name, ident, status)

    console.print(table)


@platform_app.command("test")
def platform_test(
    platform: str = typer.Argument(..., help="平台标识 (wechat/zhihu/toutiao)"),
) -> None:
    """测试平台连接"""
    plat = registry.get(platform)
    if not plat:
        console.print(f"[red]未知平台: {platform}[/red]")
        raise typer.Exit(1)

    if not plat.is_configured():
        console.print(f"[red]平台 {platform} 未配置[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]测试 {plat.display_name} 连接...[/cyan]")

    result = asyncio.run(plat.validate_credentials())

    if result:
        console.print(f"[green]{plat.display_name} 连接成功！[/green]")
    else:
        console.print(f"[red]{plat.display_name} 连接失败[/red]")


# 写作风格命令
@app.command("styles")
def list_styles() -> None:
    """列出所有写作风格"""
    from .writer import AIWriter

    # 创建临时 writer 实例
    writer = AIWriter(
        api_key=settings.ai.api_key or "temp",
        provider=settings.ai.provider,
    )

    table = Table(title="写作风格")
    table.add_column("标识", style="cyan")
    table.add_column("名称", style="yellow")
    table.add_column("描述", style="green")

    for style in writer.list_styles():
        table.add_row(style["name"], style["display_name"], style["description"])

    console.print(table)


# 排版主题命令
@app.command("themes")
def list_themes() -> None:
    """列出所有排版主题（内置 + 自定义 CSS）"""
    from .converter.themes import list_themes as get_themes_list

    table = Table(title="排版主题")
    table.add_column("标识", style="cyan")
    table.add_column("名称", style="yellow")
    table.add_column("类型", style="magenta")
    table.add_column("描述", style="green")

    for theme in get_themes_list():
        theme_type = theme.get("type", "builtin")
        type_display = "内置" if theme_type == "builtin" else "CSS"
        table.add_row(theme["name"], theme["display_name"], type_display, theme["description"])

    console.print(table)
    console.print("\n[cyan]提示: 使用 --css 参数可指定自定义 CSS 文件（兼容 wenyan-cli 格式）[/cyan]")


# 主题管理命令组
theme_app = typer.Typer(help="主题管理")
app.add_typer(theme_app, name="theme")


@theme_app.command("list")
def theme_list() -> None:
    """列出所有主题"""
    from .converter.themes import list_themes as get_themes_list

    table = Table(title="排版主题")
    table.add_column("标识", style="cyan")
    table.add_column("名称", style="yellow")
    table.add_column("类型", style="magenta")
    table.add_column("描述", style="green")

    for theme in get_themes_list():
        theme_type = theme.get("type", "builtin")
        type_display = "内置" if theme_type == "builtin" else "CSS"
        table.add_row(theme["name"], theme["display_name"], type_display, theme["description"])

    console.print(table)


@theme_app.command("add")
def theme_add(
    name: str = typer.Option(..., "--name", "-n", help="主题名称（唯一标识）"),
    path: str = typer.Option(..., "--path", "-p", help="CSS 文件路径或 URL"),
) -> None:
    """添加自定义 CSS 主题（兼容 wenyan-cli 格式）"""
    from pathlib import Path
    from .converter.themes import register_theme, THEME_DIR
    import shutil

    # 确保主题目录存在
    THEME_DIR.mkdir(parents=True, exist_ok=True)

    # 如果是本地文件，复制到主题目录
    if not path.startswith(('http://', 'https://')):
        src_path = Path(path)
        if not src_path.exists():
            console.print(f"[red]文件不存在: {path}[/red]")
            raise typer.Exit(1)

        dest_path = THEME_DIR / f"{name}.css"
        shutil.copy(src_path, dest_path)
        console.print(f"[green]已复制 CSS 文件到: {dest_path}[/green]")
        path = str(dest_path)

    # 注册主题
    try:
        register_theme(path, name)
        console.print(f"[green]主题 '{name}' 已添加[/green]")
    except Exception as e:
        console.print(f"[red]添加主题失败: {e}[/red]")
        raise typer.Exit(1)


@theme_app.command("remove")
def theme_remove(
    name: str = typer.Argument(..., help="要删除的主题名称"),
) -> None:
    """删除自定义 CSS 主题"""
    from pathlib import Path
    from .converter.themes import THEMES, THEME_DIR

    # 检查是否是内置主题
    if name in ["default", "orange", "blue", "green", "purple", "simple"]:
        console.print(f"[red]不能删除内置主题: {name}[/red]")
        raise typer.Exit(1)

    # 删除 CSS 文件
    css_file = THEME_DIR / f"{name}.css"
    if css_file.exists():
        css_file.unlink()
        console.print(f"[green]已删除主题文件: {css_file}[/green]")

    # 从注册表移除
    if name in THEMES:
        del THEMES[name]
        console.print(f"[green]主题 '{name}' 已删除[/green]")
    else:
        console.print(f"[yellow]主题 '{name}' 不存在[/yellow]")


if __name__ == "__main__":
    app()