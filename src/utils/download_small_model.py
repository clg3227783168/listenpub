#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速下载CosyVoice轻量级模型脚本
下载CosyVoice-300M-SFT模型，只需1.2GB，适合开发测试
"""

import os
import sys

def download_small_model():
    """下载CosyVoice-300M-SFT轻量级模型"""

    print("🚀 开始下载CosyVoice轻量级模型")
    print("="*50)

    try:
        # 检查是否安装了modelscope
        try:
            from modelscope import snapshot_download
            print("✅ ModelScope SDK已安装")
        except ImportError:
            print("❌ ModelScope SDK未安装")
            print("请先安装: pip install modelscope")
            return False

        # 创建模型目录
        models_dir = "CosyVoice/pretrained_models"
        os.makedirs(models_dir, exist_ok=True)
        print(f"📁 创建模型目录: {models_dir}")

        # 下载CosyVoice-300M-SFT模型
        print("\n📥 下载CosyVoice-300M-SFT模型...")
        print("   模型大小: ~1.2GB")
        print("   内存需求: 3-4GB RAM")
        print("   适用场景: 开发测试、快速验证")

        model_path = os.path.join(models_dir, "CosyVoice-300M-SFT")
        snapshot_download('iic/CosyVoice-300M-SFT', local_dir=model_path)
        print(f"✅ CosyVoice-300M-SFT下载完成: {model_path}")

        # 下载文本处理资源
        print("\n📥 下载文本处理资源...")
        ttsfrd_path = os.path.join(models_dir, "CosyVoice-ttsfrd")
        snapshot_download('iic/CosyVoice-ttsfrd', local_dir=ttsfrd_path)
        print(f"✅ CosyVoice-ttsfrd下载完成: {ttsfrd_path}")

        # 验证下载
        print("\n🔍 验证下载...")
        if os.path.exists(model_path) and os.path.exists(ttsfrd_path):
            print("✅ 所有模型文件下载成功")

            # 显示目录结构
            print(f"\n📊 模型目录结构:")
            for root, dirs, files in os.walk(models_dir):
                level = root.replace(models_dir, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files[:3]:  # 只显示前3个文件
                    print(f"{subindent}{file}")
                if len(files) > 3:
                    print(f"{subindent}... 和其他 {len(files)-3} 个文件")

            print(f"\n🎉 CosyVoice轻量级模型配置完成！")
            print(f"\n📋 下一步:")
            print(f"   1. 启动应用: python app.py")
            print(f"   2. 访问: http://localhost:7860")
            print(f"   3. 开始使用AI播客生成功能")

            return True
        else:
            print("❌ 模型下载验证失败")
            return False

    except Exception as e:
        print(f"❌ 下载过程出错: {e}")
        print(f"\n🔧 故障排除:")
        print(f"   1. 检查网络连接")
        print(f"   2. 确保有足够的磁盘空间 (~2GB)")
        print(f"   3. 尝试重新运行脚本")
        return False

def show_model_info():
    """显示模型信息对比"""
    print("\n📊 CosyVoice模型对比:")
    print("-"*60)
    print("| 模型名称              | 参数量 | 大小   | 内存需求 | 推荐用途     |")
    print("|----------------------|--------|--------|----------|-------------|")
    print("| CosyVoice-300M-SFT   | 300M   | ~1.2GB | 3-4GB    | ✅ 开发测试  |")
    print("| CosyVoice-300M       | 300M   | ~1.2GB | 3-4GB    | 基础版本     |")
    print("| CosyVoice2-0.5B      | 500M   | ~2GB   | 6-8GB    | 生产环境     |")
    print("-"*60)
    print("\n💡 建议:")
    print("   - 开发阶段: 使用 CosyVoice-300M-SFT")
    print("   - 生产环境: 升级到 CosyVoice2-0.5B")

if __name__ == "__main__":
    print("🎙️ ListenPub CosyVoice轻量级模型下载器")

    # 显示模型信息
    show_model_info()

    # 确认下载
    print(f"\n❓ 是否下载CosyVoice-300M-SFT模型? (y/n): ", end="")
    if input().lower().strip() in ['y', 'yes', '是', '']:
        success = download_small_model()
        sys.exit(0 if success else 1)
    else:
        print("取消下载")
        sys.exit(0)