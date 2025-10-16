# -*- coding: utf-8 -*-
"""
多角色对话生成引擎
实现智能对话流程、角色互动、情感变化
"""

import asyncio
import json
import random
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class EmotionState:
    """情感状态枚举"""
    NEUTRAL = "neutral"
    EXCITED = "excited"
    SERIOUS = "serious"
    CONFUSED = "confused"
    AGREEING = "agreeing"
    DISAGREEING = "disagreeing"
    THINKING = "thinking"

# 简化版的CharacterProfile数据类
@dataclass
class CharacterProfile:
    """角色配置"""
    name: str
    role: str = ""
    personality: str = ""
    expertise: List[str] = None
    speaking_style: str = ""

    def __post_init__(self):
        if self.expertise is None:
            self.expertise = []

class DialogueType(Enum):
    OPENING = "opening"
    DISCUSSION = "discussion"
    DEBATE = "debate"
    CONCLUSION = "conclusion"
    TRANSITION = "transition"

class InteractionMode(Enum):
    COLLABORATIVE = "collaborative"  # 合作模式
    DEBATE = "debate"                # 辩论模式
    INTERVIEW = "interview"          # 访谈模式
    PANEL = "panel"                  # 小组讨论

@dataclass
class DialogueTurn:
    """对话轮次"""
    speaker: str
    content: str
    emotion: EmotionState
    duration: float
    interaction_target: Optional[str] = None  # 交互对象
    gesture: Optional[str] = None             # 手势或表情

@dataclass
class DialogueSegment:
    """对话片段"""
    segment_type: DialogueType
    turns: List[DialogueTurn]
    background_music: Optional[str] = None
    sound_effects: List[str] = None

