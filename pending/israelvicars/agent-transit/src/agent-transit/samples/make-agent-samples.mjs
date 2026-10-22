import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const iso = (n) => new Date(Date.UTC(2026, 9, 16, 12, 0, n)).toISOString();
const tools = ['Read', 'Glob', 'Grep', 'Edit', 'Write', 'Bash', 'Read', 'Task', 'WebSearch', 'WebFetch', 'mcp__docs__lookup', 'MultiEdit', 'shell', 'Read', 'apply_patch', 'Bash', 'Agent', 'Write'];
const args = (name, i) => name === 'Bash' || name === 'shell' ? { command: `${i === 15 ? 'npm run build' : 'git diff --stat'} SECRET_CANARY_COMMAND_7731` } : name === 'Task' || name === 'Agent' ? { description: 'inspect tests' } : name === 'WebSearch' ? { query: 'public API docs' } : name === 'Glob' ? { pattern: 'src/**/*.mjs' } : name === 'Grep' ? { pattern: 'normalize', path: 'src' } : name === 'Read' ? { file_path: `src/module-${i}.mjs` } : name === 'Write' || name === 'Edit' || name === 'MultiEdit' || name === 'apply_patch' ? { file_path: `src/module-${i}.mjs`, content: 'SECRET_CANARY_FILE_CONTENT_7731' } : {};
function claude() {
  const out = [{ _agentFormat: 'claude-code', _comment: 'SYNTHETIC hand-built Claude Code JSONL; prompts, outputs, and file contents contain SECRET_CANARY_PROMPT_7731 / SECRET_CANARY_OUTPUT_7731 / SECRET_CANARY_COMMAND_7731.' }];
  tools.forEach((name, i) => { const id = `cc-${i + 1}`; const t = 1 + i * (i === 15 ? 4 : 1); out.push({ type: 'assistant', timestamp: iso(t), uuid: `u-${i}`, parentUuid: i ? `u-${i - 1}` : null, message: { content: [{ type: 'text', text: 'SECRET_CANARY_PROMPT_7731' }, { type: 'tool_use', id, name, input: args(name, i) }] } }); out.push({ type: 'user', timestamp: iso(t + (i === 15 ? 4 : 1)), uuid: `r-${i}`, parentUuid: `u-${i}`, message: { content: [{ type: 'tool_result', tool_use_id: id, is_error: i === 12, content: i === 12 ? 'permission denied SECRET_CANARY_OUTPUT_7731' : 'result SECRET_CANARY_OUTPUT_7731' }] } }); });
  return out;
}
function cursor() {
  const names = ['Read', 'StrReplace', 'Shell', 'TodoWrite', 'Task', 'WebSearch', 'Glob', 'Grep', 'Write', 'Delete', 'SemanticSearch', 'ReadLints', 'EditNotebook', 'WebFetch', 'Shell', 'Read', 'StrReplace', 'Task'];
  const out = [];
  names.forEach((name, i) => {
    out.push({ role: 'assistant', message: { content: [{ type: 'text', text: 'SECRET_CANARY_PROMPT_7731' }, { type: 'tool_use', name, input: { file_path: `src/module-${i}.mjs`, command: `${i === 14 ? 'npm run build' : 'git diff'} SECRET_CANARY_COMMAND_7731`, content: 'SECRET_CANARY_FILE_CONTENT_7731' } }] } });
    out.push({ type: 'turn_ended', status: i === 12 ? 'error' : 'success', ...(i === 12 ? { error: 'SECRET_CANARY_OUTPUT_7731' } : {}) });
  });
  return out;
}
function codex() {
  const out = [{ _agentFormat: 'codex', _comment: 'SYNTHETIC hand-built Codex rollout JSONL; SECRET_CANARY_PROMPT_7731 SECRET_CANARY_OUTPUT_7731 SECRET_CANARY_COMMAND_7731' }, { timestamp: iso(0), type: 'session_meta', payload: { id: 'synthetic-session' } }];
  tools.forEach((name, i) => { const id = `cx-${i + 1}`; const t = 1 + i * (i === 15 ? 4 : 1); const wrapped = i < 3; const inner = ['exec_command', 'apply_patch', 'update_plan'][i]; const payload = wrapped ? { type: 'custom_tool_call', call_id: id, name: 'exec', input: `tools.${inner}({ value: 'SECRET_CANARY_COMMAND_7731' });` } : name === 'Bash' || name === 'shell' ? { type: 'local_shell_call', call_id: id, command: `${i === 15 ? 'npm run build' : 'git diff'} SECRET_CANARY_COMMAND_7731` } : { type: 'function_call', call_id: id, name, arguments: JSON.stringify(args(name, i)) }; out.push({ timestamp: iso(t), type: 'response_item', payload }); out.push({ timestamp: iso(t + (i === 15 ? 4 : 1)), type: 'response_item', payload: { type: wrapped ? 'custom_tool_call_output' : name === 'Bash' || name === 'shell' ? 'local_shell_call_output' : 'function_call_output', call_id: id, output: wrapped ? [{ type: 'input_text', text: 'SECRET_CANARY_OUTPUT_7731' }] : i === 12 ? 'Permission denied SECRET_CANARY_OUTPUT_7731' : 'output SECRET_CANARY_OUTPUT_7731', is_error: i === 12 } }); });
  out.push({ timestamp: iso(25), type: 'mystery_future_line', payload: {} });
  return out;
}
mkdirSync(here, { recursive: true });
for (const [name, data] of [['claude-code', claude()], ['codex', codex()], ['cursor', cursor()]]) writeFileSync(join(here, `${name}-synthetic.jsonl`), data.map((x) => JSON.stringify(x)).join('\n') + '\n');
