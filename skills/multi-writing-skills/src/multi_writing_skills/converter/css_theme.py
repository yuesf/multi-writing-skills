"""
CSS 主题解析器

解析 wenyan-cli 格式的 CSS 文件，转换为微信公众号可用的内联样式。
"""

import re
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

from .theme_types import ThemeStyles, ThemeColors


@dataclass
class CSSRule:
    """CSS 规则"""
    selector: str
    properties: Dict[str, str]


def parse_css(css_content: str) -> list[CSSRule]:
    """解析 CSS 内容，提取规则"""
    rules = []

    # 移除注释
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)

    # 匹配选择器和属性块
    pattern = r'([^{]+)\{([^}]+)\}'

    for match in re.finditer(pattern, css_content, re.DOTALL):
        selector = match.group(1).strip()
        properties_str = match.group(2).strip()

        # 解析属性
        properties = {}
        for prop in properties_str.split(';'):
            prop = prop.strip()
            if ':' in prop:
                key, value = prop.split(':', 1)
                properties[key.strip()] = value.strip()

        if properties:
            rules.append(CSSRule(selector=selector, properties=properties))

    return rules


def css_to_inline_style(rules: list[CSSRule]) -> Dict[str, str]:
    """将 CSS 规则转换为元素样式映射

    wenyan-cli 格式：
    - #wenyan h1 -> h1
    - #wenyan p -> p
    - #wenyan pre code -> code_block
    - #wenyan p code -> code_inline
    - #wenyan pre -> code_block_container
    """
    styles = {}

    # 选择器映射：wenyan-cli 选择器 -> 元素类型
    selector_map = {
        '#wenyan h1': 'h1',
        '#wenyan h2': 'h2',
        '#wenyan h3': 'h3',
        '#wenyan h4': 'h4',
        '#wenyan h5': 'h5',
        '#wenyan h6': 'h6',
        '#wenyan p': 'p',
        '#wenyan blockquote': 'blockquote',
        '#wenyan pre': 'pre',
        '#wenyan pre code': 'code_block',
        '#wenyan code': 'code_inline',
        '#wenyan p code': 'code_inline',
        '#wenyan ul': 'ul',
        '#wenyan ol': 'ol',
        '#wenyan li': 'li',
        '#wenyan table': 'table',
        '#wenyan table th': 'th',
        '#wenyan table td': 'td',
        '#wenyan table tr': 'tr',
        '#wenyan img': 'img',
        '#wenyan a': 'a',
        '#wenyan hr': 'hr',
        '#wenyan strong': 'strong',
        '#wenyan p strong': 'strong',
        '#wenyan em': 'em',
        '#wenyan': 'container',
    }

    for rule in rules:
        # 处理 #wenyan 前缀的选择器
        for wenyan_selector, element in selector_map.items():
            if rule.selector == wenyan_selector:
                if element not in styles:
                    styles[element] = {}

                # 合并属性，后面的覆盖前面的
                styles[element].update(rule.properties)

                # 处理特殊选择器
                if element == 'pre':
                    # pre::before 用于代码块头部
                    styles['pre_before'] = rule.properties.copy()

    # 转换为内联样式字符串
    result = {}
    for element, props in styles.items():
        if props:
            result[element] = props_to_string(props)

    return result


def props_to_string(props: Dict[str, str]) -> str:
    """将属性字典转换为内联样式字符串"""
    # CSS 属性名转换为 camelCase（用于某些特殊情况）
    # 但微信公众号支持 kebab-case，所以直接使用
    parts = []
    for key, value in props.items():
        # 跳过伪元素和不支持的属性
        if key in ('content', 'display', 'position', 'z-index', 'transform'):
            # 这些属性在内联样式中可能不生效或不需要
            if key != 'display':  # display 通常是有用的
                continue
        parts.append(f'{key}: {value};')

    return ' '.join(parts)


def load_css_theme(css_path: str, theme_name: str = "custom") -> ThemeStyles:
    """从 CSS 文件加载主题

    Args:
        css_path: CSS 文件路径（本地路径或 URL）
        theme_name: 主题名称

    Returns:
        ThemeStyles 对象
    """
    import httpx

    # 读取 CSS 内容
    if css_path.startswith(('http://', 'https://')):
        # 网络 URL
        with httpx.Client(timeout=30.0) as client:
            response = client.get(css_path)
            css_content = response.text
    else:
        # 本地文件
        path = Path(css_path)
        if not path.exists():
            raise FileNotFoundError(f"CSS 文件不存在: {css_path}")
        css_content = path.read_text(encoding='utf-8')

    # 解析 CSS
    rules = parse_css(css_content)
    styles = css_to_inline_style(rules)

    # 创建 ThemeStyles
    return ThemeStyles(
        name=theme_name,
        display_name=theme_name.capitalize(),
        description=f"从 {css_path} 加载的主题",
        colors=ThemeColors(),
        h1_style=styles.get('h1', ''),
        h2_style=styles.get('h2', ''),
        h3_style=styles.get('h3', ''),
        h4_style=styles.get('h4', ''),
        p_style=styles.get('p', ''),
        blockquote_style=styles.get('blockquote', ''),
        code_inline_style=styles.get('code_inline', ''),
        code_block_style=styles.get('code_block', styles.get('pre', '')),
        code_header_style=styles.get('pre_before', ''),
        ul_style=styles.get('ul', ''),
        ol_style=styles.get('ol', ''),
        li_style=styles.get('li', ''),
        table_style=styles.get('table', ''),
        th_style=styles.get('th', ''),
        td_style=styles.get('td', ''),
        img_style=styles.get('img', ''),
        a_style=styles.get('a', ''),
        hr_style=styles.get('hr', ''),
        strong_style=styles.get('strong', ''),
        em_style=styles.get('em', ''),
        container_style=styles.get('container', ''),
    )


def register_css_theme(css_path: str, theme_name: str, themes_dict: Optional[dict] = None) -> ThemeStyles:
    """注册 CSS 主题

    Args:
        css_path: CSS 文件路径
        theme_name: 主题名称（唯一标识）
        themes_dict: 主题字典（可选，用于注册主题）

    Returns:
        ThemeStyles 对象
    """
    theme = load_css_theme(css_path, theme_name)
    if themes_dict is not None:
        themes_dict[theme_name] = theme
    return theme


def list_css_themes(theme_dir: Path) -> list[dict]:
    """列出目录中的所有 CSS 主题

    Args:
        theme_dir: 主题目录

    Returns:
        主题信息列表
    """
    themes = []

    if not theme_dir.exists():
        return themes

    for css_file in theme_dir.glob('*.css'):
        theme_name = css_file.stem
        themes.append({
            'name': theme_name,
            'path': str(css_file),
            'display_name': theme_name.capitalize(),
            'description': f"CSS 主题: {css_file.name}",
        })

    return themes