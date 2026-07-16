import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(TEST_DIR, '..', '..');
const WORKFLOW = readFileSync(join(REPO_ROOT, '.github/workflows/generate-packs.yml'), 'utf8');
const EVALUATOR_PREFLIGHT_PATH = join(REPO_ROOT, 'scripts/pack-evaluator-preflight.sh');
const EVALUATOR_PREFLIGHT = readFileSync(EVALUATOR_PREFLIGHT_PATH, 'utf8');
const DOWNLOAD_ACTION = readFileSync(join(REPO_ROOT, '.github/actions/download-skillstore-cli/action.yml'), 'utf8');
const EVALUATOR_PROXY = readFileSync(join(REPO_ROOT, 'scripts/pack-evaluator-proxy.mjs'), 'utf8');
const PACK_PRODUCTION = readFileSync(join(REPO_ROOT, 'scripts/pack-production.mjs'), 'utf8');
const CONTRACT_SMOKE = readFileSync(join(REPO_ROOT, 'scripts/pack-evaluator-contract-smoke.mjs'), 'utf8');
const ADMISSION_WORKFLOW = readFileSync(
  join(REPO_ROOT, '.github/workflows/pack-opportunity-admission.yml'),
  'utf8',
);
const SLO_WORKFLOW = readFileSync(join(REPO_ROOT, '.github/workflows/pack-production-slo.yml'), 'utf8');
const GENERATE_CONTENT = readFileSync(join(REPO_ROOT, '.github/workflows/generate-content.yml'), 'utf8');
const TRANSLATE_PACKS = readFileSync(join(REPO_ROOT, '.github/workflows/translate-packs.yml'), 'utf8');

function section(start, end) {
  const startIndex = WORKFLOW.indexOf(start);
  assert.notEqual(startIndex, -1, `missing workflow section ${start}`);
  const endIndex = end ? WORKFLOW.indexOf(end, startIndex + start.length) : WORKFLOW.length;
  assert.notEqual(endIndex, -1, `missing workflow boundary ${end}`);
  return WORKFLOW.slice(startIndex, endIndex);
}

test('production workflow has separate Plan, secret-free Evaluate, Persist, and production Readback jobs', () => {
  assert.match(WORKFLOW, /  contract_smoke_only:/);
  assert.match(WORKFLOW, /  plan:/);
  assert.match(WORKFLOW, /  evaluate:/);
  assert.match(WORKFLOW, /  persist:/);
  assert.match(WORKFLOW, /  enrich_publish_readback:/);
  assert.doesNotMatch(WORKFLOW, /  production_slo:/);
  assert.match(WORKFLOW, /permissions:\n  contents: read/);
});

test('manual smoke-only dispatch cannot enter Queue, generation, or persistence', () => {
  assert.match(WORKFLOW, /smoke_only:\n\s+description: 'Run exactly the Messages and Responses contract probes; never plan, generate, or persist'\n\s+type: boolean\n\s+default: false/);
  const smoke = section('  contract_smoke_only:', '  plan:');
  const plan = section('  plan:', '  evaluate:');
  assert.match(smoke, /if: github\.event_name == 'workflow_dispatch' && inputs\.smoke_only == true/);
  assert.match(smoke, /runs-on: ubuntu-latest/);
  assert.match(smoke, /PACK_EVALUATOR_HELM_API_KEY: \$\{\{ secrets\.PACK_EVALUATOR_HELM_API_KEY \}\}/);
  assert.match(smoke, /PACK_EVALUATOR_PROXY_URL=https:\/\/helm\.easymeta\.au/);
  assert.match(smoke, /pack-evaluator-contract-smoke\.mjs/);
  assert.match(smoke, /Upload sanitized contract diagnostics/);
  assert.doesNotMatch(
    smoke,
    /SKILLSTORE_API_URL|PACK_PRODUCTION_(?:PLANNER|AUTOMATION)_KEY|SUPABASE|APP_PRIVATE_KEY|skillstore-cli|api\/automation\/packs\/production|pack-production\.mjs|generate-content/
  );
  assert.match(plan, /if: github\.event_name == 'schedule' \|\| inputs\.smoke_only != true/);
  assert.match(section('  evaluate:', '  persist:'), /needs: plan/);
  assert.match(section('  persist:', '  enrich_publish_readback:'), /needs: \[plan, evaluate\]/);
  assert.match(section('  enrich_publish_readback:'), /needs: \[plan, persist\]/);
});

test('evaluate job cannot interpolate production write credentials', () => {
  const evaluate = section('  evaluate:', '  persist:');
  assert.doesNotMatch(
    evaluate,
    /secrets\.(SUPABASE|APP_PRIVATE_KEY|AUTOMATION_API_KEY|SKILLSTORE_CALLBACK_TOKEN|CACHE_INVALIDATE_SECRET)/
  );
  assert.doesNotMatch(evaluate, /--write|continue-on-error/);
  assert.match(evaluate, /set \+e[\s\S]*EVALUATOR_RC=\$\?[\s\S]*exit "\$EVALUATOR_RC"/);
  assert.match(evaluate, /SKILLSTORE_AGENT_ENV_MODE=strict/);
  assert.match(evaluate, /persist-credentials: false/);
});

