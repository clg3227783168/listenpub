import dashscope
from dashscope.audio.tts_v2 import *
import re
import os
from pydub import AudioSegment
# 若没有将API Key配置到环境变量中，需将your-api-key替换为自己的API Key
dashscope.api_key = "sk-07814aca07584d118f214fcff042ed31"
CharactertoVoice = {
    "小付": "longanwen",
    "小陈": "longanshuo",
    "Mike": "longanzhi",
    "Lily": "longanrou",
    "Helen": "longhua_v2"
}
class AudioGenerator:
    def _generate_audio(self, script_text, voice="longxiaochun_v2"):
        # 实例化SpeechSynthesizer，并在构造方法中传入模型（model）、音色（voice）等请求参数
        synthesizer = SpeechSynthesizer(model="cosyvoice-v2", voice=voice)
        # 发送待合成文本，获取二进制音频
        audio = synthesizer.call(script_text)
        return audio
        # 将音频保存至本地
        # with open('output.mp3', 'wb') as f:
        #     f.write(audio)

    def _parse_script(self, script_text):
        """
        解析脚本文本，提取角色对话

        参数:
        script_text (str): 格式为 <角色名>对话内容</角色名> 的脚本文本

        返回:
        list: 包含 (角色名, 对话内容) 元组的列表
        """
        segments = []
        # 使用正则表达式匹配 <角色名>内容</角色名> 格式
        pattern = r'<(\w+)>(.*?)</\1>'
        matches = re.findall(pattern, script_text, re.DOTALL)

        for character, content in matches:
            # 清理内容，去除多余空白
            clean_content = content.strip()
            if clean_content:  # 只添加非空内容
                segments.append((character, clean_content))

        return segments

    def batch_generate_audio(self, script_text, output_file="podcast_output.mp3"):
        """
        批量生成音频，根据脚本中每个角色使用对应的音色，并合并成完整音频

        参数:
        script_text (str): 格式为 <角色名>对话内容</角色名> 的脚本文本
        output_file (str): 输出的音频文件名

        返回:
        str: 生成的音频文件路径
        """
        # 解析脚本
        segments = self._parse_script(script_text)

        if not segments:
            raise ValueError("未能从脚本中提取到有效的对话内容")

        print(f"解析到 {len(segments)} 段对话")

        # 存储所有音频段
        audio_segments = []

        # 临时文件列表
        temp_files = []

        try:
            # 为每段对话生成音频
            for i, (character, content) in enumerate(segments):
                # 获取角色对应的音色
                voice = CharactertoVoice.get(character)
                if not voice:
                    print(f"警告: 角色 '{character}' 未找到对应音色，跳过此段")
                    continue

                print(f"正在生成第 {i+1} 段音频 - 角色: {character}, 音色: {voice}")
                print(f"内容: {content[:50]}...")  # 显示前50个字符

                # 生成音频
                try:
                    audio_data = self._generate_audio(content, voice)

                    # 保存临时音频文件
                    temp_file = f"temp_audio_{i}.mp3"
                    with open(temp_file, 'wb') as f:
                        f.write(audio_data)

                    temp_files.append(temp_file)

                    # 加载音频段
                    audio_segment = AudioSegment.from_mp3(temp_file)
                    audio_segments.append(audio_segment)

                    print(f"第 {i+1} 段音频生成完成")

                except Exception as e:
                    print(f"生成第 {i+1} 段音频时出错: {e}")
                    continue

            if not audio_segments:
                raise RuntimeError("没有成功生成任何音频段")

            # 合并所有音频段
            print("正在合并音频...")
            final_audio = sum(audio_segments)

            # 导出最终音频
            final_audio.export(output_file, format="mp3")
            print(f"完整音频已保存到: {output_file}")

            return output_file

        finally:
            # 清理临时文件
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    print(f"清理临时文件 {temp_file} 时出错: {e}")
        

if __name__ == "__main__":
    # 测试批量生成音频功能
    audioGenerator = AudioGenerator()

    # 测试脚本（模拟 dialogue_engine.py 生成的格式）
    test_script = """<小付>大家好，欢迎收听本期的"科技前沿"播客！我是主持人小付。</小付>
<小陈>很高兴来到节目，今天我们来聊聊云原生技术。</小陈>
<小付>云原生这个词现在很火，但很多人可能还不清楚它到底是什么。</小付>
<小陈>简单来说，云原生是为云环境而生的应用架构方式。</小陈>"""

    try:
        # 测试脚本解析
        segments = audioGenerator._parse_script(test_script)
        print("解析结果:")
        for i, (char, content) in enumerate(segments):
            print(f"{i+1}. 角色: {char}, 内容: {content}")

        # 批量生成音频
        print("\n开始批量生成音频...")
        output_file = audioGenerator.batch_generate_audio(test_script, "test_podcast.mp3")
        print(f"音频生成完成: {output_file}")

    except Exception as e:
        print(f"测试失败: {e}")
