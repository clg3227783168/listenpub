# -*- coding: utf-8 -*-
"""
播客生成主引擎 - 简化版
仅处理角色对话和语音合成，不包含背景音乐功能
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

try:
    from character_engine import character_engine, CharacterProfile
    from voice_engine import voice_engine, VoiceProfile
    from dialogue_engine import dialogue_engine, DialogueSegment
    ENGINES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some engine components not available: {e}")
    ENGINES_AVAILABLE = False
    # 创建模拟对象
    character_engine = None
    voice_engine = None
    dialogue_engine = None

@dataclass
class PodcastGenerationRequest:
    """播客生成请求"""
    topic: str
    character_settings: str
    voice_settings: str
    language: str = "zh"
    target_duration: int = 900  # 15分钟
    quality_level: str = "high"  # low, medium, high

@dataclass
class PodcastGenerationResult:
    """播客生成结果"""
    success: bool
    script: Optional[str] = None
    character_mapping: Optional[str] = None
    metadata: Optional[Dict] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    generation_time: Optional[float] = None

class PodcastEngine:
    """播客生成主引擎 - 简化版，仅处理脚本生成"""

    def __init__(self):
        self.character_engine = character_engine
        self.voice_engine = voice_engine
        self.dialogue_engine = dialogue_engine

    async def generate_podcast(self, request: PodcastGenerationRequest) -> PodcastGenerationResult:
        """生成播客脚本（不包含音频和背景音乐）"""
        start_time = time.time()

        try:
            # 1. 解析和验证输入
            characters, voices = await self._parse_and_validate_input(request)

            # 2. 生成对话脚本
            dialogue_segments = await self._generate_dialogue_script(
                request.topic, characters, request.target_duration, request.language
            )

            # 3. 生成脚本文本
            script_text = self._format_script_text(dialogue_segments, characters, voices)

            # 4. 生成角色音色映射
            character_mapping = self._create_character_mapping(characters, voices)

            # 5. 生成元数据
            metadata = self._create_metadata(
                request, characters, voices, dialogue_segments
            )

            generation_time = time.time() - start_time

            return PodcastGenerationResult(
                success=True,
                script=script_text,
                character_mapping=character_mapping,
                metadata=metadata,
                duration=self._calculate_total_duration(dialogue_segments),
                generation_time=generation_time
            )

        except Exception as e:
            generation_time = time.time() - start_time
            return PodcastGenerationResult(
                success=False,
                error_message=str(e),
                generation_time=generation_time
            )

    async def _parse_and_validate_input(self, request: PodcastGenerationRequest) -> Tuple[List[CharacterProfile], List[VoiceProfile]]:
        """解析和验证输入参数"""

        # 解析角色设定
        characters = self.character_engine.parse_character_settings(request.character_settings)
        if not characters:
            # 提供默认角色
            if request.language == "zh":
                default_character = "主持人：专业理性的播客主持人"
            else:
                default_character = "Host: Professional and rational podcast host"
            characters = self.character_engine.parse_character_settings(default_character)

        # 解析音色设定
        voices = self.voice_engine.parse_voice_settings(request.voice_settings)
        if not voices:
            # 提供默认音色
            if request.language == "zh":
                default_voice = "温和专业的中性声音"
            else:
                default_voice = "Warm and professional neutral voice"
            voices = self.voice_engine.parse_voice_settings(default_voice)

        # 确保角色和音色数量匹配
        voices = self._align_voices_with_characters(characters, voices)

        # 验证主题
        if not request.topic or len(request.topic.strip()) < 10:
            raise ValueError("主题内容过短，请提供更详细的主题描述")

        # 验证时长
        if request.target_duration < 180 or request.target_duration > 3600:
            raise ValueError("目标时长应在3-60分钟之间")

        return characters, voices

    def _align_voices_with_characters(self, characters: List[CharacterProfile],
                                    voices: List[VoiceProfile]) -> List[VoiceProfile]:
        """确保音色与角色数量匹配"""
        if len(voices) == len(characters):
            return voices

        # 如果音色数量不足，复制最后一个音色
        while len(voices) < len(characters):
            voices.append(voices[-1] if voices else self._create_default_voice())

        # 如果音色数量过多，截取
        if len(voices) > len(characters):
            voices = voices[:len(characters)]

        return voices

    def _create_default_voice(self) -> VoiceProfile:
        """创建默认音色"""
        from voice_engine import VoiceProfile, VoiceGender, VoiceAge, VoiceEmotion
        return VoiceProfile(
            name="Default",
            gender=VoiceGender.NEUTRAL,
            age=VoiceAge.MIDDLE,
            emotion=VoiceEmotion.NEUTRAL
        )

    async def _generate_dialogue_script(self, topic: str, characters: List[CharacterProfile],
                                      target_duration: int, language: str) -> List[DialogueSegment]:
        """生成对话脚本"""

        # 调用对话引擎生成脚本
        dialogue_segments = await self.dialogue_engine.generate_podcast_dialogue(
            topic=topic,
            characters=characters,
            voice_profiles=[],  # 这里不需要voice_profiles
            target_duration=target_duration
        )

        return dialogue_segments

    def _format_script_text(self, dialogue_segments: List[DialogueSegment],
                           characters: List[CharacterProfile],
                           voices: List[VoiceProfile]) -> str:
        """格式化脚本文本"""

        script_lines = []

        # 添加标题信息
        script_lines.append("# 播客脚本\n")

        # 添加角色信息
        script_lines.append("## 角色设定")
        for i, char in enumerate(characters):
            script_lines.append(f"{i+1}. {char.name} ({char.role})")
            script_lines.append(f"   - 性格: {char.personality}")
            script_lines.append(f"   - 专业: {', '.join(char.expertise) if char.expertise else '通用'}")
            script_lines.append(f"   - 风格: {char.speaking_style}")

        script_lines.append("")

        # 添加音色配置
        script_lines.append("## 音色配置")
        for i, voice in enumerate(voices):
            character_name = characters[i].name if i < len(characters) else f"角色{i+1}"
            script_lines.append(f"{i+1}. {character_name}: {voice.gender.value} | {voice.age.value} | {voice.emotion.value}")

        script_lines.append("")

        # 添加对话内容
        script_lines.append("## 对话内容")

        for segment_idx, segment in enumerate(dialogue_segments):
            # 段落标题
            segment_type_names = {
                "opening": "开场",
                "discussion": "讨论",
                "debate": "辩论",
                "conclusion": "结论",
                "transition": "过渡"
            }
            segment_name = segment_type_names.get(segment.segment_type.value, segment.segment_type.value)
            script_lines.append(f"### {segment_name} {segment_idx + 1}")

            # 对话内容
            for turn in segment.turns:
                emotion_desc = ""
                if turn.emotion.value != "neutral":
                    emotion_desc = f" [{turn.emotion.value}]"

                script_lines.append(f"**{turn.speaker}**{emotion_desc}: {turn.content}")

            script_lines.append("")

        return "\n".join(script_lines)

    def _create_character_mapping(self, characters: List[CharacterProfile],
                                voices: List[VoiceProfile]) -> str:
        """创建角色音色映射"""
        mapping_lines = ["角色音色映射关系:"]

        for i, char in enumerate(characters):
            voice = voices[i] if i < len(voices) else voices[0]
            voice_desc = f"{voice.gender.value}声音, {voice.age.value}年龄段, {voice.emotion.value}风格"
            mapping_lines.append(f"{char.name} ({char.role}) → {voice_desc}")

        return "\n".join(mapping_lines)

    def _create_metadata(self, request: PodcastGenerationRequest,
                        characters: List[CharacterProfile],
                        voices: List[VoiceProfile],
                        dialogue_segments: List[DialogueSegment]) -> Dict:
        """创建元数据"""

        metadata = {
            "generation_config": {
                "topic": request.topic,
                "language": request.language,
                "target_duration": request.target_duration,
                "quality_level": request.quality_level
            },
            "characters": [
                {
                    "name": char.name,
                    "role": char.role,
                    "personality": char.personality,
                    "expertise": char.expertise,
                    "speaking_style": char.speaking_style
                }
                for char in characters
            ],
            "voices": [
                {
                    "name": voice.name,
                    "gender": voice.gender.value,
                    "age": voice.age.value,
                    "emotion": voice.emotion.value,
                    "speed": voice.speed,
                    "pitch": voice.pitch
                }
                for voice in voices
            ],
            "structure": [
                {
                    "type": segment.segment_type.value,
                    "turns_count": len(segment.turns),
                    "estimated_duration": sum(turn.duration for turn in segment.turns)
                }
                for segment in dialogue_segments
            ],
            "statistics": {
                "total_segments": len(dialogue_segments),
                "total_turns": sum(len(segment.turns) for segment in dialogue_segments),
                "character_speaking_time": self._calculate_speaking_time_per_character(dialogue_segments),
                "estimated_word_count": self._calculate_word_count(dialogue_segments)
            }
        }

        return metadata

    def _calculate_total_duration(self, dialogue_segments: List[DialogueSegment]) -> float:
        """计算总时长"""
        total_duration = 0.0
        for segment in dialogue_segments:
            for turn in segment.turns:
                total_duration += turn.duration
        return total_duration

    def _calculate_speaking_time_per_character(self, dialogue_segments: List[DialogueSegment]) -> Dict[str, float]:
        """计算每个角色的发言时间"""
        speaking_time = {}
        for segment in dialogue_segments:
            for turn in segment.turns:
                if turn.speaker not in speaking_time:
                    speaking_time[turn.speaker] = 0.0
                speaking_time[turn.speaker] += turn.duration
        return speaking_time

    def _calculate_word_count(self, dialogue_segments: List[DialogueSegment]) -> int:
        """计算总字数"""
        word_count = 0
        for segment in dialogue_segments:
            for turn in segment.turns:
                word_count += len(turn.content)
        return word_count

    async def generate_quick_preview(self, request: PodcastGenerationRequest) -> PodcastGenerationResult:
        """快速预览生成（仅生成脚本）"""
        preview_request = PodcastGenerationRequest(
            topic=request.topic,
            character_settings=request.character_settings,
            voice_settings=request.voice_settings,
            language=request.language,
            target_duration=min(request.target_duration, 300),  # 最多5分钟预览
            quality_level="script_only"
        )

        return await self.generate_podcast(preview_request)

    def get_generation_estimate(self, request: PodcastGenerationRequest) -> Dict[str, Any]:
        """获取生成时间预估"""

        # 基础时间估算
        base_time = 30  # 30秒基础时间

        # 根据时长调整
        duration_factor = request.target_duration / 600  # 以10分钟为基准
        duration_time = duration_factor * 60  # 每10分钟内容约需60秒

        # 根据质量级别调整
        quality_multipliers = {
            "low": 0.5,
            "medium": 1.0,
            "high": 2.0
        }
        quality_time = duration_time * quality_multipliers.get(request.quality_level, 1.0)

        # 根据角色数量调整
        character_count = len(request.character_settings.split('\n'))
        character_time = character_count * 10  # 每个角色增加10秒

        total_estimated_time = base_time + quality_time + character_time

        return {
            "estimated_time_seconds": int(total_estimated_time),
            "breakdown": {
                "base_processing": base_time,
                "content_generation": quality_time,
                "character_processing": character_time,
                "audio_synthesis": quality_time * 0.5 if request.quality_level != "script_only" else 0
            },
            "factors": {
                "target_duration": request.target_duration,
                "quality_level": request.quality_level,
                "character_count": character_count
            }
        }

# 全局播客引擎实例
podcast_engine = PodcastEngine()