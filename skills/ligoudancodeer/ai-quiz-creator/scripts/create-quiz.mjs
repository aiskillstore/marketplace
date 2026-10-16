import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

export const ORIGIN='https://blockyoutestme.fun';
export const LANGUAGES=['en','es','fr','ms','th','pt','id','fil','ko','de','vi','hi','bn','ta','pa','ja','it','tr','ar','nl','ne','pl','sv','nb','sw'];

export function validate(input){
  if(!input||typeof input!=='object'||Array.isArray(input))throw Error('Expected a quiz object.');
  const name=typeof input.name==='string'?input.name.trim():'';
  if(!name||name.length>24||/[\u0000-\u001f\u007f]/.test(name))throw Error('Nickname must have 1–24 characters and no control characters.');
  if(!Array.isArray(input.answers)||input.answers.length!==10||!input.answers.every(x=>Number.isInteger(x)&&x>=0&&x<=3))throw Error('Provide exactly ten integer answer indices, each from 0 to 3.');
  const lang=input.lang??'en';
  if(!LANGUAGES.includes(lang))throw Error('Unsupported language code.');
  return {name,answers:[...input.answers],lang};
}

export async function preview(input){
  const payload=validate(input);
  const questions=JSON.parse(await readFile(new URL('../references/questions.json',import.meta.url),'utf8'));
  return {mode:'draft',website:ORIGIN+'/',...payload,choices:questions.map((q,i)=>({question:q[0],choice:q[payload.answers[i]+1]})),nextStep:'Review choices; use --publish only when you want this nickname and answer key hosted on the website.'};
}

export async function publish(input,transport=fetch){
  const payload=validate(input);
  const response=await transport(ORIGIN+'/api/quizzes',{
    method:'POST',headers:{'content-type':'application/json'},
    body:JSON.stringify({name:payload.name,answers:payload.answers}),
    redirect:'error',signal:AbortSignal.timeout(15000)
  });
  if(response.status!==201)throw Error(`Website returned HTTP ${response.status}. Creation was not verified; do not automatically retry.`);
  let result;try{result=await response.json()}catch{throw Error('Website returned an unreadable response. Do not automatically retry.')}
  const quiz=new URL(result.quizUrl),manage=new URL(result.manageUrl);
  for(const url of [quiz,manage])if(url.origin!==ORIGIN||url.username||url.password||url.search||url.hash)throw Error('Unexpected result URL; do not share it.');
  const match=quiz.pathname.match(/^\/q\/([A-Za-z0-9_-]{8,32})$/);
  if(!match||!new RegExp('^/manage/'+match[1]+'/[A-Za-z0-9_-]{20,64}$').test(manage.pathname))throw Error('Unexpected quiz/private link pair; do not share it.');
  if(payload.lang!=='en'){quiz.searchParams.set('lang',payload.lang);manage.searchParams.set('lang',payload.lang)}
  return {mode:'published',quizUrl:quiz.href,manageUrl:manage.href,privateLinkWarning:'Bookmark manageUrl privately. Anyone holding it can view scores and delete this quiz. Only quizUrl belongs in an invitation.'};
}

async function main(){
  const args=process.argv.slice(2);
  if(args.includes('--help')){console.log('Usage: node scripts/create-quiz.mjs --input /absolute/path/to/quiz.json [--publish]\nDefault: local draft, no network. Publish sends nickname and ten answers to https://blockyoutestme.fun/api/quizzes.');return}
  let inputPath,publishRequested=false;
  for(let i=0;i<args.length;i++){
    if(args[i]==='--input'&&args[i+1])inputPath=args[++i];
    else if(args[i]==='--publish')publishRequested=true;
    else throw Error('Unknown or incomplete option. Use --help.');
  }
  if(!inputPath)throw Error('Missing --input. Use --help.');
  const input=JSON.parse(await readFile(resolve(inputPath),'utf8'));
  console.log(JSON.stringify(await(publishRequested?publish(input):preview(input)),null,2));
}

if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
  main().catch(error=>{console.error(error?.name==='TimeoutError'?'Request timed out. Creation may have occurred; do not automatically retry.':error.message);process.exitCode=1});
}
