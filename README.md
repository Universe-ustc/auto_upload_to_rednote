# 面向小红书的全自动化科技资讯内容生成和发布系统

[English Version](#english-version)

## 项目简介

这是一个全自动化的内容生成和发布系统，专注于小红书平台，可以：

1. **自动收集资讯** - 从GitHub、arXiv、Reddit、Google News等多个来源收集最新的AI/科技资讯
2. **智能生成内容** - 使用AI模型基于真实资讯生成高质量的文章
3. **自动生成配图** - 使用AI图片生成模型为文章生成专业的封面图
4. **自动发布** - 将生成的内容自动发布到小红书平台

## 核心特性

- ✨ **完全自动化** - 从资讯收集到发布的全流程自动化
- 🤖 **AI驱动** - 使用先进的LLM模型生成高质量内容
- 📸 **智能配图** - AI生成与文章主题相关的专业配图
- 🔴 **小红书专用** - 专门针对小红书平台优化
- 🛡️ **安全可靠** - 敏感信息使用环境变量管理

## 系统要求

- Python 3.8+
- 依赖包见 `requirements.txt`

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/auto_upload_to_rednote.git
cd auto_upload_to_rednote
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境

复制配置文件模板并填入你的信息：

```bash
cp .env.example .env
cp config.yaml.example config.yaml
```

编辑 `.env` 文件，填入：
- `SILICONFLOW_API_KEY` - 硅基流动API密钥（用于内容和图片生成）
- `XIAOHONGSHU_PHONE` - 小红书账号手机号
- `XIAOHONGSHU_PASSWORD` - 小红书账号密码

编辑 `config.yaml` 文件，配置：
- 内容主题
- 任务调度时间

## 项目结构

```
auto_upload_to_rednote/
├── modules/                          # Core modules
│   ├── news_collector.py            # News collection module
│   ├── content_automation.py         # Content automation module
│   ├── image_generator.py            # Image generation module
│   ├── xiaohongshu_publisher.py      # RedNote publishing module
│   ├── xiaohongshu_auto_publisher.py # RedNote auto-publishing module
│   ├── xiaohongshu_playwright_publisher.py # Playwright-based publishing
│   └── project_detail_fetcher.py     # Project detail fetching module
├── utils/
│   └── logger.py                     # Logging utility
├── data/                             # Data directory
│   ├── news/                         # Collected news
│   ├── pending_articles/             # Articles pending review
│   ├── published_articles/           # Published articles archive
│   ├── images/                       # Generated images
│   └── logs/                         # Log files
├── main.py                           # Main entry point
├── review_content.py                 # Content review script
├── config.yaml.example               # Configuration template
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore file
└── requirements.txt                  # Dependencies list
```

## 使用指南

### 手动操作

#### 审核待发布文章

```bash
python review_content.py
```

#### 查看已发布文章

已发布的文章存档在 `data/published_articles/` 目录中，包括JSON和Markdown两种格式。

## 配置说明

### config.yaml

```yaml
content_automation:
  enabled: true                     # 是否启用内容自动化
  platforms:
    - xiaohongshu                   # 发布平台（仅支持小红书）
  topics:                           # 内容主题
    - AI Agent最新进展
    - 多智能体系统实战
  schedule: "daily"                 # 执行频率
```

## API密钥获取

### SiliconFlow API

1. 访问 [SiliconFlow官网](https://siliconflow.cn)
2. 注册账号并登录
3. 在个人中心获取API密钥
4. 将密钥填入 `.env` 文件的 `SILICONFLOW_API_KEY`

### 小红书账号

需要一个有效的小红书账号，用于自动发布内容。

## 常见问题

### Q: 如何修改发布时间？
A: 编辑 `config.yaml` 中的 `schedule` 字段，或修改 `main.py` 中的 `schedule_tasks()` 方法。

### Q: 如何添加新的资讯来源？
A: 在 `modules/news_collector.py` 中添加新的搜索方法。

### Q: 如何自定义生成的文章内容？
A: 修改 `modules/content_automation.py` 中的 `generate_article_from_news()` 方法中的prompt。

## 注意事项

⚠️ **重要提示**：
- 请确保你有权使用相关平台的自动化工具
- 遵守各平台的服务条款和使用规范
- 定期检查生成的内容质量
- 不要发布虚假或误导性信息
- 保护好你的API密钥和账号信息

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

---

# English Version

## Project Overview

This is a fully automated content generation and publishing system focused on RedNote platform that can:

1. **Automatically Collect News** - Collect latest AI/tech news from multiple sources including GitHub, arXiv, Reddit, Google News, etc.
2. **Intelligently Generate Content** - Use AI models to generate high-quality articles based on real news
3. **Auto-Generate Images** - Use AI image generation to create professional cover images for articles
4. **Auto-Publish** - Automatically publish generated content to RedNote platform

## Key Features

- ✨ **Fully Automated** - Complete automation from news collection to publishing
- 🤖 **AI-Powered** - Uses advanced LLM models to generate high-quality content
- 📸 **Smart Image Generation** - AI generates professional cover images related to article topics
- 🔴 **RedNote-Focused** - Optimized specifically for RedNote platform
- 🛡️ **Secure** - Sensitive information managed via environment variables

## System Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/auto_upload_to_rednote.git
cd auto_upload_to_rednote
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy configuration templates and fill in your information:

```bash
cp .env.example .env
cp config.yaml.example config.yaml
```

Edit `.env` file with:
- `SILICONFLOW_API_KEY` - SiliconFlow API key (for content and image generation)
- `XIAOHONGSHU_PHONE` - RedNote account phone number
- `XIAOHONGSHU_PASSWORD` - RedNote account password

Edit `config.yaml` file to configure:
- Content topics
- Task scheduling times

## Project Structure

```
auto_upload_to_rednote/
├── modules/                          # Core modules
│   ├── news_collector.py            # News collection module
│   ├── content_automation.py         # Content automation module
│   ├── image_generator.py            # Image generation module
│   ├── xiaohongshu_publisher.py      # RedNote publishing module
│   ├── xiaohongshu_auto_publisher.py # RedNote auto-publishing module
│   ├── xiaohongshu_playwright_publisher.py # Playwright-based publishing
│   └── project_detail_fetcher.py     # Project detail fetching module
├── utils/
│   └── logger.py                     # Logging utility
├── data/                             # Data directory
│   ├── news/                         # Collected news
│   ├── pending_articles/             # Articles pending review
│   ├── published_articles/           # Published articles archive
│   ├── images/                       # Generated images
│   └── logs/                         # Log files
├── main.py                           # Main entry point
├── publish_now.py                    # Immediate publish script
├── review_content.py                 # Content review script
├── config.yaml.example               # Configuration template
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore file
└── requirements.txt                  # Dependencies list
```

## Usage Guide

### Manual Operations

#### Review Pending Articles

```bash
python review_content.py
```

#### View Published Articles

Published articles are archived in `data/published_articles/` directory in both JSON and Markdown formats.

## Configuration Guide

### config.yaml

```yaml
content_automation:
  enabled: true                     # Enable content automation
  platforms:
    - xiaohongshu                   # Publishing platform (RedNote only)
  topics:                           # Content topics
    - AI Agent Latest Developments
    - Multi-Agent Systems in Practice
  schedule: "daily"                 # Execution frequency
```

## Getting API Keys

### SiliconFlow API

1. Visit [SiliconFlow Official Website](https://siliconflow.cn)
2. Register and log in
3. Get API key from personal center
4. Add key to `.env` file as `SILICONFLOW_API_KEY`

### RedNote Account

You need a valid RedNote account for automatic content publishing.

## FAQ

### Q: How to change publishing time?
A: Edit the `schedule` field in `config.yaml`, or modify the `schedule_tasks()` method in `main.py`.

### Q: How to add new news sources?
A: Add new search methods in `modules/news_collector.py`.

### Q: How to customize generated article content?
A: Modify the prompt in the `generate_article_from_news()` method in `modules/content_automation.py`.

## Important Notes

⚠️ **Important**:
- Ensure you have permission to use automation tools on relevant platforms
- Comply with each platform's terms of service and usage policies
- Regularly check the quality of generated content
- Do not publish false or misleading information
- Protect your API keys and account information

## License

MIT License

## Contributing

Welcome to submit Issues and Pull Requests!

