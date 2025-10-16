# CLAUDE.md - ListenPub 项目指南

> 本文档为 Claude AI 助手提供 ListenPub 项目的全面技术指南和上下文信息。
>
> **更新时间**: 2025-10-16
> **项目状态**: 活跃开发中 (框架已完成)

---

## 📋 项目概览

### 项目简介

**ListenPub** 是一个基于 AI 技术的智能播客生成平台，能够将文本素材转化为多角色自然互动的播客音频。项目使用 Gradio 构建 Web 界面，集成腾讯混元大模型生成对话脚本，使用 CosyVoice 2.0.5B 进行语音合成。

### 核心能力

1. **多角色互动播客生成** - 将文本素材转化为多角色自然交谈的播客音频
2. **角色人设定制** - 支持用户自定义角色人设和音色,生成契合风格的播客
3. **深度主题播客** - 基于指定主题生成有深度、引发思考的播客内容

### 技术特点

- 🎙️ **13种预设角色类型** (商业分析师、企业高管、科技记者、技术专家等)
- 🎭 **8种场景模式** (深度访谈、圆桌讨论、知识分享、辩论对话等)
- 🗣️ **8种声音风格** (温和亲切、专业权威、活泼生动等)
- 🤖 **AI 驱动的脚本生成** (腾讯混元大模型)
- 🎵 **高质量语音合成** (CosyVoice 2.0.5B)
- 🌐 **完整的中文界面** (基于 Gradio 的简洁设计)

---

## 📁 项目结构

```
/home/clg/listenpub/
├── .git/                          # Git 版本控制
├── .gitignore                     # 忽略规则: __pycache__/, .venv/, CosyVoice/
│
├── app.py                         # 主应用程序 (756行) - Gradio Web界面
├── requirements.txt               # Python依赖清单
│
├── README.md                      # 项目说明文档 (当前为空)
├── notes.md                       # 开发笔记 (未提交)
├── plan.md                        # 功能规划文档
├── task.md                        # 核心任务定义
├── rate.md                        # 评分/速率相关文档
├── EMOTION_MARKUP_INTEGRATION_REPORT.md  # 情感标记集成报告
│
├── src/                           # 源代码主目录
│   ├── __init__.py
│   │
│   ├── engines/                   # 核心引擎模块
│   │   ├── __init__.py
│   │   ├── podcast_engine.py      # 播客生成主引擎 (371行)
│   │   ├── dialogue_engine.py     # 多角色对话生成引擎 (621行)
│   │   └── voice_engine.py        # 语音合成引擎 (271行)
│   │
│   └── tts/                       # 文本转语音模块
│       ├── __init__.py
│       └── cosy_voice_tts.py      # CosyVoice 2.0.5B TTS集成 (553行)
│
└── ana/                           # 竞品和技术研究文档 (14份)
    ├── MyArxivPodcast.md
    ├── PodCast-Master.md
    ├── Podcast-Generator.md
    ├── Podcast.md
    ├── PodfAI.md
    ├── ai_beats.md
    ├── lingopod.md
    ├── llm-podcast-engine.md
    ├── open-sourced-nootbookLM.md
    ├── papercast.md
    ├── pdf-to-podcast.md
    ├── podcast-creator.md
    ├── podcast-llm.md
    ├── podcast-research-agent.md
    └── podscript.md
```

### 代码统计

| 模块 | 文件 | 行数 | 说明 |
|-----|------|------|-----|
| 主应用 | `app.py` | 756 | Gradio Web界面和主要业务逻辑 |
| 播客引擎 | `podcast_engine.py` | 371 | 播客生成流程控制 |
| 对话引擎 | `dialogue_engine.py` | 621 | 多角色对话脚本生成 |
| 音色引擎 | `voice_engine.py` | 271 | 音色档案管理 |
| TTS模块 | `cosy_voice_tts.py` | 553 | CosyVoice语音合成 |
| 工具模块 | `utils/*.py` | 110 | 模型下载等 |
| **总计** | | **2,682** | Python代码总量 |

---

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     Gradio Web Interface                     │
│                        (app.py)                              │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                  PodcastGenerator Class                      │
│  • 输入处理 • 角色管理 • 场景配置 • 历史记录                  │
└─────────────┬───────────────────────────────────────────────┘
              │
              ├──────────────┬──────────────┬─────────────────┐
              ▼              ▼              ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
