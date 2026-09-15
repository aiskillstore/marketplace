---
name: routemux-setup
description: Point a coding agent or chat client at the RouteMux AI gateway — Codex CLI, Claude Code, Cursor, Cline, OpenCode, Gemini CLI, Qwen Code, Cherry Studio and others. Use when the user asks how to configure, connect, switch or point a tool at RouteMux, asks for the base URL, asks why their tool will not connect, or says 怎么接入/怎么配置/base url 是什么/切到 routemux. Requires the ROUTEMUX_API_KEY environment variable only for verification.
---

# RouteMux Setup

Wire a tool to RouteMux. Almost every client needs exactly two things: a base URL
and a key.

## The two facts

- Gateway base URL: `https://api.routemux.com`
- Header: `Authorization: Bearer <key>`, key created at https://routemux.com/console/keys

## Pick the protocol the client speaks

RouteMux exposes three compatible surfaces on one base URL. Choose by what the
client already knows how to talk, not by which model the user wants:

| Client speaks | Use | Path |
|---|---|---|
| OpenAI Chat Completions | OpenAI-compatible | `/v1/chat/completions` |
| OpenAI Responses | OpenAI-compatible | `/v1/responses` |
| Anthropic Messages | Anthropic-compatible | `/v1/messages` |
| Google Vertex / GenAI | Vertex-compatible | `/vertex-ai/…` |

## The `/v1` trap

This is the single most common setup failure. Some clients want the base URL
**with** `/v1` and append the rest themselves; others want it **without** and add
`/v1/...`. Getting it wrong produces a 404 that looks like the gateway is down.

If the user reports 404: have them try the other form before anything else.

## Verify before declaring success

Never tell the user it is configured without a round trip:

```bash
curl -s https://api.routemux.com/v1/models \
  -H "Authorization: Bearer $ROUTEMUX_API_KEY" | head -c 400
```

A JSON model list means the key and the base URL are both good. A 401 means the key;
a 404 means the path.

## Per-tool notes

The full, maintained per-client guides live at
https://routemux.com/docs/integrations — there are guides for Codex CLI, Claude Code,
Cursor, Cline, OpenCode, Gemini CLI, Qwen Code, CC Switch, CodeBuddy, Hermes, Pi,
AnythingLLM, ChatBox, Cherry Studio, Dify and more.

**Read that page rather than reciting configuration from memory.** Client config
formats change, and a wrong config block costs the user more time than a link does.

## What pointing a coding agent at RouteMux does *not* give you

A tool's **built-in** image/audio features ride the vendor's own subscription
session and ignore your configured base URL. Codex CLI's `$imagegen` is the usual
example: after switching to any third-party gateway it silently stops working.

That is not a misconfiguration and there is nothing to fix in the config. Install
the `routemux-images` skill instead — it calls the image endpoint over plain HTTP,
which works no matter what the built-in tool is doing.

## Rules

- Never read the key from anywhere except the `ROUTEMUX_API_KEY` environment variable.
- Never write the key into a config file the user did not ask you to edit, and never
  echo it back in your reply.
- Never say "configured successfully" without a verifying request.
- Never recite a client's config block from memory when the docs page has it.
