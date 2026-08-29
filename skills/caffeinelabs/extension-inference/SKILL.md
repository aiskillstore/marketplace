---
name: extension-inference
description: >-
  MANDATORY recipe for every Caffeine build that calls an LLM, chatbot,
  GPT, or ChatGPT **on Caffeine Inference** (no user-pasted OpenAI key).
  The ONLY supported path is the `caffeineai-inference-client` mops package
  with `Config.fromEnv<system>()`, which hands the canister a ready-to-use
  authenticated config — the app never asks for, stores, or returns a key.
  Hand-rolling `ic.http_request` to `inference.caffeine.ai` (or
  `api.openai.com`) is a FORBIDDEN anti-pattern. Load this skill whenever
  the user, spec, or any prior task wants an LLM in a Caffeine app — and
  BEFORE writing any code that talks to an LLM host. Use `extension-openai`
  only when the spec explicitly requires a user- or admin-pasted `sk-...`
  key against `api.openai.com`.
version: 0.1.0
compatibility:
  mops:
    caffeineai-inference-client: "~0.1.0"
caffeineai-subscription: [none]
---

# Caffeine Inference
LLM extension for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Orchestrator routing notes

Treat “use an LLM / GPT / chatbot / summarise with AI” as a first-class
platform feature. The default path is **Caffeine Inference**: an
OpenAI-compatible chat endpoint that Caffeine hosts, authenticates, and bills
for the app. The canister gets its credentials from the platform at runtime;
nobody pastes an API key, and the app never stores or returns one.

| User intent | Capability |
| --- | --- |
| Chat / summarise / classify with an LLM in a Caffeine app | `caffeineai-inference-client` `ChatApi.createChatCompletion` via this skill |
| Call `api.openai.com` with a user-pasted `sk-...` | [`extension-openai`](../extension-openai/SKILL.md) only |

Do **not** load `extension-openai` for a normal Caffeine-app LLM. Do **not**
ask the user for an OpenAI API key. Do **not** add `setApiKey` endpoints, a
key-settings page, or a model picker.

# Backend

## 1. Add `caffeineai-inference-client` to `mops.toml`

```bash
mops add caffeineai-inference-client@0.1.0
```

Requires Mops ≥ 2.13. **Minimum version:** `caffeineai-inference-client ≥ 0.1.0`.

## 2. Config comes from the platform

`Config.fromEnv<system>()` returns a complete `Config` — endpoint, bearer, and
`is_replicated = ?false` — from the credentials the platform provisions for the
app. There is no key to collect and nothing to configure.

- Call `fromEnv<system>()` **inside** the `shared` method, or in a
  `<system>`-parameterised helper, on **every** request. A module-level
  `let config = fromEnv` will not compile, and a cached `Config` can go stale
  when the platform rotates credentials on a running canister.
- It traps when the app has no inference credentials. That is a platform
  condition, not something the app can fix — do not add a "configure AI"
  empty state or a key-input fallback for it.
- Never log the `Config`, never copy its `auth` into actor state, and never
  return it (or any part of it) from a `query` / `shared` function.

## 3. `is_replicated = ?false` is REQUIRED

`fromEnv` already sets this. Do not override it to `?true` or `null`.

1. **Security.** A replicated outcall sends the bearer from every replica.
2. **Billing.** Replicated outcalls multiply inference spend by subnet size.
3. **Determinism.** LLM bodies are sampled; consensus would fail.

## 4. Canonical layout

```motoko filepath=src/backend/main.mo
import Inference "lib/inference";

actor {
  public shared func chat(prompt : Text) : async Text {
    await* Inference.runChat<system>(prompt);
  };
};
```

