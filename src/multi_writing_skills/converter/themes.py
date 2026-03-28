"""
微信公众号主题样式配置

支持多种主题，每个主题包含完整的样式配置。
兼容 wenyan-cli 的 CSS 主题格式，使用 #wenyan 容器选择器。
"""

from pathlib import Path
from typing import Optional

from .theme_types import ThemeStyles, ThemeColors
from .css_theme import load_css_theme, register_css_theme


# 主题存储目录
THEME_DIR = Path.home() / ".multi-writing-skills" / "themes"


# ============ 预设主题 ============

# 默认主题 - 深色代码块 + 美化表格
DEFAULT_THEME = ThemeStyles(
    name="default",
    display_name="默认主题",
    description="简洁清爽的默认主题",
    colors=ThemeColors(),
    h1_style="font-size: 24px; font-weight: bold; color: #333; margin: 20px 0 10px; padding-bottom: 10px; border-bottom: 2px solid #333;",
    h2_style="font-size: 20px; font-weight: bold; color: #333; margin: 18px 0 8px; padding-left: 12px; border-left: 4px solid #333; background: linear-gradient(90deg, #f5f5f5 0%, transparent 100%);",
    h3_style="font-size: 18px; font-weight: bold; color: #333; margin: 16px 0 6px; padding-bottom: 5px; border-bottom: 1px dashed #ccc;",
    h4_style="font-size: 16px; font-weight: bold; color: #333; margin: 14px 0 4px;",
    p_style="font-size: 15px; line-height: 1.8; color: #3f3f3f; margin: 10px 0; letter-spacing: 0.5px;",
    blockquote_style="background-color: #f8f8f8; border-left: 4px solid #555; padding: 12px 16px; margin: 16px 0; color: #555; font-size: 14px; border-radius: 0 6px 6px 0;",
    code_inline_style="background-color: #f0f0f0; color: #d14; padding: 3px 8px; border-radius: 4px; font-family: 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace; font-size: 14px;",
    code_block_style="background-color: #282c34; color: #abb2bf; border-radius: 8px; padding: 16px; margin: 16px 0; overflow-x: auto; font-family: 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace; font-size: 14px; line-height: 1.7; box-shadow: 0 2px 10px rgba(0,0,0,0.1);",
    code_header_style="background-color: #21252b; color: #abb2bf; padding: 8px 16px; font-size: 12px; border-radius: 8px 8px 0 0; border-bottom: 1px solid #333; font-family: 'SF Mono', Consolas, monospace;",
    ul_style="padding-left: 20px; margin: 10px 0; list-style-type: disc;",
    ol_style="padding-left: 20px; margin: 10px 0;",
    li_style="font-size: 15px; line-height: 1.8; color: #3f3f3f; margin: 6px 0;",
    table_style="width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);",
    th_style="background-color: #333; color: #fff; font-weight: bold; padding: 12px 15px; text-align: left; border: none;",
    td_style="padding: 12px 15px; border: none; border-bottom: 1px solid #eee;",
    tr_odd_style="background-color: #fff;",
    tr_even_style="background-color: #f9f9f9;",
    img_style="max-width: 100%; height: auto; display: block; margin: 15px auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);",
    a_style="color: #333; text-decoration: none; border-bottom: 1px solid #333;",
    hr_style="border: none; height: 2px; background: linear-gradient(90deg, transparent, #333, transparent); margin: 24px 0;",
    strong_style="font-weight: bold; color: #333;",
    em_style="font-style: italic; color: #555;",
    container_style='padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;',
)

