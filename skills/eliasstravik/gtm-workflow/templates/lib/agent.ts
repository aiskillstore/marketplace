import { spawn } from "node:child_process";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { generateText, gateway, jsonSchema, Output } from "ai";
import { z } from "zod";
import { provider, ProviderPreCallError, type PaidCallMeta } from "./provider";
import { redact } from "./redact";
import { workflowModel } from "./model";
export { DEFAULT_WORKFLOW_MODEL } from "./model";

export type AgentTools = "none" | "web" | "host-default";
export type McpServer = { name: string; url: string; headers?: Record<string, string> };
export type Backend = "gateway" | "claude" | "codex";
export type CliCapability = { bin: string; headless: true; canDisableTools: boolean; canRestrictTools: boolean; budgetFlag?: string; turnsFlag?: string; mcpHeaders: boolean };
export const CLI_CAPABILITIES: Record<Exclude<Backend, "gateway">, CliCapability> = {
  claude: { bin: "claude", headless: true, canDisableTools: true, canRestrictTools: true, budgetFlag: "--max-budget-usd", mcpHeaders: true },
  codex: { bin: "codex", headless: true, canDisableTools: false, canRestrictTools: true, mcpHeaders: true },
};
const CODEX_USD_PER_MILLION: Record<string, { input: number; output: number }> = { "gpt-5.3-codex": { input: 1.75, output: 14 }, "gpt-5.4": { input: 2.5, output: 15 } };

export interface AgentInput<T extends z.ZodTypeAny> {
  prompt: string; context?: string; contextId?: string; schema: T; meta: PaidCallMeta; step: string;
  tools?: AgentTools; untrusted?: boolean; model?: string; reasoning?: Parameters<typeof generateText>[0]["reasoning"];
  maxUsd?: number; timeoutMs?: number; ttlMs?: number; signal?: AbortSignal; providerKeys?: string[];
}

export async function resolveBackend(): Promise<Backend> {
  if (process.env.AI_GATEWAY_API_KEY || process.env.VERCEL) return "gateway";
  if (process.env.GTM_HOST === "claude" || process.env.GTM_HOST === "codex") return process.env.GTM_HOST;
  if (process.env.GTM_HOST === "eve") throw new Error("This needs an AI key on the hosted project.");
  throw new Error("Add an AI key to .env, or set GTM_HOST.");
}

/** An agentic stage needs a spend cap and MCP-only tools; the Gateway and Claude Code offer both, Codex does not. */
export function canRunStage(backend: Backend): boolean {
  if (backend === "gateway") return true;
  const capability = CLI_CAPABILITIES[backend];
  return Boolean(capability.budgetFlag && capability.canRestrictTools && capability.mcpHeaders);
}

/** Headless Claude Code arguments for one agentic stage: structured output, budget cap, MCP tools only, no built-ins. */
export function claudeStageArgs(input: { prompt: string; schemaJson: unknown; maxUsd: number; mcpConfigFile: string }): string[] {
  return ["-p", input.prompt, "--output-format", "json", "--json-schema", JSON.stringify(input.schemaJson), "--permission-mode", "dontAsk", "--no-session-persistence",
    "--tools", "", "--allowedTools", "mcp__*", "--mcp-config", input.mcpConfigFile, "--strict-mcp-config", "--max-budget-usd", String(input.maxUsd)];
}

/** MCP client configuration shared by the CLI and Gateway backends; header values are environment-variable names. */
export function mcpConfig(servers: McpServer[], env: Record<string, string | undefined> = process.env) {
  return { mcpServers: Object.fromEntries(servers.map((server) => [server.name, { type: "http", url: server.url, ...(server.headers ? { headers: resolveHeaders(server.headers, env) } : {}) }])) };
}

export function resolveHeaders(headers: Record<string, string> = {}, env: Record<string, string | undefined> = process.env): Record<string, string> {
  return Object.fromEntries(Object.entries(headers).map(([name, environmentVariable]) => {
    const value = env[environmentVariable];
    if (!value) throw new Error(`Configure ${environmentVariable} on the workflow project.`);
    return [name, value];
  }));
}

/** Run a headless CLI with an allow-listed environment and a hard timeout; returns stdout. */
export function runCli(name: Exclude<Backend, "gateway">, args: string[], options: { cwd: string; timeoutMs: number; signal?: AbortSignal; extraEnv?: Record<string, string> }): Promise<string> {
  return run(CLI_CAPABILITIES[name].bin, args, { cwd: options.cwd, env: childEnv([], options.extraEnv ?? {}), timeoutMs: options.timeoutMs, signal: options.signal });
}

export async function agent<T extends z.ZodTypeAny>(input: AgentInput<T>): Promise<z.infer<T>> {
  const backend = await resolveBackend();
  if (input.untrusted && backend !== "gateway" && !CLI_CAPABILITIES[backend].canDisableTools) throw new ProviderPreCallError("This input needs an AI key so tools can be disabled.");
  const prompt = input.context ? `${input.prompt}\n\nContext${input.contextId ? ` (${input.contextId})` : ""}:\n${input.context}` : input.prompt;
  const schemaJson = strictSchema(z.toJSONSchema(input.schema));
  const model = workflowModel(input.model);
  const result = await provider({ step: input.step, name: "agent", endpoint: `${backend}/${model}`, input: { prompt, schemaJson, tools: input.tools ?? "none", reasoning: input.reasoning }, schema: input.schema, ttlMs: input.ttlMs ?? 2_592_000_000, costUsd: input.maxUsd, costSource: "projected", meta: input.meta,
    call: async () => backend === "gateway" ? viaApi({ prompt, schemaJson, model, reasoning: input.reasoning, tools: input.tools, timeoutMs: input.timeoutMs, signal: input.signal }) : viaCli(backend, { prompt, schemaJson, model: input.model ?? "default", maxUsd: input.maxUsd, timeoutMs: input.timeoutMs, signal: input.signal, providerKeys: input.providerKeys }) });
  return result.value;
}

