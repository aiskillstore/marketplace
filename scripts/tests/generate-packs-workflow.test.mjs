import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const workflow = (name) => readFileSync(join(root, '.github/workflows', name), 'utf8');
const generate = workflow('generate-packs.yml');
const admission = workflow('pack-opportunity-admission.yml');
const publish = workflow('publish-pack-production-v4.yml');
const recovery = workflow('recover-cancelled-pack-production.yml');
const cliDownloadAction = readFileSync(join(root, '.github/actions/download-skillstore-cli/action.yml'), 'utf8');
const pinnedActions = {
  checkout: 'fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09',
  upload: 'b7c566a772e6b6bfb58ed0dc250532a479d7789f',
  download: '018cc2cf5baa6db3ef3c5f8a56943fffe632ef53',
  appToken: 'bcd2ba49218906704ab6c1aa796996da409d3eb1',
};

function section(source, start, end) {
  const from = source.indexOf(start);
  assert.notEqual(from, -1, `missing ${start}`);
  const to = end ? source.indexOf(end, from + start.length) : source.length;
  assert.notEqual(to, -1, `missing ${end}`);
  return source.slice(from, to);
}

function assertPinnedSecretActions(source) {
  assert.match(source, new RegExp(`actions/checkout@${pinnedActions.checkout} # v5`));
  assert.match(source, new RegExp(`actions/upload-artifact@${pinnedActions.upload} # v6`));
  assert.doesNotMatch(source, /actions\/(?:checkout|upload-artifact|download-artifact|create-github-app-token)@v[0-9]/);
}