│  Podcast Engine  │ │Dialogue Engine│ │ Voice Engine │
│ (脚本生成控制)    │ │ (对话生成)    │ │ (音色管理)    │
│ podcast_engine.py│ │dialogue_engine│ │voice_engine.py│
└──────────────────┘ └───────┬───────┘ └──────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
    ┌─────────────────┐ ┌─────────────┐ ┌──────────────────┐
    │  OpenAI Client  │ │CosyVoice TTS│ │   Temp Files     │
    │  (混元大模型)    │ │(语音合成)    │ │   (临时音频)      │
    │   腾讯混元API    │ │cosy_voice   │ │  /tmp/gradio/    │
    └─────────────────┘ └─────────────┘ └──────────────────┘
```

### 核心工作流程

```
用户输入 (主题 + 角色选择 + 场景模式 + 声音风格)
    ↓
【1. 输入处理阶段】
    • 验证输入参数
    • 加载角色人设
    • 配置场景参数
    ↓
【2. 脚本生成阶段】
    • 调用腾讯混元大模型
    • 构建提示词 (角色设定 + 场景描述 + 情感标记规则)
    • 生成多角色对话脚本
    • 备用模板 (AI不可用时)
    ↓
【3. 音频合成阶段】
    • 使用 CosyVoice 2.0.5B
    • 支持零样本语音克隆
    • 处理情感标记 ([laughter], <strong>等)
    • 支持语速控制
    • 生成临时音频文件
    ↓
【4. 结果输出】
    • 显示脚本内容
    • 提供音频播放
    • 保存生成历史
    • 支持下载分享
    ↓
【5. 清理】
    • 清理临时音频文件
```

---

## 🛠️ 技术栈详解

### 前端界面

| 技术 | 版本 | 用途 |
|-----|------|-----|
| **Gradio** | >= 4.0.0 | 快速构建AI应用Web界面 |
| **自定义CSS** | - | 模仿ListenHub.ai的现代化设计风格 |

### AI & 大语言模型

| 技术 | 版本 | 用途 |
|-----|------|-----|
| **OpenAI SDK** | >= 1.0.0 | 调用API接口 |
| **腾讯混元大模型** | turbos-latest | 对话脚本生成 |
| **API端点** | - | `https://api.hunyuan.cloud.tencent.com/v1` |
| **python-dotenv** | >= 1.0.0 | 环境变量管理 (.env文件) |

### 语音合成 (TTS)

| 技术 | 版本 | 用途 |
|-----|------|-----|
| **CosyVoice 2.0.5B** | - | 轻量级多功能TTS模型 (仅500M) |
| **PyTorch** | >= 2.0.0 | 深度学习框架 |
| **torchaudio** | >= 2.0.0 | 音频处理库 |
| **modelscope** | - | 阿里ModelScope模型库 |

### 音频处理

| 技术 | 版本 | 用途 |
|-----|------|-----|
| **librosa** | - | 音频分析和特征提取 |
| **pyworld** | - | 语音处理信号库 |
| **onnxruntime** | - | 模型推理优化 |

### 深度学习模型

| 技术 | 版本 | 用途 |
|-----|------|-----|
| **transformers** | - | Hugging Face 模型库 |
| **diffusers** | - | 扩散模型库 |
| **lightning** | - | PyTorch Lightning 训练框架 |
| **conformer** | - | 语音识别模型架构 |

### 文本处理

| 技术 | 版本 | 用途 |
|-----|------|-----|
| **WeTextProcessing** | - | 中文文本处理和规范化 |
| **wetext** | - | 文本工具库 |
| **inflect** | - | 英文单复数处理 |

### 配置管理

| 技术 | 版本 | 用途 |
|-----|------|-----|
| **omegaconf** | - | 配置文件管理 |
| **hydra-core** | - | 配置框架 |
| **hyperpyyaml** | >= 1.2.0 | YAML配置解析 |

### 基础工具

| 技术 | 版本 | 用途 |
|-----|------|-----|
| **requests** | >= 2.30.0 | HTTP请求 |
| **numpy** | >= 1.24.0 | 数值计算 |
| **gdown** | - | Google Drive文件下载 |
| **wget** | - | 文件下载工具 |

---

## 🔑 关键模块详解

### 1. app.py - 主应用程序

**位置**: `/home/clg/listenpub/app.py`
**行数**: 756行
**职责**: Gradio Web界面和主要业务逻辑

#### 核心类: `PodcastGenerator`

