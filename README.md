从代码 src/tts/cosy_voice_tts.py 第148-150行可以看到零样本合成的实现：

  elif speaker_audio_path and os.path.exists(speaker_audio_path):
      # 零样本语音克隆
      audio_data = self._zero_shot_synthesis(processed_text,
  speaker_prompt or "", speaker_audio_path, stream)

  具体使用方式：

  1. 准备角色音频样本：
  角色A音频: ./audio_samples/host_voice.wav (主持人)
  角色B音频: ./audio_samples/expert_voice.wav (专家)
  角色C音频: ./audio_samples/guest_voice.wav (嘉宾)
  2. 生成不同角色的语音：
  # 为每个角色设置不同的音频样本
  dialogue_segments = [
      {
          'text': '大家好，欢迎收听今天的节目',
          'speaker': {
              'audio_path': './audio_samples/host_voice.wav',
              'prompt': '温和专业的主持人'
          }
      },
      {
          'text': '感谢邀请，我来分享一下我的观点',
          'speaker': {
              'audio_path': './audio_samples/expert_voice.wav',
              'prompt': '权威的专业专家'
          }
      }
  ]

      "激烈争论": "用争论的语调，情绪激动地反驳对方观点",
      "幽默接梗": "用轻松幽默的语调，开玩笑地回应",
      "深度思考": "用深沉思考的语调，缓慢而有重量地表达",
      "愉快访谈": "用友好愉快的语调，自然地交流互动",
      "理性分析": "用冷静客观的语调，条理清晰地分析"