# ✦ Muse · AI灵感捕手

> **全球首个面向知识工作者的主动灵感采集与创作引擎。100% 开源。**

灵感本易逝，行动应当时。

Muse 不帮你收藏灵感。它帮你把灵感变成可以被分发的内容。

## 🎯 核心能力

### 1. 主动捕捉 (Active Capture)
- 浏览器插件：右键菜单 / 快捷键 / 浮动按钮
- 选中文字或整页捕捉，3秒完成
- 支持 Telegram / Discord / Slack / Any Agent

### 2. AI自动提炼 (AI Extraction)
- DeepSeek V3.2 实时分析
- 自动生成：标题、摘要、关键词、情绪标签、分类
- 100+ AI模型智能路由（via TokenRouter）

### 3. 选题工厂 (Topic Factory)
- 基于灵感信号 + 创作DNA生成选题
- 病毒度评估 + 推荐内容形式
- 一键深潜：爆款标题变体、内容结构、金句

### 4. 金句配图 (Quote Image)
- AI生成金句配图
- 多风格选择（现代/赛博/温暖/大字报）

### 5. 创作DNA (Creation DNA)
- 分析你的历史内容，提取创作基因
- 雷达图可视化能力维度
- 主题、语调、优势、建议

## 🤖 AI模型路由策略

| 功能节点 | 模型 | 原因 |
|---------|------|------|
| 灵感汲取 | DeepSeek V3.2 | 快、准、成本低 |
| DNA分析 | DeepSeek V3.2 | 中文理解强 |
| 选题生成 | DeepSeek V3.2 | 创意+逻辑平衡 |
| 选题深潜 | DeepSeek V3.2 | 多维度拆解能力 |
| 内容策略 | DeepSeek V4 Pro | 深度推理 |
| 金句配图 | GPT-5 Image Mini | 图文一体生成 |
| 高质量配图 | GPT-5 Image | 细节表现最佳 |
| 图片理解 | GLM-4.6V | 多模态识别 |

Powered by TokenRouter — 100+ models via unified API.

## 🚀 快速开始

### 安装浏览器插件
1. 下载 `muse-extension-v1.2.zip`
2. 解压
3. 打开 `chrome://extensions/`
4. 开启「开发者模式」
5. 点「加载已解压的扩展程序」→ 选 extension 文件夹
6. 任意网页按 `⌘⇧M` 开捕

### 在线体验
- Landing Page: https://muse-xi-murex.vercel.app
- Dashboard: https://muse-xi-murex.vercel.app/app
- Onboarding: https://muse-xi-murex.vercel.app/onboarding

### 本地运行
```bash
pip install flask
python server.py
# 打开 http://localhost:5200
```

## 🏗️ 技术栈
- **Backend**: Python Flask + SQLite
- **LLM**: TokenRouter (100+ models, smart routing)
- **Frontend**: Vanilla HTML/CSS/JS (零框架依赖)
- **Extension**: Chrome MV3
- **Deploy**: Vercel Serverless

## 📁 项目结构
```
muse/
├── server.py          # Flask API + Dashboard
├── llm_router.py      # TokenRouter LLM路由层
├── landing.html       # Landing Page
├── index.html         # Dashboard (可视化)
├── onboarding.html    # 创作DNA Onboarding
├── extension/         # Chrome Extension
├── requirements.txt   # Python依赖
└── vercel.json        # Vercel部署配置
```

## 📄 License
MIT License — 100% Open Source

---

**BotLearn OPC 2026** · Hackathon Entry
