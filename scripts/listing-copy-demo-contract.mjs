export const ALLOWED_FIELDS = Object.freeze([
  'user_title','value_statement','actual_capabilities','use_cases','prompt_templates',
  'output_examples','best_practices','anti_patterns','faq',
]);
export const PROTECTED_FIELDS = Object.freeze([
  'limitations','seo_keywords','version','supported_tools','source_ref','source_url',
  'content_hash','tree_hash','security_audit','skill','meta','manifest',
]);
const fingerprint = base => ({packageVersion:base.packageVersion,artifactRevision:base.artifactRevision,
  reportHash:base.reportHash,copyRevision:base.copyRevision,fields:structuredClone(base.fields)});
function sameBase(a,b){return ['packageVersion','artifactRevision','reportHash','copyRevision'].every(k=>a[k]===b[k]);}
function fail(message){throw new Error(message);}
function validateDelta(delta){
  if(!delta||typeof delta!=='object'||Array.isArray(delta)||Object.keys(delta).length===0)fail('Suggestion is empty');
  const blocked=Object.keys(delta).find(k=>!ALLOWED_FIELDS.includes(k));
  if(blocked)fail(`Field is not editable: ${blocked}`);
  for(const [key,value] of Object.entries(delta)){
    if(typeof value==='string') {if(value.length<1||value.length>6000)fail(`Invalid copy length: ${key}`);}
    else if(Array.isArray(value)){
      if(value.length>12||value.some(x=>typeof x!=='string'||!x.trim()||x.length>1600))fail(`Invalid copy list: ${key}`);
    } else if(value&&typeof value==='object'&&['use_cases','prompt_templates','output_examples','faq'].includes(key)){
      const limit=key==='faq'?4:3;
      if(Object.keys(value).length!==limit)fail(`Invalid structured copy: ${key}`);
      const expected=key==='use_cases'?['title','description','target_user']
        :key==='prompt_templates'?['title','prompt','scenario']
        :key==='output_examples'?['input','output']:['question','answer'];
      const list=key==='use_cases'||key==='prompt_templates'?value[key==='use_cases'?'use_cases':'prompt_templates']:null;
      const entries=Array.isArray(list)?list:Object.values(value);
      if(entries.length>12||entries.some(entry=>!entry||typeof entry!=='object'||Object.keys(entry).some(k=>!expected.includes(k))||Object.keys(entry).length===0||Object.values(entry).some(v=>typeof v!=='string'||v.length>1600)))fail(`Invalid structured copy: ${key}`);
    } else fail(`Invalid copy value: ${key}`);
    const text=typeof value==='string'?value:Array.isArray(value)?value.join('\n'):JSON.stringify(value);
    if(/<\s*script|javascript:|data:text\/html/i.test(text))fail(`Unsafe copy content: ${key}`);
  }
}
export function createSuggestion(base,delta,{submitterId,reason,ownership='unverified'}={}){
  if(typeof submitterId!=='string'||!submitterId.trim())fail('An authenticated submitter is required');
  if(typeof reason!=='string'||!reason.trim()||reason.length>1000)fail('A concise reason is required');
  validateDelta(delta);
  if(!base||!/^\d+\.\d+\.\d+$/.test(base.packageVersion)||!Number.isSafeInteger(base.artifactRevision)||base.artifactRevision<1||!/^([a-f0-9]{64})$/.test(base.reportHash)||!Number.isSafeInteger(base.copyRevision))fail('Invalid base revision');
  return {status:'submitted',submitterId:submitterId.trim(),ownership:ownership==='verified-maintainer'?'verified-maintainer':'unverified',
    base:fingerprint(base),delta:structuredClone(delta),changedFields:Object.keys(delta).sort(),reason:reason.trim(),reviewer:null,publisher:null,receipt:null,history:[]};
}
export function transitionSuggestion(suggestion,next,{actorId,role,reason,updatedDelta,receipt}={}){
  if(!suggestion||!actorId)fail('Invalid transition actor');
  const nextCopy=structuredClone(suggestion);
  const allowed={submitted:['changes_requested','rejected','approved'],changes_requested:['submitted','rejected'],approved:['publishing'],publishing:['published','approved']};
  if(!allowed[nextCopy.status]?.includes(next))fail('Invalid suggestion state transition');
  if(['changes_requested','rejected','approved'].includes(next)){
    if(role!=='maintainer')fail('A maintainer is required for review');
    if(actorId===nextCopy.submitterId)fail('Submitter cannot self-review');
    if(!reason?.trim())fail('A review reason is required');
    nextCopy.reviewer=actorId;
  }
  if(next==='submitted'){
    if(role!=='submitter'||actorId!==nextCopy.submitterId||!updatedDelta)fail('Submitter must provide a revised delta');
    validateDelta(updatedDelta); nextCopy.delta=structuredClone(updatedDelta);nextCopy.changedFields=Object.keys(updatedDelta).sort();nextCopy.reviewer=null;
  }
  if(next==='publishing'){
    if(role!=='publisher'||actorId===nextCopy.submitterId||actorId===nextCopy.reviewer)fail('A separate publisher is required');
    nextCopy.publisher=actorId;
  }
  if(next==='published'){
    if(role!=='publisher'||actorId!==nextCopy.publisher||typeof receipt!=='string'||!receipt.trim())fail('A separate publisher receipt is required');
    nextCopy.receipt=receipt;
  }
  nextCopy.history.push({from:suggestion.status,to:next,actorId,reason:reason?.trim()||null});nextCopy.status=next;return nextCopy;
}
export function applySuggestion(suggestion,currentBase){
  if(!sameBase(suggestion.base,currentBase))return {...structuredClone(suggestion),status:'needs_rebase'};
  return {status:'preview-only',fields:{...structuredClone(currentBase.fields),...structuredClone(suggestion.delta)},
    base:fingerprint(currentBase),packageUnchanged:true,reportUnchanged:true,publishAuthorizationGranted:false};
}
