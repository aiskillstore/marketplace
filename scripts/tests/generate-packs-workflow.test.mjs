import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(TEST_DIR, '..', '..');
const WORKFLOW = readFileSync(join(REPO_ROOT, '.github/workflows/generate-packs.yml'), 'utf8');
const DOWNLOAD_ACTION = readFileSync(join(REPO_ROOT, '.github/actions/download-skillstore-cli/action.yml'), 'utf8');
const EVALUATOR_PROXY = readFileSync(join(REPO_ROOT, 'scripts/pack-evaluator-proxy.mjs'), 'utf8');
const GENERATE_CONTENT = readFileSync(join(REPO_ROOT, '.github/workflows/generate-content.yml'), 'utf8');
const TRANSLATE_PACKS = readFileSync(join(REPO_ROOT, '.github/workflows/translate-packs.yml'), 'utf8');

function section(start, end) {
  const startIndex = WORKFLOW.indexOf(start);
  assert.notEqual(startIndex, -1, `missing workflow section ${start}`);
  const endIndex = end ? WORKFLOW.indexOf(end, startIndex + start.length) : WORKFLOW.length;
  assert.notEqual(endIndex, -1, `missing workflow boundary ${end}`);
  return WORKFLOW.slice(startIndex, endIndex);
}

test('workflow has separate Plan, secret-free Evaluate, Persist, production Readback, and terminal SLO jobs', () => {
  assert.match(WORKFLOW, /  plan:/);
  assert.match(WORKFLOW, /  evaluate:/);
  assert.match(WORKFLOW, /  persist:/);
  assert.match(WORKFLOW, /  enrich_publish_readback:/);
  assert.match(WORKFLOW, /  production_slo:/);
  assert.match(WORKFLOW, /permissions:\n  contents: read/);
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
  const evaluate = section('  evaluate:', '  persist:');
  assert.match(evaluate, /runs-on: ubuntu-latest/);
  assert.match(evaluate, /@anthropic-ai\/claude-code@2\.1\.210/);
  assert.match(evaluate, /@openai\/codex@0\.139\.0/);
  assert.match(evaluate, /apt-get install --yes --no-install-recommends ffmpeg poppler-utils ripgrep/);
  assert.match(evaluate, /command -v ffprobe/);
  assert.match(evaluate, /command -v pdfinfo/);
  assert.match(evaluate, /command -v pdftotext/);
  assert.match(evaluate, /command -v rg/);
  assert.match(evaluate, /useradd .*packproxy/);
  assert.match(evaluate, /useradd .*packeval/);
  assert.match(evaluate, /\/opt\/pack-evaluator\/bin\/node/);
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
  assert.match(evaluate, /! test -w \/opt\/pack-evaluator\/codex-home\/config\.toml/);
  assert.match(evaluate, /PATH=\/opt\/pack-evaluator\/runtime\/bin:\/opt\/pack-evaluator\/bin:\/usr\/bin:\/bin/);
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
  assert.match(evaluate, /PACK_EVALUATOR_MAX_OUTPUT_TOKENS=65536/);
  assert.match(evaluate, /Pack evaluator proxy did not become healthy within 30 seconds/);
  assert.match(evaluate, /proxy-diagnostics\.json/);
  assert.doesNotMatch(evaluate, /sed -E .*Bearer|proxy\.log|proxy-failure\.log/);
  assert.match(evaluate, /evaluator-failure\.txt/);
  assert.match(evaluate, /pkill -TERM -u packeval/);
  assert.match(evaluate, /pkill -KILL -u packeval/);
  assert.match(evaluate, /EVALUATOR_PROCESSES_STOPPED=true/);
  assert.match(evaluate, /process-termination-failure\.txt/);
  assert.match(evaluate, /RESULT_BYTES=.*du -sb \/opt\/pack-evaluator\/results/);
  assert.match(evaluate, /RESULT_FILES=.*find \/opt\/pack-evaluator\/results -type f/);
  assert.match(evaluate, /find \/opt\/pack-evaluator\/results ! -type f ! -type d/);
  assert.match(evaluate, /cp -a \/opt\/pack-evaluator\/results\/\./);
  assert.match(evaluate, /find "\$GITHUB_WORKSPACE\/pack-harvest" -type d -exec chmod 0700/);
  assert.match(evaluate, /find "\$GITHUB_WORKSPACE\/pack-harvest" -type f -exec chmod 0600/);
  assert.match(evaluate, /find "\$GITHUB_WORKSPACE\/pack-harvest" ! -type f ! -type d/);
  const preflightIndex = evaluate.indexOf('if ! sudo -u packeval env -i');
  const relaxedErrorIndex = evaluate.indexOf('set +e', preflightIndex);
  const evaluatorIndex = evaluate.indexOf('sudo env -i', relaxedErrorIndex);
  assert.ok(preflightIndex >= 0);
  assert.ok(relaxedErrorIndex > preflightIndex);
  assert.ok(evaluatorIndex > relaxedErrorIndex);
  assert.match(evaluate, /pack-production\.mjs verify/);
  assert.match(evaluate, /trusted evaluation closure verification failed/);
  assert.match(evaluate, /timeout --signal=TERM --kill-after=30s 4h/);
  assert.match(evaluate, /prlimit --nproc=256:256 --as=6442450944:6442450944/);
  assert.match(EVALUATOR_PROXY, /evaluator proxy request budget exhausted/);
  assert.match(EVALUATOR_PROXY, /evaluator proxy token has expired/);
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
  assert.match(evaluate, /--evaluation-budget-ms 13800000/);
  assert.match(evaluate, /--scenario-timeout-ms 7200000/);
  assert.match(evaluate, /--minimum-fallback-ms 2700000/);
  assert.match(evaluate, /name: Upload trusted evaluation evidence\n\s+if: success\(\)/);
  assert.match(evaluate, /name: Upload bounded evaluation diagnostics\n\s+if: always\(\)/);
  assert.match(evaluate, /name: pack-production-diagnostics/);
  assert.match(evaluate, /if-no-files-found: warn/);
  assert.match(evaluate, /path: pack-trusted\//);
  assert.match(evaluate, /path: pack-diagnostics\//);
  assert.doesNotMatch(evaluate, /path: pack-harvest\//);
  assert.doesNotMatch(evaluate, /pack-diagnostics\/.*stdout\.(?:partial|json)/);
  const checkpointIndex = evaluate.indexOf('checkpoint_loop &');
  const evaluatorIndex = evaluate.indexOf('"$NODE_BIN" /opt/pack-evaluator/lib/pack-production.mjs evaluate', checkpointIndex);
  const finishIndex = evaluate.indexOf('EVALUATOR_FINISHED=true', evaluatorIndex);
  assert.ok(checkpointIndex >= 0 && evaluatorIndex > checkpointIndex && finishIndex > evaluatorIndex);
});

test('planning is bounded to three artifact scenarios and CLI release is immutable', () => {
  const plan = section('  plan:', '  evaluate:');
  assert.match(plan, /scenario-queue --limit 3/);
  assert.match(plan, /requiredArtifacts \| length >= 1/);
  assert.match(plan, /\(\.scenarios \| length\) > 0 or \.source == "signals"/);
  assert.match(plan, /marketplace\.pack-production-noop\/v1/);
  assert.match(plan, /repository: "aiskillstore\/marketplace"/);
  assert.match(plan, /runId: \$runId/);
  assert.match(plan, /commitSha: \$commitSha/);
  assert.match(plan, /has_scenarios=false/);
  const evaluate = section('  evaluate:', '  persist:');
  const persist = section('  persist:', '  enrich_publish_readback:');
  const finalize = section('  enrich_publish_readback:', '  production_slo:');
  assert.match(evaluate, /if: needs\.plan\.outputs\.has_scenarios == 'true'/);
  assert.match(persist, /if: needs\.plan\.outputs\.has_scenarios == 'true'/);
  assert.match(finalize, /if: needs\.plan\.outputs\.has_scenarios == 'true'/);
  assert.match(WORKFLOW, /group: generate-pack-production-v3/);
  assert.match(WORKFLOW, /PACK_PRODUCTION_CLI_VERSION: '2\.10\.0'/);
  assert.equal((WORKFLOW.match(/require-checksum: 'true'/g) ?? []).length, 1);
  assert.match(plan, /actions\/create-github-app-token@v3/);
  assert.match(plan, /repositories: marketplace,skillstore/);
  assert.match(plan, /name: pack-production-cli/);
  assert.match(plan, /retention-days: 1/);
  assert.doesNotMatch(WORKFLOW, /version: latest|cli_version:/);
});

test('trusted phases use the Automation API and retain full evidence for 90 days', () => {
  const persist = section('  persist:', '  enrich_publish_readback:');
  const finalize = section('  enrich_publish_readback:', '  production_slo:');
  assert.match(persist, /pack-production\.mjs persist/);
  assert.match(persist, /PACK_PRODUCTION_AUTOMATION_KEY: \$\{\{ secrets\.PACK_PRODUCTION_AUTOMATION_KEY \}\}/);
  assert.match(finalize, /pack-production\.mjs finalize/);
  assert.match(finalize, /final-result\.json/);
  assert.match(finalize, /pack-production\.mjs finalize/);
  assert.equal((WORKFLOW.match(/retention-days: 90/g) ?? []).length, 6);
  assert.match(finalize, /PACK_PRODUCTION_AUTO_PUBLISH_ENABLED == 'true'/);
  assert.match(WORKFLOW, /auto_publish:[\s\S]*?default: false/);
});

test('terminal SLO job runs after every outcome and fails below two published readbacks', () => {
  const slo = section('  production_slo:');
  assert.match(slo, /needs: \[plan, evaluate, persist, enrich_publish_readback\]/);
  assert.match(slo, /if: always\(\)/);
  assert.match(slo, /pack-production\.mjs slo/);
  assert.match(slo, /Published \+ readback passed/);
  assert.match(slo, /::error::Rolling 7-day Pack production SLO is below target/);
  assert.match(slo, /exit 1/);
  assert.doesNotMatch(slo, /::warning::Rolling 7-day Pack production SLO is below target/);
  assert.match(slo, /pack-plan\/no-op\.json/);
});

test('checkouts use isolated directories and never persist tokens', () => {
  assert.match(WORKFLOW, /marketplace-plan/);
  assert.match(WORKFLOW, /marketplace-evaluate/);
  assert.ok((WORKFLOW.match(/filter: ''/g) ?? []).length >= 1);
  assert.ok((WORKFLOW.match(/persist-credentials: false/g) ?? []).length >= 4);
  const persist = section('  persist:', '  enrich_publish_readback:');
  const finalize = section('  enrich_publish_readback:', '  production_slo:');
  const slo = section('  production_slo:');
  assert.match(persist, /sparse-checkout: scripts\/pack-production\.mjs\n\s+sparse-checkout-cone-mode: false/);
  assert.match(finalize, /sparse-checkout: scripts\/pack-production\.mjs\n\s+sparse-checkout-cone-mode: false/);
  assert.match(slo, /sparse-checkout: scripts\/pack-production\.mjs\n\s+sparse-checkout-cone-mode: false/);
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

test('translation is dispatched only after generated content succeeds', () => {
  const contentIndex = GENERATE_CONTENT.indexOf('      - name: Generate content');
  const translateIndex = GENERATE_CONTENT.indexOf('      - name: Dispatch translation after content is complete');
  assert.ok(contentIndex >= 0 && translateIndex > contentIndex);
  assert.match(GENERATE_CONTENT, /if: github\.event\.client_payload\.generationId != ''/);
  assert.match(GENERATE_CONTENT, /source_generation_id/);
  assert.match(GENERATE_CONTENT, /cli_version:\"2\.9\.0\"/);
  assert.match(GENERATE_CONTENT, /version: '2\.9\.0'/);
  assert.match(GENERATE_CONTENT, /minimum-version: '2\.9\.0'/);
  assert.match(GENERATE_CONTENT, /require-checksum: 'true'/);
  assert.match(TRANSLATE_PACKS, /github\.event\.client_payload\.cli_version/);
  assert.match(TRANSLATE_PACKS, /require-checksum: \$\{\{ github\.event\.client_payload\.source_generation_id/);
  assert.match(TRANSLATE_PACKS, /SKILLSTORE_AGENT_ENV_MODE: strict/);
});