```python
class PodcastGenerator:
    """播客生成器主类"""

    def __init__(self):
        self.generated_podcasts = []      # 生成历史
        self.ai_client = None             # AI客户端
        self.character_presets = {}       # 角色预设
        self.scene_presets = {}           # 场景预设
        self.voice_style_presets = {}     # 声音风格预设

    # 主要方法
    def _init_ai_client(self)             # 初始化AI客户端
    def _init_preset_options(self)        # 初始化预设选项
    def generate_podcast(self, ...)       # 生成播客 (主入口)
    def _build_prompt(self, ...)          # 构建AI提示词
    def _call_ai_model(self, ...)         # 调用AI模型
    def _synthesize_audio(self, ...)      # 合成音频
    def _save_history(self, ...)          # 保存生成历史
```

#### 预设配置 (前100行)

**13种角色类型**:
- 商业分析师, 企业高管, 科技记者, 技术专家
- 历史学者, 专业医师, 教育工作者, 艺术家
- 评论家, 生活主播, 新闻主播, 时事评论员

**8种场景模式**:
- 深度访谈, 圆桌讨论, 知识分享, 故事叙述
- 问答互动, 辩论对话, 经验分享, 新闻解读

**8种声音风格**:
- 温和亲切, 专业权威, 活泼生动, 深沉磁性
- 清晰标准, 温柔甜美, 成熟稳重, 青春朝气

#### Gradio界面结构

```python
def create_interface():
    """创建Gradio界面"""
    with gr.Blocks(css=custom_css) as interface:
        # Header
        gr.Markdown("# ListenPub - AI播客生成平台")

        # 输入区域
        with gr.Row():
            topic_input = gr.Textbox(label="播客主题")
            character_select = gr.CheckboxGroup(choices=characters)
            scene_select = gr.Dropdown(choices=scenes)
            voice_select = gr.Dropdown(choices=voices)

        # 生成按钮
        generate_btn = gr.Button("生成播客")

        # 输出区域
        script_output = gr.Textbox(label="生成的脚本")
        audio_output = gr.Audio(label="播客音频")

        # 历史记录
        history_display = gr.Dataframe(label="生成历史")
```

---

### 2. podcast_engine.py - 播客生成主引擎

**位置**: `/home/clg/listenpub/src/engines/podcast_engine.py`
**行数**: 371行
**职责**: 播客生成流程控制和脚本管理

#### 核心数据结构

```python
@dataclass
class PodcastGenerationRequest:
    """播客生成请求"""
    topic: str                      # 播客主题
    character_settings: str         # 角色设置
    voice_settings: str             # 音色设置
    language: str = "zh"            # 语言 (默认中文)
    target_duration: int = 900      # 目标时长 (15分钟)
    quality_level: str = "high"     # 质量级别

@dataclass
class PodcastGenerationResult:
    """播客生成结果"""
    success: bool                   # 是否成功
    script: Optional[str]           # 脚本内容
    character_mapping: Optional[str] # 角色映射
    metadata: Optional[Dict]        # 元数据
    duration: Optional[float]       # 时长
    error_message: Optional[str]    # 错误信息
    generation_time: Optional[float] # 生成耗时
```

#### 核心类: `PodcastEngine`

```python
class PodcastEngine:
    """播客生成主引擎 - 简化版，仅处理脚本生成"""

    def __init__(self):
        self.character_engine = character_engine
        self.voice_engine = voice_engine
        self.dialogue_engine = dialogue_engine

    async def generate_podcast(self, request) -> Result:
        """生成播客脚本（不包含音频和背景音乐）"""
        # 1. 解析和验证输入
        # 2. 生成对话脚本
        # 3. 生成脚本文本
        # 4. 生成角色音色映射
        # 5. 生成元数据

    async def _parse_and_validate_input(self, request):
        """解析和验证输入参数"""

    async def _generate_dialogue_script(self, topic, characters, duration, lang):
        """生成对话脚本"""

    def _format_script_text(self, segments, characters, voices):
        """格式化脚本文本"""

    def _create_character_mapping(self, characters, voices):
        """创建角色音色映射"""

    def _create_metadata(self, request, characters, voices, segments):
        """生成元数据"""
```

---

### 3. dialogue_engine.py - 多角色对话生成引擎

**位置**: `/home/clg/listenpub/src/engines/dialogue_engine.py`
**行数**: 621行
**职责**: 多角色对话脚本生成和互动模式管理

