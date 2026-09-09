import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {admitMonitor} from '../source-monitor-admission.mjs';
import {selectOldestSources} from '../observe-source-status.mjs';
test('publication backlog, active sync and failed downstream work stop monitor admission',()=>{
 const api=path=>path==='git/trees/main'?{tree:[]}:{workflow_runs:[]};assert.equal(admitMonitor(api),'');
 assert.match(admitMonitor(path=>path==='git/trees/main'?{tree:[{path:'pending',sha:'p'}]}:{tree:[{type:'blob',path:'a/SKILL.md'}]}),/Pending/);
 assert.match(admitMonitor(path=>path==='git/trees/main'?{tree:[]}:{workflow_runs:[{status:'pending'}]}),/Waiting/);
 assert.match(admitMonitor(path=>path==='git/trees/main'?{tree:[]}:{workflow_runs:[{status:'completed',event:'push',conclusion:'failure',created_at:'2026-09-09'}]}),/recovery/);
});
test('source observation rotates oldest-first, bounds writes, and never runs AI or archives',async()=>{
 let url;const env={PUBLIC_SUPABASE_URL:'https://db.example',SUPABASE_SERVICE_ROLE_KEY:'test'};
 assert.deepEqual(await selectOldestSources(async u=>{url=u;return {ok:true,json:async()=>[{slug:'owner-demo'}]};},env),['owner-demo']);
 assert.equal(url.searchParams.get('limit'),'100');assert.equal(url.searchParams.get('order'),'upstream_checked_at.asc.nullsfirst,slug.asc');
 await assert.rejects(selectOldestSources(async()=>({ok:true,json:async()=>[{slug:'bad,extra'}]}),env),/Invalid/);
 const script=readFileSync('scripts/observe-source-status.mjs','utf8');assert.doesNotMatch(script,/--updateLocal|--createPr|--archiveMissing|--deleteArchived/);
 assert.match(script,/'--write'/);assert.match(script,/admitMonitor\(\)/);
});
