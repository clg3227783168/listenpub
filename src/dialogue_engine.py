import os
from openai import OpenAI
import json

class PodcastScriptGenerator:
    def __init__(self, topic, characters={
                "小付": {
                    "gender": "女",
                    "identity": "专业播客主持人",
                    "personality": "亲和力强，善于引导话题，语言表达清晰",
                    "voice_style": "吐字清晰、标准，适合知识传播"
                },
                "小陈": {
                    "gender": "男",
                    "identity": "计算机技术专家",
                    "personality": "善于化繁为简，讲解细致，乐于授业",
                    "voice_style": "语速平稳、表达精准，适合技术讲解"
            }
            }, scenario={
                "深度访谈": [
                    "开场要有力，能吸引听众",
                    "问题要由浅入深”",
                    "嘉宾的回答要专业、有洞见",
                    "结尾要自然，并引导听众思考"]
            }):
        self.client = OpenAI(
        api_key="c1bff111ac2467e326e4103351f1975127e96e29",
        base_url="https://aistudio.baidu.com/llm/lmapi/v3",
        )
        # self.client = OpenAI(
        # api_key="sk-GNj6ikI0K6hwqJPZoO5DJjsrWo3RJAkRfKkLquRWzLCFzZIr",
        # base_url="https://api.hunyuan.cloud.tencent.com/v1",
        # )
        self.topic = topic
        system_template = """<instructions>根据用户输入，生成内容有深度的播客脚本</instructions>
<characters>{characters}</characters>
<scenario>{scenario}</scenario>
<format>
【最严格格式要求】每段对话必须严格遵循以下XML格式：
- 必须以"<角色名>"开始
- 必须以"</角色名>"结束
- 两者之间只有对话内容，没有任何"<>"标记
- 禁止添加任何说明文字、编号或其他格式

示例格式：
<小付>具体内容</小付>
<小陈>具体内容</小陈>
<Mike>具体内容</Mike>

警告：任何不符合上述格式的输出都是错误的！
</format>
<constraints>
1. 所有讨论的信息直接来自或与输入内容密切相关
2. 高度契合<characters>中的角色人设
3. 高度契合<scenario>定义的场景
4. 【最高优先级】每段对话都必须以<角色名>开始，以</角色名>结束，不得遗漏结束标签
</constraints>
<examples>
{example}
</examples>
<exact steps>
1. 分析输入: 仔细阅读并分析用户输入内容，识别关键点、主题和结构
2. 探索主题: 概述输入内容中的主要点，以在对话中覆盖，确保全面覆盖
3. 生成对话: 严格遵守<constraints>
4. 审核对话: 仔细审查生成的对话，确保其遵守<constraints>
</exact steps>"""

        example = """<小付>大家好，欢迎收听本期的"科技前沿"播客！我是主持人小付。今天我们有幸邀请到了计算机技术专家小陈，他将和我们深入聊聊"云原生"这个热门话题。小陈，欢迎来到节目！</小付>
<小陈>谢谢小付！很高兴来到这里，和听众们分享云原生的那些事儿。</小陈>"""
        formatted_characters = json.dumps(characters, indent=2, ensure_ascii=False)
        formatted_scenario = json.dumps(scenario, indent=2, ensure_ascii=False)
        self.formatted_system_prompt = system_template.format(characters=formatted_characters, scenario=formatted_scenario, example=example)
        print(self.formatted_system_prompt)
    def generate_script(self):
        """
        生成播客脚本
        
        返回:
        str: 生成的播客脚本内容
        """
        # 构建消息
        messages = [
            {"role": "system", "content": self.formatted_system_prompt},
            {"role": "user", "content": self.topic},
        ]
        
        try:
            # 调用API生成脚本
            response = self.client.chat.completions.create(
                model="ernie-4.5-turbo-128k-preview",
                # model="hunyuan-turbos-latest",
                messages=messages,
                stream=False
            )
            raw_content = response.choices[0].message.content
            print(raw_content)
            # 后处理：自动补全缺失的结束标签
            return self._fix_missing_tags(raw_content)
        except Exception as e:
            return f"API调用错误: {e}"

    def _fix_missing_tags(self, content):
        """
        后处理方法：修复XML标签配对问题

        参数:
        content (str): 原始生成的内容

        返回:
        str: 修复后的内容
        """
        import re

        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                fixed_lines.append('')
                continue

            # 匹配完整的XML标签格式：<角色名>内容</角色名>
            xml_pattern = r'^<(\w+)>(.*?)</(\w+)>$'
            match = re.match(xml_pattern, line)

            if match:
                start_tag, content_text, end_tag = match.groups()
                # 如果开始标签和结束标签不匹配，使用开始标签作为正确的角色名
                if start_tag != end_tag:
                    line = f'<{start_tag}>{content_text}</{start_tag}>'
                # 如果匹配，保持原样
                fixed_lines.append(line)
            else:
                # 检查是否只有开始标签没有结束标签
                start_only_match = re.match(r'^<(\w+)>(.*)$', line)
                if start_only_match:
                    character, content_text = start_only_match.groups()
                    # 清理content_text中可能存在的错误结束标签
                    content_text = re.sub(r'</\w+>$', '', content_text).strip()
                    line = f'<{character}>{content_text}</{character}>'

                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

if __name__ == "__main__":
    topic = """
云原生
"""
    # 创建生成器实例
    generator = PodcastScriptGenerator(
        topic=topic
    )
    # 生成并打印脚本
    script = generator.generate_script()
    print("生成的播客对话:\n")
    print(script)