# 橙心主题 - 温暖活力
ORANGE_THEME = ThemeStyles(
    name="orange",
    display_name="橙心主题",
    description="温暖活力的橙色主题",
    colors=ThemeColors(
        primary="#d9534f",
        secondary="#f0ad4e",
        accent="#ff6b6b",
        code_background="#2d2d2d",
        code_text="#f8f8f2",
        quote_border="#d9534f",
        link="#d9534f",
    ),
    h1_style="font-size: 24px; font-weight: bold; color: #d9534f; margin: 20px 0 10px; text-align: center;",
    h2_style="font-size: 20px; font-weight: bold; color: #fff; margin: 18px 0 8px; padding: 10px 16px; background: linear-gradient(135deg, #d9534f 0%, #f0ad4e 100%); border-radius: 6px;",
    h3_style="font-size: 18px; font-weight: bold; color: #d9534f; margin: 16px 0 6px; padding-left: 12px; border-left: 3px solid #f0ad4e;",
    h4_style="font-size: 16px; font-weight: bold; color: #333; margin: 14px 0 4px;",
    p_style="font-size: 15px; line-height: 1.8; color: #3f3f3f; margin: 10px 0; letter-spacing: 0.5px;",
    blockquote_style="background: linear-gradient(135deg, #fff5f5 0%, #fff 100%); border-left: 4px solid #d9534f; padding: 12px 16px; margin: 16px 0; color: #666; font-size: 14px; border-radius: 0 8px 8px 0;",
    code_inline_style="background-color: #fff5f5; color: #d9534f; padding: 3px 8px; border-radius: 4px; font-family: 'SF Mono', Consolas, monospace; font-size: 14px;",
    code_block_style="background-color: #2d2d2d; color: #f8f8f2; border-radius: 8px; padding: 16px; margin: 16px 0; overflow-x: auto; font-family: 'SF Mono', Consolas, monospace; font-size: 14px; line-height: 1.7; box-shadow: 0 4px 12px rgba(217, 83, 79, 0.15);",
    code_header_style="background-color: #252525; color: #f8f8f2; padding: 8px 16px; font-size: 12px; border-radius: 8px 8px 0 0; border-bottom: 1px solid #3a3a3a;",
    ul_style="padding-left: 20px; margin: 10px 0; list-style-type: disc;",
    ol_style="padding-left: 20px; margin: 10px 0;",
    li_style="font-size: 15px; line-height: 1.8; color: #3f3f3f; margin: 6px 0;",
    table_style="width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(217, 83, 79, 0.1);",
    th_style="background: linear-gradient(135deg, #d9534f 0%, #f0ad4e 100%); color: #fff; font-weight: bold; padding: 12px 15px; text-align: left; border: none;",
    td_style="padding: 12px 15px; border: none; border-bottom: 1px solid #f0f0f0;",
    tr_odd_style="background-color: #fff;",
    tr_even_style="background-color: #fffbf7;",
    img_style="max-width: 100%; height: auto; display: block; margin: 15px auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(217, 83, 79, 0.15);",
    a_style="color: #d9534f; text-decoration: none; border-bottom: 1px dashed #d9534f;",
    hr_style="border: none; height: 2px; background: linear-gradient(90deg, #d9534f, #f0ad4e, #d9534f); margin: 24px 0;",
    strong_style="font-weight: bold; color: #d9534f;",
    em_style="font-style: italic; color: #f0ad4e;",
    container_style='padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;',
)

