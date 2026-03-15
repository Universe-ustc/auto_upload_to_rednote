# 快速开始指南 | Quick Start Guide

## 中文版本

### 5分钟快速上手

#### 第1步：安装依赖（1分钟）

```bash
pip install -r requirements.txt
```

#### 第2步：配置账号（2分钟）

```bash
# 复制配置文件
cp .env.example .env
cp config.yaml.example config.yaml

# 编辑 .env 文件，填入以下信息：
# SILICONFLOW_API_KEY=你的API密钥
# XIAOHONGSHU_PHONE=你的小红书手机号
# XIAOHONGSHU_PASSWORD=你的小红书密码
```

#### 第3步：运行系统（2分钟）

```bash
# 启动自动化系统
python main.py

# 或者立即发布一篇文章
python publish_now.py
```

### 常用命令

```bash
# 启动主程序（自动按时间表运行）
python main.py

# 立即生成并发布一篇文章
python publish_now.py

# 审核待发布的文章
python review_content.py

# 查看已发布的文章
ls data/published_articles/
```

### 获取API密钥

1. **SiliconFlow API密钥**
   - 访问 https://siliconflow.cn
   - 注册并登录
   - 在个人中心复制API密钥
   - 粘贴到 `.env` 文件

2. **小红书账号**
   - 使用你的小红书账号手机号和密码
   - 填入 `.env` 文件

### 文件说明

| 文件 | 说明 |
|------|------|
| `main.py` | 主程序，自动按时间表运行 |
| `publish_now.py` | 立即发布脚本 |
| `review_content.py` | 内容审核脚本 |
| `config.yaml` | 系统配置文件 |
| `.env` | 环境变量（敏感信息） |
| `data/news/` | 收集的资讯 |
| `data/pending_articles/` | 待审核文章 |
| `data/published_articles/` | 已发布文章存档 |

### 工作流程

```
1. 系统启动
   ↓
2. 收集最新资讯（GitHub、arXiv、Reddit等）
   ↓
3. 使用AI生成文章
   ↓
4. 生成AI配图
   ↓
5. 保存待审核
   ↓
6. 审核通过后自动发布
   ↓
7. 存档已发布文章
```

### 故障排除

**问题1：API密钥错误**
```
解决：检查 .env 文件中的 SILICONFLOW_API_KEY 是否正确
```

**问题2：小红书登录失败**
```
解决：检查手机号和密码是否正确，确保账号未被锁定
```

**问题3：资讯收集失败**
```
解决：检查网络连接，某些来源可能需要代理
```

**问题4：图片生成失败**
```
解决：检查API配额是否充足，或稍后重试
```

### 下一步

- 📖 阅读完整文档：[README.md](README.md)
- ⚙️ 自定义配置：编辑 `config.yaml`
- 🔧 修改内容生成逻辑：编辑 `modules/content_automation.py`
- 📊 查看发布数据：打开 `data/published_articles/`

---

## English Version

### Get Started in 5 Minutes

#### Step 1: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

#### Step 2: Configure Account (2 minutes)

```bash
# Copy configuration files
cp .env.example .env
cp config.yaml.example config.yaml

# Edit .env file and fill in:
# SILICONFLOW_API_KEY=your_api_key
# XIAOHONGSHU_PHONE=your_phone_number
# XIAOHONGSHU_PASSWORD=your_password
```

#### Step 3: Run System (2 minutes)

```bash
# Start the automation system
python main.py

# Or publish an article immediately
python publish_now.py
```

### Common Commands

```bash
# Start main program (runs on schedule)
python main.py

# Generate and publish an article immediately
python publish_now.py

# Review pending articles
python review_content.py

# View published articles
ls data/published_articles/
```

### Getting API Keys

1. **SiliconFlow API Key**
   - Visit https://siliconflow.cn
   - Register and log in
   - Copy API key from personal center
   - Paste into `.env` file

2. **RedNote Account**
   - Use your RedNote phone number and password
   - Fill in `.env` file

### File Reference

| File | Description |
|------|-------------|
| `main.py` | Main program, runs on schedule |
| `publish_now.py` | Immediate publish script |
| `review_content.py` | Content review script |
| `config.yaml` | System configuration |
| `.env` | Environment variables (sensitive info) |
| `data/news/` | Collected news |
| `data/pending_articles/` | Articles pending review |
| `data/published_articles/` | Published articles archive |

### Workflow

```
1. System starts
   ↓
2. Collect latest news (GitHub, arXiv, Reddit, etc.)
   ↓
3. Generate article using AI
   ↓
4. Generate AI cover image
   ↓
5. Save for review
   ↓
6. Auto-publish after approval
   ↓
7. Archive published articles
```

### Troubleshooting

**Issue 1: API Key Error**
```
Solution: Check if SILICONFLOW_API_KEY in .env is correct
```

**Issue 2: RedNote Login Failed**
```
Solution: Verify phone number and password, ensure account is not locked
```

**Issue 3: News Collection Failed**
```
Solution: Check internet connection, some sources may need proxy
```

**Issue 4: Image Generation Failed**
```
Solution: Check API quota or try again later
```

### Next Steps

- 📖 Read full documentation: [README.md](README.md)
- ⚙️ Customize configuration: Edit `config.yaml`
- 🔧 Modify content generation: Edit `modules/content_automation.py`
- 📊 View publishing data: Open `data/published_articles/`