#### 主要功能

- **互动模式识别**: 协作/辩论/访谈/小组讨论
- **对话结构规划**: 开场、主体、互动、总结、结尾
- **AI生成对话内容**: 调用大模型生成自然对话
- **情感增强处理**: 添加情感标记
- **CosyVoice情感标记集成**: `[laughter]`, `[breath]`, `<strong>`, etc.

#### 支持的情感标记

```python
# CosyVoice 2.0.5B 支持的情感标记
EMOTION_TAGS = {
    "[laughter]": "笑声",
    "[breath]": "呼吸声",
    "[sigh]": "叹气声",
    "<strong>text</strong>": "强调语气",
    "[pause]": "停顿",
    # ... 更多标记
}
```

---

### 4. cosy_voice_tts.py - CosyVoice语音合成

**位置**: `/home/clg/listenpub/src/tts/cosy_voice_tts.py`
**行数**: 553行
**职责**: CosyVoice 2.0.5B TTS集成

#### 核心类: `CosyVoiceTTS`

```python
class CosyVoiceTTS:
    """CosyVoice 2.0.5B TTS 语音合成"""

    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.model = None
        self.is_initialized = False

    def initialize(self):
        """初始化模型"""
        # 加载 CosyVoice 2.0.5B 模型

    def synthesize_zero_shot(self, text, prompt_audio, prompt_text):
        """零样本语音克隆"""

    def synthesize_instruct(self, text, instruction):
        """指令控制合成"""

    def synthesize_podcast_segment(self, text, speaker_profile):
        """播客片段合成"""

    def synthesize_multi_speaker_dialogue(self, dialogue_segments):
        """多说话人对话合成"""

    def merge_audio_segments(self, audio_segments):
        """音频片段拼接"""
```

#### 支持的功能

1. **零样本语音克隆 (Zero-Shot Synthesis)**
   - 提供参考音频和文本
   - 克隆目标说话人的声音特征

2. **指令控制合成 (Instruction Synthesis)**
   - 通过文本指令控制合成效果
   - 例如: "用温柔的语气说这句话"

3. **播客片段合成**
   - 根据角色档案合成音频
   - 支持情感标记处理

4. **多说话人对话合成**
   - 批量处理多个角色的对话
   - 自动拼接音频片段

---

### 5. voice_engine.py - 音色管理引擎

**位置**: `/home/clg/listenpub/src/engines/voice_engine.py`
**行数**: 271行
**职责**: 音色档案管理和推荐

#### 核心数据结构

```python
@dataclass
class VoiceProfile:
    """音色档案"""
    voice_id: str                 # 音色ID
    name: str                     # 音色名称
    gender: str                   # 性别
    age_range: str                # 年龄段
    style: str                    # 风格描述
    characteristics: List[str]    # 音色特征
    sample_audio_path: Optional[str] = None  # 示例音频

class VoiceGender(Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class VoiceAge(Enum):
    """年龄段枚举"""
    YOUNG = "young"        # 青年 (18-30)
    MIDDLE = "middle"      # 中年 (30-50)
    SENIOR = "senior"      # 老年 (50+)
```

---

## 🎯 核心功能实现

### 功能 1: 文本转播客完整流程

```python
# app.py: generate_podcast()
def generate_podcast(topic, characters, scene, voice_style):
    """
    输入:
      - topic: 播客主题 (例: "人工智能的未来发展")
      - characters: 角色列表 (例: ["技术专家", "科技记者"])
      - scene: 场景模式 (例: "深度访谈")
      - voice_style: 声音风格 (例: "专业权威")

    流程:
      1. 验证输入参数
      2. 构建AI提示词 (包含角色设定、场景描述、情感标记规则)
      3. 调用腾讯混元大模型生成脚本
      4. 解析脚本内容
      5. 使用CosyVoice合成音频 (可选)
      6. 保存生成历史
      7. 返回脚本和音频

    输出:
      - script: 完整的播客脚本文本
      - audio: 合成的音频文件
      - metadata: 生成信息 (时长、角色、场景等)
    """
```

### 功能 2: AI 脚本生成

