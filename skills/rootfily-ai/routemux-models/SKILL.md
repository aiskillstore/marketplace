---
name: routemux-models
description: Look up which models a RouteMux API key can actually call, what they cost, their context window, and which capabilities and protocols they support. Use when the user asks which models are available, how much a model costs, which model to pick for a task, whether a model supports vision/images/video, or says 有哪些模型/这个模型多少钱/用哪个模型好/支持什么协议. Requires the ROUTEMUX_API_KEY environment variable.
---

# RouteMux Models

Answer "what can I call and what does it cost" from the **live catalogue**, never
from memory. Model names and prices move weekly; a model list written into a file
on someone's laptop is wrong within days.

## Before anything else

`ROUTEMUX_API_KEY` must be set. If not, point the user at
https://routemux.com/console/keys and `export ROUTEMUX_API_KEY='sk-...'`.
Do not look for the key anywhere else.

## The one endpoint

```bash
curl -s "https://api.routemux.com/v1/models" \
  -H "Authorization: Bearer $ROUTEMUX_API_KEY"
```

It returns what **this key** can call — a key can be restricted to a subset, so the
answer is per-key, not global. Filters compose:

| Filter | Example | Use it for |
|---|---|---|
| `capability=` | `?capability=image_generation` | "can it draw" |
| `input_modality=` | `?input_modality=image` | "can it read screenshots" (vision) |
| `output_modality=` | `?output_modality=video` | "can it make video" |
| `provider=` | `?provider=anthropic` | one vendor |
| `supported_parameter=` | `?supported_parameter=reasoning` | models that take a thinking budget |
| `q=` | `?q=opus` | fuzzy name search |

## Answering well

- **Quote the slug exactly as returned.** Aliases exist but the canonical `id` is
  what belongs in the user's code.
- **When asked for a recommendation, give two or three with the tradeoff**, not one.
  Name the axis you are trading on (price, context window, latency, modality).
- **Do not quote a price you did not just read.** If the response has no price field
  for that model, say the catalogue does not expose one rather than guessing.
- **Capability flags are data, not a promise of quality.** `image_generation: true`
  means the endpoint will accept it, not that it is the best choice.

## A caveat worth passing on

Capability flags are maintained per model row and can lag a newly added model. If a
user insists a model supports something the catalogue does not list, the catalogue is
the thing that governs routing — a request for an unlisted capability will be
rejected before any upstream call, regardless of what the vendor's own docs say.

## Rules

- Never read the key from anywhere except the `ROUTEMUX_API_KEY` environment variable.
- Never write the key into a file, a log, or your reply.
- Never answer a "which models are available" question from your own training data.
- Never state a price, a context window, or a capability that is not in the response
  you just fetched.