# 蓝色主题 - 清新专业
BLUE_THEME = ThemeStyles(
    name="blue",
    display_name="蓝皓主题",
    description="清新专业的蓝色主题",
    colors=ThemeColors(
        primary="#3b8bba",
        secondary="#5bc0de",
        accent="#2a6496",
        code_background="#1e3a5f",
        code_text="#e6f3ff",
        quote_border="#3b8bba",
        link="#3b8bba",
        table_header_bg="#3b8bba",
    ),
    h1_style="font-size: 24px; font-weight: bold; color: #3b8bba; margin: 20px 0 10px; text-align: center; border-bottom: 2px solid #3b8bba; padding-bottom: 10px;",
    h2_style="font-size: 20px; font-weight: bold; color: #fff; margin: 18px 0 8px; padding: 10px 16px; background: #3b8bba; border-radius: 4px; box-shadow: 0 2px 8px rgba(59, 139, 186, 0.3);",
    h3_style="font-size: 18px; font-weight: bold; color: #3b8bba; margin: 16px 0 6px; border-bottom: 2px dotted #3b8bba; padding-bottom: 5px;",
    h4_style="font-size: 16px; font-weight: bold; color: #3b8bba; margin: 14px 0 4px;",
    p_style="font-size: 15px; line-height: 1.8; color: #3f3f3f; margin: 10px 0; letter-spacing: 0.5px;",
    blockquote_style="background: linear-gradient(135deg, #f0f7ff 0%, #fff 100%); border-left: 4px solid #3b8bba; padding: 12px 16px; margin: 16px 0; color: #555; font-size: 14px; border-radius: 0 8px 8px 0;",
    code_inline_style="background-color: #e8f4fc; color: #2a6496; padding: 3px 8px; border-radius: 4px; font-family: 'SF Mono', Consolas, monospace; font-size: 14px;",
    code_block_style="background-color: #1e3a5f; color: #e6f3ff; border-radius: 8px; padding: 16px; margin: 16px 0; overflow-x: auto; font-family: 'SF Mono', Consolas, monospace; font-size: 14px; line-height: 1.7; box-shadow: 0 4px 12px rgba(30, 58, 95, 0.3);",
    code_header_style="background-color: #163252; color: #7eb8e2; padding: 8px 16px; font-size: 12px; border-radius: 8px 8px 0 0; border-bottom: 1px solid #2a4a6a;",
    ul_style="padding-left: 20px; margin: 10px 0; list-style-type: disc;",
    ol_style="padding-left: 20px; margin: 10px 0;",
    li_style="font-size: 15px; line-height: 1.8; color: #3f3f3f; margin: 6px 0;",
    table_style="width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(59, 139, 186, 0.15);",
    th_style="background: #3b8bba; color: #fff; font-weight: bold; padding: 12px 15px; text-align: left; border: none;",
    td_style="padding: 12px 15px; border: none; border-bottom: 1px solid #e8f4fc;",
    tr_odd_style="background-color: #fff;",
    tr_even_style="background-color: #f5fafd;",
    img_style="max-width: 100%; height: auto; display: block; margin: 15px auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(59, 139, 186, 0.2);",
    a_style="color: #3b8bba; text-decoration: none; border-bottom: 1px solid #3b8bba;",
    hr_style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #3b8bba, transparent); margin: 24px 0;",
    strong_style="font-weight: bold; color: #3b8bba;",
    em_style="font-style: italic; color: #5bc0de;",
    container_style='padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;',
)

# 绿色主题 - 清新自然
GREEN_THEME = ThemeStyles(
    name="green",
    display_name="绿意主题",
    description="清新自然的绿色主题",
    colors=ThemeColors(
        primary="#27ae60",
        secondary="#2ecc71",
        accent="#1e8449",
        code_background="#1a3d2e",
        code_text="#d4edda",
        quote_border="#27ae60",
        link="#27ae60",
    ),
    h1_style="font-size: 24px; font-weight: bold; color: #27ae60; margin: 20px 0 10px; text-align: center;",
    h2_style="font-size: 20px; font-weight: bold; color: #27ae60; margin: 18px 0 8px; padding-left: 12px; border-left: 4px solid #27ae60; background: linear-gradient(90deg, #e8f8ee 0%, #fff 100%);",
    h3_style="font-size: 18px; font-weight: bold; color: #27ae60; margin: 16px 0 6px;",
    h4_style="font-size: 16px; font-weight: bold; color: #333; margin: 14px 0 4px;",
    p_style="font-size: 15px; line-height: 1.8; color: #3f3f3f; margin: 10px 0; letter-spacing: 0.5px;",
    blockquote_style="background-color: #e8f8ee; border-left: 4px solid #27ae60; padding: 12px 16px; margin: 16px 0; color: #555; font-size: 14px; border-radius: 0 8px 8px 0;",
    code_inline_style="background-color: #e8f8ee; color: #1e8449; padding: 3px 8px; border-radius: 4px; font-family: 'SF Mono', Consolas, monospace; font-size: 14px;",
    code_block_style="background-color: #1a3d2e; color: #d4edda; border-radius: 8px; padding: 16px; margin: 16px 0; overflow-x: auto; font-family: 'SF Mono', Consolas, monospace; font-size: 14px; line-height: 1.7; box-shadow: 0 4px 12px rgba(39, 174, 96, 0.15);",
    code_header_style="background-color: #143024; color: #7dcea0; padding: 8px 16px; font-size: 12px; border-radius: 8px 8px 0 0; border-bottom: 1px solid #2a5a3e;",
    ul_style="padding-left: 20px; margin: 10px 0; list-style-type: disc;",
    ol_style="padding-left: 20px; margin: 10px 0;",
    li_style="font-size: 15px; line-height: 1.8; color: #3f3f3f; margin: 6px 0;",
    table_style="width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(39, 174, 96, 0.1);",
    th_style="background: #27ae60; color: #fff; font-weight: bold; padding: 12px 15px; text-align: left; border: none;",
    td_style="padding: 12px 15px; border: none; border-bottom: 1px solid #e8f8ee;",
    tr_odd_style="background-color: #fff;",
    tr_even_style="background-color: #f5fdf8;",
    img_style="max-width: 100%; height: auto; display: block; margin: 15px auto; border-radius: 8px;",
    a_style="color: #27ae60; text-decoration: none;",
    hr_style="border: none; height: 2px; background: linear-gradient(90deg, transparent, #27ae60, transparent); margin: 24px 0;",
    strong_style="font-weight: bold; color: #27ae60;",
    em_style="font-style: italic;",
    container_style='padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;',
)

