# -*- coding: utf-8 -*-
import gradio as gr
import os
import sys

class Preset:
    def __init__(self):
        # 初始化预设选项（仅用于UI展示）
        self._init_preset_options()

    def _init_preset_options(self):
        """初始化预设的角色和场景选项"""
        self.character_presets = {
            "小付": {
                "gender": "女",
                "identity": "专业播客主持人",
                "personality": "亲和力强，善于引导话题，语言表达清晰",
                "voice_style": "清晰标准 适合知识传播"
            },
            "小陈": {
                "gender": "男",
                "identity": "专家",
                "personality": "深入浅出，耐心细致，乐于分享知识",
                "voice_style": "清晰标准 适合知识传播"
            },
            "Mike": {
                "gender": "男",
                "identity": "学者",
                "personality": "博学风趣，善于讲故事，富有文化底蕴",
                "voice_style": "温和亲切 温暖柔和的声音，让人感到舒适"
            },
            "Leo": {
                "gender": "男",
                "identity": "医生",
                "personality": "权威可信，细心负责，关注民生健康",
                "voice_style": "温柔甜美 轻柔甜美的声音，很有亲和力"
            },
            "Helen": {
                "gender": "女",
                "identity": "生活方式分享者",
                "personality": "亲和力强，贴近生活，善于共情",
                "voice_style": "活泼生动 充满活力的声音，富有感染力"
            },
        }

        self.scenario_presets = {
            "深度访谈": "一对一深入探讨", # 角色为主持人和任意其他一人
            "圆桌讨论": "多人讨论，观点碰撞，互动热烈", # 角色为主持人和两位或以上其他人
            "辩论对话": "不同观点的理性辩论和讨论", # 角色为两位观点不同的两人
            "故事叙述": "以讲故事的方式展开，引人入胜", # 角色为主持人和其他一人
        }

