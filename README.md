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

## 五分钟快速上手

只需要 3 步，就能把你的 Markdown 文章发布到微信公众号：

### 第一步 获取公众号凭证

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入「开发」→「基本配置」
3. 记下你的 **AppID** 和 **AppSecret**

### 第二步 一键配置

```bash
# 初始化配置文件
multi-writing-skills config init

# 设置公众号凭证（替换成你的 AppID 和 AppSecret）
multi-writing-skills config set wechat.app_id your_app_id
multi-writing-skills config set wechat.app_secret your_app_secret
```

### 第三步 转换发布

```bash
# 把你的 Markdown 文件转换成公众号格式并发布到草稿箱
multi-writing-skills convert 你的文章.md --draft --platform wechat
```

然后打开微信公众平台，就能看到你的文章已经在草稿箱里了，直接发表就行！🎉

## 快速开始

### 1. 初始化配置

```bash
multi-writing-skills config init
```

### 2. 设置平台凭证

```bash
# 微信公众号 (必填)
multi-writing-skills config set wechat.app_id your_app_id
multi-writing-skills config set wechat.app_secret your_app_secret

# 知乎 (可选)
multi-writing-skills config set zhihu.cookie "your_zhihu_cookie"

# 今日头条 (可选)
multi-writing-skills config set toutiao.cookie "your_toutiao_cookie"

# AI 配置 (用于 AI 功能)
multi-writing-skills config set ai.provider openai
multi-writing-skills config set ai.api_key your_api_key
multi-writing-skills config set ai.model gpt-4
```

### 3. 转换并发布

```bash
# 预览转换结果
multi-writing-skills convert article.md --preview

# 发布到微信草稿箱（默认主题）
multi-writing-skills convert article.md --draft --platform wechat

# 使用指定主题发布
multi-writing-skills convert article.md --draft --platform wechat --theme blue

# 发布到知乎
multi-writing-skills convert article.md --draft --platform zhihu

# 多平台发布
multi-writing-skills convert article.md --draft --platform wechat,zhihu
```

## 命令详解

### 转换命令 `convert`

支持 Markdown 和 HTML 文件，根据文件扩展名自动识别。

```bash
# Markdown 转换预览 (使用内置样式)
multi-writing-skills convert article.md --preview

# 使用 API 模式转换 (调用 mdnice 美化服务)
multi-writing-skills convert article.md --api --preview

# 使用 AI 模式转换
multi-writing-skills convert article.md --ai --preview

# 发布到草稿箱
multi-writing-skills convert article.md --draft --platform wechat

# 直接发布 HTML 文件 (不转换)
multi-writing-skills convert article.html --draft --platform wechat

# 设置封面和作者
multi-writing-skills convert article.md --draft --cover cover.jpg --author "作者名"

# 保存输出
multi-writing-skills convert article.md --output output.html
```

**参数说明:**

| 参数 | 说明 |
|------|------|
| `--platform, -p` | 发布平台 (wechat/zhihu/toutiao)，支持逗号分隔多平台 |
| `--draft, -d` | 发布到草稿箱 |
| `--preview` | 预览 HTML 输出 |
| `--cover, -c` | 封面图片路径 |
| `--author, -a` | 作者名称 |
| `--output, -o` | 输出文件路径 |
| `--api` | 使用 API 模式转换 |
| `--ai` | 使用 AI 模式转换 |

### 发布命令 `publish`

直接发布 HTML 文件，不进行任何转换。

```bash
# 发布 HTML 到微信
multi-writing-skills publish article.html --platform wechat

# 指定标题
multi-writing-skills publish article.html --title "文章标题"

# 设置封面和作者
multi-writing-skills publish article.html --cover cover.jpg --author "作者名"

# 多平台发布
multi-writing-skills publish article.html --platform wechat,zhihu
```

**参数说明:**

| 参数 | 说明 |
|------|------|
| `--platform, -p` | 发布平台 (wechat/zhihu/toutiao)，支持逗号分隔多平台 |
| `--title, -t` | 文章标题（默认从文件名或 HTML 中提取） |
| `--cover, -c` | 封面图片路径 |
| `--author, -a` | 作者名称 |

