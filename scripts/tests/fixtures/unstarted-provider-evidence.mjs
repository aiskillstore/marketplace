import { createHash } from 'node:crypto';

const repo = 'aiskillstore/marketplace';
const commitSha = 'a'.repeat(40), head = 'b'.repeat(40), merge = 'c'.repeat(40);
export const correlation = `submission-pr-42-${head}-${merge}`;
const digest = createHash('sha256').update(correlation).digest('hex');
export function unstartedEvidence() {
  const run = {id:101, run_attempt:2, event:'push', status:'completed', conclusion:'failure', head_sha:commitSha, head_branch:'main', head_repository:{full_name:repo}, path:'.github/workflows/sync-to-supabase.yml'};
  const job = (attempt, id) => ({id, run_id:run.id, run_attempt:attempt, head_sha:commitSha, name:'sync', status:'completed', conclusion:attempt===1?'cancelled':'failure', check_run_url:`https://api.github.com/repos/${repo}/check-runs/${id}`, runner_id:attempt===1?0:9, runner_name:attempt===1?'':'runner', labels:['self-hosted'], steps:attempt===1?[]:[{name:'Guard provider write against workflow reruns',conclusion:'failure'},{name:'Wait for authoritative publication completion',conclusion:'skipped'},{name:'Sync skills to Supabase',conclusion:'skipped'}]});
  return {run, commit:{sha:commitSha, message:`Publication\n\nAgentCrew-Publication: ${correlation}`}, attempts:[
    {number:1,jobs:{total_count:1,jobs:[job(1,201)]},annotations:[{annotation_level:'failure',message:'The job was not acquired by Runner of type self-hosted even after multiple attempts'}]},
    {number:2,jobs:{total_count:1,jobs:[job(2,202)]}}
  ], statuses:[{context:`agentcrew/publication/${digest}`,state:'pending',creator:{id:254047988,login:'ai-skill-store[bot]'},target_url:`https://github.com/${repo}/actions/runs/301`}], publisher:{id:301,event:'workflow_dispatch',status:'completed',conclusion:'success',path:'.github/workflows/publish-approved-batch.yml',head_branch:'main',head_repository:{full_name:repo},display_title:`Publication batch ${digest}`}};
}

