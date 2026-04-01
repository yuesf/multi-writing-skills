"""
Markdown → PDF 转换模块
将 Markdown 内容转换为精美的 PDF 文档
"""

import re
import sys
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 页面宽度（A4，左右各 2cm 边距）
PW = A4[0]
MG = 2.0 * cm
CW = PW - 2 * MG  # 内容宽度

# 检测CJK字体
FONT = "Helvetica"
CJKFONT = None
for p in [
    "/usr/share/fonts/google-noto-cjk/NotoSansCJK-DemiLight.ttc,0",
    "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Light.ttc,0",
    "/usr/share/fonts/google-droid/DroidSansFallback.ttf",
]:
    if p.split(",")[0] if "," in p else p:
        path = p.split(",")[0]
        if Path(path).exists():
            try:
                if path.endswith(".ttc"):
                    pdfmetrics.registerFont(TTFont("CJK", path, subfontIndex=0))
                else:
                    pdfmetrics.registerFont(TTFont("CJK", path))
                CJKFONT = "CJK"
                FONT = "CJK"
                break
            except Exception:
                pass

# 颜色
white = colors.white
dark = colors.HexColor("#1E293B")
gray = colors.HexColor("#64748B")
border = colors.HexColor("#E2E8F0")
light_bg = colors.HexColor("#F8FAFC")
code_bg = colors.HexColor("#1E1E2E")
accent = colors.HexColor("#F97316")


def _S(name, **kw):
    """创建段落样式"""
    defaults = dict(fontName=FONT, fontSize=10, leading=14, textColor=dark)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)


ST = {
    "h1": _S("h1", fontSize=22, leading=28, textColor=dark, fontName=FONT, spaceAfter=6),
    "h2": _S("h2", fontSize=15, leading=20, textColor=dark, fontName=FONT, spaceBefore=14, spaceAfter=4),
    "h3": _S("h3", fontSize=12, leading=16, textColor=dark, fontName=FONT, spaceBefore=10, spaceAfter=3),
    "body": _S("body", fontSize=10, leading=15, textColor=dark),
    "small": _S("small", fontSize=9, leading=13, textColor=gray),
    "code": _S("code", fontName="Courier", fontSize=8.5, leading=13, textColor=colors.HexColor("#E2E8F0")),
    "code_cjk": _S("code_cjk", fontName=CJKFONT or FONT, fontSize=8.5, leading=13, textColor=colors.HexColor("#E2E8F0")),
    "th": _S("th", fontName=FONT, fontSize=9, textColor=white, leading=13),
    "td": _S("td", fontName=FONT, fontSize=9, textColor=dark, leading=13),
}


def _pick_font(line: str) -> str:
    """判断一行文本是否包含中文，选择合适字体"""
    return CJKFONT if CJKFONT and any(ord(c) > 0x3000 for c in line) else "Courier"


def _escape(text: str) -> str:
    """转义 HTML 特殊字符"""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;"))


def _render_inline(text: str) -> str:
    """简单渲染 inline markdown（粗体、斜体、行内代码）"""
    # 行内代码 `code`
    text = re.sub(r"`([^`]+)`", r"<font face='Courier'>\1</font>", text)
    # 粗体 **text**
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    # 斜体 *text*
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    # 图片 ![alt](url) → 显示alt文本
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"[\1]", text)
    # 链接 [text](url) → 显示text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text


def _build_table(html_content: str, styles) -> Optional[Table]:
    """解析 HTML 表格并构建 ReportLab Table"""
    # 简单处理：匹配 | col1 | col2 | 行
    rows_match = re.findall(r"<tr[^>]*>(.*?)</tr>", html_content, re.DOTALL | re.IGNORECASE)
    if not rows_match:
        return None

    table_data = []
    for row_html in rows_match:
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row_html, re.DOTALL | re.IGNORECASE)
        if cells:
            # 清理 HTML 标签
            clean_cells = []
            for cell in cells:
                cell = re.sub(r"<[^>]+>", "", cell)
                cell = _escape(cell.strip())
                clean_cells.append(Paragraph(cell, ST["td"]))
            table_data.append(clean_cells)

    if not table_data:
        return None

    col_count = max(len(row) for row in table_data)
    col_widths = [CW / col_count] * col_count

    tbl = Table(table_data, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), accent),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, border),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, light_bg]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return tbl


