# Runtime connections

Read only for the selected agent's runtime selection or connection work. Runtime IDs select guidance; they do not certify compatibility, behavioral support, or vendor endorsement. Core checks declared files and explicit TypeScript/JavaScript ESM exports, independently of the selected label.

## Select the defining SDK

Use the ID of the SDK the code calls directly. Provider packages of a listed framework keep that framework's ID; OpenAI-compatible providers called through `openai` keep `openai`. When one SDK defines the agent and another carries the request, use the defining SDK. In particular, agents defined through `@azure/ai-projects` use `microsoft-foundry` even when requests go through `openai`. Use `custom` for an evidenced project-specific runtime outside this table, with project-owned connection guidance; never use it as a fallback for missing evidence.

## Find the installed contract

These compact pointers were checked against source-owned documentation. They are starting points, not version promises. Confirm the installed package version and its types before using a field. Search once per needed field and read only its relevant definition, never whole declaration files. Names may differ between SDK versions and wire APIs. “not available” means this reference has no verified field, including APIs that do not offer one; it does not prove the installed SDK lacks that capability. Model, provider, and mode restrictions still apply.

| ID | Package(s) | Instruction | Output schema | Tools | Official documentation |
| --- | --- | --- | --- | --- | --- |
| `anthropic` | `@anthropic-ai/sdk` | Messages `system` | `output_config.format` | `tools` | [Messages](https://platform.claude.com/docs/en/api/messages/create) |
| `claude-agent-sdk` | `@anthropic-ai/claude-agent-sdk` | query `options.systemPrompt` | `options.outputFormat` | `options.tools`, `mcpServers` | [Agent SDK](https://code.claude.com/docs/en/agent-sdk) |
| `cloudflare-agents` | `agents`, `@cloudflare/think` | Think `getSystemPrompt()` or session context | not available | `getTools()` | [Think configuration](https://developers.cloudflare.com/agents/harnesses/think/configuration/) |
| `eve` | `eve` | `agent/instructions.md`, `.ts`, or `instructions/` | not available | `agent/tools/` | [Agent files](https://github.com/vercel/eve/blob/main/docs/reference/agent-files.md) |
| `google-genai` | `@google/genai` | `config.systemInstruction` | `config.responseJsonSchema` and JSON MIME type | `config.tools` | [GenerateContentConfig](https://googleapis.github.io/js-genai/release_docs/interfaces/types.GenerateContentConfig.html) |
| `langchain` | `langchain` | `createAgent.systemPrompt` | `responseFormat` | `tools` | [Agents](https://docs.langchain.com/oss/javascript/langchain/agents) |
| `langgraph` | `@langchain/langgraph` | model-call node's system message | not available | model `bindTools()` and the graph's tool node | [Quickstart](https://docs.langchain.com/oss/javascript/langgraph/quickstart) |
| `openai` | `openai` | Responses `instructions` | `text.format` | `tools` | [Responses](https://developers.openai.com/api/reference/resources/responses/methods/create) |
| `openai-agents-sdk` | `@openai/agents` | `Agent.instructions` | `outputType` | `tools` | [Agent definitions](https://developers.openai.com/api/docs/guides/agents/define-agents) |
| `vercel-ai-sdk` | `ai` | `ToolLoopAgent.instructions` | `output: Output.object({ schema })` | `tools` | [Building agents](https://ai-sdk.dev/docs/agents/building-agents) |
| `mastra` | `@mastra/core` | `Agent.instructions` | generate `structuredOutput.schema` | `Agent.tools` | [Agent.generate](https://mastra.ai/reference/agents/generate) |
| `genkit` | `genkit` | generate `system` | `output.schema` | generate `tools` | [Generating content](https://genkit.dev/docs/js/models/) |
| `strands-agents` | `@strands-agents/sdk` | `Agent.systemPrompt` | not available | `Agent.tools` | [TypeScript SDK](https://github.com/strands-agents/sdk-typescript) |
| `google-adk` | `@google/adk` | `LlmAgent.instruction` | `outputSchema` (check tool-use restrictions) | `tools` | [LLM agents](https://adk.dev/agents/llm-agents/) |
| `amazon-bedrock` | `@aws-sdk/client-bedrock-runtime` | Converse `system` | `outputConfig.textFormat` | `toolConfig.tools` | [Converse](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) |
| `microsoft-foundry` | `@azure/ai-projects` | agent definition `instructions` | not available | agent definition `tools` | [AI Projects SDK](https://learn.microsoft.com/en-us/javascript/api/overview/azure/ai-projects-readme?view=azure-node-latest) |
| `mistral` | `@mistralai/mistralai` | chat `messages`, system role | not available | chat `tools` | [TypeScript SDK](https://github.com/mistralai/client-ts) |
| `cohere` | `cohere-ai` | chat `messages`, system role | not available | chat `tools` | [Chat](https://docs.cohere.com/v2/reference/chat) |
| `groq` | `groq-sdk` | chat `messages`, system role | `response_format` | `tools` | [API reference](https://console.groq.com/docs/api-reference) |
| `ollama` | `ollama` | chat `messages`, system role | `format` | `tools` | [Chat](https://docs.ollama.com/api/chat) |
| `openrouter` | `@openrouter/sdk`, `@openrouter/agent` | SDK chat `messages`, system role; agent override: not available | not available | not available | [TypeScript SDK](https://openrouter.ai/docs/client-sdks/typescript/overview) |
| `hugging-face` | `@huggingface/inference` | chat `messages`, system role | not available | not available | [Inference client](https://huggingface.co/docs/huggingface.js/inference/README) |
| `cerebras` | `@cerebras/cerebras_cloud_sdk` | chat `messages`, system role | `response_format` | `tools` | [Chat completions](https://inference-docs.cerebras.ai/api-reference/chat-completions) |
| `ibm-watsonx-ai` | `@ibm-cloud/watsonx-ai` | textChat `messages`, system role | `guidedJSON` (model restrictions apply) | `tools` | [TextChatParams](https://ibm.github.io/watsonx-ai-node-sdk/interfaces/1_7_x.WatsonXAI.TextChatParams.html) |
| `voltagent` | `@voltagent/core` | `Agent.instructions` | generateText `output: Output.object({ schema })` | `Agent.tools` | [Agents](https://voltagent.dev/docs/agents/overview/) |
| `tanstack-ai` | `@tanstack/ai` | chat `systemPrompts` | `outputSchema` | `tools` | [TextOptions](https://tanstack.com/ai/latest/docs/reference/interfaces/TextOptions) |
| `convex-agent` | `@convex-dev/agent` | `Agent.instructions` | generateObject `schema` | `Agent.tools` or per-call `tools` | [Agent usage](https://docs.convex.dev/agents/agent-usage) |
| `livekit-agents` | `@livekit/agents` | voice agent `instructions` | not available | voice agent `tools` | [Tools](https://docs.livekit.io/agents/logic/tools/) |
| `node-llama-cpp` | `node-llama-cpp` | not available | not available | prompt `functions` | [Function calling](https://node-llama-cpp.withcat.ai/guide/function-calling) |
| `pi-agent` | `@earendil-works/pi-agent-core` | `initialState.systemPrompt` or leading system message | not available | `initialState.tools` | [Agent core](https://github.com/earendil-works/pi/blob/main/packages/agent/README.md) |
| `deep-agents` | `deepagents` | `createDeepAgent.systemPrompt` | `responseFormat` | `tools` | [Customization](https://docs.langchain.com/oss/javascript/deepagents/customization) |
| `openai-codex` | `@openai/codex-sdk`, `@openai/codex` | not available | not available | not available | [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk) |
| `github-copilot-sdk` | `@github/copilot-sdk` | session `systemMessage` | not available | session `tools` | [Node SDK](https://github.com/github/copilot-sdk/blob/main/nodejs/README.md) |
| `cursor-sdk` | `@cursor/sdk` | local `systemPrompt` (account-gated; replaces built-in prompt) | not available | `local.customTools`; built-in `tools` allowlist | [TypeScript SDK](https://cursor.com/docs/sdk/typescript) |
| `opencode-sdk` | `@opencode-ai/sdk` | not available | session prompt `body.format.schema` | not available | [SDK](https://opencode.ai/docs/sdk/) |
| `custom` | project-owned runtime | not available | not available | not available | [Project-owned connections](agent-design.md) |

## Check one connection

Follow only the selected agent's invocation path from canonical instruction and executable schema to the actual SDK call or agent definition. Confirm field semantics from the installed SDK's types, including whether description text is routing-facing or general. Check tools, variables, and relevant continuations on that same path. Stop at an opaque client, dynamic loader, mutation, or registry; name the exact unknown and its smallest reliable resolver. The result is exactly one of: connected by observed source and tests; broken with an established correction; or unknown at the named boundary with the smallest source or test that would resolve it. Unknown never justifies changing the runtime ID or removing a binding. Do not explore every SDK, enumerate dependency trees, or widen into unrelated agents.

Use `validate` counts by default. Page binding coverage only for the selected agent when its records can affect the conclusion. A passed file/export check proves only that named check. CommonJS, declarations, unresolved exports, and other unsupported syntax may be not checked without being defective. Interrupted inspections fail the whole operation and provide no partial coverage. Preserve the entrypoint's call and byte budgets.

Run an existing focused connection test as a project-native check. For agent creation, recommend a focused connection test asserting that the outgoing request carries the canonical instruction and schema. Add it only with developer authorization for implementation. Exercise the real owned loader and invocation path, substituting only the external provider boundary; a mocked internal loader or a valid manifest cannot prove consumption. Report file/export coverage, connection evidence, and untested live behavior separately.
