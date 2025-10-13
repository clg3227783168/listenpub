# -*- coding: utf-8 -*-
"""
CosyVoice2-0.5B TTS集成模块
支持多语言语音合成、零样本声音克隆和指令控制
"""

import sys
import os
import tempfile
import torch
import torchaudio
from typing import Optional, List, Dict, Any
import logging
from dataclasses import dataclass
from enum import Enum

# 添加CosyVoice路径
sys.path.append('./CosyVoice')
sys.path.append('./CosyVoice/third_party/Matcha-TTS')

logger = logging.getLogger(__name__)

class SceneType(Enum):
    """场景类型"""
    NATURAL = "自然交流"          # 正常对话
    DEBATE = "激烈争论"           # 激烈辩论
    HUMOR = "幽默接梗"            # 幽默互动
    DEEP_THINKING = "深度思考"     # 严肃思辨
    INTERVIEW = "愉快访谈"         # 友好访谈
    ANALYSIS = "理性分析"         # 客观分析
    EMOTIONAL = "情感表达"        # 情感化表达
    STORYTELLING = "故事叙述"     # 讲故事

@dataclass
class CharacterPersona:
    """角色人设"""
    name: str                              # 角色名称
    voice_style: str                       # 声音风格描述
    personality: str                       # 性格特征
    speaking_style: str                    # 说话风格
    audio_sample_path: Optional[str] = None # 音频样本路径

    def get_instruction(self, scene_type: SceneType, emotion: str = "平静") -> str:
        """根据角色人设、场景和情感生成指令文本"""
        base_style = f"用{self.voice_style}的声音，以{self.personality}的性格"
        scene_modifier = self._get_scene_modifier(scene_type)
        return f"{base_style}，{emotion}地{scene_modifier}"

    def _get_scene_modifier(self, scene_type: SceneType) -> str:
        """根据场景类型获取修饰词"""
        scene_modifiers = {
            SceneType.NATURAL: f"{self.speaking_style}地交流",
            SceneType.DEBATE: "激烈地争论和反驳",
            SceneType.HUMOR: "幽默风趣地开玩笑和接梗",
            SceneType.DEEP_THINKING: "深沉严肃地思考和阐述",
            SceneType.INTERVIEW: "友好热情地访谈交流",
            SceneType.ANALYSIS: "冷静客观地分析和说明",
            SceneType.EMOTIONAL: "充满情感地表达",
            SceneType.STORYTELLING: "生动有趣地讲述故事"
        }
        return scene_modifiers.get(scene_type, f"{self.speaking_style}地表达")

@dataclass
class PodcastSegment:
    """播客片段"""
    text: str                         # 要合成的文本
    character: CharacterPersona       # 角色人设
    scene_type: SceneType            # 场景类型
    emotion: str = "平静"             # 情感状态
    speed: float = 1.0               # 语速
    stream: bool = False             # 是否流式输出

