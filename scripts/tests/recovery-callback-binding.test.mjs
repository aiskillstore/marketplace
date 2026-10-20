import test from 'node:test';
import assert from 'node:assert/strict';
import { submissionIdentity, verifyPublishedSubmission } from '../reconcile-submission-sync.mjs';
const id='9d068c0b-c2ea-487d-8df7-2e10e21fbb3a';
const body=`**Submission ID**: \`${id}\``;
const message=`Approve reviewed skills [submission: ${id}]`;
test('recovery binds one callback identity from both approved PR and publication commit',()=>{
  assert.equal(submissionIdentity({body},message),id);
  for(const text of ['',message+message,message.replace(id,'1d068c0b-c2ea-487d-8df7-2e10e21fbb3a')]) assert.throws(()=>submissionIdentity({body},text));
  assert.throws(()=>submissionIdentity({body:body+body},message));
});
test('independent closure verifies callback business state rather than HTTP/job success',()=>{
  const receiver={status:'published',published_at:'2026-10-20T10:15:00Z',published_skill_slugs:['demo']};
  assert.doesNotThrow(()=>verifyPublishedSubmission(['demo'],[receiver]));
  for(const row of [{...receiver,status:'approved'},{...receiver,published_at:null},{...receiver,published_skill_slugs:[]},{...receiver,published_skill_slugs:['demo','extra']},{...receiver,published_skill_slugs:['demo','demo']}]) assert.throws(()=>verifyPublishedSubmission(['demo'],[row]));
  assert.throws(()=>verifyPublishedSubmission(['demo'],[]));
});
