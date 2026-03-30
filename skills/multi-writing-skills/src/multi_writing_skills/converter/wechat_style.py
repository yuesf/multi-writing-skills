"""
微信公众号样式转换器

完全重写列表和代码块转换逻辑，确保格式正确。
支持 wenyan-cli 格式的 CSS 主题。
"""

import re
from typing import Optional, List, Tuple
from dataclasses import dataclass

from .theme_types import ThemeStyles
from .themes import get_theme, THEMES


@dataclass
class CodeBlock:
    """代码块"""
    lang: str
    code: str
    start: int
    end: int


@dataclass
class ListItem:
    """列表项"""
    level: int
    ordered: bool
    content: str
    number: int = 0


class WeChatStyleConverter:
    """微信公众号样式转换器"""

    def __init__(self, theme: str = "default", css_path: Optional[str] = None):
        self.theme_name = theme
        self.css_path = css_path
        self.theme: ThemeStyles = get_theme(theme, css_path)

    def set_theme(self, theme: str, css_path: Optional[str] = None) -> None:
        self.theme_name = theme
        self.css_path = css_path
        self.theme = get_theme(theme, css_path)

    def convert(self, markdown: str, title: Optional[str] = None) -> str:
        """转换 Markdown 为带样式的 HTML"""
        # 1. 先处理代码块（避免被其他处理干扰）
        markdown, code_blocks = self._extract_code_blocks(markdown)

        # 2. 处理表格
        html = self._convert_tables(markdown)

        # 3. 处理标题
        html = self._convert_headers(html)

        # 4. 处理引用块
        html = self._convert_blockquotes(html)

        # 5. 处理列表（完全重写）
        html = self._convert_lists(html)

        # 6. 处理分割线
        html = self._convert_hr(html)

        # 7. 处理图片
        html = self._convert_images(html)

        # 8. 处理链接
        html = self._convert_links(html)

        # 9. 处理行内代码
        html = self._convert_inline_code(html)

        # 10. 处理粗体和斜体
        html = self._convert_strong_em(html)

        # 11. 处理段落
        html = self._convert_paragraphs(html)

        # 12. 恢复代码块
        html = self._restore_code_blocks(html, code_blocks)

        # 后处理
        html = self._postprocess(html)

        # 添加标题
        if title:
            html = f'<section style="text-align: center; margin-bottom: 20px;"><h1 style="{self.theme.h1_style}">{title}</h1></section>{html}'

        return html

    # ============ 代码块处理 ============

    def _extract_code_blocks(self, text: str) -> Tuple[str, List[CodeBlock]]:
        """提取代码块，用占位符替换"""
        code_blocks = []
        pattern = r'```(\w*)\n(.*?)```'

        def replace(match):
            lang = match.group(1) or "text"
            code = match.group(2)
            index = len(code_blocks)
            code_blocks.append(CodeBlock(lang=lang, code=code, start=match.start(), end=match.end()))
            return f'\x00CODE_BLOCK_{index}\x00'

        text = re.sub(pattern, replace, text, flags=re.DOTALL)
        return text, code_blocks

    def _restore_code_blocks(self, html: str, code_blocks: List[CodeBlock]) -> str:
        """恢复代码块并渲染"""
        for i, block in enumerate(code_blocks):
            placeholder = f'\x00CODE_BLOCK_{i}\x00'
            rendered = self._render_code_block(block)
            html = html.replace(placeholder, rendered)
        return html

    def _render_code_block(self, block: CodeBlock) -> str:
        """渲染单个代码块"""
        code = block.code

        # 1. 格式化代码：统一处理缩进，移除首尾空行，确保一致的行尾
        code = self._format_code(code)

        # 2. 先完全转义 HTML（此时代码是纯净的原始代码）
        code = code.replace('&', '&amp;')
        code = code.replace('<', '&lt;')
        code = code.replace('>', '&gt;')

        # 3. 然后在转义后的代码上进行高亮
        code = self._highlight_code_escaped(code, block.lang)

        # 4. 处理缩进：将前导空格转换为 &nbsp;，同时处理制表符
        # 微信公众号需要用 <br> 强制换行，仅靠 \n 在 pre 标签中不生效
        lines = code.split('\n')
        processed_lines = []
        for line in lines:
            # 将制表符转换为 4 个空格
            line = line.expandtabs(4)
            # 统计前导空格
            leading_spaces = len(line) - len(line.lstrip(' '))
            if leading_spaces > 0:
                line = '&nbsp;' * leading_spaces + line.lstrip(' ')
            processed_lines.append(line)

        code = '<br>'.join(processed_lines)

        # 语言名称和图标颜色
        lang_names = {
            'python': ('Python', '#3572A5'),
            'py': ('Python', '#3572A5'),
            'javascript': ('JavaScript', '#f7df1e'),
            'js': ('JavaScript', '#f7df1e'),
            'typescript': ('TypeScript', '#3178c6'),
            'ts': ('TypeScript', '#3178c6'),
            'java': ('Java', '#b07219'),
            'go': ('Go', '#00ADD8'),
            'rust': ('Rust', '#dea584'),
            'cpp': ('C++', '#f34b7d'),
            'c': ('C', '#555555'),
            'sql': ('SQL', '#e38c00'),
            'bash': ('Bash', '#4EAA25'),
            'shell': ('Shell', '#4EAA25'),
            'json': ('JSON', '#292929'),
            'yaml': ('YAML', '#cb171e'),
            'yml': ('YAML', '#cb171e'),
            'html': ('HTML', '#e34c26'),
            'css': ('CSS', '#563d7c'),
            'xml': ('XML', '#0060ac'),
            'markdown': ('Markdown', '#083fa1'),
            'md': ('Markdown', '#083fa1'),
            'text': ('Code', '#666666'),
            '': ('Code', '#666666'),
        }
        lang_info = lang_names.get(block.lang.lower(), (block.lang.upper() if block.lang else 'Code', '#666666'))
        lang_display = lang_info[0]
        lang_color = lang_info[1]

        # 样式 - 优化代码块视觉效果
        code_style = (
            "background-color: #282c34; "
            "color: #abb2bf; "
            "border-radius: 0 0 8px 8px; "
            "padding: 16px; "
            "margin: 0; "
            "overflow-x: auto; "
            "font-family: 'SF Mono', 'Fira Code', Consolas, 'Liberation Mono', Menlo, monospace; "
            "font-size: 13px; "
            "line-height: 1.6; "
            "box-shadow: 0 4px 12px rgba(0,0,0,0.15); "
        )

        # 代码块头部样式 - Mac 风格窗口
        header_style = (
            "background-color: #21252b; "
            "color: #abb2bf; "
            "padding: 12px 16px; "
            "font-size: 12px; "
            "border-radius: 8px 8px 0 0; "
            "border-bottom: 1px solid #181a1f; "
            "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; "
            "display: flex; "
            "align-items: center; "
            "gap: 8px;"
        )

        return f'''<figure style="margin: 24px 0; border-radius: 8px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.15); background: #282c34;">
<section style="{header_style}">
<span style="width: 12px; height: 12px; border-radius: 50%; background: #ff5f56; box-shadow: inset 0 -1px 1px rgba(0,0,0,0.1);"></span>
<span style="width: 12px; height: 12px; border-radius: 50%; background: #ffbd2e; box-shadow: inset 0 -1px 1px rgba(0,0,0,0.1);"></span>
<span style="width: 12px; height: 12px; border-radius: 50%; background: #27c93f; box-shadow: inset 0 -1px 1px rgba(0,0,0,0.1);"></span>
<span style="margin-left: 8px; color: #5c6370; font-size: 11px;">{lang_display}</span>
</section>
<pre style="{code_style}"><code>{code}</code></pre>
</figure>'''

    def _format_code(self, code: str) -> str:
        """格式化代码块：
        - 移除首尾空行
        - 统一换行符
        - 移除尾部多余空格
        """
        # 统一换行符
        code = code.replace('\r\n', '\n').replace('\r', '\n')
        # 按行分割
        lines = code.split('\n')
        # 处理每一行：移除行尾空格
        lines = [line.rstrip() for line in lines]
        # 移除开头空行
        while lines and lines[0].strip() == '':
            lines.pop(0)
        # 移除结尾空行
        while lines and lines[-1].strip() == '':
            lines.pop()
        # 重新连接
        return '\n'.join(lines)

    def _highlight_code(self, code: str, lang: str) -> str:
        """语法高亮 - 在原始代码上应用高亮（已废弃，请使用 _highlight_code_escaped）"""
        return code

    def _highlight_code_escaped(self, code: str, lang: str) -> str:
        """语法高亮 - 在已转义的代码上应用高亮

        由于代码已经被 HTML 转义（< -> &lt;, > -> &gt;），
        可以安全地使用 span 标签进行高亮，不会与 HTML 标签冲突
        """
        # 颜色定义 (One Dark 主题)
        colors = {
            'keyword': '#c678dd',      # 紫色 - 关键字
            'string': '#98c379',       # 绿色 - 字符串
            'number': '#d19a66',       # 橙色 - 数字
            'comment': '#75715e',      # 灰色 - 注释
            'class': '#e5c07b',        # 黄色 - 类名
            'decorator': '#d19a66',    # 橙色 - 装饰器
            'builtin': '#e06c75',      # 红色 - 内置函数
        }

        # 关键字列表
        keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'return',
            'import', 'from', 'as', 'try', 'except', 'finally', 'with',
            'lambda', 'yield', 'raise', 'pass', 'break', 'continue',
            'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is',
            'async', 'await', 'global', 'nonlocal', 'del', 'assert',
            'const', 'let', 'var', 'function', 'export', 'new', 'this',
            'super', 'extends', 'interface', 'type', 'struct', 'map',
            'func', 'package', 'go', 'defer', 'chan', 'range', 'select',
            'switch', 'case', 'default', 'catch', 'throw', 'typeof',
            'instanceof', 'void', 'null', 'undefined', 'true', 'false',
            'nil', 'make', 'goto', 'fallthrough']

        # 1. 字符串高亮 - 转义后双引号变成 &quot;
        code = re.sub(r'&quot;([^&]*)&quot;', rf'<span style="color: {colors["string"]};">&quot;\1&quot;</span>', code)
        code = re.sub(r'&#39;([^&]*)&#39;', rf'<span style="color: {colors["string"]};">&#39;\1&#39;</span>', code)

        # 2. 注释高亮
        code = re.sub(r'(?<=\n|\s)#(.*?)(?=\n|$)', rf'<span style="color: {colors["comment"]}; font-style: italic;">#\1</span>', code)

        # 3. 数字高亮
        code = re.sub(r'\b(\d+\.?\d*)\b', rf'<span style="color: {colors["number"]};">\1</span>', code)

        # 4. 装饰器
        code = re.sub(r'(@\w+)', rf'<span style="color: {colors["decorator"]};">\1</span>', code)

        # 5. 关键字
        for kw in keywords:
            code = re.sub(
                rf'(?<![a-zA-Z0-9_]){re.escape(kw)}(?![a-zA-Z0-9_])',
                rf'<span style="color: {colors["keyword"]};">{kw}</span>',
                code,
                flags=re.IGNORECASE
            )

        # 6. 类名 (PascalCase)
        code = re.sub(r'\b([A-Z][a-zA-Z0-9]+)\b', rf'<span style="color: {colors["class"]};">\1</span>', code)

        return code

    # ============ 列表处理（完全重写）============

    def _convert_lists(self, text: str) -> str:
        """转换列表 - 完全重写，支持嵌套"""
        lines = text.split('\n')
        result = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # 检测无序列表项（允许内容为空）
            ul_match = re.match(r'^(\s*)[-*+]\s*(.*)$', line)
            # 检测有序列表项（允许内容为空）
            ol_match = re.match(r'^(\s*)(\d+)\.\s*(.*)$', line)

            if ul_match or ol_match:
                # 找到了列表开始，收集整个列表块
                list_html, consumed = self._parse_list_block(lines, i)
                result.append(list_html)
                i += consumed
            else:
                result.append(line)
                i += 1

        return '\n'.join(result)

    def _parse_list_block(self, lines: List[str], start: int) -> Tuple[str, int]:
        """解析整个列表块（空行不中断列表，允许列表项之间有空行）"""
        items = []
        i = start
        first_is_ordered = None  # 第一个列表项是否是有序列表
        first_number = 1  # 有序列表的起始编号

        while i < len(lines):
            line = lines[i]

            # 检测无序列表项（允许内容为空）
            ul_match = re.match(r'^(\s*)[-*+]\s*(.*)$', line)
            # 检测有序列表项（允许内容为空）
            ol_match = re.match(r'^(\s*)(\d+)\.\s*(.*)$', line)

            # 跳过纯空行（检查后面是否还有列表项）
            if line.strip() == '':
                # 查找下一个非空行
                next_non_empty = i + 1
                while next_non_empty < len(lines) and lines[next_non_empty].strip() == '':
                    next_non_empty += 1

                if next_non_empty >= len(lines):
                    # 后面没有内容了，结束列表
                    i += 1
                    break

                next_line = lines[next_non_empty]
                next_ul = re.match(r'^(\s*)[-*+]\s*(.*)$', next_line)
                next_ol = re.match(r'^(\s*)(\d+)\.\s*(.*)$', next_line)

                # 如果下一个非空行还是列表项，继续
                if next_ul or (next_ol and first_is_ordered):
                    i += 1
                    continue
                else:
                    # 下一个非空行不是列表项，结束
                    i += 1
                    break

            # 跳过不匹配的行
            if not ul_match and not ol_match:
                break

            if ul_match:
                indent = len(ul_match.group(1))
                content = ul_match.group(2).strip()
                if first_is_ordered is None:
                    first_is_ordered = False
                # 跳过空内容的无序列表项（单独的 - * +）
                if content:
                    items.append((indent, False, content, 0))
                i += 1
            elif ol_match:
                indent = len(ol_match.group(1))
                number = int(ol_match.group(2))
                content = ol_match.group(3).strip()
                if first_is_ordered is None:
                    first_is_ordered = True
                    first_number = number  # 记录第一个有序列表项的编号
                # 跳过空内容的有序列表项（单独的 1. 2. 3.）
                if content:
                    # 如果第一个有内容的项编号是 first_number+1 且第一个空项编号是 first_number
                    # 说明列表应该从 first_number 开始
                    items.append((indent, True, content, number))
                i += 1

        # 调整有序列表的编号：如果第一个列表项为空且编号为 1，后续项编号减 1
        if first_is_ordered and items:
            # 检查第一个有内容的项的编号是否比 first_number 大 1
            if items[0][3] == first_number + 1:
                # 列表应该从 first_number 开始，调整所有项的编号
                adjusted_items = [(indent, ordered, content, number - 1) for indent, ordered, content, number in items]
                items = adjusted_items

        # 渲染列表
        html = self._render_list_items(items)
        return html, i - start

    def _render_list_items(self, items: List[Tuple[int, bool, str, int]]) -> str:
        """渲染列表项为 HTML - 使用 div 模拟列表，避免微信重新解析"""
        if not items:
            return ''

        # 判断列表类型
        first_ordered = items[0][1]

        # 使用 div 模拟列表，避免微信编辑器重新解析
        # 无序列表：使用圆点字符 •
        # 有序列表：使用数字编号

        html_parts = []

        if first_ordered:
            # 有序列表
            list_style = self.theme.ol_style
            # 提取 padding-left 值用于缩进
            padding_match = re.search(r'padding-left:\s*(\d+)px', list_style)
            padding_left = int(padding_match.group(1)) if padding_match else 20

            for indent, ordered, content, number in items:
                # 处理内联格式
                content = self._process_inline(content)
                # 使用 section 模拟有序列表项
                html_parts.append(
                    f'<section style="display: flex; align-items: flex-start; margin: 6px 0; padding-left: {padding_left}px;">'
                    f'<span style="min-width: 20px; color: #3f3f3f; font-size: 15px;">{number}.</span>'
                    f'<span style="flex: 1; color: #3f3f3f; font-size: 15px; line-height: 1.8;">{content}</span>'
                    f'</section>'
                )
        else:
            # 无序列表
            list_style = self.theme.ul_style
            # 提取 padding-left 值用于缩进
            padding_match = re.search(r'padding-left:\s*(\d+)px', list_style)
            padding_left = int(padding_match.group(1)) if padding_match else 20

            for indent, ordered, content, number in items:
                # 处理内联格式
                content = self._process_inline(content)
                # 使用 section 模拟无序列表项，使用 • 作为项目符号
                html_parts.append(
                    f'<section style="display: flex; align-items: flex-start; margin: 6px 0; padding-left: {padding_left}px;">'
                    f'<span style="min-width: 20px; color: #3f3f3f; font-size: 15px;">•</span>'
                    f'<span style="flex: 1; color: #3f3f3f; font-size: 15px; line-height: 1.8;">{content}</span>'
                    f'</section>'
                )

        return '\n'.join(html_parts)

    def _process_inline(self, text: str) -> str:
        """处理行内格式（粗体、斜体、行内代码）"""
        # 行内代码
        text = re.sub(r'`([^`]+)`', f'<code style="{self.theme.code_inline_style}">\\1</code>', text)
        # 粗体
        text = re.sub(r'\*\*([^*]+)\*\*', f'<strong style="{self.theme.strong_style}">\\1</strong>', text)
        text = re.sub(r'__([^_]+)__', f'<strong style="{self.theme.strong_style}">\\1</strong>', text)
        # 斜体
        text = re.sub(r'\*([^*]+)\*', f'<em style="{self.theme.em_style}">\\1</em>', text)
        # 下划线斜体：不处理包含大写字母的（避免误处理代码块占位符）
        text = re.sub(r'_([a-z][^_]*[a-z])_', f'<em style="{self.theme.em_style}">\\1</em>', text)
        return text

    # ============ 其他元素处理 ============

    def _convert_headers(self, text: str) -> str:
        """转换标题"""
        lines = text.split('\n')
        result = []

        for line in lines:
            if line.startswith('###### '):
                result.append(f'<h6 style="{self.theme.h4_style}">{line[7:]}</h6>')
            elif line.startswith('##### '):
                result.append(f'<h5 style="{self.theme.h4_style}">{line[6:]}</h5>')
            elif line.startswith('#### '):
                result.append(f'<h4 style="{self.theme.h4_style}">{line[5:]}</h4>')
            elif line.startswith('### '):
                result.append(f'<h3 style="{self.theme.h3_style}">{line[4:]}</h3>')
            elif line.startswith('## '):
                result.append(f'<h2 style="{self.theme.h2_style}">{line[3:]}</h2>')
            elif line.startswith('# '):
                result.append(f'<h1 style="{self.theme.h1_style}">{line[2:]}</h1>')
            else:
                result.append(line)

        return '\n'.join(result)

    def _convert_blockquotes(self, text: str) -> str:
        """转换引用块"""
        lines = text.split('\n')
        result = []
        quote_lines = []

        for line in lines:
            if line.startswith('> '):
                quote_lines.append(line[2:])
            elif line.startswith('>'):
                quote_lines.append(line[1:])
            else:
                if quote_lines:
                    content = '<br>'.join(quote_lines)
                    result.append(f'<blockquote style="{self.theme.blockquote_style}">{content}</blockquote>')
                    quote_lines = []
                result.append(line)

        if quote_lines:
            content = '<br>'.join(quote_lines)
            result.append(f'<blockquote style="{self.theme.blockquote_style}">{content}</blockquote>')

        return '\n'.join(result)

    def _convert_tables(self, text: str) -> str:
        """转换表格"""
        lines = text.split('\n')
        result = []
        in_table = False
        is_header = True
        row_index = 0

        for line in lines:
            if '|' in line and line.strip().startswith('|'):
                cells = [c.strip() for c in line.split('|')[1:-1]]

                if not in_table:
                    result.append(f'<table style="{self.theme.table_style}">')
                    result.append('<thead>')
                    in_table = True
                    is_header = True

                # 跳过分隔行
                if all(set(c) <= {'-', ':', ' '} for c in cells):
                    result.append('</thead><tbody>')
                    is_header = False
                    continue

                if is_header:
                    cells_html = ''.join([f'<th style="{self.theme.th_style}">{c}</th>' for c in cells])
                    result.append(f'<tr>{cells_html}</tr>')
                else:
                    row_index += 1
                    row_style = self.theme.tr_odd_style if row_index % 2 == 1 else self.theme.tr_even_style
                    cells_html = ''.join([f'<td style="{self.theme.td_style}">{c}</td>' for c in cells])
                    result.append(f'<tr style="{row_style}">{cells_html}</tr>')
            else:
                if in_table:
                    result.append('</tbody></table>')
                    in_table = False
                result.append(line)

        if in_table:
            result.append('</tbody></table>')

        return '\n'.join(result)

    def _convert_hr(self, text: str) -> str:
        """转换分割线"""
        return re.sub(r'^---+$', f'<hr style="{self.theme.hr_style}">', text, flags=re.MULTILINE)

    def _convert_images(self, text: str) -> str:
        """转换图片"""
        return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',
                      f'<img src="\\2" alt="\\1" style="{self.theme.img_style}">', text)

    def _convert_links(self, text: str) -> str:
        """转换链接"""
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                      f'<a href="\\2" style="{self.theme.a_style}">\\1</a>', text)

    def _convert_inline_code(self, text: str) -> str:
        """转换行内代码"""
        return re.sub(r'`([^`]+)`', f'<code style="{self.theme.code_inline_style}">\\1</code>', text)

    def _convert_strong_em(self, text: str) -> str:
        """转换粗体和斜体"""
        text = re.sub(r'\*\*([^*]+)\*\*', f'<strong style="{self.theme.strong_style}">\\1</strong>', text)
        text = re.sub(r'__([^_]+)__', f'<strong style="{self.theme.strong_style}">\\1</strong>', text)
        text = re.sub(r'\*([^*]+)\*', f'<em style="{self.theme.em_style}">\\1</em>', text)
        # 下划线斜体：不处理包含大写字母的（避免误处理代码块占位符如 CODE_BLOCK_0）
        text = re.sub(r'_([a-z][^_]*[a-z])_', f'<em style="{self.theme.em_style}">\\1</em>', text)
        return text

    def _convert_paragraphs(self, text: str) -> str:
        """转换段落"""
        lines = text.split('\n')
        result = []

        for line in lines:
            stripped = line.strip()
            # 跳过已转换的块元素
            if stripped.startswith(('<h1', '<h2', '<h3', '<h4', '<h5', '<h6',
                                    '<ul', '<ol', '<li', '</ul', '</ol',
                                    '<blockquote', '<figure', '<table', '<thead',
                                    '<tbody', '</thead', '</tbody', '<tr', '</tr',
                                    '<th', '<td', '</table', '</th', '</td',
                                    '<hr', '<img', '<section', '<p', '</section')):
                result.append(line)
            # 跳过代码块占位符
            elif '\x00CODE_BLOCK_' in stripped:
                result.append(line)
            # 跳过空行
            elif stripped == '':
                result.append('')
            # 跳过只包含标签的行
            elif re.match(r'^</?[a-z]+>$', stripped):
                result.append(line)
            elif stripped:
                result.append(f'<p style="{self.theme.p_style}">{stripped}</p>')

        return '\n'.join(result)

    def _postprocess(self, text: str) -> str:
        """后处理 - 使用 #wenyan 容器格式（兼容 wenyan-cli）"""
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 使用 id="wenyan" 容器，兼容 wenyan-cli 的 CSS 主题格式
        text = f'<section id="wenyan" style="{self.theme.container_style}">{text}</section>'
        return text


def get_available_themes() -> List[str]:
    """获取所有可用主题名称"""
    return list(THEMES.keys())