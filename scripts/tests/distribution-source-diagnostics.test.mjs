import assert from 'node:assert/strict';
import { test } from 'node:test';
import { verifyDistributionSource, PublicationValidationError } from '../resolve-approved-submission.mjs';
const repository='https://github.com/owner/repo/tree/'+'a'.repeat(40)+'/skills/example';
const secret='synthetic-secret-DO-NOT-LOG';
function invoke(result, inspect=()=>{}) {
 return verifyDistributionSource(repository,'skills/example',{secret,spawn:(program,args,options)=>{inspect(program,args,options);return result;}});
}
test('source verification preserves authenticated success and only exposes numeric HTTP diagnostics',()=>{
 assert.equal(invoke({status:0,stdout:'{"allowed":true,"repositoryId":123}\n200'}),123);
 for (const status of [401,403,429,500,503]) {
  assert.throws(()=>invoke({status:22,stdout:`private upstream response ${secret}\n${status}`,stderr:secret}), e=>e instanceof PublicationValidationError && e.message===`Source distribution verification unavailable (HTTP ${status}; curl exit 22)` && !e.message.includes(secret));
 }
});
test('source verification network and timeout failures stay closed and never log child errors',()=>{
 for (const status of [6,28,60,null]) assert.throws(()=>invoke({status,stdout:'',stderr:secret,error:new Error(secret)}),e=>e instanceof PublicationValidationError && e.message===`Source distribution verification unavailable (HTTP unknown; curl exit ${status===null?'unavailable':status})`);
});
test('source verification keeps credential on stdin, rejects missing auth and invalid authority',()=>{
 invoke({status:0,stdout:'{"allowed":true,"repositoryId":123}\n200'},(program,args,options)=>{
  assert.equal(program,'curl'); assert(!args.join(' ').includes(secret)); assert(options.input.includes(secret));
  assert(args.includes('--fail')); assert(args.includes('--write-out')); assert(!args.includes('--retry'));
 });
 assert.throws(()=>verifyDistributionSource(repository,'skills/example',{secret:'',spawn:()=>assert.fail('no request without auth')}),/not configured/);
 for(const body of ['{"allowed":false,"repositoryId":123}','{"allowed":true}','{"allowed":true,"repositoryId":"123"}','not json']) assert.throws(()=>invoke({status:0,stdout:body+'\n200'}),PublicationValidationError);
});
