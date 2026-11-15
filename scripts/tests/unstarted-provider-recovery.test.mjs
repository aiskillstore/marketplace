import assert from 'node:assert/strict';
import test from 'node:test';
import { loadUnstartedProviderRecovery, verifyUnstartedProviderRecovery, verifyNoOtherRecovery } from '../unstarted-provider-recovery.mjs';

import { unstartedEvidence, correlation } from './fixtures/unstarted-provider-evidence.mjs';

test('another recovery dispatch cannot be hidden by empty provider projections or concurrent/nonterminal status',()=>{
  const e=unstartedEvidence();e.run.created_at='2026-11-15T17:00:00Z';
  const current={id:401,display_title:'Recover provider sync 101'};
  assert.doesNotThrow(()=>verifyNoOtherRecovery(e.run,401,()=>({total_count:1,workflow_runs:[current]})));
  for(const state of ['queued','in_progress','failure','success','cancelled']) {
    assert.throws(()=>verifyNoOtherRecovery(e.run,401,()=>({total_count:2,workflow_runs:[current,{id:402,display_title:current.display_title,status:state}]})));
  }
  assert.throws(()=>verifyNoOtherRecovery(e.run,401,()=>({total_count:2,workflow_runs:[current]})));
  assert.throws(()=>verifyNoOtherRecovery({...e.run,created_at:null},401,()=>assert.fail('invalid time must not query')));
});

function reader(e, calls) {
  return path => {
    calls.push(path);
    const attempt=path.match(/\/attempts\/([1-9][0-9]*)\/jobs\?per_page=100$/);
    if (attempt) return e.attempts[Number(attempt[1])-1].jobs;
    if (path.endsWith('/check-runs/201/annotations?per_page=100')) return e.attempts[0].annotations;
    if (path.includes('/statuses?')) return e.statuses;
    if (path.endsWith('/actions/runs/301')) return e.publisher;
    throw new Error(`Unexpected read: ${path}`);
  };
}
test('loader reads every exact attempt, only the unacquired check annotations, and the original publisher',()=>{
  const e=unstartedEvidence(), calls=[];
  assert.deepEqual(loadUnstartedProviderRecovery(e.run,e.commit,reader(e,calls)),e);
  assert.equal(calls.length,5);
  assert.ok(calls.every(p=>p.startsWith('repos/aiskillstore/marketplace/')));
  assert.match(calls[0],/runs\/101\/attempts\/1\/jobs/);
  assert.match(calls[2],/runs\/101\/attempts\/2\/jobs/);
});
test('loader paginates statuses without falling back from a newer invalid owner or hiding unavailable proof',()=>{
  const e=unstartedEvidence(), calls=[], base=reader(e,calls);
  const filler=Array.from({length:100},(_,i)=>({context:`unrelated/${i}`}));
  const proof=loadUnstartedProviderRecovery(e.run,e.commit,path=>path.endsWith('statuses?per_page=100&page=1')?filler:base(path));
  assert.deepEqual(verifyUnstartedProviderRecovery(proof),{publisherId:301,correlation});
  assert.ok(calls.some(p=>p.endsWith('statuses?per_page=100&page=2')));
  const invalid=unstartedEvidence();invalid.statuses.unshift({...invalid.statuses[0],target_url:'https://example.invalid/run/301'});
  assert.throws(()=>loadUnstartedProviderRecovery(invalid.run,invalid.commit,reader(invalid,[])));
  assert.throws(()=>loadUnstartedProviderRecovery(e.run,e.commit,path=>{if(path.includes('/annotations'))throw new Error('annotations unavailable');return base(path);}));
  assert.throws(()=>loadUnstartedProviderRecovery({...e.run,run_attempt:9},e.commit,()=>assert.fail('must not read outside bounded attempts')));
});

test('a never-acquired original attempt and provider-skipped guard attempt prove only missing initial sync', () => {
  assert.deepEqual(verifyUnstartedProviderRecovery(unstartedEvidence()), {publisherId:301, correlation});
});
test('all historical attempts and complete authenticated job identity are required', () => {
  for (const mutate of [e=>e.run.run_attempt=3,e=>e.attempts.pop(),e=>e.attempts[1].number=1,e=>e.attempts.reverse(),e=>e.attempts[0].jobs.total_count=2,e=>e.attempts[0].jobs.jobs[0].run_id=102,e=>e.attempts[1].jobs.jobs[0].head_sha='d'.repeat(40),e=>e.attempts[1].jobs.jobs[0].run_attempt=1,e=>e.attempts[0].jobs.jobs[0].check_run_url=`https://api.github.com/repos/other/repo/check-runs/201`,e=>e.attempts[1].jobs.jobs.push({...e.attempts[1].jobs.jobs[0],id:203}),e=>e.run.conclusion='cancelled',e=>e.run.head_repository.full_name='fork/repo']) {
    const e=unstartedEvidence();mutate(e);assert.throws(()=>verifyUnstartedProviderRecovery(e));
  }
});
test('empty steps alone or a network message cannot authorize recovery; partial/unknown execution stays blocked', () => {
  for (const mutate of [e=>delete e.attempts[0].annotations,e=>e.attempts[0].annotations=[],e=>e.attempts[0].annotations[0].message='TLS timeout',e=>e.attempts[0].annotations[0].annotation_level='warning',e=>e.attempts[0].jobs.jobs[0].runner_id=9,e=>e.attempts[0].jobs.jobs[0].runner_name='runner',e=>e.attempts[0].jobs.jobs[0].conclusion='failure',e=>e.attempts[0].jobs.jobs[0].labels=['ubuntu-latest'],e=>e.attempts[1].jobs.jobs[0].steps=[],e=>e.attempts[1].jobs.jobs[0].steps[0].conclusion='success',e=>e.attempts[1].jobs.jobs[0].steps[2].conclusion='failure',e=>e.attempts[1].jobs.jobs[0].steps[2].conclusion='success',e=>e.attempts[1].jobs.jobs[0].steps[2].conclusion=null,e=>{e.attempts[0].jobs.jobs.push({name:'calculate-scores',conclusion:'success'});e.attempts[0].jobs.total_count++;}]) {
    const e=unstartedEvidence();mutate(e);assert.throws(()=>verifyUnstartedProviderRecovery(e));
  }
});
test('publisher must be the exact successful reservation owner for the original publication SHA and correlation', () => {
  for (const mutate of [e=>e.commit.sha='e'.repeat(40),e=>e.commit.message+='\nAgentCrew-Publication: '+correlation,e=>e.statuses=[],e=>e.statuses[0].creator.id=1,e=>e.statuses[0].state='failure',e=>e.statuses[0].context+='-other',e=>e.statuses[0].target_url=`https://github.com/other/repo/actions/runs/301`,e=>e.publisher.id=302,e=>e.publisher.conclusion='failure',e=>e.publisher.status='in_progress',e=>e.publisher.event='pull_request',e=>e.publisher.path='.github/workflows/other.yml',e=>e.publisher.head_repository.full_name='fork/repo',e=>e.publisher.display_title='Publication batch '+ 'f'.repeat(64)]) {
    const e=unstartedEvidence();mutate(e);assert.throws(()=>verifyUnstartedProviderRecovery(e));
  }
});
