import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { parse } from 'yaml';
import { trustedMerged, publicationIdentity, chooseAttempt, preflightContext, publicationFiles } from '../continue-merged-publications.mjs';

test('61-skill approvals fit the 64-skill bound; 65-skill approvals still fail closed', async () => {
  const { main } = await import('../continue-merged-publications.mjs');
  const counts = [61, 3, 1], writes = [];
  const prs = counts.map((_, i) => ({ number: i + 1, get changed_files() { return counts[i]; }, merged_at: `2026-09-01T00:00:0${i}Z`,
    base: { ref: 'main' }, user: { id: 254047988, login: 'ai-skill-store[bot]' },
    head: { repo: { full_name: 'aiskillstore/marketplace' }, ref: 'submission/test', sha: 'a'.repeat(40) },
    merge_commit_sha: String(i + 1).repeat(40) }));
  const files = n => Array.from({ length: counts[n - 1] }, (_, i) =>
    ({ filename: `pending/owner/s${n}-${i}/skill-report.json`, sha: `r${n}-${i}` }));
  const request = (endpoint, data) => {
    if (data) { writes.push(data); return; }
    if (endpoint.endsWith('/git/trees/main')) return { tree: [{ path: 'pending', sha: 'tree' }] };
    if (endpoint.includes('/git/trees/tree?')) return { tree: prs.flatMap(p => files(p.number)
      .map(f => ({ path: f.filename.slice('pending/'.length), sha: f.sha }))) };
    if (endpoint.includes('/pulls?')) return prs;
    const file = endpoint.match(/\/pulls\/(\d+)\/files/);
    if (file) return files(Number(file[1]));
    const pr = endpoint.match(/\/pulls\/(\d+)$/);
    if (pr) return prs[Number(pr[1]) - 1];
    if (endpoint.includes('/actions/workflows/')) return { workflow_runs: [] };
    if (endpoint.includes('/statuses?') || endpoint.includes('/git/matching-refs/')) return [];
    throw new Error(`Unexpected ${endpoint}`);
  };
  process.argv.push('--apply');
  try {
    main(request);
    assert.equal(writes.length, 1);
    assert.equal(writes[0].inputs.pr_numbers, '1,2', '61 plus 3 fits; the next Skill must wait');
    counts[0] = 65; writes.length = 0;
    assert.throws(() => main(request), /bounded batch capacity/);
    assert.equal(writes.length, 0);
  } finally { process.argv.pop(); }
});

test('only authoritative merged submissions continue; unknown effects never auto-replay', () => {
  const pr = { number: 12, merged_at: '2026-09-08T00:00:00Z', base: { ref: 'main' }, user: { id: 254047988, login: 'ai-skill-store[bot]' }, head: { repo: { full_name: 'aiskillstore/marketplace' }, ref: 'submission/test', sha: 'a'.repeat(40) }, merge_commit_sha: 'b'.repeat(40) };
  assert.ok(trustedMerged(pr));
  assert.equal(Boolean(trustedMerged({ ...pr, merged_at: null })), false);
  assert.equal(Boolean(trustedMerged({ ...pr, user: { id: 1 } })), false);
  const { digest, correlation } = publicationIdentity(pr);
  assert.ok(preflightContext(digest).length <= 100);
  assert.equal(correlation, `submission-pr-12-${'a'.repeat(40)}-${'b'.repeat(40)}`);
  const input = { refs: [], statuses: [], digest, merge: pr.merge_commit_sha, now: 1788800000000 };
  assert.equal(chooseAttempt(input).attempt, '1788800000000-1');
  for (const state of ['pending', 'success', 'failure', 'error']) {
    assert.ok(chooseAttempt({ ...input, statuses: [{ context: `agentcrew/publication/${digest}`, state }] }).wait);
  }
  assert.ok(chooseAttempt({ ...input, statuses: [{ context: `agentcrew/publication-attempt/${digest}/1`, state: 'pending' }] }).wait);
  const ref = { ref: `refs/tags/agentcrew-dispatch-outbox/publication/${digest}/${input.now}-1`, object: { type: 'commit', sha: input.merge } };
  assert.ok(chooseAttempt({ ...input, refs: [ref] }).wait);
  assert.ok(chooseAttempt({ ...input, refs: [ref], now: input.now + 900001 }).attempt);
  assert.throws(() => chooseAttempt({ ...input, refs: [{ ...ref, object: { type: 'commit', sha: 'c'.repeat(40) } }] }));
  assert.ok(chooseAttempt({ ...input, refs: Array(8).fill(ref) }).wait);
});

