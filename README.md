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