### 写作命令 `write`

```bash
# AI 写作助手
multi-writing-skills write "如何提高工作效率" --style dan-koe

# 指定文章长度
multi-writing-skills write "如何提高工作效率" --style dan-koe --length long

# 提供额外上下文
multi-writing-skills write "如何提高工作效率" --context "面向程序员群体"

# 生成封面图片提示词
multi-writing-skills write "如何提高工作效率" --cover-prompt
```

**参数说明:**

| 参数 | 说明 |
|------|------|
| `--style, -s` | 写作风格 (见下方风格列表) |
| `--length, -l` | 文章长度: short(300-500字)/medium(800-1200字)/long(2000-3000字) |
| `--context` | 额外上下文信息 |
| `--cover-prompt` | 生成封面图片的英文提示词 |

### 改写命令 `rewrite`

```bash
# 使用指定风格改写文章
multi-writing-skills rewrite article.md --style technical

# 不保留原有结构
multi-writing-skills rewrite article.md --style casual --no-keep-structure

# 保存到文件
multi-writing-skills rewrite article.md --style dan-koe --output rewritten.md
```

### AI 去痕命令 `humanize`

```bash
# 中度去痕 (默认)
multi-writing-skills humanize article.md

# 轻度去痕
multi-writing-skills humanize article.md --intensity light

# 重度去痕
multi-writing-skills humanize article.md --intensity heavy

# 保存到文件
multi-writing-skills humanize article.md --output humanized.md
```

**处理强度说明:**

| 强度 | 说明 |
|------|------|
| `light` | 轻度：保持原文大部分内容，只做轻微调整 |
| `medium` | 中度：适度调整，保留核心内容 |
| `heavy` | 重度：大幅调整，使文章焕然一新 |

### 图片生成命令 `generate-image`

```bash
# 使用 OpenAI DALL-E
multi-writing-skills generate-image "a cute cat sitting on a desk" --provider openai

# 使用 Gemini
multi-writing-skills generate-image "a sunset over mountains" --provider gemini

# 使用 ModelScope (通义万相)
multi-writing-skills generate-image "一只可爱的猫咪" --provider modelscope

# 指定尺寸
multi-writing-skills generate-image "a cute cat" --size 1024x1024

# 指定风格
multi-writing-skills generate-image "a cute cat" --style vivid

# 保存到本地
multi-writing-skills generate-image "a cute cat" --output cat.png
```

**参数说明:**

| 参数 | 说明 |
|------|------|
| `--provider, -p` | 图片生成 Provider: openai/gemini/modelscope |
| `--size, -s` | 图片尺寸: 1024x1024, 1792x1024, 1024x1792 |
| `--style` | 图片风格 (OpenAI: vivid/natural) |
| `--output, -o` | 输出文件路径 |

### 写作风格命令 `styles`

```bash
# 列出所有写作风格
multi-writing-skills styles
```

### 配置命令 `config`

```bash
# 初始化配置文件
multi-writing-skills config init

# 显示当前配置
multi-writing-skills config show

# 设置配置项
multi-writing-skills config set wechat.app_id your_app_id
multi-writing-skills config set ai.api_key your_api_key
```

### 平台命令 `platform`

```bash
# 列出所有平台
multi-writing-skills platform list

# 测试平台连接
multi-writing-skills platform test wechat
multi-writing-skills platform test zhihu
multi-writing-skills platform test toutiao
```

## 写作风格

| 风格 | 标识 | 描述 |
|------|------|------|
| Dan Koe | `dan-koe` | 简洁、直接、实用，适合个人成长类文章 |
| 技术风格 | `technical` | 严谨、详细、专业，适合技术教程 |
| 随意风格 | `casual` | 轻松、亲切、口语化，适合生活类博客 |
| 正式风格 | `formal` | 严肃、规范、学术，适合正式报告 |
| 故事风格 | `storytelling` | 叙事、引人入胜，适合案例分享 |

## 排版主题

### 内置主题

