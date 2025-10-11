# -*- coding: utf-8 -*-
"""
CosyVoice TTS集成模块
支持多语言语音合成，包括中文、英文等
"""

import sys
import os
import tempfile
import torch
import torchaudio
from typing import Optional, List, Dict, Any
import logging

# 添加CosyVoice路径
sys.path.append('./CosyVoice')
sys.path.append('./CosyVoice/third_party/Matcha-TTS')

logger = logging.getLogger(__name__)

class CosyVoiceTTS:
    """CosyVoice TTS封装类"""

    def __init__(self, model_path: str = "CosyVoice/pretrained_models/CosyVoice-300M-SFT"):
        """
        初始化CosyVoice TTS

        Args:
            model_path: 模型路径，默认使用CosyVoice2-0.5B
        """
        self.model_path = model_path
        self.cosyvoice = None
        self.sample_rate = 22050
        self.is_initialized = False

        try:
            self._initialize_model()
        except Exception as e:
            logger.error(f"CosyVoice初始化失败: {e}")
            self.is_initialized = False

    def _initialize_model(self):
        """初始化CosyVoice模型"""
        try:
            # 检查模型文件是否存在
            if not os.path.exists(self.model_path):
                logger.warning(f"模型路径不存在: {self.model_path}")
                logger.info("请参考COSYVOICE_SETUP.md下载模型文件")
                self.is_initialized = False
                return

            from cosyvoice.cli.cosyvoice import CosyVoice
            from cosyvoice.utils.file_utils import load_wav

            # 初始化CosyVoice模型（300M系列使用CosyVoice类）
            logger.info(f"正在加载CosyVoice模型: {self.model_path}")
            self.cosyvoice = CosyVoice(
                self.model_path,
                load_jit=False,
                load_trt=False,
                fp16=False
            )
            self.sample_rate = self.cosyvoice.sample_rate
            self.is_initialized = True
            logger.info(f"CosyVoice-300M模型初始化成功，采样率: {self.sample_rate}")

        except ImportError as e:
            logger.warning(f"CosyVoice导入失败: {e}")
            logger.info("请检查CosyVoice安装和依赖")
            self.is_initialized = False
        except Exception as e:
            logger.warning(f"CosyVoice模型加载失败: {e}")
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
        CosyVoice语音合成方法

        注意：文本中应该已经包含了CosyVoice情感标记，这里不再添加额外的情感处理

        Args:
            text: 要合成的文本（已包含情感标记如[laughter]、<strong></strong>等）
            speaker_name: 预设说话人名称（用于SFT模型）
            speaker_prompt: 说话人描述文本（用于零样本克隆）
            speaker_audio_path: 说话人音频文件路径（用于零样本克隆）
            language: 语言代码 (zh/en/jp/ko等)
            emotion: 情感控制（已弃用，情感标记应在文本中）
            instruction: 指令描述（用于Instruct模型）
            stream: 是否使用流式推理

        Returns:
            生成的音频文件路径，失败返回None
        """
        if not self.is_initialized:
            logger.error("CosyVoice未初始化")
            return None

        if not text.strip():
            logger.error("输入文本为空")
            return None

        try:
            # 创建临时文件保存音频
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_path = tmp_file.name

            # 处理文本，添加语言标记
            processed_text = self._process_text_for_cosyvoice(text, language)

            # 根据模型类型和参数选择合成方式
            if "SFT" in self.model_path:
                # 使用预设说话人模式
                audio_data = self._sft_synthesis(processed_text, speaker_name or "中文女", stream)
            elif "Instruct" in self.model_path:
                # 使用指令控制模式
                audio_data = self._instruct_synthesis(processed_text, speaker_name or "中文女", instruction, stream)
            elif speaker_audio_path and os.path.exists(speaker_audio_path):
                # 零样本语音克隆
                audio_data = self._zero_shot_synthesis(processed_text, speaker_prompt or "", speaker_audio_path, stream)
            else:
                # 默认使用预设说话人
                audio_data = self._preset_speaker_synthesis(processed_text, language, stream)

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

    def _process_text_for_cosyvoice(self, text: str, language: str = "zh") -> str:
        """
        为CosyVoice处理文本

        注意：文本中的情感标记已经由dialogue_engine添加，这里只需要添加语言标记
        """
        processed_text = text

        # 添加语言标记（如果需要）
        if language == "en":
            processed_text = f"<|en|>{processed_text}"
        elif language == "jp":
            processed_text = f"<|jp|>{processed_text}"
        elif language == "ko":
            processed_text = f"<|ko|>{processed_text}"
        # 中文默认不需要标记

        return processed_text

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

    def _sft_synthesis(
        self,
        text: str,
        speaker_name: str,
        stream: bool = False
    ):
        """SFT模式语音合成"""
        try:
            for i, result in enumerate(self.cosyvoice.inference_sft(
                text,
                speaker_name,
                stream=stream
            )):
                return result['tts_speech']
        except Exception as e:
            logger.error(f"SFT合成失败: {e}")
            return None

    def _instruct_synthesis(
        self,
        text: str,
        speaker_name: str,
        instruction: str,
        stream: bool = False
    ):
        """指令控制模式语音合成"""
        try:
            for i, result in enumerate(self.cosyvoice.inference_instruct(
                text,
                speaker_name,
                instruction or "用自然的语调说话",
                stream=stream
            )):
                return result['tts_speech']
        except Exception as e:
            logger.error(f"指令合成失败: {e}")
            return None

    def _preset_speaker_synthesis(
        self,
        text: str,
        language: str,
        stream: bool = False
    ):
        """使用预设说话人合成（CosyVoice-300M-SFT模式）"""
        try:
            # CosyVoice-300M-SFT支持多种预设说话人
            # 根据语言选择默认说话人
            speaker_map = {
                "zh": "中文女",
                "en": "中文女",  # 300M模型主要支持中文，但可以合成英文文本
                "jp": "中文女",
                "ko": "中文女"
            }
            speaker = speaker_map.get(language, "中文女")

            # 使用SFT模式进行合成
            for i, result in enumerate(self.cosyvoice.inference_sft(
                text,
                speaker,
                stream=stream
            )):
                return result['tts_speech']

        except Exception as e:
            logger.error(f"预设说话人合成失败: {e}")
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
        """获取可用的说话人列表"""
        if not self.is_initialized:
            return []

        try:
            if hasattr(self.cosyvoice, 'list_available_spks'):
                return self.cosyvoice.list_available_spks()
            else:
                # 返回默认说话人列表
                return ["中文女", "中文男", "英文女", "英文男"]
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

def cleanup_tts():
    """清理全局TTS实例"""
    global _tts_instance
    if _tts_instance:
        _tts_instance.cleanup()
        _tts_instance = None