```motoko filepath=src/backend/lib/inference.mo
import { fromEnv } "mo:caffeineai-inference-client/Config";
import ChatApi "mo:caffeineai-inference-client/Apis/ChatApi";
import ChatCompletionRequest "mo:caffeineai-inference-client/Models/ChatCompletionRequest";
import ChatCompletionRequestMessageOneOf2 "mo:caffeineai-inference-client/Models/ChatCompletionRequestMessageOneOf2";
import Runtime "mo:core/Runtime";

module {
  public func runChat<system>(prompt : Text) : async* Text {
    let config = fromEnv<system>();
    let userMessage = ChatCompletionRequestMessageOneOf2.JSON.init({
      content = #string(prompt);
      role = #user;
    });
    let req = ChatCompletionRequest.JSON.init({
      messages = [#user(userMessage)];
      model = "router";
    });
    let resp = await* ChatApi.createChatCompletion(config, req);
    if (resp.choices.size() == 0) {
      Runtime.trap("Inference returned no choices");
    };
    resp.choices[0].message.content
      ?? Runtime.trap("Inference returned no text content");
  };
};
```

## 5. `model = "router"` — the platform picks the model

`"router"` is the only public model id, and it is a routing tier rather than a
model name. Caffeine Inference sizes each request to the complexity of the
query — a small fast model for simple prompts, a stronger one for hard
reasoning — and reports `"router"` back as the response `model`, so provider
names never reach the app.

- Always send `model = "router"`.
- Do not add a model dropdown, a "use GPT-4" toggle, or a `model` parameter on
  the backend endpoint. There is nothing for the user to choose.
- Steer quality with the prompt and with the declared sampling fields
  (`temperature`, `top_p`, `max_completion_tokens`), not with model selection.

## 6. Call shapes

- **Function form:** `ChatApi.createChatCompletion(config, req) : async*` — use `await*`.
- **Suite form:** `let api = ChatApi(config); api.createChatCompletion(req) : async`.

## 7. Available API surface — chat completions

`caffeineai-inference-client@0.1.0` is generated from
[`public-api-v0.1.0`](https://github.com/caffeinelabs/inference/releases/tag/public-api-v0.1.0):

| Module | Entry point | Route |
| --- | --- | --- |
| `ChatApi` | `createChatCompletion` | `POST /v1/chat/completions` |
| `ModelsApi` | `listModels` | `GET /v1/models` — catalog only; the model is always `"router"`, so an app never needs this |

<!-- motoko-check:skip -->
```motoko
import ChatApi "mo:caffeineai-inference-client/Apis/ChatApi";
import { fromEnv } "mo:caffeineai-inference-client/Config";
```

Chat completions are the whole product surface. **Not available** on this host
(404, and not in the package): embeddings, images, audio, moderations, files,
legacy completions, Assistants, Responses, and raw `ic.http_request`. If the
spec genuinely needs an OpenAI-only API with a pasted `sk-...`, switch to
[`extension-openai`](../extension-openai/SKILL.md).

## 8. Cycles

`defaultConfig.cycles = 30_000_000_000`. Bump for long completions:

<!-- motoko-check:skip -->
```motoko
{ fromEnv<system>() with cycles = 100_000_000_000 }
```

Streaming (`stream = ?true`) is unsupported — management-canister HTTP returns
the full body. Leave `stream = null`.

## 9. Things that will bite you

- Call `fromEnv<system>()` inside the `shared` method (or a `<system>` helper). A module-level `let config = fromEnv` will not compile.
- `model = "router"` — not `"gpt-4o-mini"`. See §5.
- User turns are `#user(ChatCompletionRequestMessageOneOf2.JSON.init({ content = #string(prompt); role = #user }))`.
- `JSON.init` for required fields; layer optionals with record update. Do not hand-list every `null`.
- `resp.choices[0].message.content` is `?Text`. Check `choices.size()` first.
- One chat call is one HTTP outcall inside an update call: budget seconds, not milliseconds.

# Frontend

The app is ready to chat on first load — there is nothing to configure.

1. **No API-key UI.** No settings page, no password input, no "configured?"
   indicator, no localStorage. If a spec or mock shows an "AI settings"
   screen, drop it.
2. **No model picker.** See §5.
3. Call the backend chat endpoint (`chat(prompt)`) and render the returned
   text. There is no frontend LLM SDK — the canister is the client, so the
   credentials never reach the browser.
4. Show a pending state while the call is in flight (an outcall round-trip
   takes seconds) and surface a retry on trap.