```python
# dialogue_engine.py: generate_dialogue()
def generate_dialogue(topic, characters, scene, duration):
    """
    使用腾讯混元大模型生成多角色对话脚本

    提示词结构:
      [系统提示]
      你是一个专业的播客脚本创作者...

      [角色设定]
      - 角色A: {identity}, {personality}, {voice_style}
      - 角色B: {identity}, {personality}, {voice_style}

      [场景描述]
      场景类型: {scene}
      互动模式: {interaction_mode}

      [内容要求]
      1. 开场 (10%): 介绍主题和嘉宾
      2. 主体 (60%): 深度讨论和互动
      3. 互动 (20%): 问答或辩论
      4. 总结 (10%): 总结要点和结尾

      [情感标记规则]
      使用CosyVoice标记增强表现力:
      - [laughter] 表示笑声
      - <strong>text</strong> 表示强调
      - [pause] 表示停顿
      ...

      [主题]
      {topic}

    返回: 完整的多角色对话脚本
    """
```

### 功能 3: CosyVoice 语音合成

```python
# cosy_voice_tts.py: synthesize_podcast_segment()
def synthesize_podcast_segment(text, speaker_profile):
    """
    使用CosyVoice 2.0.5B合成单个播客片段

    输入:
      - text: 要合成的文本 (包含情感标记)
      - speaker_profile: 说话人档案 (音色特征)

    处理流程:
      1. 预处理文本 (规范化、添加停顿等)
      2. 解析情感标记
      3. 加载对应的音色模型
      4. 合成音频 (支持流式推理)
      5. 后处理音频 (降噪、音量归一化)

    输出:
      - audio_data: numpy数组格式的音频数据
      - sample_rate: 采样率 (通常是22050Hz)
      - duration: 音频时长 (秒)
    """
```

---

## 🔐 环境变量配置

### .env 文件示例

```bash
# AI模型配置 (腾讯混元)
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.hunyuan.cloud.tencent.com/v1
OPENAI_MODEL=hunyuan-turbos-latest

# CosyVoice模型路径
COSYVOICE_MODEL_DIR=/path/to/CosyVoice2-0.5B

# 应用配置
APP_LANGUAGE=zh
APP_PORT=7860
APP_DEBUG=False

# 音频配置
AUDIO_SAMPLE_RATE=22050
AUDIO_OUTPUT_FORMAT=wav
TEMP_AUDIO_DIR=/tmp/listenpub_audio

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/listenpub.log
```

### 必需的环境变量

| 变量名 | 说明 | 默认值 |
|-------|-----|-------|
| `OPENAI_API_KEY` | 腾讯混元API密钥 | 无 (必需) |
| `OPENAI_BASE_URL` | API端点 | `https://api.hunyuan.cloud.tencent.com/v1` |
| `OPENAI_MODEL` | 模型名称 | `hunyuan-turbos-latest` |
| `COSYVOICE_MODEL_DIR` | CosyVoice模型目录 | 无 (必需) |

---

## 🚀 安装和启动

### 1. 安装依赖

```bash
cd /home/clg/listenpub

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 下载 CosyVoice 模型

```bash
# 使用项目提供的下载工具
python src/utils/download_small_model.py

# 或手动下载到 CosyVoice/ 目录
# 模型大小: 约 500MB
```

### 3. 配置环境变量

```bash
# 创建 .env 文件
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥
nano .env
```

### 4. 启动应用

```bash
# 启动Gradio应用
python app.py

# 应用将在以下地址运行:
# Local:   http://127.0.0.1:7860
# Network: http://your-ip:7860
```

---

## 📝 开发规范

### 代码风格

项目使用以下工具进行代码规范 (来自 `plan.md`):

```bash
# 导入排序
isort ./src

# 代码格式化
black ./src

# 代码检查
flake8 ./src

# 类型检查
mypy --ignore-missing-imports ./src
```

### Git 工作流

```bash
# 当前分支
git branch
# * main

# 主要分支
main - 主分支，用于创建PR