| 主题 | 标识 | 描述 |
|------|------|------|
| 默认主题 | `default` | 简洁清爽的默认主题 |
| 橙心主题 | `orange` | 温暖活力的橙色主题 |
| 蓝皓主题 | `blue` | 清新专业的蓝色主题 |
| 绿意主题 | `green` | 清新自然的绿色主题 |
| 紫韵主题 | `purple` | 优雅神秘的紫色主题 |
| 简约主题 | `simple` | 极简风格，专注内容 |

```bash
# 查看所有主题
multi-writing-skills themes

# 使用蓝色主题发布
multi-writing-skills convert article.md --draft --platform wechat --theme blue
```

### CSS 主题（兼容 wenyan-cli）

支持加载 wenyan-cli 格式的 CSS 文件作为主题：

```bash
# 添加 CSS 主题
multi-writing-skills theme add --name my-theme --path ./custom-theme.css

# 添加网络 CSS 主题
multi-writing-skills theme add --name manhua --path https://example.com/theme.css

# 使用 CSS 主题发布
multi-writing-skills convert article.md --draft --platform wechat --theme manhua

# 直接使用 CSS 文件（不添加到主题列表）
multi-writing-skills convert article.md --draft --platform wechat --css ./custom-theme.css

# 删除自定义主题
multi-writing-skills theme remove manhua
```

**CSS 主题格式说明：**

CSS 文件使用 `#wenyan` 作为容器选择器，例如：

```css
#wenyan h1 {
    font-size: 24px;
    font-weight: bold;
    color: #333;
}
#wenyan p {
    line-height: 1.8;
    color: #3f3f3f;
}
#wenyan pre code {
    background-color: #282c34;
    color: #abb2bf;
}
```

## 配置文件

配置文件位于 `~/.multi-writing-skills/config.yaml`

```yaml
wechat:
  app_id: your_app_id
  app_secret: your_app_secret

zhihu:
  cookie: your_zhihu_cookie

toutiao:
  cookie: your_toutiao_cookie

ai:
  provider: openai
  api_key: your_api_key
  base_url: ""  # 可选，用于自定义端点
  model: gpt-4

api_endpoint: ""  # API 模式的端点
default_theme: default
```

## 环境变量

支持通过环境变量配置：

```bash
# 微信公众号
export WECHAT_APP_ID=your_app_id
export WECHAT_APP_SECRET=your_app_secret

# 知乎
export ZHIHU_COOKIE=your_cookie

# 今日头条
export TOUTIAO_COOKIE=your_cookie

# AI 配置
export AI_PROVIDER=openai
export AI_API_KEY=your_api_key
export AI_MODEL=gpt-4
```

## 获取平台凭证

### 微信公众号

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入「开发」->「基本配置」
3. 获取 AppID 和 AppSecret

### 知乎

1. 登录 [知乎](https://www.zhihu.com/)
2. 打开浏览器开发者工具 (F12)
3. 复制请求头中的 Cookie

### 今日头条

1. 登录 [头条号](https://mp.toutiao.com/)
2. 打开浏览器开发者工具 (F12)
3. 复制请求头中的 Cookie

## 支持的平台

| 平台 | 标识 | 状态 |
|------|------|------|
| 微信公众号 | `wechat` | ✅ 已支持 |
| 知乎 | `zhihu` | ✅ 已支持 |
| 今日头条 | `toutiao` | ✅ 已支持 |

## 开发

```bash
# 克隆仓库
git clone https://gitee.com/yuesf/wechat-publisher.git

# 安装开发依赖
cd wechat-publisher
uv sync

# 运行 CLI
uv run multi-writing-skills --help

# 运行测试
uv run pytest
```

## Claude Code Skill

本项目提供了 `multi-writing-skills` Claude Code Skill，可以在 Claude Code 中自动触发处理相关任务：

**触发条件：**
- 需要发布 Markdown 文章到微信公众号/知乎/今日头条
- 修复微信公众号代码块显示问题
- 配置平台凭证
- 使用 AI 写作/改写/去痕
- 生成文章封面图片
- 维护开发 `multi-writing-skills` 项目

**Skill 位置：** `~/.claude/skills/multi-writing-skills`

## 许可证

MIT