test('admission uses public demand evidence and a checksum-authenticated read-only CLI token', () => {
  assert.match(admission, /permissions:\n  actions: read\n  contents: read/);
  assert.match(admission, /github\.event_name == 'workflow_dispatch' \|\| vars\.PACK_PRODUCTION_AUTOMATION_ENABLED == 'true'/);
  const token = section(admission, '      - name: Create a read-only token', '      - name: Download the fixed public-discovery CLI');
  assert.match(token, new RegExp(`actions/create-github-app-token@${pinnedActions.appToken} # v3`));
  assert.match(token, /repositories: marketplace,skillstore/);
  assert.match(token, /permission-contents: read/);
  const download = section(admission, '      - name: Download the fixed public-discovery CLI', '      - name: Collect and post');
  assert.match(download, /require-checksum: 'true'/);
  assert.match(download, /expected-sha256: \$\{\{ env\.PACK_OPPORTUNITY_ADMISSION_CLI_SHA256 \}\}/);
  assert.match(download, /token: \$\{\{ steps\.cli-token\.outputs\.token \}\}/);
  assert.match(admission, /skill scrape-skills-sh --public-only --view trending --pages 5 --limit 1000 --output json/);
  assert.match(admission, /pack collect-public-demand --skills-sh "\$SNAPSHOT" --source github --output json --diagnostics-file "\$DIAGNOSTICS" > "\$DEMAND"/);
  assert.match(admission, /public-demand-snapshot\.json/);
  assert.match(admission, /Collector requests/);
  assert.match(admission, /Collector response bytes/);
  assert.match(admission, /Collector no-op/);
  assert.match(admission, /--request POST[\s\S]*--data-binary "@\$COMPOSITE"/);
  assert.match(admission, /--skills-sh-snapshot-sha256 "\$SNAPSHOT_SHA256"/);
  assert.match(admission, /--source-created-at "\$SOURCE_CREATED_AT"/);
  assert.match(admission, /pack-opportunity-handoff\.mjs select/);
  assert.match(admission, /name: pack-opportunity-admissions/);
  assert.match(admission, /name: pack-opportunity-admission/);
  assert.match(admission, /group: pack-opportunity-admission\n  cancel-in-progress: false/);
  assert.match(admission, /actions\/artifacts\?name=pack-opportunity-admission&per_page=100/);
  assert.match(admission, /More than 100 admission artifacts fall inside the 24-hour claim window/);
  assert.match(admission, /\.artifacts\[-1\]\.created_at/);
  assert.match(admission, /\.created_at >= \$cutoff/);
  assert.doesNotMatch(admission, /RUN_CUTOFF|actions\/workflows\/pack-opportunity-admission\.yml\/runs\?branch=main/);
  assert.match(admission, /ARTIFACT_ID" =~ \^\[0-9\]\+\$ && "\$RUN_ID" =~ \^\[0-9\]\+\$/);
  assert.match(admission, /actions\/runs\/\$RUN_ID/);
  assert.match(admission, /\.head_repository\.full_name == \$repository/);
  assert.match(admission, /\.path == "\.github\/workflows\/pack-opportunity-admission\.yml"/);
  assert.match(admission, /\.run_attempt \| type == "number" and \. >= 1 and floor == \./);
  assert.match(admission, /\^sha256:\[0-9a-f\]\{64\}\$/);
  assert.match(admission, /sha256:\$\(sha256sum "\$ARCHIVE"/);
  assert.match(admission, /test "\$\(stat -c%s "\$ARCHIVE"\)" -eq "\$ARTIFACT_SIZE"/);
  assert.match(admission, /validate-admission/);
  assert.match(admission, /Existing verified admission claim/);
  assert.equal((admission.match(/retention-days: 90/g) ?? []).length, 2);
  assert.doesNotMatch(admission, /SKILLSTORE_API_URL|SUPABASE|PACK_PRODUCTION_(?:AUTOMATION|MANUAL_PUBLISH|READBACK)_KEY/);
});

test('generation starts only from one successful admission run or an explicit manual source run', () => {
  assert.match(generate, /workflow_run:\n\s+workflows: \['Pack Opportunity Admission'\]\n\s+types: \[completed\]/);
  const trigger = generate.slice(0, generate.indexOf('\npermissions:'));
  assert.match(trigger, /source_run_id:[\s\S]*?required: true/);
  assert.doesNotMatch(trigger, /opportunity_id:|brief_digest:|schedule:/);
  assert.match(generate, /cancel-in-progress: false/);
  const prepare = section(generate, '  prepare:', '  evaluate:');
  assert.match(prepare, /github\.event_name == 'workflow_run'[\s\S]*vars\.PACK_PRODUCTION_AUTOMATION_ENABLED == 'true'[\s\S]*github\.event\.workflow_run\.conclusion == 'success'/);
  assert.match(prepare, /github\.event\.workflow_run\.conclusion == 'success'/);
  assert.match(prepare, /inputs\.smoke_only != true/);
  const smoke = section(generate, '  contract_smoke_only:', '  prepare:');
  assert.match(smoke, /github\.event_name == 'workflow_dispatch' && inputs\.smoke_only == true/);
  assert.match(smoke, /pack-evaluator-contract-smoke\.mjs/);
  assert.doesNotMatch(smoke, /PACK_PRODUCTION_(?:PLANNER|AUTOMATION|MANUAL_PUBLISH|READBACK)_KEY|SUPABASE|APP_PRIVATE_KEY|pack-production\.mjs/);
});

test('prepare authenticates and bounds the exact admission artifact before creating a generation binding', () => {
  const prepare = section(generate, '  prepare:', '  evaluate:');
  assert.match(prepare, /\.workflowName' <<<"\$RUN"\)" = 'Pack Opportunity Admission'/);
  assert.match(prepare, /\.conclusion' <<<"\$RUN"\)" = 'success'/);
  assert.match(prepare, /\.headBranch' <<<"\$RUN"\)" = main/);
  assert.match(prepare, /\.headRepository\.nameWithOwner' <<<"\$RUN"\)" = "\$GITHUB_REPOSITORY"/);
  assert.match(prepare, /test "\$RUN_PATH" = '\.github\/workflows\/pack-opportunity-admission\.yml'/);
  assert.match(prepare, /select\(\.name == "pack-opportunity-admission" and \.expired == false\)/);
  assert.match(prepare, /ARTIFACT_COUNT=\$\(jq 'length' <<<"\$ARTIFACTS"\)/);
  assert.match(prepare, /Admission run is an already-claimed 24-hour cadence no-op/);
  assert.match(prepare, /sha256:\$\(sha256sum "\$ARCHIVE"/);
  assert.match(prepare, /Admission ZIP entry count exceeds 1024/);
  assert.match(prepare, /Admission ZIP uncompressed size exceeds 128 MiB/);
  assert.match(prepare, /Admission ZIP contains an unsafe path/);
  assert.match(prepare, /Admission ZIP contains a symbolic-link entry/);
  assert.match(prepare, /Admission ZIP contains a symbolic link/);
  assert.match(prepare, /single admission required/);
  for (const option of [
    'opportunity-id', 'brief-digest', 'source-run-id', 'source-created-at',
    'admission-head-sha', 'admission-run-attempt', 'source-workflow-path', 'generation-id',
  ]) assert.match(prepare, new RegExp(`--${option}`));
  assert.match(prepare, /opportunityBinding/);
  assert.match(prepare, /retention-days: 90/);
});

test('repeated manual admissions and replays cannot create another generation claim', () => {
  const prepare = section(generate, '  prepare:', '  evaluate:');
  const replayCheck = prepare.indexOf('PLANS=$(gh api');
  const generationId = prepare.indexOf('randomUUID()');
  assert.ok(replayCheck >= 0 && generationId > replayCheck, 'replay check must precede generation id creation');
  assert.match(prepare, /actions\/artifacts\?name=pack-production-plan&per_page=100/);
  assert.match(prepare, /More than 100 generation claims may overlap this admission window/);
  assert.match(prepare, /select\(\.expired == false and \.created_at >= \$sourceCreatedAt\)/);
  assert.match(prepare, /\.workflowName' <<<"\$PLAN_RUN"\)" = 'Generate Pack'/);
  assert.match(prepare, /\.headBranch' <<<"\$PLAN_RUN"\)" = main/);
  assert.match(prepare, /actions\/runs\/\$PLAN_RUN_ID" --jq '\.path'/);
  assert.match(prepare, /validate-plan-claim/);
  assert.match(prepare, /Existing exact generation claim/);
  assert.match(prepare, /echo 'has_scenarios=false'/);
  assert.match(prepare, /Upload immutable plan\n\s+if: steps\.handoff\.outputs\.has_scenarios == 'true'/);
  assert.match(recovery, /download_artifact pack-production-plan/);
  assert.match(recovery, /workflow_run\.conclusion == 'cancelled'/);
});

test('evaluation has only the approved CLI and Helm credentials behind the candidate boundary', () => {
  const evaluate = section(generate, '  evaluate:', '  persist:');
  assert.match(evaluate, /environment:\n\s+name: pack-production-candidate/);
  assert.match(evaluate, /runs-on: ubuntu-24\.04/);
  assert.equal((evaluate.match(/\$\{\{\s*secrets\./g) ?? []).length, 2);
  assert.match(evaluate, /secrets\.APP_PRIVATE_KEY/);
  assert.match(evaluate, /repositories: marketplace,skillstore/);
  assert.match(evaluate, /permission-contents: read/);
  assert.match(evaluate, /require-checksum: 'true'/);
  assert.match(evaluate, /expected-sha256: \$\{\{ env\.PACK_PRODUCTION_CLI_SHA256 \}\}/);
  assert.match(evaluate, /npm install --global --ignore-scripts --prefix \/opt\/pack-evaluator\/runtime/);
  assert.match(evaluate, /secrets\.PACK_EVALUATOR_HELM_API_KEY/);
  assert.doesNotMatch(evaluate, /secrets\.(?:PACK_PRODUCTION_AUTOMATION_KEY|PACK_PRODUCTION_MANUAL_PUBLISH_KEY|PACK_PRODUCTION_READBACK_KEY|SUPABASE|SKILLSTORE_CALLBACK|CACHE_INVALIDATE)/);
  assert.match(evaluate, /sudo -u packproxy env -i/);
  assert.match(evaluate, /sudo -u packeval env -i/);
  assert.match(evaluate, /SKILLSTORE_AGENT_ENV_MODE=strict/);
  assert.match(evaluate, /unset PACK_EVALUATOR_HELM_API_KEY/);
  const runtimeInstall = evaluate.indexOf('Install evaluator runtimes before secrets are available');
  const userSetup = evaluate.indexOf('Prepare disposable evaluator identities and filesystem');
  const sandbox = evaluate.indexOf('Configure and prove scoped bubblewrap user namespaces before secrets');
  const egress = evaluate.indexOf('Restrict and prove evaluator egress before secrets');
  const helm = evaluate.indexOf('PACK_EVALUATOR_HELM_API_KEY: ${{ secrets.PACK_EVALUATOR_HELM_API_KEY }}');
  assert.ok(runtimeInstall >= 0 && userSetup > runtimeInstall && sandbox > userSetup && egress > sandbox && helm > egress);
});

test('evaluation is bounded, uses exact canonical skills, and fails closed', () => {
  const evaluate = section(generate, '  evaluate:', '  persist:');
  assert.match(evaluate, /git -C "\$GITHUB_WORKSPACE\/marketplace-evaluate" archive "\$SOURCE_COMMIT"/);
  assert.match(evaluate, /meta\.content_hash/);
  assert.match(evaluate, /meta\.tree_hash/);
  assert.match(evaluate, /test "\$CANDIDATE_COUNT" -ge 2/);
  assert.match(evaluate, /test "\$CANDIDATE_COUNT" -le 3/);
  assert.match(evaluate, /PACK_EVALUATOR_MAX_REQUESTS=160/);
  assert.match(evaluate, /PACK_EVALUATOR_MAX_TOTAL_OUTPUT_TOKENS=120000/);
  assert.match(evaluate, /PACK_EVALUATOR_MAX_COST_USD=10/);
  assert.match(evaluate, /PACK_EVALUATOR_MAX_CONCURRENT=1/);
  assert.match(evaluate, /timeout --signal=TERM --kill-after=30s 120m/);
  assert.match(evaluate, /prlimit --nproc=256:256 --as=6442450944:6442450944/);
  assert.match(evaluate, /EVALUATOR_RC=\$\?/);
  assert.match(evaluate, /exit "\$EVALUATOR_RC"/);
});

test('pre-publication runtime acceptance executes one staged result as the isolated evaluator user', () => {
  const evaluate = section(generate, '  evaluate:', '  persist:');
  assert.match(evaluate, /mapfile -t EVALUATION_FILES < <\(find/);
  assert.match(evaluate, /test "\$\{#EVALUATION_FILES\[@\]\}" -eq 1/);
  assert.match(evaluate, /sudo -u packeval env -i[\s\S]*pack-runtime-stage\.mjs/);
  assert.match(evaluate, /sudo -u packeval env -i[\s\S]*skillstore-cli pack runtime-accept/);
  assert.match(evaluate, /--identity-file "\$RUNTIME_ROOT\/identities\.json"/);
  assert.match(evaluate, /runtime-acceptance\.json/);
  assert.match(generate, /PACK_PRODUCTION_CLI_VERSION: '__SET_AFTER_PACK_RUNTIME_ACCEPT_CLI_RELEASE__'/);
  assert.match(generate, /PACK_PRODUCTION_CLI_SHA256: '__SET_AFTER_PACK_RUNTIME_ACCEPT_CLI_RELEASE_SHA256__'/);
});

test('evaluation checkpoints cancellation evidence and never uploads raw run logs', () => {
  const evaluate = section(generate, '  evaluate:', '  persist:');
  assert.match(evaluate, /checkpoint_loop\(\)/);
  assert.match(evaluate, /flock -x 9/);
  assert.match(evaluate, /evaluate-checkpoint\.json/);
  assert.match(evaluate, /evaluator-interrupted\.txt/);
  assert.match(evaluate, /trap 'terminate_step 143' TERM/);
  assert.match(evaluate, /sudo kill -TERM -- "-\$EVALUATOR_PID"/);
  assert.match(evaluate, /RESULT_BYTES=.*du -sb \/opt\/pack-evaluator\/results/);
  assert.match(evaluate, /RESULT_FILES=.*find \/opt\/pack-evaluator\/results -type f/);
  assert.match(evaluate, /rm -f "\$run_log"/);
  assert.match(evaluate, /proxy-activity\.jsonl/);
  assert.match(evaluate, /evaluation-budget\.json/);
  assert.match(evaluate, /Raw evaluator run logs survived bounded summarization/);
  assert.match(evaluate, /name: Upload trusted evaluation evidence\n\s+if: success\(\)/);
  assert.match(evaluate, /name: Upload bounded evaluation diagnostics\n\s+if: always\(\)/);
  assert.doesNotMatch(evaluate, /path:[^\n]*\.run\.log/);
});

test('only trusted writer jobs persist and automatic publication stays disabled', () => {
  const persist = section(generate, '  persist:', '  enrich_publish_readback:');
  const finalize = section(generate, '  enrich_publish_readback:');
  assert.match(persist, /needs: \[prepare, evaluate\]/);
  assert.match(persist, /needs\.evaluate\.result == 'success'/);
  assert.match(persist, /environment:\n\s+name: pack-production-writer/);
  assert.match(persist, /PACK_PRODUCTION_AUTOMATION_KEY: \$\{\{ secrets\.PACK_PRODUCTION_AUTOMATION_KEY \}\}/);
  assert.match(finalize, /needs: \[prepare, persist\]/);
  assert.match(finalize, /needs\.persist\.result == 'success'/);
  assert.match(finalize, /environment:\n\s+name: pack-production-writer/);
  assert.match(finalize, /AUTO_PUBLISH: 'false'/);
  assert.match(finalize, /--auto-publish "\$AUTO_PUBLISH"/);
  assert.doesNotMatch(generate, /PACK_PRODUCTION_MANUAL_PUBLISH_KEY|PACK_PRODUCTION_READBACK_KEY/);
  assert.equal((generate.match(/retention-days: 90/g) ?? []).length, 5);
});

test('manual publication authenticates and bounds one final generation artifact', () => {
  const prepare = section(publish, '  prepare:', '  publish:');
  const publishJob = section(publish, '  publish:', '  runtime:');
  assert.match(publish, /workflow_dispatch:\n\s+inputs:\n\s+source_run_id:/);
  const inputs = publish.slice(publish.indexOf('    inputs:'), publish.indexOf('\npermissions:'));
  assert.doesNotMatch(inputs, /generation_id:|pack_slug:|binding_digest:|nonce:/);
  assert.match(prepare, /PACK_PRODUCTION_AUTO_PUBLISH_ENABLED/);
  assert.match(prepare, /source_run_id must be a GitHub Actions run id/);
  assert.match(prepare, /expected one exact pack-production-final artifact/);
  assert.match(prepare, /select\(\.expired == false\)/);
  assert.match(prepare, /artifact digest mismatch/);
  assert.match(prepare, /compressed size is invalid or exceeds 32 MiB/);
  assert.match(prepare, /entry count exceeds 1024/);
  assert.match(prepare, /uncompressed size exceeds 128 MiB/);
  assert.match(prepare, /contains an unsafe ZIP path/);
  assert.match(prepare, /contains a symbolic link/);
  assert.match(prepare, /--source-run-file[\s\S]*--workflow-file[\s\S]*--artifact-file/);
  assert.match(prepare, /Quality override: \*\*forbidden\*\*/);
  const cliPreflight = section(
    publishJob,
    '      - name: Preflight the exact public Marketplace CLI release',
    '      - name: Download the reviewed immutable approval handoff',
  );
  assert.match(cliPreflight, /MARKETPLACE_CLI_VERSION: '__SET_AFTER_MARKETPLACE_CLI_RELEASE__'/);
  assert.match(cliPreflight, /must be an exact non-placeholder semver release/);
  assert.match(cliPreflight, /npm view --registry=https:\/\/registry\.npmjs\.org "skillstore@\$MARKETPLACE_CLI_VERSION" --json/);
  assert.match(cliPreflight, /\.dist\.integrity[\s\S]*sha512-/);
  assert.ok(
    publishJob.indexOf('Preflight the exact public Marketplace CLI release')
      < publishJob.indexOf('Publish through the nonce-bound manual API'),
    'the release placeholder must fail before the production publish POST',
  );
});

test('published Pack runtime uses the exact installed CLI and installed identities without write credentials', () => {
  const runtime = section(publish, '  runtime:', '  complete:');
  assert.match(runtime, /needs: \[prepare, publish\]/);
  assert.match(runtime, /environment:\n\s+name: pack-production-runtime/);
  assert.match(runtime, new RegExp(`actions/create-github-app-token@${pinnedActions.appToken} # v3`));
  assert.match(runtime, /repositories: marketplace,skillstore/);
  assert.match(runtime, /permission-contents: read/);
  assert.match(runtime, /require-checksum: 'true'/);
  assert.match(runtime, /expected-sha256: \$\{\{ needs\.prepare\.outputs\.cli_sha256 \}\}/);
  assert.match(runtime, /steps\.evaluation-cli\.outputs\.cli-sha256[\s\S]*\.runtimeCli\.sha256/);
  assert.match(runtime, /MARKETPLACE_CLI_VERSION: \$\{\{ needs\.publish\.outputs\.marketplace_cli_version \}\}/);
  assert.match(runtime, /MARKETPLACE_CLI_INTEGRITY: \$\{\{ needs\.publish\.outputs\.marketplace_cli_integrity \}\}/);
  assert.match(runtime, /npm install --ignore-scripts --save-exact "skillstore@\$MARKETPLACE_CLI_VERSION"/);
  assert.match(runtime, /package-lock\.json[\s\S]*MARKETPLACE_CLI_INTEGRITY/);
  assert.match(runtime, /npm audit signatures --json/);
  assert.match(runtime, /skillstore add "@\$PACK_SLUG" --agent codex --overwrite/);
  assert.match(runtime, /install-readback[\s\S]*installed-runtime-identities/);
  assert.match(runtime, /--identity-file "\$PACK_RUNTIME_EVIDENCE\/installed-identities\.json"/);
  assert.match(runtime, /runtime-acceptance-installed\.json/);
  assert.match(runtime, /runtime-readback/);
  assert.match(runtime, /if env \| grep -Eq 'PACK_PRODUCTION_MANUAL_PUBLISH_KEY\|PACK_PRODUCTION_AUTOMATION_KEY\|SUPABASE_SERVICE\|SKILLSTORE_CALLBACK\|CACHE_INVALIDATE'/);
  assert.doesNotMatch(runtime, /secrets\.(?:PACK_PRODUCTION_MANUAL_PUBLISH_KEY|PACK_PRODUCTION_AUTOMATION_KEY|PACK_PRODUCTION_READBACK_KEY|SKILLSTORE_API_URL|SUPABASE)/);
  const install = runtime.indexOf('Install the exact registry-authenticated CLI and published Pack before inference credentials');
  const egress = runtime.indexOf('Prove bubblewrap and restrict evaluator egress before the Helm key exists');
  const helm = runtime.indexOf('PACK_EVALUATOR_HELM_API_KEY: ${{ secrets.PACK_EVALUATOR_HELM_API_KEY }}');
  assert.ok(install >= 0 && egress > install && helm > egress);
});

test('production success requires public, install, and installed-runtime readback; failures stay failed', () => {
  const complete = section(publish, '  complete:');
  assert.match(complete, /needs: \[prepare, publish, runtime\]/);
  assert.doesNotMatch(complete, /environment:\n\s+name: pack-production-readback/);
  const succeeded = section(complete, '      - name: Record exact production acceptance', '      - name: Record terminal publish');
  for (const proof of [
    "needs.publish.result == 'success'", "needs.runtime.result == 'success'",
    "steps.public-proof.outcome == 'success'", "steps.runtime-proof.outcome == 'success'",
  ]) assert.ok(succeeded.includes(proof));
  assert.match(succeeded, /--status succeeded/);
  assert.match(succeeded, /--public-readback[\s\S]*--install-readback[\s\S]*--runtime-readback/);
  const failed = section(complete, '      - name: Record terminal publish', '      - name: Upload completed production evidence');
  assert.match(failed, /always\(\)/);
  assert.match(failed, /needs\.publish\.result != 'success'/);
  assert.match(failed, /needs\.runtime\.result != 'success'/);
  assert.match(failed, /steps\.public-proof\.outcome != 'success'/);
  assert.match(failed, /steps\.runtime-proof\.outcome != 'success'/);
  assert.match(failed, /--status failed/);
  assert.doesNotMatch(failed, /--status succeeded|--runtime-readback/);
});

test('cancelled generation recovery is exact, candidate-null only, and secret-minimal', () => {
  assert.match(recovery, /workflow_run:[\s\S]*workflows: \[Generate Pack\][\s\S]*types: \[completed\][\s\S]*branches: \[main\]/);
  assert.match(recovery, /workflow_run\.conclusion == 'cancelled'/);
  assert.match(recovery, /workflow_run\.event == 'workflow_run'.*workflow_run\.event == 'workflow_dispatch'/s);
  assert.match(recovery, /environment:\n\s+name: pack-production-writer/);
  assert.match(recovery, /actions\/runs\/\$RUN_ID\/attempts\/\$RUN_ATTEMPT/);
  assert.match(recovery, /compare\/\$SOURCE_SHA\.\.\.\$GITHUB_SHA/);
  assert.match(recovery, /generate-packs\.yml\?ref=\$SOURCE_SHA/);
  assert.match(recovery, /artifacts\?per_page=100/);
  assert.match(recovery, /actions\/artifacts\/\$artifact_id\/zip/);
  assert.match(recovery, /actual_digest=.*sha256sum/);
  assert.match(recovery, /test "\$actual_digest" = "\$expected_digest"/);
  assert.match(recovery, /ZIP contains an unsafe path/);
  assert.match(recovery, /if: steps\.prepare\.outputs\.outcome == 'candidate_null_prepared'/);
  assert.match(recovery, /PACK_PRODUCTION_AUTOMATION_KEY: \$\{\{ secrets\.PACK_PRODUCTION_AUTOMATION_KEY \}\}/);
  assert.doesNotMatch(recovery, /PACK_EVALUATOR_HELM_API_KEY|PACK_PRODUCTION_MANUAL_PUBLISH_KEY|PACK_PRODUCTION_READBACK_KEY|SUPABASE_SERVICE_ROLE|APP_PRIVATE_KEY/);
  const writeToken = recovery.indexOf('PACK_PRODUCTION_AUTOMATION_KEY:');
  assert.ok(writeToken > recovery.indexOf('Persist the exact candidate-null cancellation audit'));
  assert.match(recovery, /Never re-upload source evaluator stdout, stderr, run logs, or raw/);
  assert.match(recovery, /retention-days: 90/);
});

test('all workflow checkouts drop persisted Git credentials', () => {
  for (const [name, source] of Object.entries({ admission, generate, publish, recovery })) {
    const checkouts = (source.match(/uses: actions\/checkout@(?:v5|fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09)/g) ?? []).length;
    const disabled = (source.match(/persist-credentials: false/g) ?? []).length;
    assert.ok(checkouts > 0, `${name} has no checkout`);
    assert.equal(disabled, checkouts, `${name} checkout credential isolation drifted`);
  }
});

test('pack production pins executable Actions and requires an independent CLI digest contract', () => {
  for (const source of [admission, generate, publish, recovery]) assertPinnedSecretActions(source);
  assert.match(cliDownloadAction, /expected-sha256:/);
  assert.match(
    cliDownloadAction,
    /- name: Verify release checksum before execution[\s\S]*?env:[\s\S]*?EXPECTED_SHA256: \$\{\{ inputs\.expected-sha256 \}\}[\s\S]*?run:/,
  );
  assert.match(cliDownloadAction, /independently recorded expected digest/);
  assert.match(cliDownloadAction, /actions\/cache@0057852bfaa89a56745cba8c7296529d2fc39830/);
  const localCache = cliDownloadAction.slice(
    cliDownloadAction.indexOf('    - name: Check local cache'),
    cliDownloadAction.indexOf('    - name: Cache CLI'),
  );
  assert.match(
    localCache,
    /if \[ "\$REQUIRE_CHECKSUM" != "true" \]; then[\s\S]*CACHED_VERSION=[\s\S]*rm -f "\$CACHE_FILE" "\$GITHUB_WORKSPACE\/skillstore-cli"/,
  );
  assert.match(localCache, /Checksum-required callers do not[\s\S]*execute these bytes until the checksum gate below succeeds/);
});
