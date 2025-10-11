# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

ListenPub是一个AI驱动的播客生成器，可以将文本内容转换为音频播客。应用使用Gradio构建Web界面，支持中英文双语。

## 开发命令

### 运行应用
```bash
python app.py
```
应用将在 http://localhost:7860 启动

### Python环境
- 使用`.venv/`中的Python虚拟环境
- 安装依赖：`pip install -r requirements.txt`

## 架构设计

### 核心组件

**主应用程序 (`app.py`)**
- 包含`PodcastGenerator`类，实现核心业务逻辑
- 使用Gradio构建Web界面，包含自定义CSS样式
- 处理播客生成、脚本创建和用户交互
- 第10-136行：PodcastGenerator类，包含text_to_podcast()和get_history()方法
- 第138-623行：create_interface()函数，包含UI组件和样式设计

**国际化模块 (`i18n_helper.py`)**
- `I18nHelper`类管理中英文翻译
- 使用JSON格式的翻译文件（当前代码库中locales目录不存在）
- 提供播客类型选择和语言选项
- 第48-61行：为下拉菜单提供本地化选项的方法

### 主要功能

**播客类型**
- 快速精华（3-5分钟）：快节奏、高信息密度内容
- 深度探索（8-15分钟）：多角度全面分析
- 辩论讨论（8-15分钟）：观点交锋的辩论形式

**支持语言**
- 中文（默认）
- 英文
- 界面实时语言切换

**界面设计**
- 模仿ListenHub.ai的样式，使用渐变背景和现代卡片布局
- 自定义CSS，支持响应式设计和悬停效果
- 左侧输入面板，右侧输出面板
- 历史记录和高级设置的折叠面板

## 文件结构

```
/
├── app.py              # 主要Gradio应用程序
├── i18n_helper.py      # 国际化工具
├── requirements.txt    # Python依赖包
├── ana/               # 研究分析文档（19个markdown文件）
└── README.md          # 项目文档（空文件）
```

## 依赖包

requirements.txt中的主要包：
- gradio>=4.0.0 (Web界面框架)
- openai>=1.0.0 (AI集成)
- requests>=2.30.0 (HTTP请求)
- pydub>=0.25.1 (音频处理)
- elevenlabs>=0.2.0 (语音合成)
- streamlit>=1.28.0 (备选界面框架)

## 开发注意事项

- 应用目前使用模拟的播客生成（app.py第18行有2秒延迟）
- 翻译系统期望locales目录结构但文件尚不存在
- 高级设置包括API密钥输入、语音选择和生成参数
- 音频生成是模拟的 - 返回状态文本而不是实际音频文件