class DialogueEngine:
    """对话生成引擎"""

    def __init__(self):
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.openai_client = None
        self.interaction_patterns = self._load_interaction_patterns()
        self.dialogue_templates = self._load_dialogue_templates()

    async def generate_podcast_dialogue_simple(self,
                                             topic: str,
                                             character_names: List[str],
                                             character_presets: Dict[str, Dict],
                                             scenario: str,
                                             target_duration: int = 900) -> str:
        """简化版对话生成接口 - 直接返回带情感标记的脚本文本

        Args:
            topic: 播客主题
            character_names: 角色名称列表，例如 ["商业分析师", "科技记者"]
            character_presets: 角色预设配置字典，从app.py传入
            scenario: 场景名称，例如 "深度访谈"
            target_duration: 目标时长（秒）

        Returns:
            str: 格式化的播客脚本文本（包含CosyVoice情感标记）
        """
        # 1. 将简单参数转换为CharacterProfile对象
        characters = self._convert_to_character_profiles(character_names, character_presets)

        # 2. 生成对话片段
        dialogue_segments = await self.generate_podcast_dialogue(
            topic=topic,
            characters=characters,
            voice_profiles=[],  # 简化版不需要voice_profiles
            target_duration=target_duration
        )

        # 3. 格式化为文本脚本
        script_text = self._format_script_for_output(dialogue_segments, topic, scenario)

        return script_text

    def _convert_to_character_profiles(self,
                                       character_names: List[str],
                                       character_presets: Dict[str, Dict]) -> List[CharacterProfile]:
        """将角色名称列表转换为CharacterProfile对象列表"""
        profiles = []

        for char_name in character_names:
            if char_name in character_presets:
                preset = character_presets[char_name]
                profile = CharacterProfile(
                    name=char_name,
                    role=preset.get('identity', char_name),
                    personality=preset.get('personality', ''),
                    expertise=[],
                    speaking_style=preset.get('voice_style', '温和亲切')
                )
            else:
                # 如果没有预设，创建默认配置
                profile = CharacterProfile(
                    name=char_name,
                    role=char_name,
                    personality='专业、友好',
                    expertise=[],
                    speaking_style='温和亲切'
                )
            profiles.append(profile)

        return profiles

    def _format_script_for_output(self,
                                   dialogue_segments: List[DialogueSegment],
                                   topic: str,
                                   scenario: str) -> str:
        """格式化脚本输出"""
        script_lines = []

        # 添加标题
        script_lines.append(f"# 播客脚本：{topic}\n")
        script_lines.append(f"**场景模式**: {scenario}\n")
        script_lines.append("---\n")

        # 添加对话内容
        for segment_idx, segment in enumerate(dialogue_segments):
            # 段落标题
            segment_type_names = {
                "opening": "【开场】",
                "discussion": "【讨论】",
                "debate": "【辩论】",
                "conclusion": "【总结】",
                "transition": "【过渡】"
            }
            segment_name = segment_type_names.get(segment.segment_type.value, f"【{segment.segment_type.value}】")
            script_lines.append(f"\n## {segment_name}\n")

            # 对话内容（包含情感标记）
            for turn in segment.turns:
                # 验证并修正情感标记
                validated_content = self.validate_emotion_markup(turn.content)
                script_lines.append(f"**{turn.speaker}**: {validated_content}\n")

            script_lines.append("")

        # 添加情感标记使用统计
        tag_stats = self.get_emotion_markup_stats(dialogue_segments)
        if tag_stats:
            script_lines.append("\n---\n")
            script_lines.append("## 情感标记统计\n")
            for tag, count in tag_stats.items():
                script_lines.append(f"- `{tag}`: {count}次\n")

        return "\n".join(script_lines)

    async def generate_podcast_dialogue(self,
                                      topic: str,
                                      characters: List[CharacterProfile],
                                      voice_profiles: List,
                                      target_duration: int = 900) -> List[DialogueSegment]:
        """生成完整播客对话"""

        # 1. 分析主题和角色，确定对话模式
        interaction_mode = self._determine_interaction_mode(topic, characters)

        # 2. 规划对话结构
        dialogue_structure = self._plan_dialogue_structure(topic, characters, target_duration)

        # 3. 生成各个片段的对话
        segments = []
        for segment_plan in dialogue_structure:
            segment = await self._generate_dialogue_segment(
                segment_plan, topic, characters, interaction_mode
            )
            segments.append(segment)

        # 4. 优化对话流程和连贯性
        optimized_segments = self._optimize_dialogue_flow(segments)

        return optimized_segments

    def _determine_interaction_mode(self, topic: str, characters: List[CharacterProfile]) -> InteractionMode:
        """确定互动模式"""
        # 分析主题关键词
        controversial_keywords = ['争议', '辩论', '对比', '优缺点', '利弊']
        if any(keyword in topic for keyword in controversial_keywords):
            return InteractionMode.DEBATE

        # 分析角色配置
        if len(characters) == 2 and any('专家' in char.role for char in characters):
            return InteractionMode.INTERVIEW
        elif len(characters) > 2:
            return InteractionMode.PANEL
        else:
            return InteractionMode.COLLABORATIVE

    def _plan_dialogue_structure(self, topic: str, characters: List[CharacterProfile],
                                target_duration: int) -> List[Dict]:
        """规划对话结构"""
        structure = []

        # 开场 (10-15%)
        opening_duration = target_duration * 0.12
        structure.append({
            "type": DialogueType.OPENING,
            "duration": opening_duration,
            "participants": [characters[0].name],  # 主持人开场
            "goals": ["introduce_topic", "introduce_guests"]
        })

        # 主要讨论 (70-75%)
        main_duration = target_duration * 0.73
        num_discussion_rounds = len(characters)

        for i in range(num_discussion_rounds):
            structure.append({
                "type": DialogueType.DISCUSSION,
                "duration": main_duration / num_discussion_rounds,
                "participants": [char.name for char in characters],
                "focus_character": characters[i % len(characters)].name,
                "goals": ["deep_dive", "different_perspectives"]
            })

        # 结论 (10-15%)
        conclusion_duration = target_duration * 0.15
        structure.append({
            "type": DialogueType.CONCLUSION,
            "duration": conclusion_duration,
            "participants": [char.name for char in characters],
            "goals": ["summarize", "key_takeaways"]
        })

        return structure

    async def _generate_dialogue_segment(self, segment_plan: Dict, topic: str,
                                       characters: List[CharacterProfile],
                                       interaction_mode: InteractionMode) -> DialogueSegment:
        """生成对话片段"""

        segment_type = segment_plan["type"]
        participants = segment_plan["participants"]
        duration = segment_plan["duration"]

        # 构建对话生成提示
        prompt = self._build_dialogue_prompt(segment_plan, topic, characters, interaction_mode)

        # 调用AI生成对话
        raw_dialogue = await self._call_dialogue_ai(prompt)

        # 解析和结构化对话
        dialogue_turns = self._parse_dialogue_response(raw_dialogue, characters)

        # 添加情感和互动信息
        enhanced_turns = self._enhance_dialogue_with_emotions(dialogue_turns, interaction_mode)

        return DialogueSegment(
            segment_type=segment_type,
            turns=enhanced_turns,
            background_music=self._select_background_music(segment_type),
            sound_effects=self._select_sound_effects(segment_type)
        )

    def _build_dialogue_prompt(self, segment_plan: Dict, topic: str,
                              characters: List[CharacterProfile],
                              interaction_mode: InteractionMode) -> str:
        """构建对话生成提示"""

        segment_type = segment_plan["type"]
        participants = segment_plan["participants"]
        duration = segment_plan["duration"]

        # 角色信息
        character_info = ""
        for char in characters:
            if char.name in participants:
                character_info += f"""
{char.name} ({char.role}):
- 性格: {char.personality}
- 专业: {', '.join(char.expertise) if char.expertise else '通用'}
- 说话风格: {char.speaking_style}
"""

        # 段落特定指令
        segment_instructions = {
            DialogueType.OPENING: "介绍主题和嘉宾，营造轻松友好的氛围",
            DialogueType.DISCUSSION: "深入探讨主题，展现不同观点，保持对话自然流畅",
            DialogueType.DEBATE: "呈现观点冲突，进行有理有据的辩论",
            DialogueType.CONCLUSION: "总结讨论要点，给出关键见解和启发"
        }

        interaction_instructions = {
            InteractionMode.COLLABORATIVE: "角色间相互补充，共同探讨",
            InteractionMode.DEBATE: "角色间观点对立，进行理性辩论",
            InteractionMode.INTERVIEW: "主持人引导，专家深入解答",
            InteractionMode.PANEL: "多角色轮流发言，相互回应"
        }

        # CosyVoice情感标记规则
        emotion_markup_rules = """
## CosyVoice情感标记规则
在生成对话时，请根据情感需要在文本中加入以下标记来增强语音表现力：

### 笑声和情感
- [laughter] 或 <laughter></laughter> - 表示笑声，用于有趣、开心的内容
- [sigh] - 表示叹息，用于感慨、无奈的语气

### 呼吸和停顿
- [breath] - 表示呼吸声，用于思考或停顿
- [quick_breath] - 表示快速呼吸，用于紧张或兴奋

### 强调语气
- <strong></strong> - 强调重要内容，包围需要重读的词语

### 其他声音效果
- [cough] - 咳嗽声
- [vocalized-noise] - 发声噪音（如"嗯"、"啊"等）
- [mn] - 嗯声，表示思考或认同

### 使用示例
- "这个观点非常<strong>重要</strong>[breath]，让我们仔细分析一下。"
- "哈哈[laughter]，这确实是个有趣的问题。"
- "嗯[mn]，我觉得这个问题需要从多个角度来看[breath]。"

### 使用原则
1. 情感标记要自然融入对话，不要过度使用
2. 根据角色性格和对话内容合理选择标记
3. 重要观点用 <strong></strong> 强调
4. 轻松话题可以适当使用 [laughter]
5. 思考停顿时使用 [breath] 或 [mn]
"""

        prompt = f"""
你是一个专业的播客对话编剧。请生成一段高质量的播客对话。

## 基本信息
主题: {topic}
对话类型: {segment_type.value}
目标时长: {duration:.0f}秒
互动模式: {interaction_mode.value}

## 角色设定
{character_info}

{emotion_markup_rules}

## 对话要求
1. {segment_instructions.get(segment_type, '')}
2. {interaction_instructions.get(interaction_mode, '')}
3. 对话要自然真实，避免机械化
4. 每个角色都要体现其独特的个性和专业背景
5. 包含适当的情感变化和互动
6. **重要**: 必须在对话中合理使用上述情感标记，增强语音表现力
7. 预估字数: {int(duration * 3)}字左右

## 输出格式
请按以下格式输出对话（注意在对话内容中加入情感标记）：

[角色名]: 对话内容（包含情感标记）
[角色名]: 对话内容（包含情感标记）
...

请开始生成对话：
"""

        return prompt

    async def _call_dialogue_ai(self, prompt: str) -> str:
        """调用AI生成对话"""
        if not self.openai_client:
            return self._generate_fallback_dialogue(prompt)

        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的播客对话编剧，擅长创造自然真实的多角色对话。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI dialogue generation failed: {e}")
            return self._generate_fallback_dialogue(prompt)

    def _generate_fallback_dialogue(self, prompt: str) -> str:
        """生成备用对话（AI服务不可用时）"""
        return """
[主持人]: 欢迎大家收听今天的播客节目。
[嘉宾]: 很高兴能够参与这期节目的讨论。
[主持人]: 让我们开始今天的话题探讨。
"""

    def _parse_dialogue_response(self, raw_dialogue: str,
                                characters: List[CharacterProfile]) -> List[DialogueTurn]:
        """解析AI生成的对话"""
        turns = []
        lines = raw_dialogue.strip().split('\n')

        character_names = [char.name for char in characters]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 查找角色名称标记
            for char_name in character_names:
                if line.startswith(f'[{char_name}]') or line.startswith(f'{char_name}:'):
                    # 提取对话内容
                    if line.startswith('['):
                        content = line.split(']: ', 1)[-1]
                    else:
                        content = line.split(': ', 1)[-1]

                    # 估算说话时长（基于字数）
                    duration = len(content) * 0.2  # 假设每字0.2秒

                    turn = DialogueTurn(
                        speaker=char_name,
                        content=content,
                        emotion=EmotionState.NEUTRAL,  # 后续会增强
                        duration=duration
                    )
                    turns.append(turn)
                    break

        return turns

    def _enhance_dialogue_with_emotions(self, turns: List[DialogueTurn],
                                      interaction_mode: InteractionMode) -> List[DialogueTurn]:
        """为对话添加情感和互动信息"""
        enhanced_turns = []

        for i, turn in enumerate(turns):
            # 分析对话内容，推断情感
            emotion = self._analyze_emotion_from_content(turn.content, interaction_mode)

            # 确定交互对象
            interaction_target = None
            if i > 0 and i < len(turns) - 1:
                # 通常与前一个或后一个发言者互动
                if turn.speaker != turns[i-1].speaker:
                    interaction_target = turns[i-1].speaker

            # 添加手势信息
            gesture = self._suggest_gesture(turn.content, emotion)

            enhanced_turn = DialogueTurn(
                speaker=turn.speaker,
                content=turn.content,
                emotion=emotion,
                duration=turn.duration,
                interaction_target=interaction_target,
                gesture=gesture
            )
            enhanced_turns.append(enhanced_turn)

        return enhanced_turns

    def extract_cosyvoice_tags(self, content: str) -> Tuple[str, List[str]]:
        """提取CosyVoice情感标记

        Returns:
            Tuple[str, List[str]]: (处理后的文本, 提取的标记列表)
        """
        import re

        # 定义所有CosyVoice支持的标记
        cosyvoice_tags = [
            r'\[breath\]', r'\[quick_breath\]', r'\[laughter\]', r'\[sigh\]',
            r'\[cough\]', r'\[clucking\]', r'\[accent\]', r'\[hissing\]',
            r'\[vocalized-noise\]', r'\[lipsmack\]', r'\[mn\]', r'\[noise\]',
            r'<laughter>.*?</laughter>', r'<strong>.*?</strong>'
        ]

        extracted_tags = []
        processed_content = content

        # 提取所有标记
        for tag_pattern in cosyvoice_tags:
            matches = re.finditer(tag_pattern, content, re.IGNORECASE)
            for match in matches:
                extracted_tags.append(match.group())

        return processed_content, extracted_tags

    def validate_emotion_markup(self, content: str) -> str:
        """验证并修正情感标记

        确保情感标记符合CosyVoice规范
        """
        import re

        # 修正常见的标记错误
        corrections = {
            r'\[laugh\]': '[laughter]',
            r'\[笑\]': '[laughter]',
            r'\[呼吸\]': '[breath]',
            r'\[叹气\]': '[sigh]',
            r'\[嗯\]': '[mn]',
            r'<强调>(.*?)</强调>': r'<strong>\1</strong>',
            r'\*\*(.*?)\*\*': r'<strong>\1</strong>',  # Markdown转换
        }

        corrected_content = content
        for pattern, replacement in corrections.items():
            corrected_content = re.sub(pattern, replacement, corrected_content, flags=re.IGNORECASE)

        return corrected_content

    def get_emotion_markup_stats(self, segments: List[DialogueSegment]) -> Dict[str, int]:
        """统计情感标记使用情况"""
        import re

        tag_counts = {}
        cosyvoice_tags_pattern = r'\[(breath|quick_breath|laughter|sigh|cough|clucking|accent|hissing|vocalized-noise|lipsmack|mn|noise)\]|<(laughter|strong)>.*?</\2>'

        for segment in segments:
            for turn in segment.turns:
                matches = re.findall(cosyvoice_tags_pattern, turn.content, re.IGNORECASE)
                for match_groups in matches:
                    # match_groups 是元组，找到非空的组
                    tag = next((group for group in match_groups if group), None)
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return tag_counts

    def _analyze_emotion_from_content(self, content: str,
                                    interaction_mode: InteractionMode) -> EmotionState:
        """从对话内容分析情感（包括CosyVoice情感标记）"""

        # 首先检查CosyVoice情感标记
        cosyvoice_emotion_map = {
            '[laughter]': EmotionState.EXCITED,
            '<laughter>': EmotionState.EXCITED,
            '[sigh]': EmotionState.SERIOUS,
            '[quick_breath]': EmotionState.EXCITED,
            '[breath]': EmotionState.THINKING,
            '[mn]': EmotionState.THINKING,
            '<strong>': EmotionState.SERIOUS,
            '[cough]': EmotionState.NEUTRAL,
            '[vocalized-noise]': EmotionState.THINKING
        }

        # 检查情感标记
        for tag, emotion in cosyvoice_emotion_map.items():
            if tag in content:
                return emotion

        # 关键词情感映射
        emotion_keywords = {
            EmotionState.EXCITED: ['太棒了', '非常', '特别', '惊喜', 'excited', '哈哈'],
            EmotionState.SERIOUS: ['重要', '关键', '必须', '严肃', 'serious'],
            EmotionState.CONFUSED: ['不太明白', '疑惑', 'unclear', '困惑'],
            EmotionState.AGREEING: ['同意', '对的', '确实', '没错', 'agree'],
            EmotionState.DISAGREEING: ['不对', '我觉得', '但是', 'disagree'],
            EmotionState.THINKING: ['让我想想', '考虑', '思考', 'think', '嗯']
        }

        for emotion, keywords in emotion_keywords.items():
            if any(keyword in content for keyword in keywords):
                return emotion

        # 根据互动模式调整默认情感
        if interaction_mode == InteractionMode.DEBATE:
            return EmotionState.SERIOUS
        elif interaction_mode == InteractionMode.INTERVIEW:
            return EmotionState.THINKING
        else:
            return EmotionState.NEUTRAL

    def _suggest_gesture(self, content: str, emotion: EmotionState) -> Optional[str]:
        """建议手势或表情"""
        gesture_map = {
            EmotionState.EXCITED: "gesturing enthusiastically",
            EmotionState.SERIOUS: "leaning forward",
            EmotionState.CONFUSED: "tilting head",
            EmotionState.AGREEING: "nodding",
            EmotionState.DISAGREEING: "shaking head gently",
            EmotionState.THINKING: "pausing thoughtfully"
        }

        return gesture_map.get(emotion)

    def _optimize_dialogue_flow(self, segments: List[DialogueSegment]) -> List[DialogueSegment]:
        """优化对话流程和连贯性"""
        optimized = []

        for i, segment in enumerate(segments):
            # 添加过渡语句
            if i > 0:
                segment = self._add_transitions(segment, segments[i-1])

            # 平衡发言时间
            segment = self._balance_speaking_time(segment)

            # 调整节奏
            segment = self._adjust_pacing(segment)

            optimized.append(segment)

        return optimized

    def _add_transitions(self, current_segment: DialogueSegment,
                        previous_segment: DialogueSegment) -> DialogueSegment:
        """添加过渡语句"""
        if current_segment.turns and previous_segment.turns:
            # 在段落开始添加简单过渡
            first_turn = current_segment.turns[0]
            if not any(word in first_turn.content for word in ['那么', '接下来', '现在']):
                transition_phrases = ['那么', '接下来', '现在让我们']
                transition = random.choice(transition_phrases)
                first_turn.content = f"{transition}，{first_turn.content}"

        return current_segment

    def _balance_speaking_time(self, segment: DialogueSegment) -> DialogueSegment:
        """平衡发言时间"""
        # 统计每个角色的发言时间
        speaker_time = {}
        for turn in segment.turns:
            if turn.speaker not in speaker_time:
                speaker_time[turn.speaker] = 0
            speaker_time[turn.speaker] += turn.duration

        # 如果某个角色发言时间过少，可以适当调整
        # 这里可以实现更复杂的平衡逻辑

        return segment

    def _adjust_pacing(self, segment: DialogueSegment) -> DialogueSegment:
        """调整对话节奏"""
        # 在长句子后添加短暂停顿
        for turn in segment.turns:
            if len(turn.content) > 100:  # 长句子
                turn.duration += 0.5  # 增加停顿

        return segment

    def _select_background_music(self, segment_type: DialogueType) -> Optional[str]:
        """选择背景音乐"""
        music_map = {
            DialogueType.OPENING: "upbeat_intro.mp3",
            DialogueType.DISCUSSION: "subtle_ambient.mp3",
            DialogueType.DEBATE: "tension_light.mp3",
            DialogueType.CONCLUSION: "warm_outro.mp3"
        }

        return music_map.get(segment_type)

    def _select_sound_effects(self, segment_type: DialogueType) -> List[str]:
        """选择音效"""
        if segment_type == DialogueType.OPENING:
            return ["podcast_intro.wav"]
        elif segment_type == DialogueType.CONCLUSION:
            return ["podcast_outro.wav"]
        else:
            return []

    def _load_interaction_patterns(self) -> Dict:
        """加载互动模式配置"""
        return {
            "collaborative": {
                "turn_taking": "balanced",
                "interruption_rate": 0.1,
                "agreement_rate": 0.7
            },
            "debate": {
                "turn_taking": "competitive",
                "interruption_rate": 0.3,
                "agreement_rate": 0.3
            },
            "interview": {
                "turn_taking": "host_led",
                "interruption_rate": 0.05,
                "agreement_rate": 0.8
            }
        }

    def _load_dialogue_templates(self) -> Dict:
        """加载对话模板"""
        return {
            "opening_templates": [
                "欢迎收听{podcast_name}，我是{host_name}",
                "大家好，这里是{podcast_name}"
            ],
            "transition_templates": [
                "那么让我们来看看",
                "接下来我们讨论",
                "这让我想到了"
            ]
        }

# 全局对话引擎实例
dialogue_engine = DialogueEngine()