# 提交历史
7a9cecf feat: ...
3d2fc97 feat: 完成框架
2b17343 feat: add app.py
c7f47b7 feat: add mds
6ddeaf7 docs: add ana
5d747de Init
```

### 提交规范

```bash
# 使用 Conventional Commits 规范
feat:     新功能
fix:      Bug修复
docs:     文档更新
style:    代码格式调整
refactor: 代码重构
test:     测试相关
chore:    构建/工具相关
```

---

## 📋 项目规划和任务

### 核心任务 (来自 task.md)

#### 任务 1: 文本转多角色播客
> 将文本素材转化为多角色自然互动的播客音频。实现输入文本素材后，能输出多角色交谈的播客音频。要使多角色间的互动交流自然，精准呈现真人交流方式（如：能够接梗玩梗、立场冲突、激烈交流、愉快或不愉快的访谈等交流场景）。

**状态**: ✅ 框架已完成
**关键文件**:
- `src/engines/dialogue_engine.py` (621行) - 对话生成
- `app.py` (756行) - 主要交互逻辑

#### 任务 2: 自定义角色人设和音色
> 根据用户自定义的角色人设和音色生成契合风格的播客音频。给文字"穿人设"。按自定义角色的说话风格和音色生成播客音频，围绕用户指定的多个角色人设和音色，依据输入文本素材，生成高度契合角色人设表达风格与音色的播客音频。

**状态**: ✅ 框架已完成
**关键文件**:
- `src/engines/voice_engine.py` (271行) - 音色管理
- `src/tts/cosy_voice_tts.py` (553行) - 语音合成

#### 任务 3: 有深度的主题播客
> 基于指定主题生成有深度、引发思考的播客音频。打造有深度的播客，基于用户指定的主题，生成内容有深度的播客音频。使播客内容能够助力听众跨越认知和领域门槛，做到有依据、有见地，引发听众的深度思考。

**状态**: 🚧 进行中
**关键文件**:
- `src/engines/podcast_engine.py` (371行) - 播客生成控制
- AI提示词优化 (在 `app.py` 中)

### 未来计划 (来自 plan.md)

1. ✅ **脚本修改功能** - 可以修改生成的脚本
2. 🚧 **音频处理和背景声音** - 音质优化
3. 🚧 **并发音频生成** - 提高生成速度
4. 📅 **私人定制模式** - 可迭代优化提示词
5. 📅 **多源输入支持** - 接受PDF和上下文文件
6. 📅 **存储系统** - PDF和音频的存储
7. ✅ **Gradio界面** - 实现相关功能
8. 📅 **后端扩展** - Kafka等消息队列
9. 📅 **多语言输入** - 处理不同语言输入
10. 📅 **多模态输入** - 文字/PDF/Markdown/视频/URL/图片
11. 📅 **用户系统** - 数据库、登录管理等

---

## 🔍 竞品分析 (ana/ 目录)

项目参考了14个相关项目和平台的分析:

### 开源项目
- **NotebookLM** - Google的AI笔记工具
- **PodCast-Master** - 播客管理系统
- **MyArxivPodcast** - Arxiv论文转播客

### AI播客平台
- **PodfAI** - AI驱动的播客生成
- **Podscript** - 播客脚本生成工具
- **LingoPod** - 语言学习播客

### 技术方案
- **PDF-to-Podcast** - PDF转播客
- **Papercast** - 学术论文播客化
- **AI Beats** - AI音乐和播客生成
- **llm-podcast-engine** - LLM播客引擎
- **podcast-llm** - 播客LLM应用
- **podcast-research-agent** - 播客研究代理
- **Podcast-Generator** - 播客生成器
- **podcast-creator** - 播客创作工具

这些分析文档位于 `/home/clg/listenpub/ana/` 目录下。

---

## 🐛 已知问题和限制

### 当前限制

1. **CosyVoice模型依赖**
   - 需要手动下载500MB的模型文件
   - 模型文件不在Git仓库中 (`.gitignore`排除)

2. **AI模型可选性**
   - 依赖腾讯混元API
   - 需要API密钥才能使用完整功能
   - 提供备用脚本模板 (AI不可用时)

3. **音频处理**
   - 当前版本不包含背景音乐功能
   - 音频质量优化待完善

4. **性能**
   - 音频生成串行处理 (计划改为并发)
   - 长播客生成时间较长

5. **存储**
   - 临时文件管理 (使用 `/tmp/gradio/`)
   - 缺少持久化存储方案

### 未提交的更改

```bash
# Git状态 (截至 2025-10-16)
M  README.md     # 修改但未提交
M  app.py        # 修改但未提交
?? notes.md      # 新文件，未追踪
```

---

## 📚 文档和资源

### 项目文档

| 文件 | 说明 | 位置 |
|-----|------|-----|
| `README.md` | 项目说明 (当前为空) | `/home/clg/listenpub/README.md` |
| `plan.md` | 功能规划 | `/home/clg/listenpub/plan.md` |
| `task.md` | 核心任务 | `/home/clg/listenpub/task.md` |
| `EMOTION_MARKUP_INTEGRATION_REPORT.md` | 情感标记集成报告 | `/home/clg/listenpub/EMOTION_MARKUP_INTEGRATION_REPORT.md` |
| `notes.md` | 开发笔记 (未提交) | `/home/clg/listenpub/notes.md` |

### 外部资源

- **Gradio文档**: https://gradio.app/docs/
- **CosyVoice GitHub**: https://github.com/FunAudioLLM/CosyVoice
- **腾讯混元API**: https://cloud.tencent.com/document/product/1729
- **PyTorch文档**: https://pytorch.org/docs/

---

## 🎓 使用场景示例

### 场景 1: 技术访谈播客

```
输入:
  主题: "人工智能在医疗领域的应用"
  角色: ["专业医师", "技术专家", "科技记者"]
  场景: "深度访谈"
  声音风格: ["温柔甜美", "清晰标准", "活泼生动"]

