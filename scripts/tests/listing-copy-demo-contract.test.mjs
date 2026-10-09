import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {ALLOWED_FIELDS, PROTECTED_FIELDS, createSuggestion, transitionSuggestion, applySuggestion} from '../listing-copy-demo-contract.mjs';
const base={packageVersion:'0.22.0',artifactRevision:7,reportHash:'a'.repeat(64),copyRevision:2,
 fields:{user_title:'Antigravity delegation with independent verification',value_statement:'Delegate repository work with independent checks.',
 actual_capabilities:['Explore repositories','Review diffs'],limitations:['Codex only'],seo_keywords:['Codex']}};
test('only an explicit copy-field allowlist can be proposed; protected fields are rejected',()=>{
 assert.deepEqual(ALLOWED_FIELDS,['user_title','value_statement','actual_capabilities','use_cases','prompt_templates','output_examples','best_practices','anti_patterns','faq']);
 for(const k of ['limitations','seo_keywords','version','supported_tools','source_ref','content_hash','security_audit','manifest']) assert.ok(PROTECTED_FIELDS.includes(k));
 assert.throws(()=>createSuggestion(base,{limitations:['none']},{submitterId:'user-1',reason:'shorten'}),/not editable/);
 assert.throws(()=>createSuggestion(base,{supported_tools:['all']},{submitterId:'user-1',reason:'shorten'}),/not editable/);
});
test('suggestion is immutable-content delta bound to exact base; submitter is not owner proof or publisher',()=>{
 const s=createSuggestion(base,{user_title:'Clearer title'},{submitterId:'user-1',reason:'Current wording repeats itself'});
 assert.equal(s.status,'submitted'); assert.equal(s.base.packageVersion,'0.22.0');
 assert.equal(s.base.reportHash,'a'.repeat(64));assert.equal(s.ownership,'unverified');
 assert.equal(s.publisher,null);assert.deepEqual(s.changedFields,['user_title']);
 assert.notEqual(s.base.fields.user_title,'Clearer title');
});
test('missing authentication and incomplete rationale reject submission',()=>{
 for(const userId of [null,'',undefined]) assert.throws(()=>createSuggestion(base,{user_title:'x'},{submitterId:userId,reason:'r'}),/authenticated/);
 assert.throws(()=>createSuggestion(base,{user_title:'x'},{submitterId:'u',reason:' '}),/reason/);
 assert.throws(()=>createSuggestion(base,{}, {submitterId:'u',reason:'nothing'}),/empty/);
});
test('review and publication are distinct; only maintainer action can approve or publish',()=>{
 let s=createSuggestion(base,{user_title:'Clearer title'},{submitterId:'u',reason:'clarity'});
 assert.throws(()=>transitionSuggestion(s,'approved',{actorId:'u',role:'submitter'}),/maintainer/);
 s=transitionSuggestion(s,'changes_requested',{actorId:'m1',role:'maintainer',reason:'show the concrete benefit'});
 assert.equal(s.status,'changes_requested');
 s=transitionSuggestion(s,'submitted',{actorId:'u',role:'submitter',updatedDelta:{user_title:'Clearer benefit'}});
 s=transitionSuggestion(s,'approved',{actorId:'m2',role:'maintainer',reason:'matches package'});
 assert.equal(s.status,'approved');assert.equal(s.publisher,null);
 s=transitionSuggestion(s,'publishing',{actorId:'release-bot',role:'publisher'});
 s=transitionSuggestion(s,'published',{actorId:'release-bot',role:'publisher',receipt:'source-readback-1'});
 assert.equal(s.status,'published');assert.equal(s.publisher,'release-bot');
});
test('submitter cannot self-review any material revision',()=>{
 const s=createSuggestion(base,{user_title:'Clearer title'},{submitterId:'u',reason:'clarity'});
 assert.throws(()=>transitionSuggestion(s,'approved',{actorId:'u',role:'maintainer',reason:'looks good'}),/self-review/);
});
test('stale package or copy revision enters needs_rebase rather than applying silently',()=>{
 const s=createSuggestion(base,{user_title:'Clearer title'},{submitterId:'u',reason:'clarity'});
 const next={...base,packageVersion:'0.23.0',artifactRevision:8,reportHash:'b'.repeat(64)};
 assert.equal(applySuggestion(s,next).status,'needs_rebase');
 assert.deepEqual(applySuggestion(s,base).fields,{...base.fields,user_title:'Clearer title'});
});
test('copy-only HTML prototype is explicit offline simulation and escapes untrusted text in rendered previews',()=>{
 const html=readFileSync('docs/proposals/listing-copy-demo.html','utf8');
 assert.match(html,/离线交互演示/);assert.match(html,/不会连接平台或写入数据/);
 assert.match(html,/刷新页面会重置/);assert.match(html,/textContent/);
 assert.match(html,/escapeText\(typeof suggestion\.delta\[k\]/);
 assert.doesNotMatch(html,/fetch\s*\(|localStorage|sessionStorage|XMLHttpRequest|WebSocket/);
});
test('proposal helpers do not mutate source package, report, audit or base snapshots',()=>{
 const frozen=structuredClone(base);Object.freeze(base);Object.freeze(base.fields);
 const s=createSuggestion(base,{value_statement:'Sharper statement'},{submitterId:'u',reason:'clarity'});
 transitionSuggestion(s,'rejected',{actorId:'m',role:'maintainer',reason:'unsupported claim'});
 applySuggestion(s,base);assert.deepEqual(base,frozen);
});
