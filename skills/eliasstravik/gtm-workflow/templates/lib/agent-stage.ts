import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createMCPClient } from "@ai-sdk/mcp";
import { Output, WorkflowAgent } from "@ai-sdk/workflow";
import { jsonSchema, stepCountIs, type ToolSet } from "ai";
import { z } from "zod";
import { canRunStage, claudeStageArgs, mcpConfig, resolveBackend, resolveHeaders, runCli, type Backend, type McpServer } from "./agent";
import type { PaidCallMeta } from "./provider";
import { withSpend } from "./spend";
import { workflowModel } from "./model";

export type { McpServer } from "./agent";
export type AgentStageInput<T extends z.ZodTypeAny> = {
  /** Enclosing function name; must match a `[step: name]` node in the Diagram header. */
  step: string;
  instructions: string;
  input: unknown;
  schema: T;
  tools: McpServer[];
  maxUsd: number;
  maxTurns: number;
  deadlineMs: number;
  meta: PaidCallMeta;
  signal?: AbortSignal;
  model?: string;
};
type ToolDefinition = { server: number; name: string; description?: string; inputSchema: Record<string, unknown> };

/**
 * One agentic stage: the model chooses among the declared MCP tools for several
 * turns and returns structured output. Through the Gateway it is a WorkflowAgent
 * whose every tool call is a durable step. Locally without a key it is one
 * headless Claude Code call restricted to the same MCP tools with a budget cap.
 */
export async function agentStage<T extends z.ZodTypeAny>(input: AgentStageInput<T>): Promise<z.infer<T>> {
  if (process.env.GTM_SANDBOX === "1") throw new Error("The authoring sandbox cannot run a workflow.");
  const backend = await resolveStageBackend();
  if (!canRunStage(backend)) throw new Error(`${backend} cannot cap budget while restricting every tool. Add an AI key to use this agentic stage.`);
  const meta = { ...input.meta, step: input.step, maxSpendUsd: Math.min(input.maxUsd, input.meta.maxSpendUsd ?? input.maxUsd) };
  if (backend === "claude") return runClaudeStage(input, meta);
  return (await withSpend(meta, { step: input.step, estimateUsd: 0 }, async () => {
    const definitions = await discoverMcpTools(input.tools, input.deadlineMs);
    const tools: ToolSet = {};
    for (const definition of definitions) {
      const key = `${input.tools[definition.server].name}__${definition.name}`;
      tools[key] = {
        description: definition.description,
        inputSchema: jsonSchema(definition.inputSchema),
        execute: async (args) => (await withSpend(meta, { step: input.step, estimateUsd: 0 }, async () => ({ value: await invokeMcpTool(input.tools[definition.server], definition.name, args, input.deadlineMs), costUsd: 0 }))).value,
      };
    }
    let spent = 0;
    const agent = new WorkflowAgent({
      model: workflowModel(input.model), instructions: input.instructions, tools, output: Output.object({ schema: input.schema }), maxRetries: 0,
      stopWhen: [stepCountIs(input.maxTurns), (({ steps }: any) => { spent = steps.reduce((sum: number, step: any) => sum + Number(step.providerMetadata?.gateway?.cost ?? 0), 0); return spent >= input.maxUsd; })] as any,
    });
    const signal = AbortSignal.any([AbortSignal.timeout(input.deadlineMs), ...(input.signal ? [input.signal] : [])]);
    const result = await agent.stream({ messages: [{ role: "user", content: JSON.stringify(input.input) }], abortSignal: signal });
    if (result.error || result.finishReason === "error" || result.output === undefined) throw new Error("The agentic stage did not return structured output.");
    return { value: input.schema.parse(result.output), costUsd: spent };
  })).value;
}

async function resolveStageBackend(): Promise<Backend> {
  "use step";
  return resolveBackend();
}

async function runClaudeStage<T extends z.ZodTypeAny>(input: AgentStageInput<T>, meta: PaidCallMeta): Promise<z.infer<T>> {
  "use step";
  return (await withSpend(meta, { step: input.step, estimateUsd: 0 }, async () => {
    const directory = await mkdtemp(join(tmpdir(), "gtm-stage-"));
    try {
      const configFile = join(directory, "mcp.json");
      await writeFile(configFile, JSON.stringify(mcpConfig(input.tools)));
      const prompt = `${input.instructions}\n\nInput:\n${JSON.stringify(input.input)}`;
      const args = claudeStageArgs({ prompt, schemaJson: z.toJSONSchema(input.schema), maxUsd: input.maxUsd, mcpConfigFile: configFile });
      const stdout = await runCli("claude", args, { cwd: directory, timeoutMs: input.deadlineMs, signal: input.signal });
      const value = JSON.parse(stdout);
      if (value.is_error) throw new Error(String(value.result));
      return { value: input.schema.parse(value.structured_output), costUsd: Number(value.total_cost_usd ?? 0) };
    } finally { await rm(directory, { recursive: true, force: true }); }
  })).value;
}

async function discoverMcpTools(servers: McpServer[], timeoutMs: number): Promise<ToolDefinition[]> {
  "use step";
  const result: ToolDefinition[] = [];
  for (const [server, entry] of servers.entries()) {
    const client = await createMCPClient({ maxRetries: 0, protocolVersionDiscovery: false, transport: { type: "http", url: entry.url, headers: resolveHeaders(entry.headers), redirect: "error" }, initializationOptions: { timeout: timeoutMs } });
    try {
      let page = await client.listTools();
      while (true) {
        result.push(...page.tools.map((tool) => ({ server, name: tool.name, description: tool.description, inputSchema: tool.inputSchema as Record<string, unknown> })));
        if (!page.nextCursor) break;
        page = await client.listTools({ params: { cursor: page.nextCursor } });
      }
    } finally { await client.close(); }
  }
  return result;
}

async function invokeMcpTool(server: McpServer, name: string, args: unknown, timeoutMs: number) {
  "use step";
  const signal = AbortSignal.timeout(timeoutMs);
  const client = await createMCPClient({ maxRetries: 0, protocolVersionDiscovery: false, transport: { type: "http", url: server.url, headers: resolveHeaders(server.headers), redirect: "error" }, initializationOptions: { timeout: timeoutMs, signal } });
  try {
    const result = await client.callTool({ name, arguments: args as Record<string, unknown>, options: { timeout: timeoutMs, signal } });
    if (Buffer.byteLength(JSON.stringify(result)) > 256_000) throw new Error("The MCP tool returned too much data.");
    return result;
  } finally { await client.close(); }
}

resolveStageBackend.maxRetries = 0;
runClaudeStage.maxRetries = 0;
discoverMcpTools.maxRetries = 0;
invokeMcpTool.maxRetries = 0;
