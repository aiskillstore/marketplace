import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {validate,preview,publish,ORIGIN} from '../scripts/create-quiz.mjs';

const sample={name:'Alex',answers:[0,1,2,0,3,1,2,0,1,0],lang:'hi'};
const questions=JSON.parse(await readFile(new URL('../references/questions.json',import.meta.url),'utf8'));
assert.equal(questions.length,10);assert.ok(questions.every(q=>q.length===5));
const draft=await preview(sample);assert.equal(draft.mode,'draft');assert.equal(draft.choices[1].choice,'Tea');
for(const invalid of [{...sample,name:''},{...sample,name:'x'.repeat(25)},{...sample,name:'a\nb'},{...sample,answers:[0]},{...sample,answers:Array(10).fill(4)},{...sample,answers:Array(10).fill('0')},{...sample,lang:'unknown'}])assert.throws(()=>validate(invalid));
let calls=0;
const transport=async(url,options)=>{calls++;assert.equal(url,ORIGIN+'/api/quizzes');assert.equal(options.redirect,'error');assert.deepEqual(JSON.parse(options.body),{name:'Alex',answers:sample.answers});return new Response(JSON.stringify({quizUrl:ORIGIN+'/q/ABcd_12345',manageUrl:ORIGIN+'/manage/ABcd_12345/abcdefghijklmnopqrstuvwx'}),{status:201})};
const result=await publish(sample,transport);assert.equal(calls,1);assert.ok(result.quizUrl.endsWith('?lang=hi'));assert.ok(result.manageUrl.includes('/manage/ABcd_12345/'));assert.ok(result.privateLinkWarning);
await assert.rejects(()=>publish(sample,async()=>new Response('Blocked',{status:403})),/HTTP 403/);
await assert.rejects(()=>publish(sample,async()=>new Response(JSON.stringify({quizUrl:'https://evil.example/q/ABcd_12345',manageUrl:ORIGIN+'/manage/ABcd_12345/abcdefghijklmnopqrstuvwx'}),{status:201})),/Unexpected/);
await assert.rejects(()=>publish(sample,async()=>new Response(JSON.stringify({quizUrl:ORIGIN+'/q/ABcd_12345',manageUrl:ORIGIN+'/manage/OtherQuiz9/abcdefghijklmnopqrstuvwx'}),{status:201})),/Unexpected/);
console.log('Offline checks passed: fixed question mapping, validation, public/private URLs, language, blocked responses, and no production requests.');
