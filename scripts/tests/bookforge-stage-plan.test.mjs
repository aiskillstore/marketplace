import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {EXPECTED, readPlan} from '../bookforge-readonly-diagnostic.mjs';
import {stageReadPlan, bindExpectedCurrent, compareExpectedCurrent} from '../bookforge-stage-plan.mjs';
const skill='11111111-1111-4111-8111-111111111111';
const artifact='22222222-2222-4222-8222-222222222222';
const other='33333333-3333-4333-8333-333333333333';
function snapshot() {
  const identity={marketplace_commit_sha:EXPECTED.publicationSha,content_hash:EXPECTED.contentHash,tree_hash:EXPECTED.treeHash};
  const row={id:artifact,skill_id:skill,source_path:EXPECTED.root,...identity,artifact_revision:1,snapshot_status:'exact'};
  return {schemaVersion:1,slug:EXPECTED.slug,publicationSha:EXPECTED.publicationSha,
    skills:[{id:skill,slug:EXPECTED.slug,plugin_path:EXPECTED.root,...identity,current_artifact_version_id:artifact,artifact_revision:1}],
    publicationArtifacts:[{...row}],currentArtifacts:[{...row}],
    observations:[{skill_id:skill,artifact_version_id:artifact,marketplace_commit_sha:EXPECTED.publicationSha,source_path:EXPECTED.root,upstream_commit_sha:EXPECTED.sourceRef}]};
}
test('stage plan is a separate proposal, not expansion of the approved three-table diagnostic',()=>{
  assert.equal(new Set(readPlan().queries.map(q=>q.table)).size,3);
  const p=stageReadPlan();
  assert.equal(p.slug,EXPECTED.slug);assert.equal(p.publicationSha,EXPECTED.publicationSha);
  assert.equal(p.authorizesExecution,false);assert.equal(p.productionState,'UNKNOWN');
  assert.equal(p.replayAllowed,false);assert.equal(p.continuationAllowed,false);
  assert.equal(p.readScopeApproved,false);assert.equal(p.executorImplemented,false);
  assert.deepEqual(p.stages.map(s=>s.name),['catalog','ai-content','audit','durable-event','eligibility-attestation','callback','score','cache']);
  for(const s of p.stages){assert.equal(s.state,'UNKNOWN');assert.ok(s.proofRequirements.length>0);}
});
test('every query has bounded safe columns and dependent object filters; no credentials, risk conclusions or user data',()=>{
  const p=stageReadPlan();
  for(const q of p.queries){
    assert.equal(q.method,'GET');assert.equal(q.schema,'skillstore');assert.equal(q.limit,2);
    assert.ok(q.select.length>0);assert.ok(!q.select.includes('*'));
    assert.ok(Object.keys(q.filters).length>0);
    assert.doesNotMatch(q.select.join(','),/email|user_id|risk_level|risk_factors|safe_to_publish|is_blocked|summary|findings|signature|payload$/);
  }
  const queries=Object.fromEntries(p.queries.map(q=>[q.name,q]));
  for(const name of ['catalog','eligibility','score']) assert.equal(queries[name].filters.id,'$expectedCurrent.skillId');
  for(const name of ['aiContent','audit','projectionJob','projectionEvent'])assert.equal(queries[name].filters.skill_id,'$expectedCurrent.skillId');
  assert.equal(queries.projectionJob.filters.source_id,'$verifiedAudit.id');
  assert.equal(queries.projectionEvent.filters.id,'$verifiedProjectionJob.projected_event_id');
  assert.equal(queries.attestation.filters.audit_id,'$verifiedAudit.id');
  assert.equal(queries.submission.filters.id,p.submissionId);
  assert.equal(queries.notification.filters.submission_id,p.submissionId);
  assert.equal(queries.notification.filters.event,'published');
  assert.deepEqual(queries.audit.order,['version.desc','created_at.desc','id.desc']);
});
test('metadata proposal uses actual immutable audit and durable event schema, without invented binding columns',()=>{
  const queries=Object.fromEntries(stageReadPlan().queries.map(q=>[q.name,q]));
  for(const field of ['subject_marketplace_commit_sha','subject_content_hash','subject_tree_hash','subject_plugin_path','audit_payload_hash']) assert.ok(queries.audit.select.includes(field));
  assert.ok(queries.aiContent.select.includes('content_hash'));
  assert.ok(queries.projectionEvent.select.includes('idempotency_key'));
  assert.ok(!queries.projectionEvent.select.includes('event_key'));
  assert.ok(!queries.audit.select.some(c=>c.startsWith('binding_')));
});
test('expected identity binds only exact complete incident snapshot; input is not mutated',()=>{
  const s=snapshot(),before=JSON.stringify(s),id=bindExpectedCurrent(s);
  assert.equal(id.skillId,skill);assert.equal(id.artifactVersionId,artifact);assert.equal(id.artifactRevision,1);
  assert.equal(id.sourceRef,EXPECTED.sourceRef);assert.equal(id.contentHash,EXPECTED.contentHash);
  assert.equal(JSON.stringify(s),before);
  for(const collection of ['skills','publicationArtifacts','currentArtifacts','observations']){
    for(const rows of [[],[s[collection][0],s[collection][0]]]){
      const value=snapshot();value[collection]=rows;assert.throws(()=>bindExpectedCurrent(value),/Invalid stage plan input/);
    }
  }
});
test('offline matching is not database CAS, provider verification, a successful stage or permission to write',()=>{
  const r=compareExpectedCurrent(bindExpectedCurrent(snapshot()),snapshot());
  assert.equal(r.identityMatches,true);assert.equal(r.atomicCasPerformed,false);
  assert.equal(r.productionState,'UNKNOWN');assert.equal(r.replayAllowed,false);
  assert.equal(r.continuationAllowed,false);
  assert.match(stageReadPlan().casContract,/same transaction/);
});
test('internally consistent newer pointer, revision or skill identity fails expected-current comparison',()=>{
  for(const mutate of [s=>{s.skills[0].artifact_revision=2;s.publicationArtifacts[0].artifact_revision=2;s.currentArtifacts[0].artifact_revision=2;},
    s=>{s.skills[0].current_artifact_version_id=other;s.publicationArtifacts[0].id=other;s.currentArtifacts[0].id=other;s.observations[0].artifact_version_id=other;},
    s=>{s.skills[0].id=other;s.publicationArtifacts[0].skill_id=other;s.currentArtifacts[0].skill_id=other;s.observations[0].skill_id=other;}]){
    const s=snapshot();mutate(s);const r=compareExpectedCurrent(bindExpectedCurrent(snapshot()),s);
    assert.equal(r.identityMatches,false);assert.equal(r.replayAllowed,false);
  }
});
test('malformed, divergent and over-scoped objects fail closed without echoing input',()=>{
  const mutations=[s=>s.publicationSha='0'.repeat(40),s=>s.skills[0].tree_hash='0'.repeat(64),
    s=>s.currentArtifacts[0].snapshot_status='pending',s=>s.observations[0].upstream_commit_sha='0'.repeat(40),
    s=>s.slug='other',s=>s.receipt={status:'success',trusted:true},s=>s.secret='SYNTHETIC_DO_NOT_ECHO'];
  for(const mutate of mutations){const s=snapshot();mutate(s);assert.throws(()=>bindExpectedCurrent(s),e=>e.message==='Invalid stage plan input');}
  const id=bindExpectedCurrent(snapshot());
  for(const bad of [null,{}, {...id,artifactRevision:0},{...id,skillId:'wrong'},{...id,sourceRef:'0'.repeat(40)},{...id,verified:true}]){
    assert.throws(()=>compareExpectedCurrent(bad,snapshot()),e=>e.message==='Invalid stage plan input');
  }
});
test('expected-current errors remain generic even for hostile accessors and proxy traps',()=>{
  const id=bindExpectedCurrent(snapshot());
  const bad={...id};Object.defineProperty(bad,'schemaVersion',{enumerable:true,get(){throw new Error('SYNTHETIC_DO_NOT_ECHO');}});
  for(const value of [bad,new Proxy(id,{ownKeys(){throw new Error('SYNTHETIC_DO_NOT_ECHO');}})]){
    assert.throws(()=>compareExpectedCurrent(value,snapshot()),e=>e.message==='Invalid stage plan input');
  }
});
test('snapshot accessor cannot substitute an unvalidated pointer after assessment',()=>{
  const good=snapshot(),expected={...bindExpectedCurrent(good),artifactVersionId:other};
  let reads=0;
  const hostile={...good};
  Object.defineProperty(hostile,'skills',{enumerable:true,get(){
    return ++reads>=8 ? [{...good.skills[0],current_artifact_version_id:other}] : good.skills;
  }});
  assert.throws(()=>compareExpectedCurrent(expected,hostile),e=>e.message==='Invalid stage plan input');
  assert.equal(reads,0);
});
for(const kind of ['hidden','symbol'])test(`identity rejects ${kind} extra own field`,()=>{
  const id=bindExpectedCurrent(snapshot());
  Object.defineProperty(id,kind==='hidden'?'receipt':Symbol('receipt'),{value:{status:'success'}});
  assert.throws(()=>compareExpectedCurrent(id,snapshot()),e=>e.message==='Invalid stage plan input');
});
test('identity rejects non-throwing accessor before it can add extra fields',()=>{
  const id=bindExpectedCurrent(snapshot());let reads=0;
  Object.defineProperty(id,'schemaVersion',{enumerable:true,get(){reads++;id.extraPointer=other;return 1;}});
  assert.throws(()=>compareExpectedCurrent(id,snapshot()),e=>e.message==='Invalid stage plan input');
  assert.equal(reads,0);assert.equal(Object.hasOwn(id,'extraPointer'),false);
});
for(const level of ['row','array'])test(`snapshot rejects non-throwing ${level} accessor without invoking it`,()=>{
  const s=snapshot();let reads=0;
  if(level==='row')Object.defineProperty(s.skills[0],'current_artifact_version_id',{enumerable:true,get(){reads++;return artifact;}});
  else Object.defineProperty(s.skills,'0',{enumerable:true,get(){reads++;return snapshot().skills[0];}});
  assert.throws(()=>bindExpectedCurrent(s),e=>e.message==='Invalid stage plan input');
  assert.equal(reads,0);
});
test('snapshot rejects hidden and symbol extras at every data boundary',()=>{
  for(const key of ['receipt',Symbol('receipt')])for(const level of ['snapshot','array','row']){
    const s=snapshot(),target=level==='snapshot'?s:level==='array'?s.skills:s.skills[0];
    Object.defineProperty(target,key,{value:'SYNTHETIC_DO_NOT_ECHO'});
    assert.throws(()=>bindExpectedCurrent(s),e=>e.message==='Invalid stage plan input');
  }
});
test('comparison retains owned expected identity if snapshot traps mutate caller identity',()=>{
  const id=bindExpectedCurrent(snapshot()),s=snapshot();
  s.skills[0]=new Proxy(s.skills[0],{ownKeys(target){id.artifactVersionId=other;return Reflect.ownKeys(target);}});
  const result=compareExpectedCurrent(id,s);
  assert.equal(id.artifactVersionId,other);
  assert.equal(result.identityMatches,true);
});
test('data-only proxies are captured through descriptors, never direct caller property reads',()=>{
  const trap={get(){throw new Error('SYNTHETIC_DO_NOT_ECHO');}};
  const s=snapshot();
  for(const name of ['skills','publicationArtifacts','currentArtifacts','observations'])s[name]=new Proxy(s[name].map(row=>new Proxy(row,trap)),trap);
  const id=new Proxy(bindExpectedCurrent(snapshot()),trap);
  assert.equal(compareExpectedCurrent(id,new Proxy(s,trap)).identityMatches,true);
  const bad=new Proxy(snapshot(),{getOwnPropertyDescriptor(){throw new Error('SYNTHETIC_DO_NOT_ECHO');}});
  assert.throws(()=>bindExpectedCurrent(bad),e=>e.message==='Invalid stage plan input');
});
test('history reads are bounded latest selections, not singleton lookups or proof of complete history',()=>{
  const p=stageReadPlan(),q=Object.fromEntries(p.queries.map(q=>[q.name,q]));
  assert.equal(q.audit.cardinality,'latest-candidate');assert.equal(q.audit.completeness,'latest-only');
  assert.equal(q.attestation.cardinality,'bounded-candidates');
  for(const name of ['catalog','aiContent','projectionJob','projectionEvent','eligibility','submission','notification','score'])assert.equal(q[name].cardinality,'zero-or-one');
  assert.match(p.dependencies,/two historical audits/);
  assert.match(p.dependencies,/no complete-history claim/);
});
test('receipt contract requires independent durable evidence and cannot consume claimed success',()=>{
  const p=stageReadPlan();
  assert.equal(p.receiptContract.verifierImplemented,false);
  assert.deepEqual(p.receiptContract.requiredFields,['stage','scope','expectedCurrent','inputDigest','beforeReadRef','effectRef','afterReadRef','observedAt','outcome']);
  assert.match(p.receiptContract.trust,/cannot authenticate/);
  assert.match(p.receiptContract.unknownEffect,/no replay/);
  assert.match(p.stages.find(s=>s.name==='callback').proofRequirements.join(' '),/favorites/);
  assert.match(p.stages.find(s=>s.name==='ai-content').proofRequirements.join(' '),/digest/);
  assert.match(p.stages.find(s=>s.name==='cache').proofRequirements.join(' '),/pack/);
  assert.throws(()=>stageReadPlan({success:true}),/Invalid stage plan input/);
});
test('CLI only prints proposed plan and rejects effects or extra input without echo',()=>{
  const script='scripts/bookforge-stage-plan.mjs';
  const ok=spawnSync(process.execPath,[script,'--plan'],{encoding:'utf8'});
  assert.equal(ok.status,0);assert.equal(JSON.parse(ok.stdout).productionState,'UNKNOWN');
  for(const args of [[],['--apply'],['--plan','SYNTHETIC_DO_NOT_ECHO'],['--receipt','SYNTHETIC_DO_NOT_ECHO']]){
    const r=spawnSync(process.execPath,[script,...args],{encoding:'utf8'});
    assert.equal(r.status,1);assert.equal(r.stdout,'');assert.equal(r.stderr,'Stage plan rejected; no production operation performed.\n');
  }
});
test('implementation has no network, environment credentials, subprocess, mutation or receipt ingestion',()=>{
  const s=readFileSync('scripts/bookforge-stage-plan.mjs','utf8');
  assert.doesNotMatch(s,/node:(?:child_process|http|https|net|tls|fs)|\bfetch\s*\(|process\.env|writeFile|\.rpc\(|\.update\(|\.upsert\(|\.insert\(/);
});
test('ordinary CI watches the new source and runs its offline tests',()=>{
  const w=readFileSync('.github/workflows/validate-marketplace.yml','utf8');
  assert.equal((w.match(/- "scripts\/bookforge-stage-plan\.mjs"/g)??[]).length,2);
  assert.match(w,/scripts\/tests\/bookforge-stage-plan\.test\.mjs/);
});