test('merged-only continuation runs trusted main code and reuses the existing receiver', () => {
  const source = readFileSync('.github/workflows/continue-merged-publications.yml', 'utf8');
  const workflow = parse(source);
  assert.deepEqual(workflow.on.push.branches, ['main']);
  assert.ok(workflow.on.schedule.length);
  assert.equal(workflow.jobs.continue.steps[0].with.ref, 'main');
  assert.equal(workflow.jobs.continue.steps[0].with['persist-credentials'], false);
  const script = readFileSync('scripts/continue-merged-publications.mjs', 'utf8');
  assert.match(script, /publish-approved-batch.yml\/dispatches/);
  assert.match(script, /syncRuns.some\(r => r.status !== 'completed'\)/);
  assert.doesNotMatch(script, /\/merge['`"]|update-branch|safe_to_publish|is_blocked|risk_level/);
});

test('sync baseline selection sorts workflow runs newest first', () => {
  const source = readFileSync('.github/workflows/sync-to-supabase.yml', 'utf8');
  assert.match(source, /sort_by\(\.created_at\) \| reverse\[\]/);
});

test('current pending inventory stops after its exact owners; fresh A prevents dispatching B', async () => {
  const { main } = await import('../continue-merged-publications.mjs');
  const makePr = (number, date, sha) => ({ number, changed_files: 1, merged_at: date, base: { ref: 'main' }, user: { id: 254047988, login: 'ai-skill-store[bot]' }, head: { repo: { full_name: 'aiskillstore/marketplace' }, ref: 'submission/test', sha: 'a'.repeat(40) }, merge_commit_sha: sha.repeat(40) });
  const a = makePr(1, '2026-09-01T00:00:00Z', 'b');
  const b = makePr(2, '2026-09-02T00:00:00Z', 'c');
  const { digest } = publicationIdentity(a);
  const calls = [];
  let syncRuns = [];
  const request = (endpoint, data) => {
    calls.push(endpoint);
    assert.equal(data, undefined, 'fresh earlier outbox must prevent every write');
    if (endpoint.endsWith('/git/trees/main')) return { tree: [{ path: 'pending', sha: 'tree' }] };
    if (endpoint.includes('/git/trees/tree?')) return { tree: [{ path: 'owner/a/skill-report.json', sha: 'ra' }, { path: 'owner/b/skill-report.json', sha: 'rb' }] };
    if (endpoint.includes('/pulls?')) {
      assert.ok(endpoint.endsWith('page=1'), 'do not scan 1000 old PRs after finding all current owners');
      return [b, a, ...Array(98).fill({ merged_at: null })];
    }
    if (endpoint.includes('/pulls/1/files')) return [{ filename: 'pending/owner/a/skill-report.json', sha: 'ra' }];
    if (endpoint.includes('/pulls/2/files')) return [{ filename: 'pending/owner/b/skill-report.json', sha: 'rb' }];
    if (endpoint.includes('/actions/workflows/')) return { workflow_runs: endpoint.includes('sync-to-supabase') ? syncRuns : [] };
    if (endpoint.endsWith('/pulls/1')) return a;
    if (endpoint.includes('/git/matching-refs/')) return [{ ref: `refs/tags/agentcrew-dispatch-outbox/publication/${digest}/${Date.now()}-1`, object: { type: 'commit', sha: a.merge_commit_sha } }];
    if (endpoint.includes('/statuses?')) return [];
    throw new Error(`Unexpected request: ${endpoint}`);
  };
  main(request);
  assert.ok(!calls.some(p => p.endsWith('/pulls/2')));
  syncRuns = [{ id: 12, event: 'push', status: 'completed', conclusion: 'failure', created_at: '2026-09-08T00:00:00Z' }];
  assert.throws(() => main(request), /Previous push sync 12 is failure/);
  syncRuns = [{id:13,status:'pending',created_at:new Date(Date.now()-3_600_001).toISOString()}];
  assert.throws(() => main(request), /stalled over 60 minutes: 13/);
});

test('automatic continuation dispatches at most 25 approvals and leaves reservations to the receiver', async () => {
  const { main, batchIdentity } = await import('../continue-merged-publications.mjs');
  const prs = Array.from({length:26}, (_,i) => ({number:i+1, changed_files:1, merged_at:`2026-09-01T00:00:${String(i).padStart(2,'0')}Z`, base:{ref:'main'}, user:{id:254047988,login:'ai-skill-store[bot]'}, head:{repo:{full_name:'aiskillstore/marketplace'},ref:'submission/test',sha:'a'.repeat(40)},merge_commit_sha:(i+1).toString(16).padStart(40,'0')}));
  const writes=[];
  let preflightStatus = null, receiverStatus = null;
  const request=(endpoint,data)=>{
    if(data){writes.push({endpoint,data});return;}
    if(endpoint.endsWith('/git/trees/main'))return {tree:[{path:'pending',sha:'tree'}]};
    if(endpoint.includes('/git/trees/tree?'))return {tree:prs.map(p=>({path:`owner/s${p.number}/skill-report.json`,sha:`r${p.number}`}))};
    if(endpoint.includes('/pulls?'))return prs;
    const file=endpoint.match(/\/pulls\/(\d+)\/files/);
    if(file)return [{filename:`pending/owner/s${file[1]}/skill-report.json`,sha:`r${file[1]}`}];
    const pr=endpoint.match(/\/pulls\/(\d+)$/);
    if(pr)return prs[Number(pr[1])-1];
    if(endpoint.includes('/actions/workflows/'))return {workflow_runs:[]};
    if(endpoint.includes('/statuses?'))return endpoint.includes(prs[0].merge_commit_sha)?[preflightStatus,receiverStatus].filter(Boolean):[];
    if(endpoint.includes('/git/matching-refs/'))return [];
    throw new Error(`Unexpected ${endpoint}`);
  };
  process.argv.push('--apply');
  try{main(request);}finally{process.argv.pop();}
  assert.equal(writes.length,1);
  assert.match(writes[0].endpoint,/publish-approved-batch.yml\/dispatches$/);
  assert.deepEqual(writes[0].data,{ref:'main',inputs:{pr_numbers:prs.slice(0,25).map(p=>p.number).join(','),batch_id:batchIdentity(prs.slice(0,25).map(p=>publicationIdentity(p).correlation))}});
  preflightStatus={context:preflightContext(publicationIdentity(prs[0]).digest),state:'failure'};
  writes.length=0;process.argv.push('--apply');try{main(request);}finally{process.argv.pop();}
  assert.equal(writes[0].data.inputs.pr_numbers,prs.slice(1).map(p=>p.number).join(','),'invalid first item must not consume capacity or poison later approvals');
  assert.equal(writes[0].data.inputs.batch_id,batchIdentity(prs.slice(1).map(p=>publicationIdentity(p).correlation)));
  receiverStatus={context:`agentcrew/publication/${publicationIdentity(prs[0]).digest}`,state:'failure'};
  writes.length=0;process.argv.push('--apply');try{main(request);}finally{process.argv.pop();}
  assert.equal(writes.length,0,'receiver evidence overrides a preflight rejection; unknown effects still block');
  receiverStatus=null;preflightStatus={...preflightStatus,context:preflightStatus.context.replace(/[^/]+$/, 'old-validator')};
  writes.length=0;process.argv.push('--apply');try{main(request);}finally{process.argv.pop();}
  assert.match(writes[0].data.inputs.pr_numbers,/^1,/,'a new validator must recheck previous preflight failures');

});

 test('publication file inventory accepts large approvals and rejects incomplete API evidence', () => {
  for (const count of [1, 1000, 2614, 3000]) {
    let pages = 0;
    const result = publicationFiles({number:1,changed_files:count}, endpoint => {
      const page = Number(new URL(`https://api.github.com/${endpoint}`).searchParams.get('page'));
      pages++;
      return Array.from({length:Math.min(100,count-(page-1)*100)}, (_,i)=>({filename:`pending/owner/demo/f${(page-1)*100+i}`}));
    });
    assert.equal(result.length,count);assert.equal(pages,Math.ceil(count/100));
  }
  assert.throws(()=>publicationFiles({number:1,changed_files:3001},()=>[]),/bound/);
  assert.throws(()=>publicationFiles({number:1,changed_files:2},()=>[]),/Incomplete/);
  assert.throws(()=>publicationFiles({number:1,changed_files:2},()=>[{filename:'same'},{filename:'same'}]),/duplicate/);
});