class CosyVoiceTTS:
    """CosyVoice2-0.5B TTS封装类"""

    def __init__(self, model_path: str = "CosyVoice/pretrained_models/CosyVoice2-0.5B"):
        """
        初始化CosyVoice2-0.5B TTS

        Args:
            model_path: 模型路径，默认使用CosyVoice2-0.5B
        """
        self.model_path = model_path
        self.cosyvoice = None
        self.sample_rate = 22050
        self.is_initialized = False
        self.audio_samples_dir = "./audio_samples"  # 音频样本目录

        try:
            self._initialize_model()
        except Exception as e:
            logger.error(f"CosyVoice2初始化失败: {e}")
            self.is_initialized = False

    def _initialize_model(self):
        """初始化CosyVoice2-0.5B模型"""
        try:
            # 检查模型文件是否存在
            if not os.path.exists(self.model_path):
                logger.warning(f"模型路径不存在: {self.model_path}")
                logger.info("请下载CosyVoice2-0.5B模型文件")
                self.is_initialized = False
                return

            from cosyvoice.cli.cosyvoice import CosyVoice2
            from cosyvoice.utils.file_utils import load_wav

            # 初始化CosyVoice2-0.5B模型
            logger.info(f"正在加载CosyVoice2-0.5B模型: {self.model_path}")
            self.cosyvoice = CosyVoice2(
                self.model_path,
                load_jit=False,
                load_trt=False,
                load_vllm=False,
                fp16=False
            )
            self.sample_rate = self.cosyvoice.sample_rate
            self.is_initialized = True
            logger.info(f"CosyVoice2-0.5B模型初始化成功，采样率: {self.sample_rate}")

        except ImportError as e:
            logger.warning(f"CosyVoice2导入失败: {e}")
            logger.info("请检查CosyVoice安装和依赖")
            self.is_initialized = False
        except Exception as e:
            logger.warning(f"CosyVoice2模型加载失败: {e}")
            logger.info("可能是模型文件损坏或不完整，请重新下载")
            self.is_initialized = False

    def synthesize_speech_enhanced(
        self,
        text: str,
        speaker_name: Optional[str] = None,
        speaker_prompt: Optional[str] = None,
        speaker_audio_path: Optional[str] = None,
        language: str = "zh",
        emotion: Optional[str] = None,
        instruction: Optional[str] = None,
        stream: bool = False
    ) -> Optional[str]:
        """
        CosyVoice2-0.5B语音合成方法

        Args:
            text: 要合成的文本（已包含情感标记如[laughter]、<strong></strong>等）
            speaker_name: 预设说话人名称（暂不使用）
            speaker_prompt: 说话人描述文本（用于零样本克隆）
            speaker_audio_path: 说话人音频文件路径（用于零样本克隆）
            language: 语言代码 (zh/en/jp/ko等)
            emotion: 情感控制（已弃用，情感标记应在文本中）
            instruction: 指令描述（用于指令控制）
            stream: 是否使用流式推理

        Returns:
            生成的音频文件路径，失败返回None
        """
        if not self.is_initialized:
            logger.error("CosyVoice2未初始化")
            return None

        if not text.strip():
            logger.error("输入文本为空")
            return None

        try:
            # 创建临时文件保存音频
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_path = tmp_file.name

            # 根据参数选择合成方式
            if instruction:
                # 指令控制模式
                audio_data = self._instruct_synthesis(text, speaker_audio_path, instruction, stream)
            elif speaker_audio_path and os.path.exists(speaker_audio_path):
                # 零样本语音克隆
                audio_data = self._zero_shot_synthesis(text, speaker_prompt or "", speaker_audio_path, stream)
            else:
                logger.error("请提供说话人音频文件或指令描述")
                return None

            if audio_data is not None:
                # 保存音频
                torchaudio.save(output_path, audio_data, self.sample_rate)
                logger.info(f"语音合成成功，保存到: {output_path}")
                return output_path
            else:
                logger.error("语音合成失败，未获得音频数据")
                return None

        except Exception as e:
            logger.error(f"语音合成过程出错: {e}")
            return None

    def _zero_shot_synthesis(
        self,
        text: str,
        speaker_prompt: str,
        audio_path: str,
        stream: bool = False
    ):
        """零样本语音克隆合成"""
        try:
            from cosyvoice.utils.file_utils import load_wav

            # 加载参考音频
            prompt_speech_16k = load_wav(audio_path, 16000)

            # 零样本合成
            for i, result in enumerate(self.cosyvoice.inference_zero_shot(
                text,
                speaker_prompt,
                prompt_speech_16k,
                stream=stream
            )):
                # 返回第一个结果
                return result['tts_speech']

        except Exception as e:
            logger.error(f"零样本合成失败: {e}")
            return None

    def _instruct_synthesis(
        self,
        text: str,
        speaker_audio_path: Optional[str],
        instruction: str,
        stream: bool = False,
        speed: float = 1.0
    ):
        """指令控制模式语音合成"""
        try:
            from cosyvoice.utils.file_utils import load_wav

            if speaker_audio_path and os.path.exists(speaker_audio_path):
                prompt_speech_16k = load_wav(speaker_audio_path, 16000)
            else:
                # 使用默认音频文件
                default_audio = './CosyVoice/asset/zero_shot_prompt.wav'
                if os.path.exists(default_audio):
                    prompt_speech_16k = load_wav(default_audio, 16000)
                else:
                    logger.error("未找到参考音频文件")
                    return None

            for i, result in enumerate(self.cosyvoice.inference_instruct2(
                text,
                instruction or "用自然的语调说话",
                prompt_speech_16k,
                stream=stream,
                speed=speed  # 添加语速控制
            )):
                return result['tts_speech']
        except Exception as e:
            logger.error(f"指令合成失败: {e}")
            return None

    def synthesize_podcast_segment(
        self,
        segment: PodcastSegment
    ) -> Optional[str]:
        """
        播客片段合成 - 为dialogue_engine调用的主要接口

        Args:
            segment: 播客片段信息，包含文本、角色人设和场景

        Returns:
            生成的音频文件路径，失败返回None
        """
        if not self.is_initialized:
            logger.error("CosyVoice2未初始化")
            return None

        if not segment.text.strip():
            logger.error("输入文本为空")
            return None

        try:
            # 获取角色的音频样本
            audio_sample_path = self._get_character_audio_sample(segment.character)
            if not audio_sample_path:
                logger.warning(f"未找到角色 {segment.character.name} 的音频样本，使用默认音频")
                audio_sample_path = self._get_default_audio_sample()

            # 生成指令文本
            instruction = segment.character.get_instruction(segment.scene_type, segment.emotion)
            logger.info(f"角色 {segment.character.name} 指令: {instruction}")

            # 创建临时文件保存音频
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_path = tmp_file.name

            # 调用指令控制合成
            audio_data = self._instruct_synthesis(
                text=segment.text,
                speaker_audio_path=audio_sample_path,
                instruction=instruction,
                stream=segment.stream,
                speed=segment.speed  # 添加语速控制
            )

            if audio_data is not None:
                # 保存音频
                torchaudio.save(output_path, audio_data, self.sample_rate)
                logger.info(f"角色 {segment.character.name} 语音合成成功: {output_path}")
                return output_path
            else:
                logger.error(f"角色 {segment.character.name} 语音合成失败")
                return None

        except Exception as e:
            logger.error(f"播客片段合成过程出错: {e}")
            return None

    def synthesize_podcast_dialogue(
        self,
        segments: List[PodcastSegment],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        播客对话全段合成

        Args:
            segments: 播客片段列表
            output_path: 输出文件路径

        Returns:
            合成的完整播客音频文件路径
        """
        if not segments:
            logger.error("播客片段列表为空")
            return None

        try:
            audio_segments = []

            logger.info(f"开始合成 {len(segments)} 个播客片段")

            # 逐个合成片段
            for i, segment in enumerate(segments, 1):
                logger.info(f"正在处理第 {i}/{len(segments)} 个片段: {segment.character.name}")

                segment_audio_path = self.synthesize_podcast_segment(segment)

                if segment_audio_path:
                    # 加载音频数据
                    audio_data, sr = torchaudio.load(segment_audio_path)
                    audio_segments.append(audio_data)

                    # 清理临时文件
                    try:
                        os.unlink(segment_audio_path)
                    except:
                        pass
                else:
                    logger.warning(f"第 {i} 个片段合成失败，跳过")
                    continue

            if not audio_segments:
                logger.error("所有片段合成失败")
                return None

            # 拼接音频片段
            final_audio = torch.cat(audio_segments, dim=1)

            # 保存最终音频
            if output_path is None:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    output_path = tmp_file.name

            torchaudio.save(output_path, final_audio, self.sample_rate)
            logger.info(f"播客对话合成完成: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"播客对话合成失败: {e}")
            return None

    def _get_character_audio_sample(self, character: CharacterPersona) -> Optional[str]:
        """获取角色的音频样本路径"""
        # 如果角色指定了音频样本路径
        if character.audio_sample_path and os.path.exists(character.audio_sample_path):
            return character.audio_sample_path

        # 在audio_samples目录中查找同名文件
        if os.path.exists(self.audio_samples_dir):
            # 支持多种音频格式
            audio_extensions = ['.wav', '.mp3', '.flac', '.m4a']
            for ext in audio_extensions:
                sample_path = os.path.join(self.audio_samples_dir, f"{character.name}{ext}")
                if os.path.exists(sample_path):
                    logger.info(f"找到角色 {character.name} 的音频样本: {sample_path}")
                    return sample_path

        return None

    def _get_default_audio_sample(self) -> Optional[str]:
        """获取默认音频样本"""
        # 优先使用CosyVoice官方的示例音频
        default_paths = [
            './CosyVoice/asset/zero_shot_prompt.wav',
            './audio_samples/default.wav',
            './audio_samples/default.mp3'
        ]

        for path in default_paths:
            if os.path.exists(path):
                logger.info(f"使用默认音频样本: {path}")
                return path

        logger.error("未找到任何可用的音频样本")
        return None


    def synthesize_multi_speaker(
        self,
        dialogue_segments: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        多说话人对话合成

        Args:
            dialogue_segments: 对话片段列表，每个元素包含:
                - text: 文本内容
                - speaker: 说话人信息
                - emotion: 情感（可选）
                - language: 语言（可选）
            output_path: 输出文件路径

        Returns:
            合成的音频文件路径
        """
        if not dialogue_segments:
            return None

        try:
            audio_segments = []

            for segment in dialogue_segments:
                text = segment.get('text', '')
                speaker = segment.get('speaker', {})
                language = segment.get('language', 'zh')

                # 合成单个片段
                segment_audio_path = self.synthesize_speech_enhanced(
                    text=text,
                    speaker_prompt=speaker.get('prompt'),
                    speaker_audio_path=speaker.get('audio_path'),
                    language=language,
                    stream=False
                )

                if segment_audio_path:
                    # 加载音频数据
                    audio_data, sr = torchaudio.load(segment_audio_path)
                    audio_segments.append(audio_data)

                    # 清理临时文件
                    try:
                        os.unlink(segment_audio_path)
                    except:
                        pass

            if not audio_segments:
                return None

            # 拼接音频片段
            final_audio = torch.cat(audio_segments, dim=1)

            # 保存最终音频
            if output_path is None:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    output_path = tmp_file.name

            torchaudio.save(output_path, final_audio, self.sample_rate)
            logger.info(f"多说话人音频合成完成: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"多说话人合成失败: {e}")
            return None

    def get_available_speakers(self) -> List[str]:
        """获取可用的说话人列表（CosyVoice2主要使用零样本克隆）"""
        if not self.is_initialized:
            return []

        try:
            # CosyVoice2支持零样本克隆和指令控制
            return ["零样本克隆", "指令控制"]
        except:
            return []

    def cleanup(self):
        """清理资源"""
        if self.cosyvoice:
            del self.cosyvoice
            self.cosyvoice = None
        self.is_initialized = False

# 全局TTS实例
_tts_instance = None

def get_tts_instance() -> CosyVoiceTTS:
    """获取全局TTS实例"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = CosyVoiceTTS()
    return _tts_instance

def create_podcast_segment(text: str, character_name: str, voice_style: str,
                          personality: str, speaking_style: str, scene_type: SceneType,
                          emotion: str = "平静", speed: float = 1.0,
                          audio_sample_path: Optional[str] = None) -> PodcastSegment:
    """
    创建播客片段的便捷函数，供dialogue_engine调用

    Args:
        text: 要合成的文本
        character_name: 角色名称
        voice_style: 声音风格描述
        personality: 性格特征
        speaking_style: 说话风格
        scene_type: 场景类型
        emotion: 情感状态
        speed: 语速
        audio_sample_path: 音频样本路径（可选）

    Returns:
        PodcastSegment对象
    """
    character = CharacterPersona(
        name=character_name,
        voice_style=voice_style,
        personality=personality,
        speaking_style=speaking_style,
        audio_sample_path=audio_sample_path
    )

    return PodcastSegment(
        text=text,
        character=character,
        scene_type=scene_type,
        emotion=emotion,
        speed=speed
    )

def cleanup_tts():
    """清理全局TTS实例"""
    global _tts_instance
    if _tts_instance:
        _tts_instance.cleanup()
        _tts_instance = None