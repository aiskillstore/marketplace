import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync, spawnSync} from 'node:child_process';
import {mkdtempSync, writeFileSync, readFileSync, rmSync, symlinkSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {EXPECTED, readPlan, assessSnapshot} from '../bookforge-readonly-diagnostic.mjs';
const skillId='11111111-1111-4111-8111-111111111111';
const artifactId='22222222-2222-4222-8222-222222222222';
const otherId='33333333-3333-4333-8333-333333333333';
function snapshot() {
  const identity={marketplace_commit_sha:EXPECTED.publicationSha,content_hash:EXPECTED.contentHash,tree_hash:EXPECTED.treeHash};
  return {schemaVersion:1,slug:EXPECTED.slug,publicationSha:EXPECTED.publicationSha,
    skills:[{id:skillId,slug:EXPECTED.slug,plugin_path:EXPECTED.root,...identity,current_artifact_version_id:artifactId,artifact_revision:1}],
    publicationArtifacts:[{id:artifactId,skill_id:skillId,source_path:EXPECTED.root,...identity,artifact_revision:1,snapshot_status:'exact'}],
    currentArtifacts:[{id:artifactId,skill_id:skillId,source_path:EXPECTED.root,...identity,artifact_revision:1,snapshot_status:'exact'}],
    observations:[{skill_id:skillId,artifact_version_id:artifactId,marketplace_commit_sha:EXPECTED.publicationSha,source_path:EXPECTED.root,upstream_commit_sha:EXPECTED.sourceRef}]};
}
test('query plan fixes incident and permits only three tables, GET and bounded explicit columns',()=>{
  const p=readPlan();
  assert.equal(p.slug,'gongnyang-bookforge');
  assert.equal(p.publicationSha,'549325ce6f288514ab5da9bf11af95814f848048');
  assert.equal(p.authorizesExecution,false);
  assert.deepEqual([...new Set(p.queries.map(q=>q.table))].sort(),['skill_artifact_observations','skill_artifact_versions','skills']);
  for(const q of p.queries){assert.equal(q.method,'GET');assert.equal(q.limit,2);assert.ok(!q.select.includes('*'));}
  assert.deepEqual(p.queries[0].filters,{slug:EXPECTED.slug});
  assert.equal(p.queries[1].filters.marketplace_commit_sha,EXPECTED.publicationSha);
  assert.equal(p.queries[2].filters.id,'$uniqueSkill.current_artifact_version_id');
  assert.equal(p.queries[3].filters.marketplace_commit_sha,EXPECTED.publicationSha);
  for(const q of p.queries.slice(1))assert.equal(q.filters.skill_id,'$uniqueSkill.id');
});
test('exact snapshot consistency is not production verification or permission to replay',()=>{
  const s=snapshot(), before=JSON.stringify(s); const r=assessSnapshot(s);
  assert.equal(r.classification,'exact-current-snapshot');
  assert.equal(r.productionState,'UNKNOWN'); assert.equal(r.replayAllowed,false);
  assert.equal(r.inputTrust,'unverified-offline-snapshot');
  assert.equal(JSON.stringify(s),before);
});
test('missing and duplicate results never become complete',()=>{
  for(const key of ['skills','publicationArtifacts','currentArtifacts','observations']) {
    for(const rows of [[],[snapshot()[key][0],snapshot()[key][0]]]){
      const s=snapshot();s[key]=rows;
      assert.notEqual(assessSnapshot(s).classification,'exact-current-snapshot');
      assert.equal(assessSnapshot(s).replayAllowed,false);
    }
  }
});
test('current projection, artifact, observation and hashes must all agree',()=>{
  const mutations=[s=>s.skills[0].current_artifact_version_id=otherId,
    s=>s.skills[0].artifact_revision=2,s=>s.skills[0].tree_hash='0'.repeat(64),
    s=>s.skills[0].marketplace_commit_sha='0'.repeat(40),
    s=>s.currentArtifacts[0].id=otherId,s=>s.currentArtifacts[0].artifact_revision=2,
    s=>s.currentArtifacts[0].snapshot_status='legacy_unknown',
    s=>s.publicationArtifacts[0].id=otherId,s=>s.publicationArtifacts[0].content_hash='0'.repeat(64),
    s=>s.observations[0].artifact_version_id=otherId,s=>s.observations[0].upstream_commit_sha='0'.repeat(40)];
  for(const mutate of mutations){const s=snapshot();mutate(s);assert.notEqual(assessSnapshot(s).classification,'exact-current-snapshot');}
});
test('wrong incident, scope, linkage, malformed, oversized or extra fields are rejected without payload echo',()=>{
  const mutations=[s=>s.slug='other',s=>s.publicationSha='0'.repeat(40),s=>s.schemaVersion=2,
    s=>s.skills[0].slug='other',s=>s.skills[0].id='not-uuid',
    s=>s.publicationArtifacts[0].skill_id=otherId,s=>s.currentArtifacts[0].skill_id=otherId,
    s=>s.observations[0].skill_id=otherId,s=>s.observations[0].source_path='skills/other/root',
    s=>s.publicationArtifacts[0].marketplace_commit_sha='0'.repeat(40),
    s=>s.token='SYNTHETIC_SECRET_DO_NOT_ECHO',s=>s.skills[0].private_note='SYNTHETIC_SECRET_DO_NOT_ECHO',
    s=>s.observations=Array(3).fill(s.observations[0]),s=>delete s.currentArtifacts,
    s=>s.skills[0].artifact_revision=-1];
  for(const mutate of mutations){const s=snapshot();mutate(s);assert.throws(()=>assessSnapshot(s),e=>e.message==='Invalid diagnostic snapshot');}
  for(const s of [null,[],{},{...snapshot(),skills:null}])assert.throws(()=>assessSnapshot(s));
});
test('pending or absent artifact pointers remain inconclusive, never zero-write proof',()=>{
  const s=snapshot();s.skills[0].current_artifact_version_id=null;s.skills[0].artifact_revision=0;s.currentArtifacts=[];
  assert.notEqual(assessSnapshot(s).classification,'exact-current-snapshot');
  s.publicationArtifacts=[];s.observations=[];
  assert.equal(assessSnapshot(s).productionState,'UNKNOWN');
  assert.equal(assessSnapshot(s).replayAllowed,false);
});
test('CLI output never echoes secrets, parser errors, file paths or provider payload',()=>{
 const dir=mkdtempSync(join(tmpdir(),'bookforge-readonly-'));
 try{
  const input=join(dir,'snapshot.json'),script='scripts/bookforge-readonly-diagnostic.mjs';
  writeFileSync(input,JSON.stringify(snapshot()));
  const success=spawnSync(process.execPath,[script,'--snapshot',input],{encoding:'utf8',env:{...process.env,SUPABASE_SERVICE_KEY:'SYNTHETIC_SECRET_DO_NOT_ECHO'}});
  assert.equal(success.status,0);assert.equal(JSON.parse(success.stdout).productionState,'UNKNOWN');
  for(const content of ['{"token":"SYNTHETIC_SECRET_DO_NOT_ECHO",',JSON.stringify({...snapshot(),token:'SYNTHETIC_SECRET_DO_NOT_ECHO'}),'SYNTHETIC_SECRET_DO_NOT_ECHO'.repeat(5000)]){
    writeFileSync(input,content);const r=spawnSync(process.execPath,[script,'--snapshot',input],{encoding:'utf8'});
    assert.equal(r.status,1);assert.equal(r.stdout,'');assert.equal(r.stderr,'Read-only diagnostic rejected; no production operation performed.\n');
  }
  const link=join(dir,'link.json');symlinkSync(input,link);
  assert.equal(spawnSync(process.execPath,[script,'--snapshot',link]).status,1);
  assert.equal(spawnSync(process.execPath,[script,'--apply','SYNTHETIC_SECRET_DO_NOT_ECHO']).status,1);
 }finally{rmSync(dir,{recursive:true,force:true});}
});
test('CI runs the diagnostic contract and source-only changes trigger it',()=>{
 const workflow=readFileSync('.github/workflows/validate-marketplace.yml','utf8');
 assert.equal((workflow.match(/- "scripts\/bookforge-readonly-diagnostic\.mjs"/g) ?? []).length,2);
 assert.match(workflow,/scripts\/tests\/bookforge-readonly-diagnostic\.test\.mjs/);
});
test('diagnostic has no network, process execution, environment credentials or mutation dependencies',()=>{
 const source=readFileSync('scripts/bookforge-readonly-diagnostic.mjs','utf8');
 assert.doesNotMatch(source,/node:(?:child_process|http|https|net|tls)|\bfetch\s*\(|process\.env|writeFile|appendFile|unlink|\.rpc\(|\.update\(|\.upsert\(|\.insert\(|SUPABASE_SERVICE|Authorization/);
 const plan=JSON.parse(execFileSync(process.execPath,['scripts/bookforge-readonly-diagnostic.mjs','--plan'],{encoding:'utf8'}));
 assert.equal(plan.authorizesExecution,false);
});
