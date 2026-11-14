import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
const workflow=readFileSync('.github/workflows/sync-to-supabase.yml','utf8');
const step=workflow.split('      - name: Sync skills to Supabase')[1].split('      - name:')[0];
const script=step.split('        run: |\n')[1].split('\n          # One bounded attempt')[0].split('\n').map(l=>l.replace(/^          /,'')).join('\n');
function run(t,overrides={}) {
  const cwd=mkdtempSync(join(process.cwd(),'.provider-mode-test-'));
  t.after(()=>rmSync(cwd,{recursive:true,force:true}));
  return spawnSync('bash',['-e','-c',`timeout(){ printf 'CLI_ARG:%s\\n' "$@"; }; tee(){ cat; };\n${script}\nrun_sync_once skills/owner/demo 1 ignored.log`],{cwd,encoding:'utf8',env:{PATH:process.env.PATH,CI:'true',GITHUB_WORKSPACE:cwd,GITHUB_OUTPUT:join(cwd,'output'),PROVIDER_COMPLETE:'false',PROVIDER_MODE:'',RESUME_FAILED_RUN:'',VERIFIED_RECOVERY_SLUGS:'owner-demo',CHANGED_SKILLS:'owner/demo',SYNC_COMMIT_SHA:'a'.repeat(40),SYNC_MODE:'manual-slugs',...overrides}});
}
test('normal push/manual sync does not request current-artifact resume',t=>{
 const r=run(t);assert.equal(r.status,0,r.stderr);assert.match(r.stdout,/CLI_ARG:skill/);assert.doesNotMatch(r.stdout,/CLI_ARG:--resume-current/);
});
test('verified never-started provider uses initial sync without --resume-current',t=>{
 assert.match(step,/PROVIDER_MODE: \$\{\{ steps\.trusted-correlation\.outputs\.provider_mode \}\}/);
 const r=run(t,{RESUME_FAILED_RUN:'1',PROVIDER_MODE:'initial-sync'});assert.equal(r.status,0,r.stderr);assert.match(r.stdout,/CLI_ARG:skill/);assert.doesNotMatch(r.stdout,/CLI_ARG:--resume-current/);
});
test('ordinary failed-provider recovery retains --resume-current',t=>{
 const r=run(t,{RESUME_FAILED_RUN:'1',PROVIDER_MODE:'resume-current'});assert.equal(r.status,0,r.stderr);assert.match(r.stdout,/CLI_ARG:--resume-current/);
});
test('provider-complete recovery exits without invoking CLI',t=>{
 const r=run(t,{RESUME_FAILED_RUN:'1',PROVIDER_COMPLETE:'true',PROVIDER_MODE:'ancillary-only'});assert.equal(r.status,0,r.stderr);assert.doesNotMatch(r.stdout,/CLI_ARG:/);
});
test('missing, unknown and contradictory recovery modes stop before CLI',t=>{
 for(const env of [{RESUME_FAILED_RUN:'1'},{RESUME_FAILED_RUN:'1',PROVIDER_MODE:'typo'},{RESUME_FAILED_RUN:'1',PROVIDER_MODE:'ancillary-only'},{PROVIDER_MODE:'initial-sync'}]){
  const r=run(t,env);assert.notEqual(r.status,0);assert.doesNotMatch(r.stdout,/CLI_ARG:/);
 }
});
