"""
主题数据类型定义

定义主题的数据结构，避免循环导入。
"""

from dataclasses import dataclass, field


@dataclass
class ThemeColors:
    """主题颜色配置"""

    primary: str = "#333333"
    secondary: str = "#666666"
    accent: str = "#3f3f3f"
    background: str = "#ffffff"
    code_background: str = "#282c34"
    code_text: str = "#abb2bf"
    quote_background: str = "#f7f7f7"
    quote_border: str = "#ddd"
    link: str = "#576b95"
    table_header_bg: str = "#f5f5f5"


@dataclass
class ThemeStyles:
    """主题样式配置 - 兼容 wenyan-cli 的 #wenyan 容器格式"""

    name: str = "default"
    display_name: str = "默认主题"
    description: str = "简洁清爽的默认主题"
    colors: ThemeColors = field(default_factory=ThemeColors)

    # 标题样式
    h1_style: str = ""
    h2_style: str = ""
    h3_style: str = ""
    h4_style: str = ""

    # 段落样式
    p_style: str = ""

    # 引用样式
    blockquote_style: str = ""

    # 代码样式
    code_inline_style: str = ""
    code_block_style: str = ""
    code_header_style: str = ""  # 代码块头部样式

    # 列表样式
    ul_style: str = ""
    ol_style: str = ""
    li_style: str = ""

    # 表格样式
    table_style: str = ""
    th_style: str = ""
    td_style: str = ""
    tr_odd_style: str = ""  # 奇数行样式
    tr_even_style: str = ""  # 偶数行样式

    # 图片样式
    img_style: str = ""

    # 其他样式
    a_style: str = ""
    hr_style: str = ""
    strong_style: str = ""
    em_style: str = ""

    # 整体容器样式 - 使用 #wenyan 选择器格式
    container_style: str = ""