输出:
  脚本预览:
  ---
  [开场 - 科技记者 (活泼生动)]
  大家好！欢迎来到本期播客。今天我们邀请到了...

  [主体 - 专业医师 (温柔甜美)]
  [sigh] 说到AI在医疗领域的应用，其实有很多值得探讨的地方。
  <strong>最核心的还是诊断辅助系统</strong>...

  [互动 - 技术专家 (清晰标准)]
  [laughter] 说得对！从技术角度来看...
  ---

  音频: 15分钟的多角色对话音频
```

### 场景 2: 商业分析播客

```
输入:
  主题: "2024年科技行业投资趋势"
  角色: ["商业分析师", "企业高管"]
  场景: "圆桌讨论"
  声音风格: ["专业权威", "成熟稳重"]

输出:
  - 专业的商业分析内容
  - 基于数据的观点讨论
  - 自然的圆桌讨论互动
  - 10-15分钟音频
```

### 场景 3: 知识分享播客

```
输入:
  主题: "量子计算入门"
  角色: ["技术专家", "教育工作者"]
  场景: "知识分享"
  声音风格: ["清晰标准", "温和亲切"]

输出:
  - 深入浅出的技术讲解
  - 循序渐进的知识结构
  - 互动式的问答环节
  - 15-20分钟音频
```

---

## 💡 开发建议

### 针对 Claude AI 助手的建议

1. **文件定位**
   - 主应用逻辑在 `app.py:21-756`
   - 核心引擎在 `src/engines/` 目录
   - TTS相关在 `src/tts/cosy_voice_tts.py`

2. **修改角色/场景预设**
   - 编辑 `app.py` 的 `_init_preset_options()` 方法
   - 添加新的角色到 `character_presets` 字典
   - 添加新的场景到 `scene_presets` 字典

3. **优化AI提示词**
   - 修改 `app.py` 中的 `_build_prompt()` 方法
   - 或修改 `dialogue_engine.py` 中的提示词构建逻辑

4. **调整音频合成**
   - 修改 `cosy_voice_tts.py` 中的合成参数
   - 调整采样率、音量、语速等参数

5. **添加新功能**
   - 背景音乐: 在 `podcast_engine.py` 中添加音乐混音逻辑
   - 并发生成: 使用 `asyncio` 改造音频合成流程
   - 用户系统: 添加数据库模型和认证逻辑

---

## 🔗 相关链接

- **项目目录**: `/home/clg/listenpub/`
- **Git仓库**: 本地仓库 (未配置远程)
- **主分支**: `main`

---

## 📌 版本信息

- **项目状态**: 活跃开发中
- **框架完成度**: 80%
- **最新提交**: `7a9cecf feat: ...`
- **提交日期**: 2025-10-16 (推测)
- **Python版本**: >= 3.8
- **Gradio版本**: >= 4.0.0
- **PyTorch版本**: >= 2.0.0

---

## 🙏 致谢

本项目参考了多个优秀的开源项目和商业产品，包括但不限于:
- Google NotebookLM
- CosyVoice (阿里巴巴达摩院)
- Gradio (Hugging Face)
- 腾讯混元大模型

详细分析文档见 `ana/` 目录。

---

## 📧 联系方式

- **开发者**: clg
- **工作目录**: `/home/clg/listenpub/`
- **平台**: Linux (WSL2)

---

**文档结束**

_本文档由 Claude AI 助手自动生成，旨在为未来的 Claude 助手提供完整的项目上下文。_
_最后更新: 2025-10-16_
