# -*- coding: utf-8 -*-
"""音频生成引擎"""

from typing import List, Dict, Optional, Tuple
import re


class AudioEngine:
    """播客音频生成引擎"""

    def __init__(self):
        """初始化音频引擎"""
        # 音色映射（这里先用文本描述，后续可以对接真实的TTS API）
        self.voice_styles = {
            "专业权威 沉稳有力的声音，体现专业性": "professional_male",
            "活泼生动 充满活力的声音，富有感染力": "energetic_female",
            "清晰标准 适合知识传播": "standard_male",
            "温和亲切 温暖柔和的声音，让人感到舒适": "warm_female",
            "温柔甜美 轻柔甜美的声音，很有亲和力": "sweet_female",
            "深沉磁性 低沉有磁性的声音，很有吸引力": "deep_male",
        }

    def parse_script(self, script: str) -> List[Dict[str, str]]:
        """
        解析播客脚本，提取对话段落

        Args:
            script: 播客脚本文本

        Returns:
            对话段落列表，每个段落包含 speaker 和 text
        """
        dialogues = []

        # 分割脚本为行
        lines = script.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 匹配格式：**角色**: 对话内容
            match = re.match(r'\*\*([^*]+)\*\*:\s*(.+)', line)
            if match:
                speaker = match.group(1).strip()
                text = match.group(2).strip()

                # 过滤掉音效标记
                if not text.startswith('[') and not text.endswith(']'):
                    dialogues.append({
                        "speaker": speaker,
                        "text": text
                    })

        return dialogues

    def generate_audio(
        self,
        script: str,
        characters: List[Dict[str, str]],
        output_path: Optional[str] = None
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        生成播客音频（当前版本返回解析后的对话列表）

        Args:
            script: 播客脚本
            characters: 角色信息列表
            output_path: 输出音频文件路径（可选）

        Returns:
            状态信息和对话段落列表
        """
        # 解析脚本
        dialogues = self.parse_script(script)

        if not dialogues:
            return "脚本解析失败：未找到有效的对话内容", []

        # 构建角色-音色映射
        character_voice_map = {}
        for char in characters:
            identity = char.get('identity', '')
            voice_style = char.get('voice_style', '')
            if identity and voice_style:
                voice_id = self.voice_styles.get(voice_style, 'default')
                character_voice_map[identity] = voice_id

        # 为每个对话段落分配音色
        for dialogue in dialogues:
            speaker = dialogue['speaker']
            # 尝试从角色映射中找到匹配的音色
            for identity, voice_id in character_voice_map.items():
                if identity in speaker:
                    dialogue['voice'] = voice_id
                    break
            else:
                dialogue['voice'] = 'default'

        status = f"✓ 脚本解析完成\n✓ 共 {len(dialogues)} 个对话段落\n✓ 已为每个角色分配音色\n\n"
        status += "注意：当前版本为演示模式，音频生成功能需要配置 TTS API。\n"
        status += "您可以集成以下 TTS 服务：\n"
        status += "- OpenAI TTS\n"
        status += "- Azure Speech Services\n"
        status += "- Google Cloud Text-to-Speech\n"
        status += "- 本地 TTS 引擎（如 Coqui TTS）"

        return status, dialogues

    def preview_audio_info(self, dialogues: List[Dict[str, str]]) -> str:
        """
        生成音频信息预览

        Args:
            dialogues: 对话段落列表

        Returns:
            格式化的预览信息
        """
        if not dialogues:
            return "暂无对话内容"

        preview = "## 音频预览信息\n\n"
        preview += f"总对话数：{len(dialogues)} 条\n\n"

        # 统计每个说话者的对话数
        speaker_stats = {}
        for dialogue in dialogues:
            speaker = dialogue['speaker']
            speaker_stats[speaker] = speaker_stats.get(speaker, 0) + 1

        preview += "### 角色对话分布：\n"
        for speaker, count in speaker_stats.items():
            voice = dialogues[0].get('voice', 'default')
            for d in dialogues:
                if d['speaker'] == speaker:
                    voice = d.get('voice', 'default')
                    break
            preview += f"- {speaker}：{count} 条对话 (音色: {voice})\n"

        return preview

    def estimate_duration(self, dialogues: List[Dict[str, str]]) -> float:
        """
        估算音频时长（基于文本长度）

        Args:
            dialogues: 对话段落列表

        Returns:
            估算的时长（秒）
        """
        # 简单估算：平均每个字0.3秒（中文），每个单词0.5秒（英文）
        total_chars = sum(len(d['text']) for d in dialogues)

        # 粗略估算（中文为主）
        estimated_seconds = total_chars * 0.3

        return estimated_seconds

    def generate_audio_with_api(
        self,
        dialogues: List[Dict[str, str]],
        api_config: Dict[str, str]
    ) -> str:
        """
        使用真实的 TTS API 生成音频（占位方法）

        Args:
            dialogues: 对话段落列表
            api_config: API 配置信息

        Returns:
            生成的音频文件路径
        """
        # TODO: 实现真实的 TTS API 调用
        # 可以集成 OpenAI TTS, Azure Speech, Google TTS 等
        raise NotImplementedError("TTS API 集成功能待实现，请配置您的 TTS 服务")
