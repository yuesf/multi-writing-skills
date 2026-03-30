# multi-writing-skills

多平台 Markdown 发布工具，支持微信公众号、知乎、今日头条。

## 功能特性

- **Markdown 转换**: 支持基础模式、API 模式、AI 模式三种转换方式
- **多平台发布**: 一键发布到微信公众号、知乎、今日头条草稿箱
- **代码块格式化**: 自动处理缩进和换行，微信公众号完美展示代码
- **AI 写作助手**: 多种写作风格支持
- **AI 去痕**: 去除 AI 写作痕迹
- **AI 图片生成**: 支持 ModelScope、阿里百炼、Minimax，可生成文章封面配图

## 触发条件

当用户需要以下操作时自动触发：
- 将 Markdown 文章发布到微信公众号、知乎或今日头条
- 转换 Markdown 为公众号格式 HTML
- 修复微信公众号代码块显示问题
- 使用 AI 写作、改写或去痕
- 生成文章封面图片

## 使用方式

在 Claude Code 中直接用自然语言描述你的需求即可，例如：

- "帮我把这篇 Markdown 发布到微信公众号"
- "转换 article.md 为公众号格式"
- "用 AI 写一篇关于 Python 的文章"
- "给这篇文章去痕"

也可以手动调用：

```
/multi-writing-skills <任务描述>
```

## openclaw CLI

如果需要使用命令行工具（openclaw）：

```bash
# 初始化配置
openclaw config init

# 转换并发布
openclaw convert article.md --draft --platform wechat

# AI 写作
openclaw write "写一篇关于Python的文章"

# AI 去痕
openclaw humanize article.md -o article_clean.md

# AI 图片生成
openclaw generate-image "一只在海边看日出的猫" --provider minimax --size 1024x1024 -o cover.png
```

## 发布到 clawhub

```bash
clawhub publish ./multi-writing-skills \
  --slug multi-writing-skills \
  --name "multi-writing-skills" \
  --version 1.1.1 \
  --tags latest \
  --changelog "新增 AI 图片生成功能说明"
```

## 作者

yuesf

## 许可证

MIT
