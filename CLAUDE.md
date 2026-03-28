# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`multi-writing-skills` 是一个多平台 Markdown 发布工具，支持微信公众号、知乎、今日头条的 Markdown 文章转换与发布。项目使用 Python 3.12+ 开发，约 4200 行代码。

## Common Commands

```bash
# 安装依赖
uv sync

# 运行 CLI
uv run multi-writing-skills --help

# 运行测试
uv run pytest

# 代码格式化
uv run black .

# Linting
uv run ruff check .

# 类型检查
uv run mypy .
```

## Architecture

项目采用模块化架构，主要模块如下：

```
src/multi_writing_skills/
├── cli.py           # CLI 入口，使用 typer 构建
├── config.py        # 配置管理（YAML 配置 + 环境变量）
├── platforms/       # 多平台发布模块
│   ├── base.py      # 平台基类，定义发布接口
│   ├── wechat.py    # 微信公众号发布
│   ├── zhihu.py     # 知乎发布
│   └── toutiao.py   # 今日头条发布
├── converter/       # Markdown 转换模块
│   ├── wechat_style.py  # 微信样式转换器
│   ├── themes.py    # 内置主题管理
│   ├── css_theme.py # 自定义 CSS 主题
│   ├── api.py       # API 模式（调用 mdnice 服务）
│   └── ai.py        # AI 模式转换
├── image/           # AI 图片生成
│   └── providers/   # 支持 OpenAI DALL-E、Gemini、ModelScope
├── writer/          # AI 写作助手
└── humanizer/       # AI 去痕模块
```

## Key Design Patterns

- **平台适配器模式**: `platforms/base.py` 定义抽象基类，各平台实现独立
- **配置分层**: 支持 YAML 配置文件 + 环境变量覆盖
- **多模式转换**: 内置模式/API 模式/AI 模式三种 Markdown 转换方式