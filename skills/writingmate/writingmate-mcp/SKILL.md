---
name: writingmate-mcp
description: Use Writingmate's remote MCP server to discover and compare AI models, create text responses, generate images, and generate videos. Use when a user asks to call multiple AI models, compare model answers, or create media through Writingmate from Claude Code, Codex, ChatGPT, Cursor, or another MCP host.
license: MIT
compatibility: Requires an MCP host with remote Streamable HTTP support and a Writingmate account. OAuth is preferred; a Writingmate Developer Key can be used when the host only supports bearer tokens.
metadata:
  author: writingmate
  version: "1.0.0"
  homepage: https://writingmate.ai/developers
  repository: https://github.com/writingmate/skills
---

# Writingmate MCP

Use Writingmate as a remote Model Context Protocol (MCP) server. It gives an MCP host tools for model discovery, text generation, image generation, and video generation.

Official endpoint:

```text
https://writingmate.ai/api/mcp
```

## Connect the server

Use OAuth when the MCP host supports it. OAuth opens Writingmate in the user's browser and asks the user to approve access.

For Claude Code:

```bash
claude mcp add --transport http writingmate https://writingmate.ai/api/mcp
claude mcp list
```

For Codex, add this to `~/.codex/config.toml` when a fixed Developer Key is required:

```toml
[mcp_servers.writingmate]
url = "https://writingmate.ai/api/mcp"
bearer_token_env_var = "WRITINGMATE_DEVELOPER_KEY"
```

Never paste a Developer Key into a public file, issue, screenshot, or prompt. Keep it in an environment variable or the host's secure credential storage.

## Available tools

The server exposes these tools:

- `list_models`: list models available to the authenticated Writingmate account
- `get_model`: retrieve current metadata for one exact model ID
- `create_chat_completion`: create an OpenAI-compatible chat completion
- `create_response`: create an OpenAI-compatible Responses API response
- `generate_image`: generate one image from a prompt
- `generate_video`: start a video generation
- `get_video`: check a video generation by ID

Tool names may appear with a server namespace, such as `writingmate.list_models`. Match by the final tool name instead of assuming a namespace.

## Operating rules

1. Call `list_models` before choosing a model. The catalog and account access can change.
2. Use exact model IDs returned by the server. Do not invent or silently substitute an ID.
3. Call `get_model` when the task depends on current modality, limits, or other metadata.
4. Tell the user which model IDs you used.
5. Surface tool errors and unavailable models. Do not claim that a generation ran when no successful tool result exists.
6. Ask before making a large batch of paid or allowance-consuming generations.
7. Do not send secrets, private source code, personal data, or regulated data unless the user confirms that the transfer is allowed.

## Compare AI models

Use this workflow when the user asks to compare, benchmark, debate, or get a second opinion from multiple models:

1. Call `list_models`.
2. Select only models that fit the requested modality and are available to the account.
3. Show the exact selected model IDs before a large comparison. For a small comparison of two models, proceed unless the user's request is ambiguous.
4. Send every model the same user message independently.
5. Keep shared generation settings equal where the models support them.
6. Preserve each raw response before evaluating it.
7. Report failures instead of replacing a failed model.
8. Compare outputs with criteria tied to the user's task.

For a text comparison, call `create_chat_completion` once per model with a new message array:

```json
{
  "model": "MODEL_ID",
  "messages": [
    {
      "role": "user",
      "content": "USER_TASK"
    }
  ],
  "temperature": 0.2,
  "max_tokens": 800
}
```

Return:

- exact model ID
- raw answer
- latency or usage only when the tool returns it
- task-specific scores with brief evidence
- a recommendation that explains the trade-off

Do not describe one model as universally best from a single prompt.

## Generate an image

1. Call `list_models` and select an available image model when the user did not provide an exact ID.
2. Preserve the user's requested subject, composition, aspect ratio, text, and exclusions.
3. Call `generate_image`.
4. Return the generated asset from the tool result. Do not claim that an image exists if the call failed.

Example arguments:

```json
{
  "model": "MODEL_ID",
  "prompt": "A precise description of the requested image",
  "size": "1024x1024",
  "n": 1
}
```

Use only one output per call because the server currently accepts `n: 1`.

## Generate a video

1. Call `list_models` and select an available video model when needed.
2. Call `generate_video` with the prompt and supported options.
3. Save the returned generation ID.
4. Poll `get_video` at reasonable intervals until the job succeeds or fails.
5. Return the final video asset or the exact failure.

Example start arguments:

```json
{
  "model": "MODEL_ID",
  "prompt": "A precise description of the requested video",
  "seconds": "8",
  "size": "1280x720"
}
```

Do not start duplicate video jobs merely because a generation is still processing.

## Troubleshooting

### Authentication required

- With OAuth: disconnect and reconnect the server, then complete browser approval.
- With a Developer Key: confirm the host sends `Authorization: Bearer ...` without exposing the key.
- Confirm the key belongs to Writingmate, not an upstream model provider.

### Model is listed but the call fails

- Call `get_model` for current metadata.
- Check the Writingmate plan and workspace access.
- Report the exact model ID and error.
- Offer another model only after telling the user why.

### The host describes results but shows no tool call

Treat the work as not executed. Call the appropriate Writingmate tool and return its actual result.

## References

- Setup and product page: https://writingmate.ai/developers
- MCP documentation: https://writingmate.ai/docs/plugins/mcp-integration
- Live model directory: https://writingmate.ai/models
- Pricing and plan limits: https://writingmate.ai/pricing
