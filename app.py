# -*- coding: utf-8 -*-
import gradio as gr
import os
import tempfile
import json
import asyncio
from typing import Optional, Tuple, List
import time
from src.utils.i18n_helper import i18n
from openai import OpenAI

# 导入CosyVoice TTS - 唯一的语音引擎
try:
    from src.tts.cosy_voice_tts import get_tts_instance
    COSYVOICE_AVAILABLE = True
except ImportError as e:
    print(f"Error: CosyVoice is required but not available: {e}")
    print("Please install CosyVoice dependencies and download models.")
    COSYVOICE_AVAILABLE = False

class PodcastGenerator:
    def __init__(self):
        self.generated_podcasts = []
        # 检查CosyVoice是否可用
        if not COSYVOICE_AVAILABLE:
            raise RuntimeError("CosyVoice is required but not available. Please check installation and model files.")

        # 初始化TTS实例
        self.tts_instance = get_tts_instance()
        if not self.tts_instance.is_initialized:
            raise RuntimeError("CosyVoice failed to initialize. Please check model files and dependencies.")

        # 初始化混元大模型客户端
        self.hunyuan_client = self._init_hunyuan_client()

    def _init_hunyuan_client(self):
        """初始化混元大模型客户端"""
        try:
            api_key = os.environ.get("HUNYUAN_API_KEY")
            if not api_key:
                print("Warning: HUNYUAN_API_KEY not found in environment variables")
                return None

            client = OpenAI(
                api_key=api_key,
                base_url="https://api.hunyuan.cloud.tencent.com/v1"
            )

            # 测试连接
            test_response = client.chat.completions.create(
                model="hunyuan-turbos-latest",
                messages=[{"role": "user", "content": "测试连接"}],
                max_tokens=10,
                extra_body={"enable_enhancement": True}
            )
            print("✅ 混元大模型连接成功")
            return client
        except Exception as e:
            print(f"❌ 混元大模型初始化失败: {e}")
            return None

    def text_to_podcast(self, topic: str, character_settings: str, voice_settings: str, language: str) -> Tuple[str, str, str]:
        """使用CosyVoice生成播客内容和脚本"""
        return self._generate_with_cosyvoice(topic, character_settings, voice_settings, language)

    def _generate_with_cosyvoice(self, topic: str, character_settings: str, voice_settings: str, language: str) -> Tuple[str, str, str]:
        """使用CosyVoice生成播客"""
        # 解析角色和音色设定
        characters = character_settings.strip().split('\n') if character_settings.strip() else []
        if not characters:
            if language == 'zh':
                characters = ["主持人：专业、理性的播客主持人"]
            else:
                characters = ["Host: Professional and rational podcast host"]

        voices = voice_settings.strip().split('\n') if voice_settings.strip() else []
        if not voices:
            if language == 'zh':
                voices = ["温和中性的声音"]
            else:
                voices = ["Warm and neutral voice"]

        # 生成播客脚本
        script_content = self._generate_podcast_script(topic, characters, language)

        # 使用CosyVoice合成示例音频
        sample_text = f"欢迎收听今天的播客，主题是{topic}" if language == 'zh' else f"Welcome to today's podcast about {topic}"

        audio_path = self.tts_instance.synthesize_speech(
            text=sample_text,
            language=language,
            emotion="friendly",
            stream=False
        )

        # 生成状态信息
        model_status = "✅ 混元大模型" if self.hunyuan_client else "❌ 混元大模型未配置"
        audio_info = f"""
🎙️ ListenPub AI播客生成完成！

📊 生成信息：
- 脚本生成: {model_status}
- 语音合成: CosyVoice-300M-SFT (轻量级)
- 语言: {language}
- 角色数量: {len(characters)}
- 音色类型: {len(voices)}

🤖 大模型状态: {"已连接腾讯混元" if self.hunyuan_client else "未配置 HUNYUAN_API_KEY"}
🎵 音频状态: {"成功生成示例音频" if audio_path else "音频生成失败"}
📝 脚本: 已生成完整播客脚本

✨ 支持特性:
- AI智能脚本生成 (混元大模型)
- 预设音色合成 (CosyVoice)
- 多语言支持 (主要中文)
- 高质量语音
- 快速推理 (内存友好)
"""

        # 角色音色映射
        character_voice_mapping = f"{i18n.t('character_voice_mapping')}\n"
        for i, character in enumerate(characters):
            voice = voices[i] if i < len(voices) else voices[0] if voices else "默认音色"
            character_voice_mapping += f"{character} → {voice} (CosyVoice)\n"

        # 保存到历史记录
        podcast_data = {
            "topic": topic,
            "characters": len(characters),
            "character_settings": character_settings[:100] + "..." if len(character_settings) > 100 else character_settings,
            "voice_settings": voice_settings[:100] + "..." if len(voice_settings) > 100 else voice_settings,
            "duration": "5-15分钟",
            "language": language,
            "engine": "CosyVoice",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.generated_podcasts.append(podcast_data)

        # 清理临时音频文件
        if audio_path and os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
            except:
                pass

        return script_content, audio_info, character_voice_mapping

    def _generate_podcast_script(self, topic: str, characters: List[str], language: str) -> str:
        """使用混元大模型生成播客脚本"""
        if not self.hunyuan_client:
            return self._generate_fallback_script(topic, characters, language)

        try:
            # 构建提示词
            prompt = self._build_script_prompt(topic, characters, language)

            # 调用混元大模型
            response = self.hunyuan_client.chat.completions.create(
                model="hunyuan-turbos-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的播客内容制作专家，擅长根据主题和角色设定生成有趣、专业的播客脚本。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7,
                extra_body={
                    "enable_enhancement": True
                }
            )

            script_content = response.choices[0].message.content
            return f"🎙️ AI生成播客脚本 (混元大模型)\n\n{script_content}"

        except Exception as e:
            print(f"❌ 混元大模型生成脚本失败: {e}")
            return self._generate_fallback_script(topic, characters, language)

    def _build_script_prompt(self, topic: str, characters: List[str], language: str) -> str:
        """构建脚本生成提示词"""
        if language == 'zh':
            prompt = f"""
请为播客生成一个关于"{topic}"的完整脚本。

角色设定：
{chr(10).join([f"• {char}" for char in characters])}

要求：
1. 生成一个8-15分钟的播客脚本
2. 包含开场、主体内容、互动讨论、总结和结尾
3. 确保内容专业、有趣且有教育意义
4. 角色之间要有自然的对话和互动
5. 语言风格要符合播客特点，轻松但不失深度
6. 在适当的地方添加音效提示，如[音乐]、[掌声]等

请生成完整的脚本内容：
"""
        else:
            prompt = f"""
Please generate a complete podcast script about "{topic}".

Character Setup:
{chr(10).join([f"• {char}" for char in characters])}

Requirements:
1. Generate an 8-15 minute podcast script
2. Include opening, main content, interactive discussion, summary, and closing
3. Ensure content is professional, engaging, and educational
4. Natural dialogue and interaction between characters
5. Language style should be podcast-appropriate - relaxed but insightful
6. Add sound effect cues where appropriate, like [music], [applause], etc.

Please generate the complete script content:
"""
        return prompt

    def _generate_fallback_script(self, topic: str, characters: List[str], language: str) -> str:
        """备用脚本生成（原有的静态模板）"""
        if language == 'zh':
            script = f"""
🎙️ 播客脚本 - {topic} (备用模板)

👥 角色设定：
{chr(10).join([f"• {char}" for char in characters])}

📝 内容大纲：

【开场】
主持人：大家好，欢迎收听今天的播客。今天我们要聊的话题是"{topic}"。

【主体内容】
让我们深入探讨这个话题的各个方面...

【互动讨论】
{chr(10).join([f"角色{i+1}：从{char.split('：')[1] if '：' in char else char}的角度分享观点..." for i, char in enumerate(characters)])}

【总结】
通过今天的讨论，我们对"{topic}"有了更深入的理解...

【结尾】
感谢大家的收听，我们下期再见！

🎵 [使用CosyVoice进行语音合成，支持多角色、多情感表达]
"""
        else:
            script = f"""
🎙️ Podcast Script - {topic} (Fallback Template)

👥 Character Setup:
{chr(10).join([f"• {char}" for char in characters])}

📝 Content Outline:

【Opening】
Host: Hello everyone, welcome to today's podcast. Today we're discussing "{topic}".

【Main Content】
Let's dive deep into various aspects of this topic...

【Interactive Discussion】
{chr(10).join([f"Character {i+1}: Sharing perspectives from {char.split(':')[1] if ':' in char else char}..." for i, char in enumerate(characters)])}

【Summary】
Through today's discussion, we've gained deeper insights into "{topic}"...

【Closing】
Thank you for listening, see you next time!

🎵 [Generated using CosyVoice with multi-character and emotional expression support]
"""
        return script

    def get_history(self) -> str:
        """获取生成历史"""
        if not self.generated_podcasts:
            return i18n.t("no_history")

        history = i18n.t("history_title")
        for i, podcast in enumerate(self.generated_podcasts, 1):
            history += i18n.t("history_item",
                            index=i,
                            topic=podcast['topic'],
                            characters=podcast['characters'],
                            character_settings=podcast['character_settings'],
                            voice_settings=podcast['voice_settings'],
                            duration=podcast['duration'],
                            language=podcast['language'],
                            timestamp=podcast['timestamp'])

        return history

def create_error_interface(error_message: str):
    """创建错误信息界面"""
    with gr.Blocks(
        title="ListenPub - CosyVoice Required",
        theme=gr.themes.Soft(
            primary_hue="red",
            secondary_hue="orange",
            neutral_hue="slate"
        )
    ) as app:

        gr.HTML("""
        <div style="text-align: center; padding: 3rem 0; background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%); border-radius: 20px; margin-bottom: 2rem; color: white;">
            <h1 style="font-size: 3rem; margin-bottom: 1rem;">⚠️ CosyVoice Required</h1>
            <p style="font-size: 1.2rem; opacity: 0.9;">ListenPub requires CosyVoice to be properly configured</p>
        </div>
        """)

        with gr.Column():
            gr.Markdown(f"""
            ## ❌ Error

            **{error_message}**

            ## 🔧 解决方案

            请按照以下步骤配置CosyVoice：

            ### 1. 安装依赖
            ```bash
            pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
            ```

            ### 2. 下载CosyVoice模型 (推荐轻量级版本)
            ```python
            from modelscope import snapshot_download
            snapshot_download('iic/CosyVoice-300M-SFT',
                             local_dir='CosyVoice/pretrained_models/CosyVoice-300M-SFT')
            ```

            ### 3. 重新启动应用
            ```bash
            python app.py
            ```

            ## 📚 详细文档

            请查看 `COSYVOICE_SETUP.md` 获取详细的安装和配置指南。

            ## 🎯 ListenPub特性

            配置完成后，您将享受到：
            - 🎤 高质量AI语音合成
            - 🌍 多语言支持（中英日韩）
            - 🎭 零样本语音克隆
            - 😊 情感控制
            - 👥 多说话人对话
            """)

            gr.HTML("""
            <div style="text-align: center; margin-top: 2rem; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
                <p>配置完成后，刷新页面或重新启动应用即可正常使用</p>
            </div>
            """)

    return app

def create_interface():
    try:
        generator = PodcastGenerator()
    except RuntimeError as e:
        # 如果CosyVoice不可用，显示错误信息界面
        return create_error_interface(str(e))

    # 自定义CSS样式，模仿ListenHub的设计
    custom_css = """
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }

    .hero-section {
        text-align: center;
        padding: 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #FCA76F, #ED8FE5, #7EBDEA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 2rem;
    }

    .language-switcher {
        margin-bottom: 1rem;
        padding: 1rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }

    .language-switcher .wrap {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 1rem;
    }

    .card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 1px solid #f0f0f0;
    }

    .input-group {
        margin-bottom: 1.5rem;
    }

    .generate-btn {
        background: linear-gradient(135deg, #FCA76F, #ED8FE5);
        border: none;
        color: white;
        padding: 1rem 2rem;
        border-radius: 15px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
    }

    .generate-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(252, 167, 111, 0.3);
    }

    .output-card {
        background: #f8fafc;
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1rem;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }

    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }

    .feature-card:hover {
        transform: translateY(-5px);
    }

    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .footer-info {
        margin-top: 2rem;
        padding: 1rem 0;
        border-top: 1px solid #e2e8f0;
        align-items: center;
    }

    .footer-info .wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    """

    def update_interface_language(lang):
        """更新界面语言"""
        i18n.set_language(lang)
        return create_interface_components()

    def create_interface_components():
        """创建界面组件"""
        components = {}

        # 主标题和介绍
        components['hero'] = gr.HTML(f"""
        <div class="hero-section">
            <h1 class="hero-title">{i18n.t("hero_title")}</h1>
            <p class="hero-subtitle">{i18n.t("hero_subtitle")}</p>
        </div>
        """)

        # 输入组件
        components['topic_input'] = gr.Textbox(
            label=i18n.t("podcast_topic"),
            placeholder=i18n.t("topic_placeholder"),
            lines=3,
            container=True
        )

        components['podcast_type_dropdown'] = gr.Dropdown(
            choices=i18n.get_podcast_type_choices(),
            label=i18n.t("podcast_type"),
            value=i18n.get_podcast_type_choices()[0],
            info=i18n.t("type_info")
        )

        components['language_dropdown'] = gr.Dropdown(
            choices=i18n.get_language_choices(),
            label=i18n.t("language"),
            value=i18n.get_language_choices()[0]
        )

        components['generate_btn'] = gr.Button(
            i18n.t("generate_btn"),
            variant="primary",
            size="lg",
            elem_classes=["generate-btn"]
        )

        # 输出组件
        components['script_output'] = gr.Textbox(
            label=i18n.t("podcast_script"),
            lines=20,
            max_lines=25,
            placeholder=i18n.t("script_placeholder"),
            container=True
        )

        components['audio_status'] = gr.Textbox(
            label=i18n.t("generation_status"),
            lines=2,
            placeholder=i18n.t("status_placeholder"),
            container=True
        )

        # 特色功能展示
        components['features'] = gr.HTML(f"""
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3>{i18n.t("feature_quick_title")}</h3>
                <p>{i18n.t("feature_quick_desc")}</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <h3>{i18n.t("feature_deep_title")}</h3>
                <p>{i18n.t("feature_deep_desc")}</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💬</div>
                <h3>{i18n.t("feature_debate_title")}</h3>
                <p>{i18n.t("feature_debate_desc")}</p>
            </div>
        </div>
        """)

        return components

    # 创建Gradio界面
    with gr.Blocks(
        title=i18n.t("app_title"),
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="pink",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter")
        ),
        css=custom_css
    ) as app:

        # 移除原来的顶部语言切换器，将在底部实现

        # 主标题和介绍
        hero_section = gr.HTML(f"""
        <div class="hero-section">
            <h1 class="hero-title">{i18n.t("hero_title")}</h1>
            <p class="hero-subtitle">{i18n.t("hero_subtitle")}</p>
        </div>
        """)

        # 主要功能区域
        with gr.Row():
            # 左侧输入区
            with gr.Column(scale=1):
                with gr.Group():
                    settings_title = gr.Markdown(f"### {i18n.t('podcast_settings')}")

                    topic_input = gr.Textbox(
                        label=i18n.t("podcast_topic"),
                        placeholder=i18n.t("topic_placeholder"),
                        lines=3,
                        container=True
                    )

                    character_input = gr.Textbox(
                        label=i18n.t("character_settings"),
                        placeholder=i18n.t("character_placeholder"),
                        lines=4,
                        container=True,
                        info=i18n.t("character_info")
                    )

                    voice_input = gr.Textbox(
                        label=i18n.t("voice_settings"),
                        placeholder=i18n.t("voice_placeholder"),
                        lines=3,
                        container=True,
                        info=i18n.t("voice_info")
                    )

                    language_dropdown = gr.Dropdown(
                        choices=i18n.get_language_choices(),
                        label=i18n.t("language"),
                        value=i18n.get_language_choices()[0]
                    )

                    generate_btn = gr.Button(
                        i18n.t("generate_btn"),
                        variant="primary",
                        size="lg",
                        elem_classes=["generate-btn"]
                    )

            # 右侧输出区
            with gr.Column(scale=2):
                with gr.Group():
                    results_title = gr.Markdown(f"### {i18n.t('generation_results')}")

                    script_output = gr.Textbox(
                        label=i18n.t("podcast_script"),
                        lines=15,
                        max_lines=20,
                        placeholder=i18n.t("script_placeholder"),
                        container=True
                    )

                    audio_status = gr.Textbox(
                        label=i18n.t("generation_status"),
                        lines=2,
                        placeholder=i18n.t("status_placeholder"),
                        container=True
                    )

                    character_voice_output = gr.Textbox(
                        label=i18n.t("character_voice_mapping"),
                        lines=4,
                        placeholder=i18n.t("mapping_placeholder"),
                        container=True
                    )

        # 特色功能展示
        features_section = gr.HTML(f"""
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🎭</div>
                <h3>{i18n.t("feature_character_title")}</h3>
                <p>{i18n.t("feature_character_desc")}</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎤</div>
                <h3>{i18n.t("feature_voice_title")}</h3>
                <p>{i18n.t("feature_voice_desc")}</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎙️</div>
                <h3>{i18n.t("feature_interaction_title")}</h3>
                <p>{i18n.t("feature_interaction_desc")}</p>
            </div>
        </div>
        """)

        # 历史记录和设置（折叠面板）
        with gr.Accordion(i18n.t("generation_history"), open=False) as history_accordion:
            history_title = gr.Markdown(f"### {i18n.t('generation_history')}")
            history_output = gr.Markdown(i18n.t("no_history"))
            refresh_history_btn = gr.Button(i18n.t("refresh_history"), variant="secondary")

        with gr.Accordion(i18n.t("advanced_settings"), open=False) as settings_accordion:
            settings_title_adv = gr.Markdown(f"### {i18n.t('advanced_settings')}")
            with gr.Row():
                api_key_input = gr.Textbox(
                    label="OpenAI API Key",
                    type="password",
                    placeholder=i18n.t("api_key_placeholder"),
                    info=i18n.t("api_key_info")
                )

                voice_dropdown = gr.Dropdown(
                    choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                    label=i18n.t("voice_selection"),
                    value="alloy",
                    info=i18n.t("voice_info")
                )

            with gr.Row():
                temperature_slider = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.7,
                    step=0.1,
                    label=i18n.t("creativity"),
                    info=i18n.t("creativity_info")
                )

                max_tokens_slider = gr.Slider(
                    minimum=100,
                    maximum=4000,
                    value=2000,
                    step=100,
                    label=i18n.t("content_length"),
                    info=i18n.t("content_length_info")
                )

        # 关于信息
        with gr.Accordion(i18n.t("about_listenpub"), open=False) as about_accordion:
            about_title_section = gr.Markdown(f"### {i18n.t('about_listenpub')}")
            about_content_md = gr.Markdown(f"""
            ## {i18n.t("about_title")}

            **{i18n.t("about_subtitle")}**

            ### {i18n.t("core_features")}
            - {i18n.t("feature_ai")}
            - {i18n.t("feature_fast")}
            - {i18n.t("feature_formats")}
            - {i18n.t("feature_multilang")}
            - {i18n.t("feature_responsive")}

            ### {i18n.t("usage_steps")}
            {i18n.t("step1")}
            {i18n.t("step2")}
            {i18n.t("step3")}
            {i18n.t("step4")}
            {i18n.t("step5")}
            {i18n.t("step6")}

            ### {i18n.t("tech_stack")}
            - {i18n.t("tech_frontend")}
            - {i18n.t("tech_ai")}
            - {i18n.t("tech_backend")}
            """)

        # 底部版本信息和语言切换器
        with gr.Row(elem_classes=["footer-info"]):
            with gr.Column(scale=3):
                version_info = gr.Markdown(f"""
                {i18n.t("version_info")}
                """)
            with gr.Column(scale=1):
                language_switcher = gr.Radio(
                    choices=["🇨🇳 中文", "🇺🇸 English"],
                    value="🇨🇳 中文",
                    label="Language / 语言",
                    show_label=False,
                    container=False
                )

        # 语言切换功能
        def switch_language(selected_lang):
            if "中文" in selected_lang:
                i18n.set_language('zh')
            else:
                i18n.set_language('en')

            # 生成更新的关于信息内容
            about_content = f"""
            ## {i18n.t("about_title")}

            **{i18n.t("about_subtitle")}**

            ### {i18n.t("core_features")}
            - {i18n.t("feature_ai")}
            - {i18n.t("feature_fast")}
            - {i18n.t("feature_formats")}
            - {i18n.t("feature_multilang")}
            - {i18n.t("feature_responsive")}

            ### {i18n.t("usage_steps")}
            {i18n.t("step1")}
            {i18n.t("step2")}
            {i18n.t("step3")}
            {i18n.t("step4")}
            {i18n.t("step5")}
            {i18n.t("step6")}

            ### {i18n.t("tech_stack")}
            - {i18n.t("tech_frontend")}
            - {i18n.t("tech_ai")}
            - {i18n.t("tech_backend")}
            """

            # 返回更新后的组件
            return (
                # 更新hero section
                gr.HTML(f"""
                <div class="hero-section">
                    <h1 class="hero-title">{i18n.t("hero_title")}</h1>
                    <p class="hero-subtitle">{i18n.t("hero_subtitle")}</p>
                </div>
                """),
                # 更新设置标题
                gr.Markdown(f"### {i18n.t('podcast_settings')}"),
                # 更新输入组件
                gr.Textbox(
                    label=i18n.t("podcast_topic"),
                    placeholder=i18n.t("topic_placeholder"),
                    lines=3,
                    container=True
                ),
                gr.Textbox(
                    label=i18n.t("character_settings"),
                    placeholder=i18n.t("character_placeholder"),
                    lines=4,
                    container=True,
                    info=i18n.t("character_info")
                ),
                gr.Textbox(
                    label=i18n.t("voice_settings"),
                    placeholder=i18n.t("voice_placeholder"),
                    lines=3,
                    container=True,
                    info=i18n.t("voice_info")
                ),
                gr.Dropdown(
                    choices=i18n.get_language_choices(),
                    label=i18n.t("language"),
                    value=i18n.get_language_choices()[0]
                ),
                gr.Button(
                    i18n.t("generate_btn"),
                    variant="primary",
                    size="lg",
                    elem_classes=["generate-btn"]
                ),
                # 更新结果标题
                gr.Markdown(f"### {i18n.t('generation_results')}"),
                # 更新输出组件
                gr.Textbox(
                    label=i18n.t("podcast_script"),
                    lines=15,
                    max_lines=20,
                    placeholder=i18n.t("script_placeholder"),
                    container=True
                ),
                gr.Textbox(
                    label=i18n.t("generation_status"),
                    lines=2,
                    placeholder=i18n.t("status_placeholder"),
                    container=True
                ),
                gr.Textbox(
                    label=i18n.t("character_voice_mapping"),
                    lines=4,
                    placeholder=i18n.t("mapping_placeholder"),
                    container=True
                ),
                # 更新功能展示
                gr.HTML(f"""
                <div class="feature-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🎭</div>
                        <h3>{i18n.t("feature_character_title")}</h3>
                        <p>{i18n.t("feature_character_desc")}</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🎤</div>
                        <h3>{i18n.t("feature_voice_title")}</h3>
                        <p>{i18n.t("feature_voice_desc")}</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🎙️</div>
                        <h3>{i18n.t("feature_interaction_title")}</h3>
                        <p>{i18n.t("feature_interaction_desc")}</p>
                    </div>
                </div>
                """),
                # 更新折叠面板内的标题和内容
                gr.Markdown(f"### {i18n.t('generation_history')}"),
                gr.Markdown(i18n.t("no_history")),
                gr.Button(i18n.t("refresh_history"), variant="secondary"),
                gr.Markdown(f"### {i18n.t('advanced_settings')}"),
                gr.Markdown(f"### {i18n.t('about_listenpub')}"),
                gr.Markdown(about_content),
                # 更新底部版本信息
                gr.Markdown(f"""
                {i18n.t("version_info")}
                """)
            )

        # 绑定语言切换事件
        language_switcher.change(
            fn=switch_language,
            inputs=[language_switcher],
            outputs=[
                hero_section, settings_title, topic_input, character_input,
                voice_input, language_dropdown, generate_btn, results_title, script_output,
                audio_status, character_voice_output, features_section, history_title, history_output,
                refresh_history_btn, settings_title_adv, about_title_section,
                about_content_md, version_info
            ]
        )

        # 绑定生成事件
        generate_btn.click(
            fn=generator.text_to_podcast,
            inputs=[topic_input, character_input, voice_input, language_dropdown],
            outputs=[script_output, audio_status, character_voice_output]
        )

        # 绑定历史刷新事件
        refresh_history_btn.click(
            fn=generator.get_history,
            outputs=history_output
        )

    return app

if __name__ == "__main__":
    # 创建并启动应用
    app = create_interface()

    print("🎙️ 启动 ListenPub AI播客生成器...")
    print("🌐 访问地址: http://localhost:7860")
    print("🌍 支持中英文切换")
    print("✨ 界面风格: 模仿 ListenHub.ai 设计")

    # 启动Gradio应用
    port = int(os.getenv("GRADIO_SERVER_PORT", 7860))
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True,
        debug=True
    )