# 紫色主题 - 优雅神秘
PURPLE_THEME = ThemeStyles(
    name="purple",
    display_name="紫韵主题",
    description="优雅神秘的紫色主题",
    colors=ThemeColors(
        primary="#9b59b6",
        secondary="#8e44ad",
        accent="#6c3483",
        code_background="#2d1f3d",
        code_text="#e8daef",
        quote_border="#9b59b6",
        link="#9b59b6",
    ),
    h1_style="font-size: 24px; font-weight: bold; color: #9b59b6; margin: 20px 0 10px; text-align: center;",
    h2_style="font-size: 20px; font-weight: bold; color: #fff; margin: 18px 0 8px; padding: 10px 16px; background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); border-radius: 20px; display: inline-block;",
    h3_style="font-size: 18px; font-weight: bold; color: #9b59b6; margin: 16px 0 6px; padding-bottom: 5px; border-bottom: 2px dotted #9b59b6;",
    h4_style="font-size: 16px; font-weight: bold; color: #8e44ad; margin: 14px 0 4px;",
    p_style="font-size: 15px; line-height: 1.8; color: #3f3f3f; margin: 10px 0; letter-spacing: 0.5px;",
    blockquote_style="background-color: #f9f5fc; border-left: 4px solid #9b59b6; padding: 12px 16px; margin: 16px 0; color: #555; font-size: 14px; border-radius: 0 8px 8px 0;",
    code_inline_style="background-color: #f9f5fc; color: #9b59b6; padding: 3px 8px; border-radius: 4px; font-family: 'SF Mono', Consolas, monospace; font-size: 14px;",
    code_block_style="background-color: #2d1f3d; color: #e8daef; border-radius: 8px; padding: 16px; margin: 16px 0; overflow-x: auto; font-family: 'SF Mono', Consolas, monospace; font-size: 14px; line-height: 1.7; box-shadow: 0 4px 12px rgba(155, 89, 182, 0.2);",
    code_header_style="background-color: #231730; color: #bb8fce; padding: 8px 16px; font-size: 12px; border-radius: 8px 8px 0 0; border-bottom: 1px solid #3d2a50;",
    ul_style="padding-left: 20px; margin: 10px 0; list-style-type: disc;",
    ol_style="padding-left: 20px; margin: 10px 0;",
    li_style="font-size: 15px; line-height: 1.8; color: #3f3f3f; margin: 6px 0;",
    table_style="width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(155, 89, 182, 0.15);",
    th_style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); color: #fff; font-weight: bold; padding: 12px 15px; text-align: left; border: none;",
    td_style="padding: 12px 15px; border: none; border-bottom: 1px solid #f3e5f5;",
    tr_odd_style="background-color: #fff;",
    tr_even_style="background-color: #fcf5fe;",
    img_style="max-width: 100%; height: auto; display: block; margin: 15px auto; border-radius: 8px;",
    a_style="color: #9b59b6; text-decoration: none;",
    hr_style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #9b59b6, transparent); margin: 24px 0;",
    strong_style="font-weight: bold; color: #9b59b6;",
    em_style="font-style: italic; color: #8e44ad;",
    container_style='padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;',
)