def markdown_to_pdf(
    markdown_content: str,
    output_path: str,
    title: Optional[str] = None,
) -> bool:
    """
    将 Markdown 内容转换为 PDF

    Args:
        markdown_content: Markdown 文本
        output_path: 输出 PDF 路径
        title: 文章标题（从内容中提取或手动指定）

    Returns:
        True 成功，False 失败
    """
    try:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=MG,
            rightMargin=MG,
            topMargin=MG,
            bottomMargin=MG,
        )

        story = []
        lines = markdown_content.split("\n")
        i = 0

        # 提取标题
        if not title:
            for line in lines:
                m = re.match(r"^#\s+(.+)", line)
                if m:
                    title = m.group(1).strip()
                    break

        # 封面
        if title:
            story.append(Spacer(1, 3 * cm))
            story.append(Paragraph(title, _S("cover", fontSize=26, leading=32, textColor=dark, fontName=FONT)))
            story.append(Spacer(1, 0.4 * cm))
            story.append(Table([[""]], colWidths=[CW], rowHeights=[3],
                               style=TableStyle([("BACKGROUND", (0, 0), (0, 0), accent)])))
            story.append(Spacer(1, 0.5 * cm))

        while i < len(lines):
            line = lines[i]

            # 跳过 HTML 标签行
            if re.match(r"^\s*<[^>]+>\s*$", line):
                i += 1
                continue

            # 跳过图片行
            if re.match(r"^\s*!\[", line):
                i += 1
                continue

            # H1
            m = re.match(r"^#\s+(.+)", line)
            if m:
                # 封面已经在开头处理了，跳过第一个 H1
                if i > 0:
                    story.append(PageBreak())
                    story.append(Paragraph(m.group(1), ST["h1"]))
                i += 1
                continue

            # H2
            m = re.match(r"^##\s+(.+)", line)
            if m:
                story.append(Spacer(1, 0.3 * cm))
                story.append(Paragraph(m.group(1), ST["h2"]))
                i += 1
                continue

            # H3
            m = re.match(r"^###\s+(.+)", line)
            if m:
                story.append(Paragraph(m.group(1), ST["h3"]))
                i += 1
                continue

            # 水平线
            if re.match(r"^---+$", line.strip()) or re.match(r"^\*\*\*+$", line.strip()):
                story.append(Spacer(1, 0.2 * cm))
                i += 1
                continue

            # 无序列表
            m = re.match(r"^[\-\*]\s+(.+)", line)
            if m:
                item_text = _render_inline(m.group(1).strip())
                story.append(Paragraph(f"• {item_text}", ST["body"]))
                i += 1
                continue

            # 有序列表
            m = re.match(r"^\d+\.\s+(.+)", line)
            if m:
                item_text = _render_inline(m.group(1).strip())
                story.append(Paragraph(f"1. {item_text}", ST["body"]))
                i += 1
                continue

            # 引用块
            if line.strip().startswith(">"):
                # 收集整个引用块
                quote_lines = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    q = lines[i].strip()[1:].strip()
                    if q:
                        quote_lines.append(q)
                    i += 1
                if quote_lines:
                    quote_text = " ".join(_render_inline(q) for q in quote_lines)
                    q_tbl = Table([[Paragraph(quote_text, _S("quote", fontSize=10, leading=15, textColor=gray, fontName=FONT))]],
                                  colWidths=[CW])
                    q_tbl.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, -1), light_bg),
                        ("LEFTPADDING", (0, 0), (-1, -1), 12),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
                    ]))
                    story.append(q_tbl)
                continue

            # 代码块 ```...```
            if line.strip().startswith("```"):
                lang = line.strip()[3:]
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # 跳过结束 ```

                if code_lines:
                    code_text = "\n".join(code_lines)
                    fn = _pick_font(code_text)
                    items = [Paragraph(code_text, _S("code_cjk" if fn == CJKFONT else "code",
                                                    fontName=fn, fontSize=8.5, leading=13,
                                                    textColor=colors.HexColor("#E2E8F0")))]
                    code_tbl = Table([[items]], colWidths=[CW])
                    code_tbl.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, -1), code_bg),
                        ("TOPPADDING", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                        ("LEFTPADDING", (0, 0), (-1, -1), 14),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                    ]))
                    story.append(code_tbl)
                    story.append(Spacer(1, 0.15 * cm))
                continue

            # 表格（简单 HTML 表格支持）
            if "<table" in line.lower():
                tbl_lines = [line]
                i += 1
                while i < len(lines) and "</table" not in lines[i].lower():
                    tbl_lines.append(lines[i])
                    i += 1
                tbl_lines.append(lines[i])  # 包含 </table>
                i += 1
                tbl_html = "\n".join(tbl_lines)
                tbl = _build_table(tbl_html, ST)
                if tbl:
                    story.append(tbl)
                    story.append(Spacer(1, 0.2 * cm))
                continue

            # 空行
            if not line.strip():
                i += 1
                continue

            # 普通文本段落
            rendered = _render_inline(line.strip())
            if rendered:
                story.append(Paragraph(rendered, ST["body"]))
            i += 1

        doc.build(story)
        return True

    except Exception as e:
        print(f"PDF 生成失败: {e}", file=sys.stderr)
        return False
