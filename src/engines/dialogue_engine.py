# -*- coding: utf-8 -*-
"""对话脚本生成引擎"""

import json
from typing import List, Dict, Any, Optional
import re


class DialogueEngine:
    """播客对话脚本生成引擎"""

    def __init__(self):
        """初始化对话引擎"""
        self.conversation_templates = {
            "深度访谈": self._generate_interview_script,
            "圆桌讨论": self._generate_roundtable_script,
            "知识分享": self._generate_knowledge_script,
            "故事叙述": self._generate_story_script,
            "问答互动": self._generate_qa_script,
            "辩论对话": self._generate_debate_script,
            "经验分享": self._generate_experience_script,
            "新闻解读": self._generate_news_script,
        }

    def generate_script(
        self,
        topic: str,
        characters: List[Dict[str, str]],
        scenario: str,
        duration_minutes: int = 5
    ) -> str:
        """
        生成播客脚本

        Args:
            topic: 播客主题
            characters: 角色列表，每个角色包含 identity, personality, voice_style
            scenario: 场景类型
            duration_minutes: 预期时长（分钟）

        Returns:
            格式化的播客脚本
        """
        # 获取对应的脚本生成器
        generator = self.conversation_templates.get(
            scenario,
            self._generate_default_script
        )

        # 生成脚本
        script = generator(topic, characters, duration_minutes)

        return script

    def _generate_interview_script(
        self,
        topic: str,
        characters: List[Dict[str, str]],
        duration: int
    ) -> str:
        """生成深度访谈脚本"""
        if len(characters) < 2:
            characters = characters * 2  # 至少需要2个角色

        interviewer = characters[0]
        guest = characters[1]

        script = f"""# 播客脚本：{topic}
## 场景类型：深度访谈
## 角色设定：
- **主持人（{interviewer['identity']}）**: {interviewer['personality']}
- **嘉宾（{guest['identity']}）**: {guest['personality']}

---

**[开场音乐淡入]**

**主持人**: 大家好，欢迎收听本期播客。我是{interviewer['identity']}。今天我们将深入探讨"{topic}"这个话题。

**主持人**: 很高兴邀请到{guest['identity']}作为我们的嘉宾。欢迎您！

**嘉宾**: 谢谢邀请，很高兴能够和大家分享关于{topic}的见解。

**主持人**: 首先，能否请您从专业角度，为我们简单介绍一下{topic}的核心概念？

**嘉宾**: 当然。{topic}其实是一个非常有深度的话题。简单来说，它涉及到多个层面的问题...

**主持人**: 这确实很有意思。那么在实际应用中，您认为{topic}最大的挑战是什么？

**嘉宾**: 我认为最大的挑战在于如何平衡理论与实践。很多时候，理想的方案在现实中会遇到各种限制...

**主持人**: 您提到了一个很关键的点。能否分享一个具体的案例，让听众更好地理解？

**嘉宾**: 好的，让我举一个实际的例子。在我的工作经历中，有一次...

**主持人**: 这个案例非常生动。从中我们可以看到，{topic}不仅仅是理论概念，更是实践智慧的体现。

**嘉宾**: 没错。而且随着时间的发展，我们对{topic}的理解也在不断深化。

**主持人**: 那么展望未来，您认为{topic}会向什么方向发展？

**嘉宾**: 我认为未来的趋势会更加注重...这将为整个领域带来革命性的变化。

**主持人**: 非常精彩的分享！感谢{guest['identity']}今天的深度解读。

**嘉宾**: 谢谢，希望今天的分享对听众有所帮助。

**主持人**: 好的，今天的播客就到这里。感谢大家的收听，我们下期再见！

**[结束音乐淡入]**
"""
        return script

    def _generate_roundtable_script(
        self,
        topic: str,
        characters: List[Dict[str, str]],
        duration: int
    ) -> str:
        """生成圆桌讨论脚本"""
        # 确保至少有3个角色
        while len(characters) < 3:
            characters.extend(characters)
        characters = characters[:3]

        script = f"""# 播客脚本：{topic}
## 场景类型：圆桌讨论
## 参与者：
"""
        for i, char in enumerate(characters, 1):
            script += f"- **嘉宾{i}（{char['identity']}）**: {char['personality']}\n"

        script += f"""
---

**[开场音乐淡入]**

**嘉宾1**: 欢迎来到本期圆桌讨论，今天我们要探讨的主题是"{topic}"。我是{characters[0]['identity']}。

**嘉宾2**: 大家好，我是{characters[1]['identity']}，很高兴参与这次讨论。

**嘉宾3**: 我是{characters[2]['identity']}，期待和大家交流观点。

**嘉宾1**: 那我们直接进入主题吧。关于{topic}，我先抛砖引玉。我认为这个话题的核心在于...

**嘉宾2**: 我有不同的看法。从我的角度来看，{topic}更多地体现在...

**嘉宾3**: 两位说的都很有道理，但我想补充一点。我们不能忽视...

**嘉宾1**: 这是个很好的观点。这让我想到...

**嘉宾2**: 确实，如果从这个角度来看，我们可以发现...

**嘉宾3**: 而且在实际操作层面，{topic}还涉及到...

**嘉宾1**: 这个讨论太精彩了。我注意到大家虽然角度不同，但都强调了...

**嘉宾2**: 是的，我想这也说明{topic}的复杂性和多面性。

**嘉宾3**: 总结一下，我认为对于{topic}，我们需要保持开放和包容的态度。

**嘉宾1**: 非常好的总结。感谢两位的精彩分享，也感谢听众朋友们的收听！

**[结束音乐淡入]**
"""
        return script

    def _generate_knowledge_script(
        self,
        topic: str,
        characters: List[Dict[str, str]],
        duration: int
    ) -> str:
        """生成知识分享脚本"""
        expert = characters[0] if characters else {"identity": "专家", "personality": "专业"}

        script = f"""# 播客脚本：{topic}
## 场景类型：知识分享
## 主讲人：{expert['identity']}

---

**[开场音乐淡入]**

**主讲人**: 大家好，欢迎来到今天的知识分享时间。我是{expert['identity']}，今天要和大家分享的主题是"{topic}"。

**主讲人**: 首先，让我们从基础开始。什么是{topic}呢？

**主讲人**: 简单来说，{topic}是指...这个概念在我们的日常生活和专业领域中都有广泛的应用。

**主讲人**: 接下来，我想和大家分享{topic}的三个核心要点。

**主讲人**: 第一点，我们需要理解...这是整个框架的基础。

**主讲人**: 第二点，在实践中，我们会发现...这需要我们特别注意。

**主讲人**: 第三点，也是最重要的一点，那就是...这将帮助我们避免常见的误区。

**主讲人**: 让我通过一个实际案例来说明。比如说...

**主讲人**: 从这个案例中，我们可以清楚地看到{topic}的实际价值。

**主讲人**: 最后，我想给大家几点建议：首先...其次...最后...

**主讲人**: 好了，今天的分享就到这里。希望对大家有所帮助。如果有问题，欢迎随时交流。谢谢大家！

**[结束音乐淡入]**
"""
        return script

    def _generate_story_script(
        self,
        topic: str,
        characters: List[Dict[str, str]],
        duration: int
    ) -> str:
        """生成故事叙述脚本"""
        narrator = characters[0] if characters else {"identity": "讲述者", "personality": "生动"}

        script = f"""# 播客脚本：{topic}
## 场景类型：故事叙述
## 讲述者：{narrator['identity']}

---

**[舒缓的背景音乐]**

**讲述者**: 今天，我想和大家分享一个关于{topic}的故事。

**讲述者**: 故事要从很久以前说起...那时候，一切都还很简单。

**讲述者**: 在那个时代，人们对{topic}的理解还很有限。直到有一天...

**讲述者**: 这个转折点彻底改变了一切。人们开始重新思考...

**讲述者**: 故事的主人公面临着艰难的选择。一方面...另一方面...

**讲述者**: 经过深思熟虑，他决定...这个决定看似冒险，却蕴含着深刻的智慧。

**讲述者**: 接下来发生的事情，出乎所有人的意料...

**讲述者**: 最终，这个故事告诉我们，{topic}不仅仅是一个概念，更是一种态度和选择。

**讲述者**: 而这个故事，直到今天仍在继续，影响着每一个人...

**讲述者**: 这就是我今天想分享的故事。希望它能给你带来启发。

**[音乐渐弱]**
"""
        return script

    def _generate_qa_script(
        self,
        topic: str,
        characters: List[Dict[str, str]],
        duration: int
    ) -> str:
        """生成问答互动脚本"""
        if len(characters) < 2:
            characters = characters * 2

        host = characters[0]
        expert = characters[1]

        script = f"""# 播客脚本：{topic}
## 场景类型：问答互动
## 角色：
- **主持人（{host['identity']}）**: {host['personality']}
- **专家（{expert['identity']}）**: {expert['personality']}

---

**[开场音乐]**

**主持人**: 欢迎来到本期问答节目，今天的话题是"{topic}"。让我们有请专家来为大家答疑解惑。

**专家**: 大家好，很高兴能够回答关于{topic}的问题。

**主持人**: 第一个问题：{topic}对普通人来说意味着什么？

**专家**: 这是个很好的问题。对于普通人来说，{topic}其实就在我们身边...

**主持人**: 明白了。那么第二个问题：初学者应该如何入门{topic}？

**专家**: 我的建议是，首先要建立正确的认知框架...然后再逐步深入。

**主持人**: 很实用的建议。接下来这个问题可能有点深入：{topic}常见的误区有哪些？

**专家**: 最常见的误区就是...很多人以为...实际上并非如此。

**主持人**: 确实需要避免这些误区。最后一个问题：未来{topic}会如何发展？

**专家**: 我认为未来的趋势会是...这将带来巨大的机遇和挑战。

**主持人**: 太精彩了！感谢专家的详细解答，也感谢听众朋友们的收听！

**[结束音乐]**
"""
        return script

    def _generate_debate_script(
        self,
        topic: str,
        characters: List[Dict[str, str]],
        duration: int
    ) -> str:
        """生成辩论对话脚本"""
        if len(characters) < 2:
            characters = characters * 2

        script = f"""# 播客脚本：{topic}
## 场景类型：辩论对话
## 辩论双方：
- **正方（{characters[0]['identity']}）**: {characters[0]['personality']}
- **反方（{characters[1]['identity']}）**: {characters[1]['personality']}

---

**[开场音乐]**

**主持人**: 欢迎来到今天的辩论环节。今天的辩题是关于"{topic}"。

**正方**: 我方认为，{topic}具有重要的积极意义，理由如下...

**反方**: 我方持不同观点。虽然{topic}有其价值，但我们必须看到...

**正方**: 反方的担忧我理解，但是我们不能因噎废食...

**反方**: 这恰恰说明了问题的复杂性。在实际操作中...

**正方**: 关于这一点，我想举个例子来说明...

**反方**: 这个例子确实有一定代表性，但是如果我们换一个角度看...

**正方**: 即便如此，我们也不能否认{topic}的核心价值在于...

**反方**: 我同意核心价值的重要性，但实现路径同样关键...

**主持人**: 双方的观点都很有价值。这场辩论让我们看到了{topic}的多个维度。

**主持人**: 感谢两位嘉宾的精彩辩论，也感谢听众朋友们的收听！

**[结束音乐]**
"""
        return script

    def _generate_experience_script(
        self,
        topic: str,
        characters: List[Dict[str, str]],
        duration: int
    ) -> str:
        """生成经验分享脚本"""
        sharer = characters[0] if characters else {"identity": "分享者", "personality": "经验丰富"}

        script = f"""# 播客脚本：{topic}
## 场景类型：经验分享
## 分享者：{sharer['identity']}

---

**[轻松的背景音乐]**

**分享者**: 大家好，今天我想和大家分享一下我在{topic}方面的一些经验和心得。

**分享者**: 说起{topic}，我的第一次接触是在...那时候我还是个新手，犯了很多错误。

**分享者**: 最大的教训是...这让我意识到，{topic}并不像想象的那么简单。

**分享者**: 经过多年的实践，我总结出了几点经验。首先...

**分享者**: 其次，在处理{topic}相关问题时，一定要注意...

**分享者**: 还有一点很重要，那就是...这是很多人容易忽略的。

**分享者**: 让我分享一个印象最深的案例。当时...

**分享者**: 这次经历让我明白，{topic}需要的不仅是技能，更是...

**分享者**: 如果让我给新手一些建议，我会说：保持耐心，持续学习，勇于实践。

**分享者**: 希望我的分享能给大家带来一些启发。记住，每个人的路都不同，找到适合自己的方式最重要。

**分享者**: 谢谢大家的收听，祝你们在{topic}的道路上越走越好！

**[音乐渐弱]**
"""
        return script

    def _generate_news_script(
        self,
        topic: str,
        characters: List[Dict[str, str]],
        duration: int
    ) -> str:
        """生成新闻解读脚本"""
        if len(characters) < 2:
            characters = characters * 2

        anchor = characters[0]
        analyst = characters[1]

        script = f"""# 播客脚本：{topic}
## 场景类型：新闻解读
## 角色：
- **新闻主播（{anchor['identity']}）**: {anchor['personality']}
- **分析师（{analyst['identity']}）**: {analyst['personality']}

---

**[新闻音乐]**

**主播**: 各位听众大家好，欢迎收听本期新闻解读。今天我们关注的焦点是"{topic}"。

**主播**: 我们邀请到了{analyst['identity']}为我们深入分析。欢迎！

**分析师**: 谢谢，很高兴能够和大家分享我的分析。

**主播**: 首先，能否为我们简要介绍一下{topic}的基本情况？

**分析师**: 好的。根据最新的信息，{topic}主要涉及...这是近期备受关注的热点。

**主播**: 这个事件背后的深层原因是什么？

**分析师**: 我认为主要有以下几个方面。首先...其次...

**主播**: 那么这对普通民众会有什么影响？

**分析师**: 影响是多方面的。短期来看...长期来看...

**主播**: 您预测接下来的发展趋势会是怎样的？

**分析师**: 根据目前的情况分析，我认为未来可能会出现几种情景...

**主播**: 非常专业的分析。感谢分析师为我们带来的深度解读。

**分析师**: 不客气，希望能帮助大家更好地理解{topic}。

**主播**: 好的，以上就是本期新闻解读的全部内容。感谢收听，我们下期再见！

**[结束音乐]**
"""
        return script

    def _generate_default_script(
        self,
        topic: str,
        characters: List[Dict[str, str]],
        duration: int
    ) -> str:
        """生成默认脚本"""
        return self._generate_interview_script(topic, characters, duration)
