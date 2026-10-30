import assert from 'node:assert/strict';
import test from 'node:test';
import { collectAuditRecovery } from '../reconcile-audit-sync.mjs';
const repo='aiskillstore/marketplace', prefix=`repos/${repo}`;
const A='a'.repeat(40), F='f'.repeat(40), C='c'.repeat(40), G='d'.repeat(40), P='e'.repeat(40), T='b'.repeat(40);
const path='skills/owner/skill/skill-report.json';
const mkRun=(id,event,conclusion,head,created_at)=>({id,event,conclusion,head_sha:head,created_at,run_attempt:1,status:'completed',head_branch:'main',head_repository:{full_name:repo},path:'.github/workflows/sync-to-supabase.yml'});
async function scenario(failedTimestamp) {
  const baseline=mkRun(1,'push','success',A,'2026-10-27T00:00:00Z');
  const hidden=mkRun(2,'push','failure',F,failedTimestamp);
  const push=mkRun(3,'push','failure',P,'2026-10-29T01:00:00Z');
  const recovery=mkRun(4,'workflow_dispatch','success',P,'2026-10-30T01:00:00Z');
  const pr={number:42,state:'closed',draft:false,merged:true,merge_commit_sha:P,changed_files:1,created_at:'2026-10-29T00:10:00Z',user:{id:254047988,login:'ai-skill-store[bot]'},head:{sha:G,ref:'audit/20261029-001000',repo:{full_name:repo}},base:{sha:C,ref:'main',repo:{full_name:repo}}};
  const producer={id:10,workflow_id:20,path:'.github/workflows/audit-skills.yml',event:'workflow_dispatch',head_branch:'main',head_sha:C,status:'completed',conclusion:'success',repository:{full_name:repo},head_repository:{full_name:repo},created_at:'2026-10-29T00:00:00Z',updated_at:'2026-10-29T00:20:00Z'};
  const file={filename:path,status:'modified'};
  const compared=[];
  const mkJobs=(pairs)=>({total_count:1,jobs:[{name:'sync',conclusion:'success',steps:pairs.map(([name,conclusion])=>({name,conclusion}))}]});
  const original=mkJobs([['Wait for authoritative publication completion','success'],['Find last successful sync commit','failure'],...['Download skillstore-cli','Sync skills to Supabase','Reconcile durable security change events','Notify skillstore - Published submissions'].map(n=>[n,'skipped'])]);
  const recovered=mkJobs([...['Sync skills to Supabase','Upload provider-complete synced slugs artifact','Save synced slugs to artifact','Reconcile durable security change events','Resolve published submissions'].map(n=>[n,'success']),['Notify skillstore - Published submissions','skipped']]);
  recovered.jobs.push(...['calculate-scores','cache-invalidate'].map(name=>({name,conclusion:'success'}))); recovered.total_count=3;
  const api=(endpoint,raw=false)=>{
    if(endpoint===`${prefix}/actions/runs/3`) return push;
    if(endpoint===`${prefix}/actions/runs/4`) return recovery;
    if(endpoint===`${prefix}/actions/workflows/sync-to-supabase.yml/runs?per_page=100`) return {total_count:4,workflow_runs:[recovery,push,hidden,baseline]};
    if(endpoint===`${prefix}/pulls/42`) return pr;
    if(endpoint.includes('/pulls/42/files?')) return [file];
    if(endpoint.endsWith('/actions/workflows/audit-skills.yml')) return {id:20};
    if(endpoint.includes('/actions/workflows/20/runs?')) return {workflow_runs:[producer]};
    if(endpoint.includes('/actions/runs/10/jobs?')) return {jobs:[{id:30,name:'merge',conclusion:'success',steps:[{name:'Apply results and create PR',conclusion:'success'}]}]};
    if(endpoint.endsWith('/actions/jobs/30/logs') && raw) return `[audit/20261029-001000 ${G}] chore(audit): audit 1 skills\n##[notice]Created PR: https://github.com/${repo}/pull/42\n`;
    if(endpoint===`${prefix}/commits/${G}`) return {sha:G,parents:[{sha:C}]};
    if(endpoint.startsWith(`${prefix}/commits/${G}?`)) return {files:[file]};
    if(endpoint===`${prefix}/compare/${A}...${P}` || endpoint===`${prefix}/compare/${A}...${F}`){
      compared.push(endpoint);
      const messages=endpoint.endsWith(F)?['source update in other/root']:['source update in other/root','revert other/root','audit report repair','merge audit'];
      return {status:'ahead',total_commits:messages.length,commits:messages.map(message=>({commit:{message}})),files:endpoint.endsWith(F)?[{filename:'skills/other/root/SKILL.md',status:'modified'}]:[file]};
    }
    if(endpoint.startsWith(`${prefix}/contents/${path}?`)) return {type:'file',sha:T,encoding:'base64',size:200,content:Buffer.from(JSON.stringify({meta:{slug:'owner-skill',content_hash:'1'.repeat(64),tree_hash:'2'.repeat(64)}})).toString('base64')};
    if(endpoint===`${prefix}/git/commits/${P}`) return {tree:{sha:T},parents:[{sha:C},{sha:G}]};
    if(endpoint===`${prefix}/git/commits/${G}`) return {tree:{sha:T}};
    if(endpoint===`${prefix}/git/trees/${T}`) return {truncated:false,tree:['skills','owner','skill'].map(path=>({path,type:'tree',mode:'040000',sha:T}))};
    if(endpoint===`${prefix}/actions/runs/3/attempts/1/jobs?per_page=100`) return original;
    if(endpoint===`${prefix}/actions/runs/4/attempts/1/jobs?per_page=100`) return recovered;
    throw new Error(`Unmocked endpoint: ${endpoint}`);
  };
  return {result:await collectAuditRecovery({failedRunId:3,recoveryRunId:4,auditPr:42},api,()=>['owner-skill']),compared};
}
test('F8619-AUDIT-HISTORY-001 rejects same-second failed root hidden by later revert', async () => {
  await assert.rejects(scenario('2026-10-27T00:00:00Z'), /Ambiguous push creation time/);
});
test('distinct timestamps still detect the reverted historical uncovered root', async () => {
  await assert.rejects(scenario('2026-10-27T00:00:01Z'), /Uncovered canonical change/);
});
test('unambiguous complete baseline can precede a repaired audit range', async () => {
  const {result}=await scenario('2026-10-26T00:00:00Z');
  assert.deepEqual(result.plan.map(p=>p.slug),['owner-skill']);
});
test('rejects same-second failed pushes at the repaired-tip boundary too', async () => {
  await assert.rejects(scenario('2026-10-29T01:00:00Z'), /Ambiguous push creation time/);
});
