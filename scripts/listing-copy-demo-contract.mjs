// In-memory simulation ONLY. This actor registry is not authentication or a server boundary.
export const ALLOWED_FIELDS = Object.freeze([
  'user_title','value_statement','actual_capabilities','use_cases','prompt_templates',
  'output_examples','best_practices','anti_patterns','faq',
]);
export const PROTECTED_FIELDS = Object.freeze([
  'limitations','seo_keywords','version','supported_tools','source_ref','source_url',
  'content_hash','tree_hash','security_audit','skill','meta','manifest',
]);
const ACTORS = Object.freeze({
  'demo-login-user': Object.freeze({role:'submitter',ownership:'unverified'}),
  'demo-verified-user': Object.freeze({role:'submitter',ownership:'verified-maintainer'}),
  'demo-maintainer-role': Object.freeze({role:'maintainer',ownership:'unverified'}),
  'demo-release-role': Object.freeze({role:'publisher',ownership:'unverified'}),
});
const STRUCTURED = Object.freeze({
  use_cases:['title','description','target_user'], prompt_templates:['title','prompt','scenario'],
  output_examples:['input','output'], faq:['question','answer'],
});
const fail = message => {throw new Error(message);};
const clone = value => structuredClone(value);
const canonical = value => JSON.stringify(value, function(key, item) {
  return item && typeof item==='object' && !Array.isArray(item)
    ? Object.fromEntries(Object.keys(item).sort().map(k=>[k,item[k]])) : item;
});
function fingerprint(base) {
  return {packageVersion:base.packageVersion,artifactRevision:base.artifactRevision,
    reportHash:base.reportHash,copyRevision:base.copyRevision,fields:clone(base.fields)};
}
function validateBase(base) {
  if(!base || !/^\d+\.\d+\.\d+$/.test(base.packageVersion) || !Number.isSafeInteger(base.artifactRevision) || base.artifactRevision<1
    || !/^[a-f0-9]{64}$/.test(base.reportHash) || !Number.isSafeInteger(base.copyRevision) || base.copyRevision<0
    || !base.fields || typeof base.fields!=='object' || Array.isArray(base.fields))fail('Invalid base revision');
}
function sameBase(a,b) {validateBase(b);return canonical(fingerprint(a))===canonical(fingerprint(b));}
function text(value,max,key) {
  if(typeof value!=='string'||!value.trim()||value.length>max)fail(`Invalid copy value: ${key}`);
  if(/<\s*script|javascript:|data:text\/html/i.test(value))fail(`Unsafe copy content: ${key}`);
}
function validateDelta(delta,base) {
  if(!delta || typeof delta!=='object'||Array.isArray(delta)||!Object.keys(delta).length)fail('Suggestion is empty');
  for(const [key,value] of Object.entries(delta)) {
    if(!ALLOWED_FIELDS.includes(key))fail(`Field is not editable: ${key}`);
    if(key==='user_title'||key==='value_statement')text(value,key==='user_title'?120:600,key);
    else {
      if(!Array.isArray(value)||value.length<1||value.length>12)fail(`Invalid copy list: ${key}`);
      for(const entry of value) {
        const keys=STRUCTURED[key];
        if(!keys)text(entry,1600,key);
        else {
          if(!entry||typeof entry!=='object'||Array.isArray(entry)||canonical(Object.keys(entry).sort())!==canonical([...keys].sort()))fail(`Invalid structured copy: ${key}`);
          for(const v of Object.values(entry))text(v,1600,key);
        }
      }
    }
  }
  if(base && Object.keys(delta).every(k=>canonical(delta[k])===canonical(base.fields[k])))fail('Suggestion is empty: no changes');
}
// A canonical snapshot binds the mock approval to exact revision + foundation + delta.
// It is intentionally not presented as a signed or cryptographic production receipt.
const approvalBinding = s => canonical({revision:s.revision,base:s.base,delta:s.delta});
export function createSuggestion(base,delta,{submitterId,reason}={}) {
  const actor=Object.hasOwn(ACTORS,submitterId??'')?ACTORS[submitterId]:null;
  if(!actor)fail('An authenticated simulated submitter is required');
  text(reason,1000,'reason');validateBase(base);validateDelta(delta,base);
  return {status:'submitted',revision:1,submitterId,ownership:actor.ownership,
    base:fingerprint(base),delta:clone(delta),changedFields:Object.keys(delta).sort(),reason:reason.trim(),
    approval:null,reviewer:null,publisher:null,receipt:null,history:[]};
}
export function transitionSuggestion(suggestion,next,{actorId,role,reason,updatedDelta,receipt,currentBase}={}) {
  if(!suggestion||!actorId)fail('Invalid transition actor');
  const allowed={submitted:['submitted','changes_requested','rejected','approved'],changes_requested:['submitted','rejected'],approved:['submitted','publishing'],publishing:['published']};
  if(!allowed[suggestion.status]?.includes(next))fail('Invalid suggestion state transition');
  const actor=Object.hasOwn(ACTORS,actorId)?ACTORS[actorId]:null;
  if(['changes_requested','rejected','approved'].includes(next)) {
    if(role!=='maintainer'||actor?.role!=='maintainer')fail('A registered simulated maintainer is required');
    if(actorId===suggestion.submitterId)fail('Submitter cannot self-review');
    text(reason,1000,'review reason');
  }
  if(next==='submitted') {
    if(!actor||role!=='submitter'||actorId!==suggestion.submitterId||!updatedDelta)fail('Submitter must provide a revised delta');
    validateDelta(updatedDelta,suggestion.base);
    if(canonical(updatedDelta)===canonical(suggestion.delta))fail('Invalid state: duplicate revision');
  }
  if(next==='publishing'||next==='published') {
    if(role!=='publisher'||actor?.role!=='publisher'||actorId===suggestion.submitterId||actorId===suggestion.reviewer)fail('A separate registered simulated publisher is required');
    if(!suggestion.approval||suggestion.approval.binding!==approvalBinding(suggestion))fail('Invalid approval binding');
    if(next==='published' && (actorId!==suggestion.publisher||receipt!=='demo-only-no-authoritative-receipt'))fail('A simulated publisher receipt is required');
  }
  const result=clone(suggestion);
  if(['approved','publishing','published'].includes(next) && !sameBase(result.base,currentBase)) {
    result.status='needs_rebase';result.approval=null;
    result.history.push({from:suggestion.status,to:'needs_rebase',actorId,reason:'Foundation changed'});return result;
  }
  if(next==='submitted') {
    result.delta=clone(updatedDelta);result.changedFields=Object.keys(updatedDelta).sort();result.revision++;
    result.approval=null;result.reviewer=null;result.publisher=null;result.receipt=null;
  }
  if(['changes_requested','rejected','approved'].includes(next))result.reviewer=actorId;
  if(next==='approved')result.approval={revision:result.revision,binding:approvalBinding(result)};
  if(next==='publishing')result.publisher=actorId;
  if(next==='published')result.receipt=receipt;
  result.history.push({from:suggestion.status,to:next,actorId,reason:reason?.trim()||null});result.status=next;
  return result;
}
export function applySuggestion(suggestion,currentBase) {
  if(!sameBase(suggestion.base,currentBase))return {...clone(suggestion),status:'needs_rebase',approval:null};
  validateDelta(suggestion.delta,suggestion.base);
  return {status:'preview-only',fields:{...clone(currentBase.fields),...clone(suggestion.delta)},
    base:fingerprint(currentBase),packageUnchanged:true,reportUnchanged:true,publishAuthorizationGranted:false};
}