async function viaApi(input: { prompt: string; schemaJson: any; model: string; reasoning?: any; tools?: AgentTools; timeoutMs?: number; signal?: AbortSignal }) {
  const abortSignal = AbortSignal.any([AbortSignal.timeout(input.timeoutMs ?? 240_000), ...(input.signal ? [input.signal] : [])]);
  const result = await generateText({ model: input.model, reasoning: input.reasoning ?? "high", prompt: input.prompt, output: Output.object({ schema: jsonSchema(input.schemaJson) }), ...(input.tools === "web" ? { tools: { exa_search: gateway.tools.exaSearch({ type: "fast", numResults: 5 }) } } : {}), abortSignal });
  const cost = (result.providerMetadata?.gateway as { cost?: number | string } | undefined)?.cost;
  return { value: result.output, costUsd: cost === undefined ? undefined : Number(cost) };
}

async function viaCli(name: Exclude<Backend, "gateway">, input: { prompt: string; schemaJson: any; model: string; maxUsd?: number; timeoutMs?: number; signal?: AbortSignal; providerKeys?: string[] }) {
  const directory = await mkdtemp(join(tmpdir(), "gtm-agent-"));
  try {
    const schemaFile = join(directory, "schema.json"), outputFile = join(directory, "out.json");
    await writeFile(schemaFile, JSON.stringify(input.schemaJson));
    const args = name === "claude"
      ? ["-p", input.prompt, "--output-format", "json", "--json-schema", JSON.stringify(input.schemaJson), "--permission-mode", "dontAsk", "--no-session-persistence", "--tools", "", ...(input.maxUsd ? ["--max-budget-usd", String(input.maxUsd)] : [])]
      : ["exec", "--output-schema", schemaFile, "-o", outputFile, "--sandbox", "read-only", "--ephemeral", "--skip-git-repo-check", "--json", input.prompt];
    const stdout = await run(CLI_CAPABILITIES[name].bin, args, { cwd: directory, env: childEnv(input.providerKeys, name === "claude" && input.model !== "default" ? { ANTHROPIC_MODEL: input.model } : {}), timeoutMs: input.timeoutMs ?? 240_000, signal: input.signal });
    if (name === "claude") { const value = JSON.parse(stdout); if (value.is_error) throw new Error(String(value.result)); return { value: value.structured_output, costUsd: value.total_cost_usd }; }
    const value = JSON.parse(await readFile(outputFile, "utf8"));
    const usage = [...stdout.matchAll(/"input_tokens":(\d+).*?"output_tokens":(\d+)/g)].at(-1);
    const price = CODEX_USD_PER_MILLION[input.model] ?? CODEX_USD_PER_MILLION["gpt-5.3-codex"];
    return { value, costUsd: usage ? (Number(usage[1]) * price.input + Number(usage[2]) * price.output) / 1_000_000 : undefined };
  } finally { await rm(directory, { recursive: true, force: true }); }
}

export function childEnv(providerKeys: string[] = [], extra: Record<string, string> = {}) {
  const env: Record<string, string> = { PATH: process.env.PATH ?? "", HOME: process.env.HOME ?? "", NO_COLOR: "1", TERM: "dumb", ...extra };
  for (const [key, value] of Object.entries(process.env)) if (value && (/^(?:TURSO|GTM|WORKFLOW)_/.test(key) || key === "AI_GATEWAY_API_KEY" || providerKeys.includes(key))) env[key] = value;
  return env;
}

function run(bin: string, args: string[], options: { cwd: string; env: Record<string, string>; timeoutMs: number; signal?: AbortSignal }): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = spawn(bin, args, { cwd: options.cwd, env: options.env, stdio: ["ignore", "pipe", "pipe"], detached: true }); let stdout = "", stderr = "";
    child.stdout.on("data", (data) => stdout += data); child.stderr.on("data", (data) => stderr += data);
    const stop = (error: Error) => { try { process.kill(-child.pid!, "SIGKILL"); } catch {} reject(error); };
    const timer = setTimeout(() => stop(new Error(`${bin} timed out`)), options.timeoutMs);
    const abort = () => stop(new Error(`${bin} aborted`)); options.signal?.addEventListener("abort", abort, { once: true });
    child.on("error", (error) => { clearTimeout(timer); reject(new ProviderPreCallError(error.message)); });
    child.on("close", (code) => { clearTimeout(timer); options.signal?.removeEventListener("abort", abort); code === 0 ? resolve(stdout) : reject(new Error(`${bin} exited ${code}: ${redact(stderr)}`)); });
  });
}

function strictSchema(schema: any): any { if (Array.isArray(schema)) return schema.map(strictSchema); if (schema && typeof schema === "object") { const result: any = {}; for (const key of Object.keys(schema)) if (key !== "$schema") result[key] = strictSchema(schema[key]); if (result.type === "object") { result.additionalProperties = false; result.required = Object.keys(result.properties ?? {}); } return result; } return schema; }
