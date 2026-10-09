import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {ALLOWED_FIELDS, PROTECTED_FIELDS, createSuggestion, transitionSuggestion, applySuggestion} from '../listing-copy-demo-contract.mjs';
import {fixture} from '../listing-copy-demo-fixture.mjs';
const base={packageVersion:fixture.packageVersion,artifactRevision:7,reportHash:fixture.source.baseReportHash,copyRevision:2,fields:fixture.before};
const user='demo-login-user', maintainer='demo-maintainer-role', publisher='demo-release-role';
const create=(delta={user_title:'Clearer title'},submitterId=user)=>createSuggestion(base,delta,{submitterId,reason:'clarity'});
const review={actorId:maintainer,role:'maintainer',reason:'matches bound package',currentBase:base};
const release={actorId:publisher,role:'publisher',currentBase:base};
const approve=s=>transitionSuggestion(s,'approved',review);

test('fixed public PR3699 fixture preserves excluded SEO and protected provenance',()=>{
 assert.equal(fixture.source.head,'268edece37b97b1ba6daa5e310845ea8b3390b70');
 assert.equal(fixture.packageVersion,'0.22.0');assert.equal(fixture.nonContentEqual,true);assert.equal(fixture.limitationsEqual,true);
 assert.deepEqual(Object.keys(fixture.proposed).sort(),[...ALLOWED_FIELDS].sort());
 assert.deepEqual(fixture.excludedFields,['seo_keywords']);
 const s=create(fixture.proposed);const preview=applySuggestion(s,base);
 assert.deepEqual(preview.fields.limitations,fixture.before.limitations);
 assert.deepEqual(preview.fields.seo_keywords,fixture.before.seo_keywords);
 assert.equal(preview.publishAuthorizationGranted,false);
});
test('all nonallowlisted fields reject, including protected names and prototype keys',()=>{
 for(const key of [...PROTECTED_FIELDS,'arbitrary','__proto__','constructor']){
  assert.throws(()=>create(JSON.parse(`{"${key}":"changed"}`)),/not editable/);
 }
});
test('field schemas require text, text lists and exact-key structured lists',()=>{
 for(const delta of [{user_title:[]},{actual_capabilities:'not a list'},{faq:['not an object']},{faq:[{question:'q',answer:'a',role:'admin'}]},{faq:[{question:'q'}]},{user_title:' '},{user_title:'x'.repeat(121)},{value_statement:'x'.repeat(601)}])assert.throws(()=>create(delta),/Invalid/);
 for(const delta of [{faq:[{question:'q',answer:'a'}]},{output_examples:[{input:'i',output:'o'}]}])assert.equal(create(delta).status,'submitted');
});
test('empty/no-op and script-bearing edits reject',()=>{
 for(const delta of [{},{user_title:base.fields.user_title},{user_title:'<script>alert(1)</script>'}])assert.throws(()=>create(delta));
});
test('unknown or missing mock identities cannot submit or forge owner badges',()=>{
 for(const id of [null,'',undefined,'forged-user'])assert.throws(()=>createSuggestion(base,{}, {submitterId:id,reason:'clarity'}),/authenticated/);
 assert.equal(createSuggestion(base,{user_title:'New'},{submitterId:user,reason:'r',ownership:'verified-maintainer'}).ownership,'unverified');
 assert.equal(create({user_title:'New'},'demo-verified-user').ownership,'verified-maintainer');
});
test('repository badge does not confer a platform role; forged role rejected',()=>{
 for(const actorId of [user,'demo-verified-user','invented-maintainer'])assert.throws(()=>transitionSuggestion(create(),'approved',{...review,actorId}),/maintainer/);
});
test('submitter cannot self-review, even with a real simulated platform role',()=>{
 assert.throws(()=>transitionSuggestion(create({user_title:'New'},maintainer),'approved',review),/self-review/);
});
test('review rationale required and approval is not publication',()=>{
 assert.throws(()=>transitionSuggestion(create(),'approved',{...review,reason:' '}),/reason/);
 const s=approve(create());assert.equal(s.status,'approved');assert.equal(s.publisher,null);assert.equal(s.receipt,null);assert.equal(s.approval.revision,1);
});
test('changes requested, revised and approved use the same suggestion revision history',()=>{
 let s=transitionSuggestion(create(),'changes_requested',review);
 s=transitionSuggestion(s,'submitted',{actorId:user,role:'submitter',updatedDelta:{user_title:'Revised'}});
 assert.equal(s.revision,2);assert.equal(s.approval,null);assert.equal(s.history.length,2);
 assert.equal(approve(s).status,'approved');
});
test('editing an approved revision invalidates the approval and cannot publish',()=>{
 const s=transitionSuggestion(approve(create()),'submitted',{actorId:user,role:'submitter',updatedDelta:{user_title:'Changed again'}});
 assert.equal(s.revision,2);assert.equal(s.approval,null);assert.equal(s.reviewer,null);
 assert.throws(()=>transitionSuggestion(s,'publishing',release),/state/);
});
test('approval is bound to delta and rejects post-review mutation',()=>{
 const s=approve(create());s.delta.user_title='Tampered after review';
 assert.throws(()=>transitionSuggestion(s,'publishing',release),/approval/);
});
test('each changed foundation enters needs_rebase at approval or publication',()=>{
 for(const change of [{packageVersion:'0.23.0'},{artifactRevision:8},{reportHash:'b'.repeat(64)},{copyRevision:3},{fields:{...base.fields,user_title:'Concurrent edit'}}]){
  const currentBase={...base,...change};
  assert.equal(transitionSuggestion(create(),'approved',{...review,currentBase}).status,'needs_rebase');
  assert.equal(transitionSuggestion(approve(create()),'publishing',{...release,currentBase}).status,'needs_rebase');
  assert.equal(applySuggestion(create(),currentBase).status,'needs_rebase');
 }
 assert.throws(()=>transitionSuggestion(create(),'approved',{...review,currentBase:undefined}),/base/);
});
test('publication requires separate registered actor and a simulated receipt',()=>{
 const s=approve(create());
 for(const actorId of [user,maintainer,'forged-release'])assert.throws(()=>transitionSuggestion(s,'publishing',{...release,actorId}),/publisher/);
 const p=transitionSuggestion(s,'publishing',release);
 assert.throws(()=>transitionSuggestion(p,'published',release),/receipt/);
 const done=transitionSuggestion(p,'published',{...release,receipt:'demo-only-no-authoritative-receipt'});
 assert.equal(done.status,'published');assert.equal(done.publisher,publisher);
});
test('foundation changes after simulated publication invalidate active approval too',()=>{
 const published=transitionSuggestion(transitionSuggestion(approve(create()),'publishing',release),'published',{...release,receipt:'demo-only-no-authoritative-receipt'});
 const stale=applySuggestion(published,{...base,copyRevision:3});
 assert.equal(stale.status,'needs_rebase');assert.equal(stale.approval,null);
 assert.equal(published.status,'published');
});
test('repeated transitions reject deterministically without altering accepted state',()=>{
 for(const s of [approve(create()),transitionSuggestion(approve(create()),'publishing',release)]){
  const prior=structuredClone(s);assert.throws(()=>transitionSuggestion(s,s.status,{...review,...release}),/state/);assert.deepEqual(s,prior);
 }
});
test('preview remains a draft-only result and helpers never mutate base or input',()=>{
 const snapshot=structuredClone(base),s=create(),prior=structuredClone(s);
 approve(s);const preview=applySuggestion(s,base);assert.equal(preview.status,'preview-only');assert.equal(preview.reportUnchanged,true);
 assert.deepEqual(s,prior);assert.deepEqual(base,snapshot);
});
test('CI filters and sparse checkout include both module and fixture sources',()=>{
 for(const path of ['.github/workflows/validate-marketplace.yml','.github/workflows/test-recalculate-scores.yml']){
  const workflow=readFileSync(path,'utf8');
  assert.equal((workflow.match(/- "scripts\/listing-copy-demo-\*\.mjs"/g)??[]).length,2);
 }
 const isolated=readFileSync('.github/workflows/test-recalculate-scores.yml','utf8');
 assert.match(isolated,/sparse-checkout:[\s\S]*\n            docs\/proposals\n/);
});
test('HTML discloses simulation, imports fixed fixture, uses safe text and no remote effects',()=>{
 const html=readFileSync('docs/proposals/listing-copy-demo.html','utf8');
 assert.match(html,/离线交互演示/);assert.match(html,/不会连接平台或写入数据/);assert.match(html,/刷新页面会重置/);
 assert.match(html,/listing-copy-demo-fixture/);assert.match(html,/textContent/);
 assert.doesNotMatch(html,/fetch\s*\(|localStorage|sessionStorage|XMLHttpRequest|WebSocket/);
 assert.match(html,/id="staleBtn"/);assert.match(html,/id="publicSource"/);
});
