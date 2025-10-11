# -*- coding: utf-8 -*-
"""
角色人设处理引擎
实现角色个性化设定、对话风格匹配、情感状态管理
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class EmotionState(Enum):
    """情感状态枚举"""
    NEUTRAL = "neutral"
    EXCITED = "excited"
    SERIOUS = "serious"
    CONFUSED = "confused"
    AGREEING = "agreeing"
    DISAGREEING = "disagreeing"
    THINKING = "thinking"

@dataclass
class CharacterProfile:
    """角色档案"""
    name: str
    role: str  # 主持人、嘉宾、专家等
    personality: str  # 性格描述
    expertise: List[str]  # 专业领域
    speaking_style: str  # 说话风格
    catchphrases: List[str] = None  # 口头禅
    emotion_tendency: str = "balanced"  # 情感倾向
    interaction_style: str = "collaborative"  # 互动风格

    def __post_init__(self):
        if self.catchphrases is None:
            self.catchphrases = []

class CharacterEngine:
    """角色引擎"""

    def __init__(self):
        self.character_templates = self._load_character_templates()
        self.interaction_patterns = self._load_interaction_patterns()

    def parse_character_settings(self, character_input: str) -> List[CharacterProfile]:
        """解析用户输入的角色设定"""
        characters = []
        lines = [line.strip() for line in character_input.split('\n') if line.strip()]

        for i, line in enumerate(lines):
            character = self._parse_single_character(line, i)
            characters.append(character)

        return characters

    def _parse_single_character(self, line: str, index: int) -> CharacterProfile:
        """解析单个角色设定"""
        # 解析格式：角色名：描述
        if '：' in line:
            name_part, desc_part = line.split('：', 1)
        elif ':' in line:
            name_part, desc_part = line.split(':', 1)
        else:
            name_part = f"角色{index+1}"
            desc_part = line

        # 提取角色信息
        profile = self._extract_character_traits(name_part.strip(), desc_part.strip())
        return profile

    def _extract_character_traits(self, name: str, description: str) -> CharacterProfile:
        """从描述中提取角色特征"""
        # 使用NLP技术提取关键特征
        role = self._extract_role(description)
        personality = self._extract_personality(description)
        expertise = self._extract_expertise(description)
        speaking_style = self._extract_speaking_style(description)

        return CharacterProfile(
            name=name,
            role=role,
            personality=personality,
            expertise=expertise,
            speaking_style=speaking_style
        )

    def _extract_role(self, description: str) -> str:
        """提取角色类型"""
        role_keywords = {
            '主持人': ['主持', 'host', '引导'],
            '专家': ['专家', '学者', '教授', '博士', 'expert'],
            '嘉宾': ['嘉宾', '客人', 'guest'],
            '观众': ['观众', '听众', '用户', 'audience'],
            '评论员': ['评论', '分析师', 'analyst']
        }

        for role, keywords in role_keywords.items():
            if any(keyword in description for keyword in keywords):
                return role
        return '参与者'

    def _extract_personality(self, description: str) -> str:
        """提取性格特征"""
        personality_map = {
            '专业': ['专业', '理性', '客观'],
            '热情': ['热情', '激情', '活跃'],
            '严谨': ['严谨', '认真', '细致'],
            '幽默': ['幽默', '风趣', '轻松'],
            '质疑': ['质疑', '批判', '挑战']
        }

        traits = []
        for trait, keywords in personality_map.items():
            if any(keyword in description for keyword in keywords):
                traits.append(trait)

        return ', '.join(traits) if traits else '平衡'

    def _extract_expertise(self, description: str) -> List[str]:
        """提取专业领域"""
        expertise_keywords = {
            'AI': ['人工智能', 'AI', '机器学习', '深度学习'],
            '技术': ['技术', '工程', '开发', '编程'],
            '商业': ['商业', '管理', '创业', '投资'],
            '教育': ['教育', '教学', '培训'],
            '医疗': ['医疗', '健康', '医学']
        }

        expertise = []
        for field, keywords in expertise_keywords.items():
            if any(keyword in description for keyword in keywords):
                expertise.append(field)

        return expertise

    def _extract_speaking_style(self, description: str) -> str:
        """提取说话风格"""
        style_map = {
            '简洁明了': ['简洁', '直接', '明了'],
            '详细解释': ['详细', '深入', '全面'],
            '生动形象': ['生动', '形象', '比喻'],
            '数据导向': ['数据', '证据', '事实'],
            '情感丰富': ['感性', '情感', '感受']
        }

        for style, keywords in style_map.items():
            if any(keyword in description for keyword in keywords):
                return style

        return '自然对话'

    def generate_dialogue_prompts(self, characters: List[CharacterProfile], topic: str) -> Dict[str, str]:
        """为每个角色生成对话提示词"""
        prompts = {}

        for character in characters:
            prompt = self._create_character_prompt(character, topic, characters)
            prompts[character.name] = prompt

        return prompts

    def _create_character_prompt(self, character: CharacterProfile, topic: str, all_characters: List[CharacterProfile]) -> str:
        """创建单个角色的对话提示词"""
        other_characters = [c for c in all_characters if c.name != character.name]

        prompt = f"""
你是播客中的{character.name}，角色定位：{character.role}

## 角色设定
- 性格特征：{character.personality}
- 专业领域：{', '.join(character.expertise) if character.expertise else '通用'}
- 说话风格：{character.speaking_style}
- 互动方式：{character.interaction_style}

## 对话场景
主题：{topic}
其他参与者：{', '.join([c.name + '(' + c.role + ')' for c in other_characters])}

## 对话要求
1. 保持角色设定的一致性
2. 根据专业领域提供相应观点
3. 与其他角色自然互动，可以有不同观点
4. 使用符合角色身份的语言风格
5. 适当表达情感和态度变化

请以这个角色的身份参与播客对话。
"""
        return prompt

    def _load_character_templates(self) -> Dict:
        """加载角色模板"""
        # 这里可以从文件或数据库加载预设角色模板
        return {}

    def _load_interaction_patterns(self) -> Dict:
        """加载互动模式"""
        # 这里可以加载不同的互动模式（协作、辩论、访谈等）
        return {}

# 全局角色引擎实例
character_engine = CharacterEngine()