test('evaluate runs on a disposable VM with a user-separated job-local inference proxy', () => {
  const evaluateWorkflow = section('  evaluate:', '  persist:');
  const evaluate = `${evaluateWorkflow}\n${EVALUATOR_PREFLIGHT}`;
  assert.match(evaluateWorkflow, /scripts\/pack-evaluator-preflight\.sh/);
  const continuation = String.fromCharCode(92);
  const preflightCallLines = evaluateWorkflow
    .split('\n')
    .filter((line) => /^\s+(PACK_EVALUATOR_PROXY_TOKEN|PACK_DIAGNOSTICS_DIR)=/.test(line));
  assert.ok(preflightCallLines.length >= 3);
  assert.ok(preflightCallLines.every((line) => line.endsWith(` ${continuation}`)));
  assert.ok(preflightCallLines.every((line) => !line.endsWith(` ${continuation}${continuation}`)));
  assert.match(evaluate, /runs-on: ubuntu-24\.04/);
  assert.match(evaluate, /@anthropic-ai\/claude-code@2\.1\.210/);
  assert.match(evaluate, /@openai\/codex@0\.139\.0/);
  assert.match(
    evaluate,
    /apt-get install --yes --no-install-recommends[\s\\]+apparmor bubblewrap ffmpeg poppler-utils ripgrep util-linux/,
  );
  assert.match(evaluate, /test "\$\(command -v bwrap\)" = \/usr\/bin\/bwrap/);
  assert.match(evaluate, /command -v ffprobe/);
  assert.match(evaluate, /command -v pdfinfo/);
  assert.match(evaluate, /command -v pdftotext/);
  assert.match(evaluate, /command -v rg/);
  assert.match(evaluate, /test "\$\(command -v google-chrome\)" = \/usr\/bin\/google-chrome/);
  assert.match(evaluate, /test -x \/usr\/bin\/google-chrome/);
  assert.match(evaluate, /PACK_EVALUATOR_CHROMIUM_PATH=\/usr\/bin\/google-chrome/);
  assert.match(evaluate, /SKILLSTORE_AGENT_ENV_ALLOWLIST=.*PACK_EVALUATOR_CHROMIUM_PATH/);
  assert.match(evaluate, /useradd .*packproxy/);
  assert.match(evaluate, /useradd .*packeval/);
  assert.match(evaluate, /\/opt\/pack-evaluator\/bin\/node/);
  assert.match(evaluate, /\/opt\/pack-evaluator\/runtime\/bin\/node/);
  assert.match(evaluate, /\/opt\/pack-evaluator\/bin\/skillstore-cli/);
  assert.match(evaluate, /\/opt\/pack-evaluator\/lib\/pack-evaluator-proxy\.mjs/);
  assert.match(evaluate, /\/opt\/pack-evaluator\/lib\/pack-production\.mjs/);
  assert.match(evaluate, /\/opt\/pack-evaluator\/input\/plan\.json/);
  assert.match(evaluate, /\/opt\/pack-evaluator\/input\/skills/);
  assert.match(evaluate, /\/opt\/pack-evaluator\/results/);
  assert.match(evaluate, /npm install --global --prefix \/opt\/pack-evaluator\/runtime/);
  assert.match(evaluate, /\/opt\/pack-evaluator\/runtime\/bin\/claude/);
  assert.match(evaluate, /\/opt\/pack-evaluator\/runtime\/bin\/codex/);
  assert.match(evaluate, /! test -w \/opt\/pack-evaluator\/runtime\/bin/);
  assert.match(evaluate, /CODEX_HOME=\/opt\/pack-evaluator\/codex-home/);
  assert.match(evaluate, /install -d -o root -g root -m 1777[\s\S]*\/opt\/pack-evaluator\/codex-home/);
  assert.match(evaluate, /test -w \/opt\/pack-evaluator\/codex-home/);
  assert.match(evaluate, /stat -c '%U:%G:%a' \/opt\/pack-evaluator\/codex-home/);
  assert.match(evaluate, /! test -w \/opt\/pack-evaluator\/codex-home\/config\.toml/);
  assert.match(evaluate, /PATH=\/opt\/pack-evaluator\/runtime\/bin:\/usr\/bin:\/bin/);
  assert.doesNotMatch(evaluate, /PATH=\/usr\/local\/bin/);
  assert.match(evaluate, /NODE_BIN=\/opt\/pack-evaluator\/bin\/node/);
  assert.match(evaluate, /sha256sum \/opt\/pack-evaluator\/bin\/skillstore-cli/);
  assert.match(evaluate, /sha256sum \/opt\/pack-evaluator\/bin\/node/);
  assert.match(evaluate, /! test -w \/opt\/pack-evaluator\/bin/);
  assert.match(evaluate, /! test -w \/opt\/pack-evaluator\/lib/);
  assert.match(evaluate, /find \/opt\/pack-evaluator\/input\/skills -name skill-report\.json -print -quit/);
  assert.match(evaluate, /marketplace-evaluate\/skills" -type l/);
  assert.match(evaluate, /PACKEVAL_UID=\$\(id -u packeval\)/);
  assert.match(evaluate, /PACKEVAL_GID=\$\(id -g packeval\)/);
  assert.match(evaluate, /--evaluator-uid "\$PACKEVAL_UID"/);
  assert.match(evaluate, /--evaluator-gid "\$PACKEVAL_GID"/);
  assert.match(evaluate, /--evaluator-cwd \/home\/packeval/);
  assert.match(evaluate, /--evaluator-runtime-root \/opt\/pack-evaluator\/generations/);
  assert.match(evaluate, /! test -w \/opt\/pack-evaluator\/generations/);
  assert.match(evaluate, /sudo -u packproxy env -i/);
  assert.match(evaluate, /sudo -u packeval env -i/);
  assert.match(evaluate, /! sudo -n true/);
  assert.match(evaluate, /! test -r .*PROXY_PID.*environ/);
  assert.match(evaluate, /PACK_EVALUATOR_HELM_API_KEY: \$\{\{ secrets\.PACK_EVALUATOR_HELM_API_KEY \}\}/);
  assert.match(evaluate, /PACK_EVALUATOR_PROXY_TOKEN="\$LOCAL_TOKEN"/);
  assert.match(evaluate, /supports_websockets = false/);
  assert.match(evaluate, /! test -e \/home\/packeval\/\.codex\/auth\.json/);
  assert.doesNotMatch(evaluate, /cp .*\.codex\/auth\.json|\/home\/runner\/_work\/_cache/);
  assert.match(evaluate, /name: pack-production-cli/);
  assert.match(evaluate, /sha256sum -c checksums\.txt/);
  assert.match(evaluate, /Verify Plan CLI handoff before execution/);
  assert.doesNotMatch(evaluate, /secrets\.APP_PRIVATE_KEY|steps\.cli-app-token/);
  assert.match(EVALUATOR_PROXY, /127\.0\.0\.1/);
  assert.match(EVALUATOR_PROXY, /ALLOWED_PATHS/);
  assert.match(EVALUATOR_PROXY, /authorization.*Bearer.*upstreamKey/s);
  assert.match(evaluate, /PACK_EVALUATOR_ALLOWED_MODELS=claude-sonnet-4\.6,claude-sonnet-4-6,claude-sonnet-5,sonnet,gpt-5\.5/);
  assert.match(evaluate, /PACK_EVALUATOR_MAX_REQUESTS=256/);
  assert.match(evaluate, /PACK_EVALUATOR_MAX_CONCURRENT=4/);
  assert.match(evaluate, /PACK_EVALUATOR_MAX_OUTPUT_TOKENS=16384/);
  assert.match(evaluate, /PACK_EVALUATOR_ACTIVITY_FILE="\$PROXY_ACTIVITY"/);
  assert.match(evaluate, /PACK_EVALUATOR_ACTIVITY_FILE="\$PROXY_ACTIVITY"[\s\\]+bash .*pack-evaluator-preflight\.sh/);
  assert.match(evaluate, /sudo rm -f "\$PROXY_ACTIVITY"/);
  assert.match(evaluate, /Pack evaluator proxy did not become healthy within 30 seconds/);
  assert.match(evaluate, /proxy-diagnostics\.json/);
  assert.match(evaluate, /Reply with exactly PACK_EVALUATOR_READY and nothing else/);
  assert.match(evaluate, /pack-evaluator-contract-smoke\.mjs/);
  assert.match(evaluate, /PACK_EVALUATOR_CONTRACT_TIMEOUT_MS=30000/);
  assert.match(evaluate, /contract-smoke\.json/);
  assert.ok(evaluate.indexOf('pack-evaluator-contract-smoke.mjs') < evaluate.indexOf('pack-evaluator-preflight.sh'));
  assert.match(CONTRACT_SMOKE, /path: '\/v1\/messages'/);
  assert.match(CONTRACT_SMOKE, /path: '\/v1\/responses'/);
  assert.match(CONTRACT_SMOKE, /max_tokens: 16/);
  assert.match(CONTRACT_SMOKE, /max_output_tokens: 16/);
  assert.match(CONTRACT_SMOKE, /model: 'claude-sonnet-5'/);
  assert.equal((CONTRACT_SMOKE.match(/stream: true/g) ?? []).length, 2);
  assert.match(CONTRACT_SMOKE, /content_block_delta/);
  assert.match(CONTRACT_SMOKE, /response\.output_text\.delta/);
  assert.match(evaluate, /readonly PREFLIGHT_TIMEOUT_SECONDS=180/);
  assert.match(evaluate, /timeout --signal=TERM --kill-after=5s "\$\{PREFLIGHT_TIMEOUT_SECONDS\}s"/);
  assert.match(evaluate, /\/opt\/pack-evaluator\/runtime\/bin\/claude/);
  assert.match(evaluate, /--permission-mode bypassPermissions/);
  assert.match(evaluate, /--model sonnet/);
  assert.match(evaluate, /\/opt\/pack-evaluator\/runtime\/bin\/codex/);
  assert.match(evaluate, /exec\s+\\\n\s+--skip-git-repo-check/);
  assert.match(evaluate, /--sandbox read-only/);
  assert.match(evaluate, /--cd \/home\/packeval/);
  assert.match(evaluate, /--ephemeral/);
  assert.match(evaluate, /--color never/);
  assert.match(evaluate, /-m gpt-5\.5/);
  assert.match(evaluate, /CLAUDE_OUTCOME=command_failed/);
  assert.match(evaluate, /CODEX_OUTCOME=command_failed/);
  assert.match(evaluate, /for ATTEMPT in 1 2/);
  assert.match(evaluate, /should_retry_preflight[\s\\]+"\$CODEX_OUTCOME" "\$CODEX_ERROR_CLASS" "\$ATTEMPT"/);
  assert.match(EVALUATOR_PREFLIGHT, /retryable_http\) return 0/);
  assert.match(EVALUATOR_PREFLIGHT, /\[ "\$attempt" -ge 2 \]/);
  assert.match(evaluate, /cleanup_processes\(\)/);
  assert.match(evaluate, /RETRY_CLEANUP_OUTCOME=passed/);
  assert.match(evaluate, /sleep 5/);
  assert.match(evaluate, /attempts: \$codexAttempts/);
  assert.match(evaluate, /durationMs: \$durationMs/);
  assert.doesNotMatch(evaluate, /connect\|connection\|transport\|request/);
  assert.match(evaluate, /SKILLSTORE_AGENTS=codex,claude/);
  assert.match(evaluate, /agent-preflight-diagnostics\.json/);
  assert.match(evaluate, /CLAUDE_OUTCOME=invalid_response/);
  assert.match(evaluate, /CODEX_OUTCOME=invalid_response/);
  assert.match(evaluate, /classify_error\(\)/);
  assert.match(evaluate, /state_storage/);
  assert.match(evaluate, /authentication/);
  assert.match(evaluate, /model_route/);
  assert.match(evaluate, /upstream_transport/);
  assert.match(evaluate, /errorClass: \$claudeErrorClass/);
  assert.match(evaluate, /errorClass: \$codexErrorClass/);
  assert.match(evaluate, /claude:\s*\{/);
  assert.match(evaluate, /codex:\s*\{/);
  assert.match(evaluate, /cleanup:\s*\{[\s\S]*outcome: \$cleanupOutcome,[\s\S]*retryOutcome: \$retryCleanupOutcome/);
  assert.match(evaluate, /CLEANUP_OUTCOME=failed/);
  assert.match(evaluate, /CLEANUP_OUTCOME=probe_failed/);
  assert.match(evaluate, /CLEANUP_RC/);
  assert.match(evaluate, /tr -d '\\r\\n'/);
  assert.doesNotMatch(evaluate, /SKILLSTORE_AGENTS: \$\{\{ vars\.SKILLSTORE_AGENTS \}\}/);
  assert.doesNotMatch(evaluate, /sed -E .*Bearer|proxy\.log|proxy-failure\.log/);
  assert.match(evaluate, /evaluator-failure\.txt/);
  assert.match(evaluate, /pkill -TERM -u packeval/);
  assert.match(evaluate, /pkill -KILL -u packeval/);
  assert.match(evaluate, /pkill -TERM -u packproxy -f pack-evaluator-proxy\.mjs/);
  assert.match(evaluate, /pkill -KILL -u packproxy -f pack-evaluator-proxy\.mjs/);
  assert.match(evaluate, /pgrep -u packproxy -f pack-evaluator-proxy\.mjs/);
  assert.match(evaluate, /proxy-termination-failure\.txt/);
  assert.match(evaluate, /EVALUATOR_PROCESSES_STOPPED=true/);
  assert.match(evaluate, /process-termination-failure\.txt/);
  assert.match(evaluate, /RESULT_BYTES=.*du -sb \/opt\/pack-evaluator\/results/);
  assert.match(evaluate, /RESULT_FILES=.*find \/opt\/pack-evaluator\/results -type f/);
  assert.match(evaluate, /find \/opt\/pack-evaluator\/results ! -type f ! -type d/);
  assert.match(evaluate, /cp -a \/opt\/pack-evaluator\/results\/\./);
  assert.match(evaluate, /find "\$GITHUB_WORKSPACE\/pack-harvest" -type d -exec chmod 0700/);
  assert.match(evaluate, /find "\$GITHUB_WORKSPACE\/pack-harvest" -type f -exec chmod 0600/);
  assert.match(evaluate, /find "\$GITHUB_WORKSPACE\/pack-harvest" ! -type f ! -type d/);
  const preflightIndex = evaluateWorkflow.indexOf('scripts/pack-evaluator-preflight.sh');
  const relaxedErrorIndex = evaluateWorkflow.indexOf('set +e', preflightIndex);
  const evaluatorIndex = evaluateWorkflow.indexOf('sudo env -i', relaxedErrorIndex);
  assert.ok(preflightIndex >= 0);
  assert.ok(relaxedErrorIndex > preflightIndex);
  assert.ok(evaluatorIndex > relaxedErrorIndex);
  assert.match(evaluate, /pack-production\.mjs verify/);
  assert.match(evaluate, /trusted evaluation closure verification failed/);
  assert.match(evaluate, /timeout --signal=TERM --kill-after=30s 4h/);
  assert.match(evaluate, /prlimit --nproc=256:256 --as=6442450944:6442450944/);
  assert.match(EVALUATOR_PROXY, /evaluator proxy request budget exhausted/);
  assert.match(EVALUATOR_PROXY, /evaluator proxy token has expired/);
  assert.match(EVALUATOR_PROXY, /response\.once\('close', abortUpstream\)/);
  assert.match(EVALUATOR_PROXY, /isDeterministicClientFailure/);
  assert.match(EVALUATOR_PROXY, /phase: 'circuit_open'/);
  assert.match(evaluate, /Reject plans outside the bounded evaluation budget/);
  assert.match(evaluate, /MAX_CANDIDATES=2/);
  assert.match(evaluate, /MAX_BEST_SINGLE_COMPETITORS=\$\(\(SLOT_COUNT \* MAX_CANDIDATES\)\)/);
  assert.match(evaluate, /CONTRACT_PROBES=2/);
  assert.match(evaluate, /MAX_CLI_PREFLIGHT_REQUESTS=4/);
  assert.match(evaluate, /TOOL_LOOP_HEADROOM=64/);
  assert.match(evaluate, /PROXY_REQUEST_BUDGET=256/);
  assert.match(evaluate, /3 \* SLOT_COUNT \* MAX_CANDIDATES/);
  assert.match(evaluate, /3 \* HIDDEN_VARIANTS \* MAX_BEST_SINGLE_COMPETITORS/);
  assert.match(evaluate, /HIDDEN_VARIANTS \* MAX_PACK_SKILLS \* \(MAX_PACK_SKILLS \+ 1\)/);
  assert.match(evaluate, /skillToolFollowupsIncluded: true/);
  assert.match(evaluate, /maxBestSingleCompetitors: \$maxBestSingleCompetitors/);
  assert.match(evaluate, /ESTIMATED_REQUESTS[\s\S]*PROXY_REQUEST_BUDGET/);
  const maximumWireRequests = 2 + 4 + (3 * 4 * 2) + 3 + (3 * (4 + 2))
    + (2 * 3) + (3 * 3 * 8) + (3 * 4 * (4 + 1));
  assert.equal(maximumWireRequests, 189);
  assert.equal(maximumWireRequests + 64, 253);
  assert.ok(maximumWireRequests + 64 <= 256);
  assert.match(evaluate, /SKILLSTORE_AGENT_SANDBOX_MODE=bwrap/);
  assert.match(evaluate, /SKILLSTORE_AGENT_SANDBOX_RUNTIME_ROOT=\/opt\/pack-evaluator\/runtime/);
  assert.match(
    evaluate,
    /--unshare-all\s+--share-net\s+--unshare-user\s+--disable-userns\s+--cap-drop ALL/,
  );
  assert.match(evaluate, /! test -r "\/proc\/\$PROXY_PID\/environ"/);
  assert.doesNotMatch(evaluate, /PATH=\/opt\/pack-evaluator\/runtime\/bin:\/opt\/pack-evaluator\/bin/);
});

test('extracted evaluator preflight is valid bounded bash', () => {
  const result = spawnSync('bash', ['-n', EVALUATOR_PREFLIGHT_PATH], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  assert.match(EVALUATOR_PREFLIGHT, /for ATTEMPT in 1 2/);
  assert.match(EVALUATOR_PREFLIGHT, /CLAUDE_EXIT_CODE=\$\?/);
  assert.match(EVALUATOR_PREFLIGHT, /CODEX_EXIT_CODE=\$\?/);
  assert.match(EVALUATOR_PREFLIGHT, /"\$exit_code" -eq 124/);
  assert.match(EVALUATOR_PREFLIGHT, /CLAUDE_ATTEMPTS=/);
  assert.match(EVALUATOR_PREFLIGHT, /--argjson claudeAttempts/);
  assert.match(EVALUATOR_PREFLIGHT, /exitCode: \$exitCode/);
  assert.doesNotMatch(EVALUATOR_PREFLIGHT, /if ! printf '%s\\n' 'Reply with exactly PACK_EVALUATOR_READY/);
  assert.match(EVALUATOR_PREFLIGHT, /PACK_DIAGNOSTICS_DIR\/agent-preflight-diagnostics\.json/);
  assert.match(EVALUATOR_PREFLIGHT, /PACK_DIAGNOSTICS_DIR\/proxy-activity\.ndjson/);
  assert.match(EVALUATOR_PREFLIGHT, /readonly -a AGENT_BWRAP=/);
  assert.match(EVALUATOR_PREFLIGHT, /--tmpfs \//);
  assert.match(
    EVALUATOR_PREFLIGHT,
    /--unshare-all\s+--share-net\s+--unshare-user\s+--disable-userns\s+--cap-drop ALL/,
  );
  assert.match(EVALUATOR_PREFLIGHT, /--tmpfs \/run/);
  assert.match(EVALUATOR_PREFLIGHT, /--ro-bind \/opt\/pack-evaluator\/runtime \/opt\/pack-evaluator\/runtime/);
  assert.doesNotMatch(EVALUATOR_PREFLIGHT, /--ro-bind \/ \//);
  assert.doesNotMatch(EVALUATOR_PREFLIGHT, /--(?:ro-)?bind \/opt\/pack-evaluator\/(?:bin|lib|input|results)/);
  assert.doesNotMatch(EVALUATOR_PREFLIGHT, /GITHUB_WORKSPACE/);
});

test('evaluator preflight retries only an exact bounded HTTP failure once', () => {
  const start = EVALUATOR_PREFLIGHT.indexOf('should_retry_preflight() {');
  const end = EVALUATOR_PREFLIGHT.indexOf('\n}\n', start);
  assert.ok(start >= 0 && end > start, 'retry policy function must be extractable');
  const policy = EVALUATOR_PREFLIGHT.slice(start, end + 3);

  for (const errorClass of ['retryable_http']) {
    const result = spawnSync(
      'bash',
      ['-c', `${policy}\nshould_retry_preflight "$1" "$2" "$3"`, 'policy', 'command_failed', errorClass, '1'],
      { encoding: 'utf8' }
    );
    assert.equal(result.status, 0, `${errorClass} should receive one retry`);
  }
  for (const errorClass of [
    'authentication',
    'model_route',
    'cli_arguments',
    'state_storage',
    'deterministic_http',
    'upstream_transport',
    'timeout',
    'unknown',
  ]) {
    const result = spawnSync(
      'bash',
      ['-c', `${policy}\nshould_retry_preflight "$1" "$2" "$3"`, 'policy', 'command_failed', errorClass, '1'],
      { encoding: 'utf8' }
    );
    assert.equal(result.status, 1, `${errorClass} must fail closed without retry`);
  }
  assert.equal(
    spawnSync(
      'bash',
      ['-c', `${policy}\nshould_retry_preflight "$1" "$2" "$3"`, 'policy', 'command_failed', 'retryable_http', '2'],
      { encoding: 'utf8' }
    ).status,
    1,
    'the second retryable HTTP failure must stop'
  );
  assert.equal(
    spawnSync(
      'bash',
      ['-c', `${policy}\nshould_retry_preflight "$1" "$2" "$3"`, 'policy', 'invalid_response', 'unknown', '1'],
      { encoding: 'utf8' }
    ).status,
    1,
    'invalid responses must not be retried'
  );
});

test('evaluate emits bounded progress and checkpoints cancellation-safe evidence', () => {
  const evaluate = section('  evaluate:', '  persist:');
  assert.match(evaluate, /checkpoint_loop\(\)/);
  assert.match(evaluate, /checkpoint_loop\(\) \{\n\s+trap - EXIT INT TERM/);
  assert.match(evaluate, /flock -x 9/);
  assert.match(evaluate, /\.tmp\.\$\{BASHPID\}/);
  assert.match(evaluate, /mv -f "\$temporary"/);
  assert.match(evaluate, /sleep 30/);
  assert.match(evaluate, /evaluate-progress\.ndjson/);
  assert.match(evaluate, /evaluate-checkpoint\.json/);
  assert.match(evaluate, /evaluate-summary\.json/);
  assert.match(evaluate, /evaluator-interrupted\.txt/);
  assert.doesNotMatch(evaluate, /proxy-interrupted\.log/);
  assert.match(evaluate, /EVALUATOR_FINISHED=false/);
  assert.match(evaluate, /EVALUATOR_PID=\$!/);
  assert.match(evaluate, /wait "\$EVALUATOR_PID"/);
  assert.match(evaluate, /trap 'terminate_step 143' TERM/);
  assert.match(evaluate, /trap 'terminate_step 130' INT/);
  assert.match(evaluate, /trap 'terminate_step 129' HUP/);
  assert.match(evaluate, /for _ in \$\(seq 1 40\)/);
  assert.match(evaluate, /for _ in \$\(seq 1 10\)/);
  assert.match(evaluate, /timeout --signal=TERM --kill-after=0\.2s 1s bash -c 'checkpoint_progress'/);
  const cleanupIndex = evaluate.indexOf('cleanup() {');
  const markerIndex = evaluate.indexOf('write_interrupted_marker', cleanupIndex);
  const snapshotIndex = evaluate.indexOf('bounded_checkpoint_progress', cleanupIndex);
  const terminateIndex = evaluate.indexOf('sudo kill -TERM -- "-$EVALUATOR_PID"', cleanupIndex);
  assert.ok(cleanupIndex >= 0 && markerIndex > cleanupIndex);
  assert.ok(snapshotIndex > markerIndex && terminateIndex > snapshotIndex);
  assert.match(evaluate, /if \[ -n "\$EVALUATOR_PID" \] && \[ "\$EVALUATOR_FINISHED" != "true" \]; then/);
  assert.match(evaluate, /setsid sudo env -i/);
  assert.match(evaluate, /sudo ps -o stat= -g "\$EVALUATOR_PID"/);
  assert.match(evaluate, /sudo kill -TERM -- "-\$EVALUATOR_PID"/);
  assert.doesNotMatch(evaluate, /pgrep -f '\/opt\/pack-evaluator\/lib\/pack-production\.mjs evaluate'/);
  assert.match(evaluate, /--model sonnet/);
  assert.match(evaluate, /--judge-model gpt-5\.5/);
  assert.match(evaluate, /--max-candidates 2/);
  assert.match(evaluate, /--agent-timeout-ms 360000/);
  assert.match(evaluate, /--agent-max-retries 1/);
  assert.match(evaluate, /--evaluation-budget-ms 13800000/);
  assert.match(evaluate, /--scenario-timeout-ms 7200000/);
  assert.match(evaluate, /--minimum-fallback-ms 2700000/);
  assert.match(evaluate, /--scenario-idle-timeout-ms 1200000/);
  assert.match(evaluate, /--proxy-activity-file "\$PROXY_ACTIVITY"/);
  assert.match(evaluate, /name: Upload trusted evaluation evidence\n\s+if: success\(\)/);
  assert.match(evaluate, /name: Upload bounded evaluation diagnostics\n\s+if: always\(\)/);
  assert.match(evaluate, /name: pack-production-diagnostics/);
  assert.match(evaluate, /if-no-files-found: warn/);
  assert.match(evaluate, /path: pack-trusted\//);
  assert.match(evaluate, /path: pack-diagnostics\//);
  assert.doesNotMatch(evaluate, /path: pack-harvest\//);
  assert.doesNotMatch(evaluate, /pack-diagnostics\/.*stdout\.(?:partial|json)/);
  assert.doesNotMatch(evaluate, /(?:cp|install|mv)[^\n]*\.run\.log/);
  assert.doesNotMatch(evaluate, /-name '\*\.run\.log'[\s\\]+-exec (?:cp|install|mv)/);
  assert.doesNotMatch(evaluate, /path:[^\n]*\.run\.log/);
  assert.match(evaluate, /marketplace\.pack-production-run-log-summaries\/v1/);
  assert.match(evaluate, /\{basename: \$basename, bytes: \$bytes, sha256: \$sha256\}/);
  assert.match(evaluate, /rm -f "\$run_log"/);
  assert.match(evaluate, /Raw evaluator run logs survived bounded summarization/);
  assert.match(evaluate, /run-log-summaries\.json/);
  const checkpointIndex = evaluate.indexOf('checkpoint_loop &');
  const evaluatorIndex = evaluate.indexOf('"$NODE_BIN" /opt/pack-evaluator/lib/pack-production.mjs evaluate', checkpointIndex);
  const finishIndex = evaluate.indexOf('EVALUATOR_FINISHED=true', evaluatorIndex);
  assert.ok(checkpointIndex >= 0 && evaluatorIndex > checkpointIndex && finishIndex > evaluatorIndex);
  assert.match(evaluate, /infrastructure-failure\.json/);
  assert.match(evaluate, /CONTRACT_RC=\$\?/);
  assert.match(evaluate, /PREFLIGHT_RC=\$\?/);
  assert.match(evaluate, /--infrastructure-failure-file/);
  assert.match(PACK_PRODUCTION, /buildInfrastructureCliReport/);
  assert.match(PACK_PRODUCTION, /outcome: 'infrastructure_failed'/);
  assert.match(PACK_PRODUCTION, /infrastructureAudit: true/);
});

test('planning uses a read-only API and admits at most one artifact scenario', () => {
  const plan = section('  plan:', '  evaluate:');
  assert.match(plan, /permission-contents: read/);
  assert.match(plan, /production\/queue/);
  assert.match(plan, /PACK_PRODUCTION_PLANNER_KEY/);
  assert.match(plan, /--data-urlencode 'limit=1'/);
  assert.doesNotMatch(plan, /SUPABASE_SERVICE|PUBLIC_SUPABASE|scenario-queue/);
  assert.match(plan, /requiredArtifacts \| length >= 1/);
  assert.match(plan, /\.source == "signals"/);
  assert.match(plan, /\.source == "no-op"/);
  assert.match(plan, /marketplace\.pack-production-noop\/v1/);
  assert.match(plan, /repository: "aiskillstore\/marketplace"/);
  assert.match(plan, /runId: \$runId/);
  assert.match(plan, /commitSha: \$commitSha/);
  assert.match(plan, /has_scenarios=false/);
  assert.match(plan, /require\('node:crypto'\)\.randomUUID\(\)/);
  assert.match(plan, /\.scenarios\[0\]\.generationId = \$generationId/);
  assert.match(plan, /workflow: "Generate Pack"/);
  assert.match(plan, /runAttempt: \$runAttempt/);
  assert.match(plan, /scenarioId: \.scenarios\[0\]\.id/);
  assert.match(plan, /\(has\("generationId"\) \| not\)/);
  assert.match(plan, /\(has\("workflowBinding"\) \| not\)/);
  const allocationIndex = plan.indexOf('.scenarios[0].generationId = $generationId');
  const uploadIndex = plan.indexOf('name: Upload immutable plan');
  assert.ok(allocationIndex >= 0 && uploadIndex > allocationIndex);
  const noOpStart = plan.indexOf('if [ "$SCENARIO_COUNT" -eq 0 ]; then');
  const noOpEnd = plan.indexOf('\n          else', noOpStart);
  assert.ok(noOpStart >= 0 && noOpEnd > noOpStart);
  assert.doesNotMatch(
    plan.slice(noOpStart, noOpEnd),
    /randomUUID|\.scenarios\[[^\]]+\]\.generationId\s*=|\.workflowBinding\s*=/,
  );
  assert.doesNotMatch(PACK_PRODUCTION, /randomUUID/);
  assert.match(PACK_PRODUCTION, /const generationId = scenario\.generationId/);
  assert.match(PACK_PRODUCTION, /Evaluate summary generation id differs from the immutable plan/);
  const evaluate = section('  evaluate:', '  persist:');
  const persist = section('  persist:', '  enrich_publish_readback:');
  const finalize = section('  enrich_publish_readback:');
  assert.match(evaluate, /if: needs\.plan\.outputs\.has_scenarios == 'true'/);
  assert.match(persist, /if: needs\.plan\.outputs\.has_scenarios == 'true'/);
  assert.match(finalize, /if: needs\.plan\.outputs\.has_scenarios == 'true'/);
  assert.match(WORKFLOW, /group: generate-pack-production-v4/);
  assert.match(WORKFLOW, /cron: '17 19 \* \* 1,3,5'/);
  assert.match(WORKFLOW, /PACK_PRODUCTION_CLI_VERSION: '2\.13\.2'/);
  assert.doesNotMatch(WORKFLOW, /2\.12\.0|RELEASE BLOCKER/);
  assert.equal((WORKFLOW.match(/require-checksum: 'true'/g) ?? []).length, 1);
  assert.match(plan, /actions\/create-github-app-token@v3/);
  assert.match(plan, /repositories: marketplace,skillstore/);
  assert.match(plan, /name: pack-production-cli/);
  assert.match(plan, /retention-days: 1/);
  assert.doesNotMatch(WORKFLOW, /version: latest|cli_version:/);
});

test('trusted phases use the Automation API and retain full evidence for 90 days', () => {
  const persist = section('  persist:', '  enrich_publish_readback:');
  const finalize = section('  enrich_publish_readback:');
  assert.match(persist, /pack-production\.mjs persist/);
  assert.match(persist, /PACK_PRODUCTION_AUTOMATION_KEY: \$\{\{ secrets\.PACK_PRODUCTION_AUTOMATION_KEY \}\}/);
  assert.match(finalize, /pack-production\.mjs finalize/);
  assert.match(finalize, /final-result\.json/);
  assert.match(finalize, /pack-production\.mjs finalize/);
  assert.equal((WORKFLOW.match(/retention-days: 90/g) ?? []).length, 5);
  assert.match(finalize, /PACK_PRODUCTION_AUTO_PUBLISH_ENABLED == 'true'/);
  assert.match(finalize, /--poll-seconds 60/);
  assert.match(finalize, /--max-poll-seconds 180/);
  assert.match(PACK_PRODUCTION, /nextPollSeconds = Math\.min\(maxPollSeconds, nextPollSeconds \* 2\)/);
  assert.match(PACK_PRODUCTION, /attemptNumber <= 10/);
  assert.match(WORKFLOW, /auto_publish:[\s\S]*?default: false/);
  assert.match(PACK_PRODUCTION, /skillstore\.pack-evaluation\/v4/);
  assert.match(PACK_PRODUCTION, /candidate_ready evidence is incomplete; persistence and enrichment are forbidden/);
  assert.match(PACK_PRODUCTION, /auditOnly: true/);
  assert.match(PACK_PRODUCTION, /candidateNullPosts/);
  assert.match(PACK_PRODUCTION, /Persist response did not bind the exact candidate-null v4 audit outcome/);
  assert.match(PACK_PRODUCTION, /bestSingle/);
  assert.match(PACK_PRODUCTION, /executionDag/);
  assert.match(PACK_PRODUCTION, /usageProvenance/);
});

test('daily admission and SLO observation are independent and read-only', () => {
  assert.match(ADMISSION_WORKFLOW, /cron: '47 18 \* \* \*'/);
  assert.match(ADMISSION_WORKFLOW, /PACK_PRODUCTION_PLANNER_KEY/);
  assert.match(ADMISSION_WORKFLOW, /--data-urlencode 'limit=1'/);
  assert.doesNotMatch(ADMISSION_WORKFLOW, /PACK_PRODUCTION_AUTOMATION_KEY|SUPABASE|method: 'POST'/);
  assert.match(SLO_WORKFLOW, /cron: '47 20 \* \* \*'/);
  assert.match(SLO_WORKFLOW, /pack-production\.mjs slo/);
  assert.match(SLO_WORKFLOW, /PACK_PRODUCTION_PLANNER_KEY/);
  assert.match(SLO_WORKFLOW, /::warning::Rolling 7-day Pack production SLO is below target/);
  assert.doesNotMatch(SLO_WORKFLOW, /PACK_PRODUCTION_AUTOMATION_KEY|::error::Rolling|exit 1/);
  assert.match(PACK_PRODUCTION, /::warning::Rolling 7-day Pack production SLO is below target/);
  assert.doesNotMatch(PACK_PRODUCTION, /::error::Rolling 7-day Pack production SLO is below target/);
});

test('checkouts use isolated directories and never persist tokens', () => {
  assert.match(WORKFLOW, /marketplace-plan/);
  assert.match(WORKFLOW, /marketplace-evaluate/);
  assert.ok((WORKFLOW.match(/filter: ''/g) ?? []).length >= 1);
  assert.ok((WORKFLOW.match(/persist-credentials: false/g) ?? []).length >= 4);
  const persist = section('  persist:', '  enrich_publish_readback:');
  const finalize = section('  enrich_publish_readback:');
  assert.match(persist, /sparse-checkout: scripts\/pack-production\.mjs\n\s+sparse-checkout-cone-mode: false/);
  assert.match(finalize, /sparse-checkout: scripts\/pack-production\.mjs\n\s+sparse-checkout-cone-mode: false/);
  assert.match(SLO_WORKFLOW, /sparse-checkout: scripts\/pack-production\.mjs\n\s+sparse-checkout-cone-mode: false/);
});

test('CLI downloader verifies checksum before execution and shared-cache writes', () => {
  assert.match(DOWNLOAD_ACTION, /require-checksum:/);
  assert.match(DOWNLOAD_ACTION, /--pattern checksums\.txt/);
  assert.match(DOWNLOAD_ACTION, /CLI checksum mismatch/);
  assert.match(DOWNLOAD_ACTION, /cli-sha256=/);
  const checksumIndex = DOWNLOAD_ACTION.indexOf('    - name: Verify release checksum before execution');
  const executeIndex = DOWNLOAD_ACTION.indexOf('    - name: Verify CLI');
  const saveIndex = DOWNLOAD_ACTION.indexOf('    - name: Save verified CLI to local cache');
  assert.ok(checksumIndex >= 0 && executeIndex > checksumIndex && saveIndex > executeIndex);
  const cacheReadSection = DOWNLOAD_ACTION.slice(
    DOWNLOAD_ACTION.indexOf('    - name: Check local cache'),
    checksumIndex,
  );
  assert.match(cacheReadSection, /REQUIRE_CHECKSUM: \$\{\{ inputs\.require-checksum \}\}/);
  assert.match(
    cacheReadSection,
    /if \[ "\$REQUIRE_CHECKSUM" != "true" \]; then[\s\S]*CACHED_VERSION=/,
  );
  assert.match(DOWNLOAD_ACTION, /TEMP_CACHE_FILE=/);
  assert.match(DOWNLOAD_ACTION, /mv -f "\$TEMP_CACHE_FILE" "\$CACHE_FILE"/);
});

test('production content is nonce-bound and never dispatches the legacy translation writer', () => {
  const contentIndex = GENERATE_CONTENT.indexOf('      - name: Generate content');
  assert.ok(contentIndex >= 0);
  assert.doesNotMatch(GENERATE_CONTENT, /Dispatch translation after content is complete/);
  assert.doesNotMatch(GENERATE_CONTENT, /event_type:\"translate-packs\"/);
  assert.match(GENERATE_CONTENT, /if \[ -n "\$GENERATION_ID" \]; then/);
  assert.match(GENERATE_CONTENT, /version: '2\.13\.2'/);
  assert.match(GENERATE_CONTENT, /minimum-version: '2\.13\.2'/);
  assert.match(GENERATE_CONTENT, /bindingDigest/);
  assert.match(GENERATE_CONTENT, /usageGuideMarker/);
  assert.match(GENERATE_CONTENT, /github\.event\.client_payload\.contentDispatchNonce/);
  assert.match(GENERATE_CONTENT, /--generation-id \"\$GENERATION_ID\"/);
  assert.match(GENERATE_CONTENT, /--content-dispatch-nonce \"\$CONTENT_DISPATCH_NONCE\"/);
  assert.match(GENERATE_CONTENT, /--execution-binding-digest \"\$BINDING_DIGEST\"/);
  assert.match(GENERATE_CONTENT, /--usage-guide-marker \"\$USAGE_GUIDE_MARKER\"/);
  assert.match(GENERATE_CONTENT, /SKILLSTORE_API_URL: \$\{\{ secrets\.SKILLSTORE_API_URL \}\}/);
  assert.match(GENERATE_CONTENT, /PACK_PRODUCTION_AUTOMATION_KEY: \$\{\{ secrets\.PACK_PRODUCTION_AUTOMATION_KEY \}\}/);
  assert.doesNotMatch(GENERATE_CONTENT, /2\.12\.0|RELEASE BLOCKER/);
  assert.match(GENERATE_CONTENT, /require-checksum: 'true'/);
  assert.match(GENERATE_CONTENT, /name: Mark failed or cancelled production enrichment/);
  assert.match(GENERATE_CONTENT, /\(failure\(\) \|\| cancelled\(\)\).*generationId != ''/);
  assert.match(GENERATE_CONTENT, /--request PATCH/);
  assert.match(GENERATE_CONTENT, /--max-time 15 --retry 0/);
  assert.match(GENERATE_CONTENT, /outcome: "enrichment_failed"/);
  assert.match(GENERATE_CONTENT, /contentDispatchNonce: \$contentDispatchNonce/);
  assert.match(GENERATE_CONTENT, /contentStatus: "failed"/);
  assert.match(GENERATE_CONTENT, /translationStatus: null/);
  assert.match(GENERATE_CONTENT, /\.data\.content_dispatch_nonce/);
  assert.match(GENERATE_CONTENT, /\.data\.content_dispatch_status == "failed"/);
  assert.match(TRANSLATE_PACKS, /github\.event\.client_payload\.cli_version/);
  assert.match(TRANSLATE_PACKS, /require-checksum: \$\{\{ github\.event\.client_payload\.source_generation_id/);
  assert.match(TRANSLATE_PACKS, /SKILLSTORE_AGENT_ENV_MODE: strict/);
});
