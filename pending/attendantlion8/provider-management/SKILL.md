---
name: Provider Management
description: Skill for managing model provider priorities with authentication (OAuth/Subscription/API), usage limits, and automatic fallback across all major AI providers
version: 2.0.0
---

# Provider Management Skill

Comprehensive management of AI models across all major providers with multi-auth support and automatic fallback.

## Overview

Supports ALL major AI providers and models with three authentication methods:

| Priority | Auth Type | Description |
|----------|-----------|-------------|
| 100 | **Subscription** | Pro/Plus/Max subscriptions (highest priority) |
| 50 | **OAuth** | OAuth 2.0 tokens (Antigravity-style) |
| 10 | **API** | Direct API keys (lowest priority) |

## Supported Models

### Claude (Anthropic)
- `claude-4-opus`, `claude-sonnet-4`, `claude-3.5-sonnet`, `claude-3.5-haiku`, `claude-3-opus`
- Providers: anthropic-subscription, anthropic-oauth, anthropic-api, bedrock, vertex, openrouter

### GPT (OpenAI)
- `gpt-4.1`, `gpt-4.1-mini`, `gpt-4o`, `gpt-4o-mini`, `o1`, `o3-mini`
- Providers: openai-subscription, openai-oauth, openai-api, azure, openrouter

### Gemini (Google)
- `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-pro`
- Providers: google-subscription, google-oauth, google-api, vertex-google, openrouter

### Grok (xAI)
- `grok-3`, `grok-3-mini`
- Providers: xai-subscription, xai-api, openrouter

### Other Models
- **Llama**: `llama-4-maverick`, `llama-3.3-70b` (bedrock, together, groq, openrouter)
- **DeepSeek**: `deepseek-r1`, `deepseek-v3` (deepseek-api, together, openrouter)
- **Mistral**: `mistral-large`, `codestral` (mistral-api, bedrock, azure, openrouter)
- **Cohere**: `command-r-plus` (cohere-api, bedrock, openrouter)
- **Qwen**: `qwen-2.5-72b` (together, openrouter)

## Provider-Specific Model IDs

| Canonical | anthropic-api | bedrock | vertex | openrouter |
|-----------|---------------|---------|--------|------------|
| claude-sonnet-4 | claude-sonnet-4-20250514 | anthropic.claude-sonnet-4-20250514-v1:0 | claude-sonnet-4@20250514 | anthropic/claude-sonnet-4 |
| gpt-4o | gpt-4o-2024-11-20 | - | - | openai/gpt-4o |
| gemini-2.5-pro | - | - | gemini-2.5-pro-preview-05-06 | google/gemini-2.5-pro-preview |

## Available Commands

### `/provider-auth`

Configure authentication for providers.

```bash
# View all auth status
/provider-auth status

# Set API key
/provider-auth setup anthropic-api --key sk-ant-...

# Start OAuth flow (Antigravity-style)
/provider-auth oauth google-oauth

# Set subscription token
/provider-auth setup anthropic-subscription --key <session-token>
```

### `/provider-models`

List models and provider mappings.

```bash
# List all models
/provider-models list

# Filter by family
/provider-models list --filter claude

# Get model info with all provider IDs
/provider-models info claude-sonnet-4

# Filter by capability
/provider-models capability reasoning
```

### `/provider-priority`

Manage provider order.

```bash
/provider-priority
/provider-priority set anthropic-subscription,anthropic-api,bedrock
/provider-priority move bedrock 1
```

### `/provider-limits`

Configure usage limits.

```bash
/provider-limits
/provider-limits anthropic-api --daily 1M --monthly 10M
```

### `/provider-status`

View usage dashboard.

```bash
/provider-status
/provider-status bedrock
/provider-status --reset
```

### `/provider-switch`

Manual control.

```bash
/provider-switch bedrock
/provider-switch --auto on
```

## Configuration Files

```
~/.opencode/provider-fallback/
├── config.json   # Priority, limits, settings
├── usage.json    # Usage tracking
├── auth.json     # Stored credentials (0600 permissions)
└── tokens.json   # OAuth tokens
```

## Authentication Priority Flow

```
1. Request comes in for model (e.g., claude-sonnet-4)
2. Get all configured providers for that model's vendor
3. Sort by auth priority: subscription (100) > oauth (50) > api (10)
4. Filter by usage capacity
5. Select best available provider
6. Get provider-specific model ID
7. Make request with appropriate credentials
```

## OAuth Setup (Antigravity-style)

For Google, Anthropic, or OpenAI OAuth:

```bash
# 1. Start OAuth flow
/provider-auth oauth google-oauth

# 2. Enter client ID and secret when prompted
# 3. Browser opens for authorization
# 4. Callback server receives token
# 5. Tokens stored securely
```

OAuth tokens auto-refresh when within 60 seconds of expiry.

## Best Practices

### Prioritize Subscriptions

1. Configure subscription auth first (highest priority, often includes extra features)
2. Add OAuth as secondary (good for personal accounts)
3. Use API keys as fallback

### Multi-Vendor Setup

```bash
# Configure multiple vendors
/provider-auth setup anthropic-subscription --key <token>
/provider-auth setup openai-api --key sk-...
/provider-auth setup google-api --key AIza...

# System auto-selects best for each model family
```

### For Reliability

1. Configure 2-3 auth methods per vendor
2. Set conservative limits (80% of actual)
3. Keep auto-switch enabled
4. OAuth tokens refresh automatically

## Troubleshooting

### OAuth Token Expired

Tokens refresh automatically. If manual refresh needed:
```bash
/provider-auth refresh google-oauth
```

### Subscription Not Detected

Ensure session token is valid and not expired:
```bash
/provider-auth setup anthropic-subscription --key <new-token>
```

### Wrong Auth Method Used

Check configured providers and priorities:
```bash
/provider-auth status
```

The system always prefers: subscription > oauth > api
