#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 dialogue_engine 脚本生成功能
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.engines.dialogue_engine import DialogueEngine

# 模拟 app.py 中的角色预设
CHARACTER_PRESETS = {
    "商业分析师": {
        "identity": "资深商业分析师",
        "personality": "专业理性，逻辑思维强，善于数据分析",
        "voice_style": "专业权威"
    },
    "科技记者": {
        "identity": "科技领域记者",
        "personality": "善于提问，好奇心强，关注科技趋势",
        "voice_style": "活泼生动"
    },
    "技术专家": {
        "identity": "技术领域专家",
        "personality": "深入浅出，耐心细致，乐于分享知识",
        "voice_style": "清晰标准"
    }
}

async def test_dialogue_generation():
    """测试对话生成功能"""

    print("=" * 60)
    print("测试 DialogueEngine 脚本生成功能")
    print("=" * 60)

    # 初始化对话引擎
    engine = DialogueEngine()
    print("✅ DialogueEngine 初始化成功")

    # 测试参数
    topic = "人工智能在医疗领域的应用与挑战"
    character_names = ["商业分析师", "科技记者", "技术专家"]
    scenario = "圆桌讨论"
    target_duration = 300  # 5分钟测试

    print(f"\n📋 测试参数:")
    print(f"  主题: {topic}")
    print(f"  角色: {', '.join(character_names)}")
    print(f"  场景: {scenario}")
    print(f"  时长: {target_duration}秒")

    # 生成脚本
    print(f"\n🚀 开始生成脚本...")
    try:
        script = await engine.generate_podcast_dialogue_simple(
            topic=topic,
            character_names=character_names,
            character_presets=CHARACTER_PRESETS,
            scenario=scenario,
            target_duration=target_duration
        )

        print("\n" + "=" * 60)
        print("✅ 脚本生成成功！")
        print("=" * 60)
        print("\n" + script)
        print("\n" + "=" * 60)

        # 保存到文件
        output_file = "test_output_script.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(script)
        print(f"\n💾 脚本已保存到: {output_file}")

        return True

    except Exception as e:
        print(f"\n❌ 脚本生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_mode():
    """测试简化模式（不使用OpenAI）"""

    print("\n" + "=" * 60)
    print("测试简化模式（备用脚本生成）")
    print("=" * 60)

    # 临时禁用 OpenAI 客户端
    engine = DialogueEngine()
    original_client = engine.openai_client
    engine.openai_client = None

    try:
        script = await engine.generate_podcast_dialogue_simple(
            topic="量子计算的未来",
            character_names=["技术专家", "科技记者"],
            character_presets=CHARACTER_PRESETS,
            scenario="深度访谈",
            target_duration=180
        )

        print("\n✅ 备用模式脚本生成成功")
        print(f"\n脚本长度: {len(script)} 字符")

    except Exception as e:
        print(f"\n❌ 备用模式失败: {e}")
    finally:
        engine.openai_client = original_client

def main():
    """主测试函数"""
    print("\n🎙️ ListenPub DialogueEngine 测试工具\n")

    # 测试1: 完整脚本生成
    result = asyncio.run(test_dialogue_generation())

    # 测试2: 备用模式
    asyncio.run(test_simple_mode())

    print("\n" + "=" * 60)
    if result:
        print("✅ 所有测试完成")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
