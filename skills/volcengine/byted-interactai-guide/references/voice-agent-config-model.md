# Voice Agent 核心配置模型

**Domain**: voice-agent

本文提供可编辑的核心模型，以及自然语言意图到字段的映射。字段范围和完整枚举需要动态核验。

## 核心

```json
{
  "AgentConfig": {
    "WelcomeMessage": "你好，我是小宁，有什么需要帮忙的吗？",
    "UserId": "voice_agent",
    "EnableConversationStateCallback": true
  },
  "Config": {
    "ASRConfig": {
      "Provider": "volcano",
      "ProviderParams": {
        "Mode": "bigmodel",
        "ApiResourceId": "volc.bigasr.sauc.duration",
        "StreamMode": 2,
        "enable_nonstream": true,
        "context_history_length": 3
      },
      "VADConfig": {
        "SilenceTime": 600,
        "AIVAD": false,
        "ForceBeginThreshold": 0,
        "ForceEnd": false,
        "VolumeGain": 1.0
      },
      "InterruptConfig": {"InterruptSpeechDuration": 0, "InterruptKeywords": []},
      "TurnDetectionMode": 0
    },
    "TTSConfig": {
      "AutoActive": true,
      "Provider": "volcano_bidirection",
      "ProviderParams": {
        "ResourceId": "volc.service_type.10029",
        "audio": {"voice_type": "zh_female_linjianvhai_moon_bigtts", "speech_rate": 0},
        "Additions": {"enable_latex_tn": false}
      },
      "IgnoreBracketText": [],
      "Context": {"TagParse": false, "QuoteUserQuestion": true},
      "Prefill": true,
      "InterruptMode": 0
    },
    "LLMConfig": {
      "AutoActive": true,
      "Mode": "ArkV3",
      "ModelName": "doubao-seed-2-0-lite-260428",
      "SystemMessages": ["你是一个简洁、友好的语音助手。"],
      "UserPrompts": [],
      "HistoryLength": 3,
      "Temperature": 0.1,
      "MaxTokens": 1024,
      "TopP": 0.3,
      "Prefill": false,
      "ThinkingType": "disabled",
      "VisionConfig": {
        "Enable": true,
        "SnapshotConfig": {
          "StreamType": 0,
          "ImageDetail": "auto",
          "Height": 640,
          "Interval": 2000,
          "ImagesLimit": 1,
          "AutoSelect": false
        }
      }
    },
    "InterruptMode": 0
  }
}
```

这份启动模板不代表当前官方限制。用户未修改的模板值可以复用；涉及身份或兼容性变化时，按
验证 reference 核对。

## 常见口语映射

| 意图 | 规范路径 |
|---|---|
| 说快点、语速 | `/Config/TTSConfig/ProviderParams/audio/speech_rate` |
| 换声音、音色 | `/Config/TTSConfig/ProviderParams/audio/voice_type` |
| 停多久算说完 | `/Config/ASRConfig/VADConfig/SilenceTime` |
| 语义判停 | `/Config/ASRConfig/VADConfig/AIVAD` |
| 回答随机性、温度 | `/Config/LLMConfig/Temperature` |
| 最大回答 token | `/Config/LLMConfig/MaxTokens` |
| 历史轮数 | `/Config/LLMConfig/HistoryLength` |
| 系统提示词、人设 | `/Config/LLMConfig/SystemMessages` |
| 欢迎词、开场白 | `/AgentConfig/WelcomeMessage` |
| 视觉输入 | `/Config/LLMConfig/VisionConfig/Enable` |

单位明确时可以无损换算。用户只给出“快一点、随机一点、停久点”等方向时，询问一个最小问题
取得目标值，不自行选择步长。认证 Token 与回答 token 预算按语境区分。
