
## 📊 支持的情感标记完整列表

基于 `CosyVoice/cosyvoice/tokenizer/tokenizer.py` 第248-256行：

| 标记 | 用途 | 示例 |
|------|------|------|
| `[breath]` | 呼吸、思考停顿 | `让我想想[breath]这个问题` |
| `[quick_breath]` | 快速呼吸、紧张兴奋 | `太激动了[quick_breath]！` |
| `[laughter]` | 短笑声 | `有趣[laughter]` |
| `<laughter></laughter>` | 长笑声 | `<laughter>哈哈哈</laughter>` |
| `<strong></strong>` | 强调重读 | `<strong>重要</strong>观点` |
| `[sigh]` | 叹息、感慨 | `时间过得真快[sigh]` |
| `[mn]` | 嗯声、思考认同 | `嗯[mn]，有道理` |
| `[cough]` | 咳嗽声 | `[cough]不好意思` |
| `[vocalized-noise]` | 发声噪音 | `[vocalized-noise]` |
| `[lipsmack]` | 唇音 | `[lipsmack]` |
| `[hissing]` | 嘶嘶声 | `[hissing]` |
| `[clucking]` | 咂嘴声 | `[clucking]` |
| `[accent]` | 重音标记 | `[accent]` |
| `[noise]` | 一般噪音 | `[noise]` |
