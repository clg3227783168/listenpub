# -*- coding: utf-8 -*-
import gradio as gr
import os
import tempfile
import json
from typing import Optional, Tuple
import time
from i18n_helper import i18n

class PodcastGenerator:
    def __init__(self):
        self.generated_podcasts = []

    def text_to_podcast(self, topic: str, podcast_type: str, language: str) -> Tuple[str, str]:
        """生成播客内容和脚本"""
        try:
            # 模拟播客生成过程
            time.sleep(2)  # 模拟处理时间

            # 根据播客类型设置内容框架
            if i18n.t("quick_essence") in podcast_type:
                duration = "3-5分钟" if i18n.get_language() == 'zh' else "3-5 minutes"
                if i18n.get_language() == 'zh':
                    content_outline = """
1. 核心观点提炼
2. 关键信息速递
3. 实用要点总结
"""
                    style_description = "快节奏、高信息密度的精华内容"
                else:
                    content_outline = """
1. Core insights extraction
2. Key information delivery
3. Practical points summary
"""
                    style_description = "fast-paced, high information density content"

            elif i18n.t("deep_exploration") in podcast_type:
                duration = "8-15分钟" if i18n.get_language() == 'zh' else "8-15 minutes"
                if i18n.get_language() == 'zh':
                    content_outline = """
1. 话题背景介绍
2. 多角度深入分析
3. 相关案例研究
4. 实际应用探讨
5. 未来趋势展望
"""
                    style_description = "深入浅出、全面系统的探索分析"
                else:
                    content_outline = """
1. Topic background introduction
2. Multi-perspective in-depth analysis
3. Related case studies
4. Practical application discussion
5. Future trend outlook
"""
                    style_description = "comprehensive and systematic exploration analysis"

            elif i18n.t("debate_discussion") in podcast_type:
                duration = "8-15分钟" if i18n.get_language() == 'zh' else "8-15 minutes"
                if i18n.get_language() == 'zh':
                    content_outline = """
1. 争议焦点提出
2. 正方观点阐述
3. 反方观点辩驳
4. 观点交锋分析
5. 思辨启发总结
"""
                    style_description = "观点交锋、激发思考的辩论形式"
                else:
                    content_outline = """
1. Controversial focus presentation
2. Pro arguments explanation
3. Counter arguments rebuttal
4. Viewpoint clash analysis
5. Critical thinking inspiration
"""
                    style_description = "debate format that inspires critical thinking"
            else:
                duration = i18n.t("unknown") if i18n.get_language() == 'zh' else "Unknown"
                content_outline = "1. Content TBD"
                style_description = "Standard podcast format"

            # 生成播客脚本
            script = f"""
{i18n.t("script_title", topic=topic)}
{i18n.t("script_type", podcast_type=podcast_type)}
{i18n.t("script_duration", duration=duration)}

{i18n.t("script_opening")}
{i18n.t("opening_text", topic=topic, style_description=style_description)}

{i18n.t("script_content")}
{content_outline}

{i18n.t("script_language")}
{i18n.t("language_text", language=language)}

{i18n.t("script_ending")}
{i18n.t("ending_text")}
"""

            # 模拟音频文件路径
            audio_info = i18n.t("audio_generated", duration=duration, podcast_type=podcast_type)

            # 保存到历史记录
            podcast_data = {
                "topic": topic,
                "podcast_type": podcast_type,
                "duration": duration,
                "language": language,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self.generated_podcasts.append(podcast_data)

            return script, audio_info

        except Exception as e:
            return i18n.t("generation_failed", error=str(e)), i18n.t("generation_failed_short")

    def get_history(self) -> str:
        """获取生成历史"""
        if not self.generated_podcasts:
            return i18n.t("no_history")

        history = i18n.t("history_title")
        for i, podcast in enumerate(self.generated_podcasts, 1):
            history += i18n.t("history_item",
                            index=i,
                            topic=podcast['topic'],
                            podcast_type=podcast['podcast_type'],
                            duration=podcast['duration'],
                            language=podcast['language'],
                            timestamp=podcast['timestamp'])

        return history

def create_interface():
    generator = PodcastGenerator()

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

        # 语言切换器
        with gr.Row(elem_classes=["language-switcher"]):
            with gr.Column(scale=8):
                gr.HTML("<div style='height: 1px;'></div>")  # 占位符
            with gr.Column(scale=4):
                language_switcher = gr.Radio(
                    choices=["🇨🇳 中文", "🇺🇸 English"],
                    value="🇨🇳 中文",
                    label="Language / 语言",
                    show_label=True,
                    container=True
                )

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

                    podcast_type_dropdown = gr.Dropdown(
                        choices=i18n.get_podcast_type_choices(),
                        label=i18n.t("podcast_type"),
                        value=i18n.get_podcast_type_choices()[0],
                        info=i18n.t("type_info")
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
                        lines=20,
                        max_lines=25,
                        placeholder=i18n.t("script_placeholder"),
                        container=True
                    )

                    audio_status = gr.Textbox(
                        label=i18n.t("generation_status"),
                        lines=2,
                        placeholder=i18n.t("status_placeholder"),
                        container=True
                    )

        # 特色功能展示
        features_section = gr.HTML(f"""
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

        # 历史记录和设置（折叠面板）
        with gr.Accordion(i18n.t("generation_history"), open=False):
            history_output = gr.Markdown(i18n.t("no_history"))
            refresh_history_btn = gr.Button(i18n.t("refresh_history"), variant="secondary")

        with gr.Accordion(i18n.t("advanced_settings"), open=False):
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
        with gr.Accordion(i18n.t("about_listenpub"), open=False):
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

            ---
            {i18n.t("version_info")}
            """
            gr.Markdown(about_content)

        # 语言切换功能
        def switch_language(selected_lang):
            if "中文" in selected_lang:
                i18n.set_language('zh')
            else:
                i18n.set_language('en')

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
                    container=True,
                    value=topic_input.value
                ),
                gr.Dropdown(
                    choices=i18n.get_podcast_type_choices(),
                    label=i18n.t("podcast_type"),
                    value=i18n.get_podcast_type_choices()[0],
                    info=i18n.t("type_info")
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
                    lines=20,
                    max_lines=25,
                    placeholder=i18n.t("script_placeholder"),
                    container=True,
                    value=script_output.value
                ),
                gr.Textbox(
                    label=i18n.t("generation_status"),
                    lines=2,
                    placeholder=i18n.t("status_placeholder"),
                    container=True,
                    value=audio_status.value
                ),
                # 更新功能展示
                gr.HTML(f"""
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
            )

        # 绑定语言切换事件
        language_switcher.change(
            fn=switch_language,
            inputs=[language_switcher],
            outputs=[
                hero_section, settings_title, topic_input, podcast_type_dropdown,
                language_dropdown, generate_btn, results_title, script_output,
                audio_status, features_section
            ]
        )

        # 绑定生成事件
        generate_btn.click(
            fn=generator.text_to_podcast,
            inputs=[topic_input, podcast_type_dropdown, language_dropdown],
            outputs=[script_output, audio_status]
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
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        debug=True
    )