import os
from openai import OpenAI

class PodcastScriptGenerator:
    def __init__(self, conversation_style="友好、深入", speakers=["小陈", "小付"], input_text=""):
        self.conversation_style = conversation_style
        self.speakers = speakers
        self.input_text = input_text
        self.client = OpenAI(
        # api_key=os.environ.get("HUNYUAN_API_KEY"),
        api_key="sk-GNj6ikI0K6hwqJPZoO5DJjsrWo3RJAkRfKkLquRWzLCFzZIr",
        base_url="https://api.hunyuan.cloud.tencent.com/v1",
)        
        self.speaker_num = len(speakers)
        self.system_template = """
<role>你是一个专业的博客脚本生成助手</role>
<style>保持{conversation_style}。在可能的情况下超越人类水平推理</style>
<characters>{speakers}。</characters>
<examples>
<小付> "今天，我们将讨论一个关于[输入文本主题]的有趣内容。让我们开始吧！"</小付>
<小陈> "我很兴奋讨论这个！我们今天覆盖的内容的主要点是什么？"</小陈>
<小付> "我认为[输入文本主题]是一个非常重要的话题。"</小付>
...<examples>
详细流程：
'''
输入内容分析: 仔细阅读并分析提供的输入内容，识别关键点、主题和结构
主题探索: 概述输入内容中的主要点，以在对话中覆盖，确保全面覆盖
信息准确性：确保所有讨论的信息直接来自或与输入内容密切相关
用对话式语言呈现文本信息，富有情感。模拟多说话者对话，带有重叠说话者和来回调侃。每个说话者回合不应持续太久。结果应努力实现重叠对话，经常使用短句模拟自然对话。
融入吸引人元素，同时忠于输入内容，包括至少一个实例，其中一个人尊重地挑战或批评另一个人提出的点
有时使用填充词，如嗯、呃、你知道，以及一些结巴。有时提供口头反馈，如“我明白了、有趣、懂了”。
【重要约束 - 必须严格遵守】
情感标记限制：你必须且只能使用以下指定的情感标记，绝对不允许使用任何其他标记：
    [breath], 
    [noise],
    <strong>, </strong>,
    [laughter],
    [cough],
    [clucking]',
    [accent]',
    [quick_breath],
    <laughter>, </laughter>,
    [hissing],
    [sigh],
    [vocalized-noise],
    [lipsmack], 
    [mn]
    示例:<小付>在面对挑战时，他展现了非凡的<strong>勇气</strong>与<strong>智慧</strong>。</小付>
持续参考输入内容，确保对话保持主题
确保TTS标签正确关闭，例如<strong>应使用</strong>关闭
'''
生成TTS优化的播客对话，准确讨论提供的输入内容，遵守所有指定要求。
"""
    def generate_script(self):
        """
        生成播客脚本
        
        返回:
        str: 生成的播客脚本内容
        """
        # 格式化系统提示
        formatted_system_prompt = self.system_template.format(
            conversation_style=self.conversation_style,
            speakers=self.speakers,
        )
        
        # 构建消息
        messages = [
            {"role": "system", "content": formatted_system_prompt},
            {"role": "user", "content": f"请基于以下内容生成播客对话：\n\n{self.input_text}"},
        ]
        
        try:
            # 调用API生成脚本
            response = self.client.chat.completions.create(
                model="hunyuan-turbos-latest",
                messages=messages,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"API调用错误: {e}"

if __name__ == "__main__":
    input_text = """
雷军今日新闻
"""
    
    # 创建生成器实例
    generator = PodcastScriptGenerator(
        conversation_style="友好、深入",
        input_text=input_text
    )
    
    # 生成并打印脚本
    script = generator.generate_script()
    print("生成的播客对话:\n")
    print(script)