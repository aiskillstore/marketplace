# Model List

Complete guide to AI models available on NEAR AI Cloud. Choose the right model for your use case based on privacy, cost, context size, and capabilities.

> Quick links:
> - [Model Comparison Table](#model-comparison)
> - [Privacy Types](#privacy-types)
> - [Usage Examples](#using-models)
> - [Common Patterns](#common-patterns)

---

## Model Comparison

| Model             | Model ID                            | Type       | Context | Input Cost | Output Cost | Best For                              |
|-------------------|-------------------------------------|------------|---------|------------|-------------|---------------------------------------|
| Claude Opus 4.6   | `anthropic/claude-opus-4-6`         | Anonymised | 200K    | $5/M       | $25/M       | Agents, coding, complex reasoning     |
| Claude Sonnet 4.5 | `anthropic/claude-sonnet-4-5`       | Anonymised | 200K    | $3/M       | $15.5/M     | Balanced intelligence and speed       |
| Flux.2 [klein]    | `black-forest-labs/FLUX.2-klein-4B` | Private    | 128K    | $1/M       | $1/M        | Image model                           |
| DeepSeek V3.1     | `deepseek-ai/DeepSeek-V3.1`         | Private    | 128K    | $1.05/M    | $3.1/M      | Tool usage, thinking mode             |
| Gemini 3 Pro      | `google/gemini-3-pro`               | Anonymised | 1000K   | $1.25/M    | $15/M       | Long documents, multimodal            |
| OpenAI GPT-5.2    | `openai/gpt-5.2`                    | Anonymised | 400K    | $1.8/M     | $15.5/M     | Deep reasoning, large contexts        |
| GPT OSS 120B      | `openai/gpt-oss-120b`               | Private    | 131K    | $0.15/M    | $0.55/M     | Mixture-of-Experts, general purpose   |
| Qwen3 30B         | `Qwen/Qwen3-30B-A3B-Instruct-2507`  | Private    | 262K    | $0.15/M    | $0.55/M     | Cost-efficient, instruction following |
| GLM 4.7           | `zai-org/GLM-4.7`                   | Private    | 131K    | $0.85/M    | $3.3/M      | Coding, reasoning                     |

---

## Privacy types

When choosing a model, consider the privacy type:

- **Private** — Your data stays encrypted within TEE hardware. Recommended for sensitive data.
- **Anonymised** — Requests routed without identifying information. Good balance of cost and privacy.

---

## Using Models

Make chat completion requests to NEAR AI Cloud with your chosen model:

### curl

```bash
curl https://cloud-api.near.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $NEAR_API_KEY" \
  -d '{
    "model": "deepseek-ai/DeepSeek-V3.1",
    "messages": [
      {"role": "user", "content": "Explain quantum computing"}
    ]
  }'
```

### JavaScript

```js
const response = await fetch('https://cloud-api.near.ai/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.NEAR_API_KEY}`
  },
  body: JSON.stringify({
    model: 'deepseek-ai/DeepSeek-V3.1',
    messages: [
      { role: 'user', content: 'Explain quantum computing' }
    ]
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
```

### Python

```python
import os
import requests

response = requests.post(
    'https://cloud-api.near.ai/v1/chat/completions',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.environ["NEAR_API_KEY"]}'
    },
    json={
        'model': 'deepseek-ai/DeepSeek-V3.1',
        'messages': [
            {'role': 'user', 'content': 'Explain quantum computing'}
        ]
    }
)

data = response.json()
print(data['choices'][0]['message']['content'])
```

---

## Common Patterns

### Streaming Responses

```bash
curl https://cloud-api.near.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $NEAR_API_KEY" \
  -d '{
    "model": "deepseek-ai/DeepSeek-V3.1",
    "messages": [{"role": "user", "content": "Write a story"}],
    "stream": true
  }'
```

### Model Reasoning

Both `deepseek-ai/DeepSeek-V3.1` and `zai-org/GLM-4.7` support a "thinking mode" that enables the model to generate intermediate reasoning steps before providing a final answer. This feature can improve the quality of responses for complex tasks that require step-by-step reasoning.

To enable reasoning set `"thinking": true` in the `chat_template_kwargs`:

```bash
curl https://cloud-api.near.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "model": "deepseek-ai/DeepSeek-V3.1",
    "messages": [
      {"role": "user", "content": "What is sqrt of 11"}
    ],
    "temperature": 1,
    "n": 1,
    "chat_template_kwargs": {
      "thinking": true
    },
    "stream": true
  }'
```

> To disable thinking mode, set `"thinking": false`

---

## Best Practices

### 1. Match model to task complexity

Don't use Claude Opus for simple tasks. Don't use Qwen3 for complex reasoning. Choose the right tool for the job.

### 2. Use private models for sensitive data

If processing user data, financial information, or proprietary code, always use Private models to ensure data stays encrypted in TEE hardware.

---

## Next Steps

- [Model Verification Guide](model-verification.md) — Verify models run in genuine TEE hardware
- [API Reference](https://docs.near.ai/api) — Complete API documentation
- [NEAR AI Cloud Dashboard](https://cloud.near.ai) — Manage API keys and monitor usage