def create_interface():
    generator = Preset()
    
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

    # 创建Gradio界面
    with gr.Blocks(
        title="ListenPub - AI播客生成平台",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="pink",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter")
        ),
        css=custom_css
    ) as app:

        # 主标题和介绍
        hero_section = gr.HTML("""
        <div class="hero-section">
            <h1 class="hero-title">ListenPub - AI播客生成平台</h1>
        </div>
        """)

        # 主要功能区域
        with gr.Row():
            # 左侧输入区
            with gr.Column(scale=1):
                with gr.Group():
                    settings_title = gr.Markdown("### 播客设置")

                    topic_input = gr.Textbox(
                        label="播客主题或文本内容",
                        placeholder="请输入您想要生成播客的主题或文本内容...",
                        lines=3,
                        container=True
                    )

                    character_checkbox = gr.CheckboxGroup(
                        choices=list(generator.character_presets.keys()),
                        label="角色类型选择（多选）",
                        value=[list(generator.character_presets.keys())[0], list(generator.character_presets.keys())[1]],
                        container=True,
                        info="选择适合您播客主题的角色组合"
                    )

                    # 显示选中角色的详细信息
                    character_info = gr.Markdown(
                        "",
                        label="角色详细信息",
                        container=True
                    )

                    scenario_dropdown = gr.Dropdown(
                        choices=list(generator.scenario_presets.keys()),
                        label="场景模式选择",
                        value=list(generator.scenario_presets.keys())[0],
                        container=True,
                        info="选择播客的呈现形式和互动风格"
                    )

                    # 显示选中场景的详细信息
                    scenario_info = gr.Markdown(
                        "",
                        label="场景详细信息",
                        container=True
                    )

                    generate_btn = gr.Button(
                        "生成播客",
                        variant="primary",
                        size="lg",
                        elem_classes=["generate-btn"]
                    )

            # 右侧输出区
            with gr.Column(scale=2):
                with gr.Group():
                    results_title = gr.Markdown("### 生成结果")

                    script_output = gr.Textbox(
                        label="播客脚本",
                        lines=15,
                        max_lines=20,
                        placeholder="生成的播客脚本将显示在这里...",
                        container=True
                    )

                    audio_status = gr.Textbox(
                        label="生成状态",
                        lines=2,
                        placeholder="准备就绪，等待生成...",
                        container=True
                    )


        # 特色功能展示
        features_section = gr.HTML("""
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🎭</div>
                <h3>多角色人设</h3>
                <p>13种预设角色类型，支持自定义角色人设和个性化配置</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎤</div>
                <h3>多样音色风格</h3>
                <p>8种声音风格可选，支持零样本语音克隆和情感表达</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎙️</div>
                <h3>自然互动对话</h3>
                <p>AI驱动的多场景对话生成，呈现真实的播客互动体验</p>
            </div>
        </div>
        """)

        # 历史记录和设置（折叠面板）
        with gr.Accordion("生成历史", open=False) as history_accordion:
            history_title = gr.Markdown("### 生成历史")
            history_output = gr.Markdown("暂无生成历史")
            refresh_history_btn = gr.Button("刷新历史", variant="secondary")

        # 更新角色信息的函数
        def update_character_info(selected_characters):
            if not selected_characters:
                return "请选择至少一个角色类型"

            info_text = "### 选中角色详情：\n\n"
            for char in selected_characters:
                if char in generator.character_presets:
                    char_data = generator.character_presets[char]
                    info_text += f"**{char}**\n"
                    info_text += f"- 性别：{char_data['gender']}\n"
                    info_text += f"- 身份：{char_data['identity']}\n"
                    info_text += f"- 性格：{char_data['personality']}\n"
                    info_text += f"- 音色：{char_data['voice_style']}\n\n"

            return info_text

        # 更新场景信息的函数
        def update_scenario_info(selected_scenario):
            if not selected_scenario:
                return "请选择一个场景模式"

            if selected_scenario in generator.scenario_presets:
                scenario_desc = generator.scenario_presets[selected_scenario]
                info_text = f"**描述：** {scenario_desc}\n\n"
                return info_text
            return ""

        # 绑定角色选择变化事件
        character_checkbox.change(
            fn=update_character_info,
            inputs=character_checkbox,
            outputs=character_info
        )

        # 绑定场景选择变化事件
        scenario_dropdown.change(
            fn=update_scenario_info,
            inputs=scenario_dropdown,
            outputs=scenario_info
        )

        # 页面加载时初始化场景信息
        app.load(
            fn=update_scenario_info,
            inputs=scenario_dropdown,
            outputs=scenario_info
        )

        # 生成播客的主函数
        def generate_podcast(topic, selected_characters, scenario):
            """生成播客脚本和音频信息"""
            # 验证输入
            if not topic.strip():
                return "请输入播客主题或文本内容", "请先输入主题或文本内容"

            if not selected_characters:
                return "请至少选择一个角色类型", "请先选择角色"

            if not scenario:
                return "请选择一个场景模式", "请先选择场景"

            # 准备角色信息
            characters_data = []
            for char_name in selected_characters:
                if char_name in generator.character_presets:
                    characters_data.append(generator.character_presets[char_name])

            # try:
            #     # 生成脚本
            #     script = dialogue_engine.generate_script(
            #         topic=topic.strip(),
            #         characters=characters_data,
            #         scenario=scenario,
            #         duration_minutes=5 # 预设生成5分钟播客，可根据需要调整
            #     )

            #     # 解析脚本并生成音频信息
            #     audio_status, dialogues = audio_engine.generate_audio(
            #         script=script,
            #         characters=characters_data,
            #         scenario=scenario
            #     )

            #     # 添加统计信息
            #     if dialogues:
            #         duration = audio_engine.estimate_duration(dialogues)
            #         minutes = int(duration // 60)
            #         seconds = int(duration % 60)
            #         audio_status += f"\n\n预估时长：{minutes} 分 {seconds} 秒"

            #         # 添加预览信息
            #         preview = audio_engine.preview_audio_info(dialogues)
            #         audio_status += f"\n\n{preview}"

            #     return script, audio_status

            # except Exception as e:
            #     error_msg = f"生成失败：{str(e)}"
            #     return error_msg, error_msg

        # 绑定生成按钮的点击事件
        generate_btn.click(
            fn=generate_podcast,
            inputs=[topic_input, character_checkbox, scenario_dropdown],
            outputs=[script_output, audio_status]
        )

    return app

if __name__ == "__main__":
    # 创建并启动应用
    app = create_interface()

    print("🎙️ 启动 ListenPub AI播客生成器...")
    print("🌐 访问地址: http://localhost:7860")

    # 启动Gradio应用
    port = int(os.getenv("GRADIO_SERVER_PORT", 7860))
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=True,
        show_error=True,
        debug=True
    )