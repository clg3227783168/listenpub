# -*- coding: utf-8 -*-
"""
CosyVoice语音合成引擎
专门处理包含情感标记的文本，生成高质量语音
"""

import asyncio
import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# 导入CosyVoice TTS模块
try:
    import sys
    sys.path.append('./src/tts')
    from cosy_voice_tts import get_tts_instance
    COSYVOICE_AVAILABLE = True
except ImportError as e:
    COSYVOICE_AVAILABLE = False
    print(f"Warning: CosyVoice not available: {e}")

logger = logging.getLogger(__name__)

class VoiceGender(Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class VoiceAge(Enum):
    YOUNG = "young"      # 18-30
    MIDDLE = "middle"    # 30-50
    MATURE = "mature"    # 50+

@dataclass
class VoiceProfile:
    """音色档案"""
    name: str
    gender: VoiceGender = VoiceGender.NEUTRAL
    age: VoiceAge = VoiceAge.MIDDLE
    speaker_audio_path: Optional[str] = None  # 零样本克隆音频路径
    speaker_prompt: Optional[str] = None      # 说话人描述文本
    language: str = "zh"                      # 语言代码

class VoiceEngine:
    """CosyVoice语音合成引擎"""

    def __init__(self):
        """初始化CosyVoice语音引擎"""
        if not COSYVOICE_AVAILABLE:
            raise RuntimeError("CosyVoice不可用，请检查安装和配置")

        self.tts_instance = None
        self._initialize_tts()

    def _initialize_tts(self):
        """初始化CosyVoice TTS实例"""
        try:
            self.tts_instance = get_tts_instance()
            if not self.tts_instance.is_initialized:
                logger.error("CosyVoice初始化失败")
                raise RuntimeError("CosyVoice初始化失败")
            logger.info("CosyVoice语音引擎初始化成功")
        except Exception as e:
            logger.error(f"CosyVoice初始化错误: {e}")
            raise

    def parse_voice_settings(self, voice_input: str) -> List[VoiceProfile]:
        """解析用户输入的音色设定

        支持格式：
        - 角色名：音频文件路径|描述文本
        - 角色名：描述文本（使用预设说话人）
        """
        voices = []
        lines = [line.strip() for line in voice_input.split('\n') if line.strip()]

        for i, line in enumerate(lines):
            voice = self._parse_single_voice(line, i)
            voices.append(voice)

        return voices

    def _parse_single_voice(self, line: str, index: int) -> VoiceProfile:
        """解析单个音色设定"""
        # 解析格式：角色名：音频路径|描述 或 角色名：描述
        if '：' in line:
            name_part, desc_part = line.split('：', 1)
        elif ':' in line:
            name_part, desc_part = line.split(':', 1)
        else:
            name_part = f"角色{index+1}"
            desc_part = line

        name = name_part.strip()

        # 检查是否包含音频文件路径
        speaker_audio_path = None
        speaker_prompt = desc_part.strip()

        if '|' in desc_part:
            audio_part, prompt_part = desc_part.split('|', 1)
            audio_part = audio_part.strip()
            if os.path.exists(audio_part):
                speaker_audio_path = audio_part
                speaker_prompt = prompt_part.strip()

        # 提取基本特征
        gender = self._extract_gender(desc_part)
        age = self._extract_age(desc_part)
        language = self._extract_language(desc_part)

        return VoiceProfile(
            name=name,
            gender=gender,
            age=age,
            speaker_audio_path=speaker_audio_path,
            speaker_prompt=speaker_prompt,
            language=language
        )

    def _extract_gender(self, description: str) -> VoiceGender:
        """提取性别特征"""
        if any(keyword in description for keyword in ['男性', '男声', '雄性', 'male', '男']):
            return VoiceGender.MALE
        elif any(keyword in description for keyword in ['女性', '女声', '雌性', 'female', '女']):
            return VoiceGender.FEMALE
        else:
            return VoiceGender.NEUTRAL

    def _extract_age(self, description: str) -> VoiceAge:
        """提取年龄特征"""
        if any(keyword in description for keyword in ['年轻', '青春', 'young', '活泼', '少年']):
            return VoiceAge.YOUNG
        elif any(keyword in description for keyword in ['成熟', '稳重', 'mature', '资深', '老年']):
            return VoiceAge.MATURE
        else:
            return VoiceAge.MIDDLE

    def _extract_language(self, description: str) -> str:
        """提取语言代码"""
        if any(keyword in description for keyword in ['英文', 'english', 'en', 'English']):
            return "en"
        elif any(keyword in description for keyword in ['日文', 'japanese', 'jp', '日语']):
            return "jp"
        elif any(keyword in description for keyword in ['韩文', 'korean', 'ko', '韩语']):
            return "ko"
        else:
            return "zh"  # 默认中文

    async def synthesize_speech(self, text: str, voice_profile: VoiceProfile) -> Optional[str]:
        """语音合成主函数

        Args:
            text: 包含CosyVoice情感标记的文本
            voice_profile: 音色配置

        Returns:
            生成的音频文件路径，失败返回None
        """
        if not self.tts_instance or not self.tts_instance.is_initialized:
            logger.error("CosyVoice未初始化")
            return None

        try:
            # 调用CosyVoice进行语音合成
            audio_path = self.tts_instance.synthesize_speech_enhanced(
                text=text,
                speaker_name=self._get_speaker_name(voice_profile),
                speaker_prompt=voice_profile.speaker_prompt,
                speaker_audio_path=voice_profile.speaker_audio_path,
                language=voice_profile.language,
                stream=False
            )

            if audio_path:
                logger.info(f"语音合成成功: {audio_path}")
                return audio_path
            else:
                logger.error("语音合成失败，未返回音频文件")
                return None

        except Exception as e:
            logger.error(f"语音合成错误: {e}")
            return None

    def _get_speaker_name(self, voice_profile: VoiceProfile) -> str:
        """根据音色配置获取说话人名称"""
        # 如果有音频文件，使用零样本克隆，不需要预设说话人
        if voice_profile.speaker_audio_path:
            return None

        # 根据性别和语言选择预设说话人
        if voice_profile.language == "zh":
            if voice_profile.gender == VoiceGender.MALE:
                return "中文男"
            elif voice_profile.gender == VoiceGender.FEMALE:
                return "中文女"
            else:
                return "中文女"  # 默认
        else:
            # 其他语言也使用中文女作为基础（CosyVoice2支持跨语言合成）
            return "中文女"

    async def synthesize_multi_speaker(self, dialogue_segments: List[Dict]) -> Optional[str]:
        """多说话人对话合成

        Args:
            dialogue_segments: 对话片段列表，每个元素包含:
                - text: 文本内容（包含情感标记）
                - voice_profile: VoiceProfile对象

        Returns:
            合成的完整对话音频文件路径
        """
        if not dialogue_segments:
            logger.warning("对话片段为空")
            return None

        try:
            # 转换格式供CosyVoice使用
            cosyvoice_segments = []
            for segment in dialogue_segments:
                text = segment.get('text', '')
                voice_profile = segment.get('voice_profile')

                if not text or not voice_profile:
                    continue

                cosyvoice_segments.append({
                    'text': text,
                    'speaker': {
                        'prompt': voice_profile.speaker_prompt,
                        'audio_path': voice_profile.speaker_audio_path
                    },
                    'language': voice_profile.language
                })

            # 调用CosyVoice多说话人合成
            audio_path = self.tts_instance.synthesize_multi_speaker(cosyvoice_segments)

            if audio_path:
                logger.info(f"多说话人合成成功: {audio_path}")
                return audio_path
            else:
                logger.error("多说话人合成失败")
                return None

        except Exception as e:
            logger.error(f"多说话人合成错误: {e}")
            return None

    def get_available_speakers(self) -> List[str]:
        """获取可用的说话人列表"""
        if not self.tts_instance or not self.tts_instance.is_initialized:
            return []

        try:
            return self.tts_instance.get_available_speakers()
        except Exception as e:
            logger.error(f"获取说话人列表失败: {e}")
            return []

    def cleanup(self):
        """清理资源"""
        if self.tts_instance:
            self.tts_instance.cleanup()
            self.tts_instance = None

# 全局语音引擎实例
voice_engine = VoiceEngine()