# 简约主题 - 极简风格
SIMPLE_THEME = ThemeStyles(
    name="simple",
    display_name="简约主题",
    description="极简风格，专注内容",
    colors=ThemeColors(
        primary="#333333",
        secondary="#666666",
        code_background="#fafafa",
        code_text="#333",
        quote_border="#e0e0e0",
        link="#333333",
    ),
    h1_style="font-size: 22px; font-weight: bold; color: #333; margin: 25px 0 15px; text-align: center;",
    h2_style="font-size: 18px; font-weight: bold; color: #333; margin: 20px 0 10px;",
    h3_style="font-size: 16px; font-weight: bold; color: #333; margin: 15px 0 8px;",
    h4_style="font-size: 15px; font-weight: bold; color: #333; margin: 12px 0 6px;",
    p_style="font-size: 15px; line-height: 2; color: #333; margin: 12px 0;",
    blockquote_style="border-left: 3px solid #e0e0e0; padding-left: 15px; margin: 15px 0; color: #666; font-size: 14px;",
    code_inline_style="color: #c7254e; font-family: 'SF Mono', Consolas, monospace; font-size: 14px;",
    code_block_style="background-color: #fafafa; padding: 16px; margin: 16px 0; overflow-x: auto; font-family: 'SF Mono', Consolas, monospace; font-size: 14px; line-height: 1.7; border: 1px solid #eee; border-radius: 4px;",
    code_header_style="background-color: #f5f5f5; color: #666; padding: 6px 16px; font-size: 12px; border-bottom: 1px solid #eee; font-family: 'SF Mono', Consolas, monospace;",
    ul_style="padding-left: 20px; margin: 10px 0; list-style-type: disc;",
    ol_style="padding-left: 20px; margin: 10px 0;",
    li_style="font-size: 15px; line-height: 2; color: #333; margin: 3px 0;",
    table_style="width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px;",
    th_style="font-weight: bold; border-bottom: 2px solid #333; padding: 12px; text-align: left; background: none;",
    td_style="border-bottom: 1px solid #eee; padding: 12px;",
    tr_odd_style="background-color: #fff;",
    tr_even_style="background-color: #fafafa;",
    img_style="max-width: 100%; height: auto; display: block; margin: 20px auto;",
    a_style="color: #333; text-decoration: underline;",
    hr_style="border: none; border-top: 1px solid #e0e0e0; margin: 25px 0;",
    strong_style="font-weight: bold;",
    em_style="font-style: italic;",
    container_style='padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;',
)

# 主题注册表
THEMES: dict[str, ThemeStyles] = {
    "default": DEFAULT_THEME,
    "orange": ORANGE_THEME,
    "blue": BLUE_THEME,
    "green": GREEN_THEME,
    "purple": PURPLE_THEME,
    "simple": SIMPLE_THEME,
}


def get_theme(name: str, css_path: Optional[str] = None) -> ThemeStyles:
    """获取主题配置

    Args:
        name: 主题名称
        css_path: 可选的 CSS 文件路径（本地或 URL）

    Returns:
        ThemeStyles 对象
    """
    # 如果指定了 CSS 文件，加载 CSS 主题
    if css_path:
        return load_css_theme(css_path, name)

    # 如果是内置主题，直接返回
    if name in THEMES:
        return THEMES[name]

    # 检查是否是用户自定义 CSS 主题
    css_file = THEME_DIR / f"{name}.css"
    if css_file.exists():
        return load_css_theme(str(css_file), name)

    # 返回默认主题
    return DEFAULT_THEME


def register_theme(css_path: str, name: Optional[str] = None) -> ThemeStyles:
    """注册自定义 CSS 主题

    Args:
        css_path: CSS 文件路径（本地或 URL）
        name: 主题名称，默认从文件名提取

    Returns:
        ThemeStyles 对象
    """
    global THEMES
    if not name:
        name = Path(css_path).stem

    theme = register_css_theme(css_path, name, THEMES)
    return theme


def list_themes() -> list[dict]:
    """列出所有主题（内置 + 自定义 CSS）"""
    result = []

    # 内置主题
    for theme in THEMES.values():
        result.append({
            "name": theme.name,
            "display_name": theme.display_name,
            "description": theme.description,
            "type": "builtin",
        })

    # 自定义 CSS 主题
    if THEME_DIR.exists():
        for css_file in THEME_DIR.glob("*.css"):
            name = css_file.stem
            result.append({
                "name": name,
                "display_name": name.capitalize(),
                "description": f"CSS 主题: {css_file.name}",
                "type": "css",
                "path": str(css_file),
            })

    return result