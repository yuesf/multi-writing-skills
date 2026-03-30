# multi-writing-skills

多平台 Markdown 发布工具，支持微信公众号、知乎、今日头条。

## 功能特性

- **Markdown 转换**: 基础模式、API 模式、AI 模式
- **多平台发布**: 微信公众号、知乎、今日头条
- **代码块格式化**: 自动处理缩进和换行，微信公众号完美展示代码
- **图片上传**: 自动上传到各平台图床
- **AI 写作助手**: 5种写作风格支持
- **AI 去痕**: 去除 AI 写作痕迹
- **图片生成**: 支持 OpenAI DALL-E、Gemini、ModelScope

## 安装

```bash
pip install multi-writing-skills
```

或使用 uv:

```bash
uv tool install multi-writing-skills
```

## 快速开始

### 第一步 配置凭证

首次使用时，运行以下命令初始化配置：

```bash
openclaw config init
```

然后设置各平台的凭证：

- **微信公众号**: 登录微信公众平台，获取 AppID 和 AppSecret
- **知乎**: 登录知乎，从浏览器开发者工具复制 Cookie
- **今日头条**: 登录头条号，从浏览器开发者工具复制 Cookie

```bash
openclaw config set wechat.app_id <你的AppID>
openclaw config set wechat.app_secret <你的AppSecret>
```

### 第二步 转换并发布

把 Markdown 文章发布到微信公众号草稿箱：

```bash
openclaw convert 你的文章.md --draft --platform wechat
```

发布到知乎或今日头条：

```bash
openclaw convert 你的文章.md --draft --platform zhihu
openclaw convert 你的文章.md --draft --platform toutiao
```

### 第三步 发表文章

打开对应平台的后台，就能看到文章已经在草稿箱里了。

## AI 写作

用自然语言描述你想写的内容：

```bash
openclaw write "写一篇关于Python入门的教程"
```

指定写作风格和长度：

```bash
openclaw write "写一篇关于Python的文章" --style technical --length long
```

## AI 去痕

去除 AI 写作痕迹，让文章更自然：

```bash
openclaw humanize article.md -o article_clean.md
```

可选择轻度、中度、重度去痕强度。

## 图片生成

生成文章封面图片：

```bash
openclaw generate-image "一只可爱的猫咪" --provider openai
```

支持 OpenAI DALL-E、Gemini、ModelScope。

## Claude Code 集成

在 Claude Code 中，可以直接用自然语言描述需求：

- "帮我把这篇 Markdown 发布到微信公众号"
- "转换 article.md 为公众号格式"
- "用 AI 写一篇关于 Python 的文章"
- "给这篇文章去痕"

## 写作风格

| 风格 | 描述 |
|------|------|
| Dan Koe | 简洁、直接、实用 |
| 技术风格 | 严谨、详细、专业 |
| 随意风格 | 轻松、亲切、口语化 |
| 正式风格 | 严肃、规范、学术 |
| 故事风格 | 叙事、引人入胜 |

## 排版主题

内置多种主题：默认、橙色、蓝色、绿色、紫色、简约。

使用主题发布：

```bash
openclaw convert article.md --draft --platform wechat --theme blue
```

## 开发

```bash
git clone <仓库地址>
cd wechat-publisher
uv sync
uv run openclaw --help
```

## 许可证

MIT
