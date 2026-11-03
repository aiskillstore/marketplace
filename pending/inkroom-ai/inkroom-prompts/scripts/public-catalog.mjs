// MIT. Shared keyless catalog client for the standalone Skill and MCP server.
// This module does not read configuration files, credentials or environment variables.
import {PromptError} from './client.mjs';

export const PUBLIC_CATALOG_ENDPOINT = 'https://mcp.inkroom.ai';
const MAX_RESPONSE_BYTES = 512 * 1024;
const PROTOCOL_VERSION = '2025-03-26';

export function publicCapabilities() {
  return {
    kind:'capabilities', scope:'public_information', serviceStatus:'not_checked',
    tools:[
      {name:'help',purpose:'Local capability and cost-boundary descriptions.',upstreamModelTokens:false},
      {name:'list_models',purpose:'Current public InkRoom model names, parameters and official sale prices from the main public MCP catalog.',upstreamModelTokens:false},
      {name:'search_prompts',purpose:'Public prompt-library lookup with original examples.',upstreamModelTokens:false},
      {name:'optimize_prompt',purpose:'Explicit rewriting or one optimization after a successful empty search, within the existing free quota.',upstreamModelTokens:true},
    ],
    catalog:{endpoint:PUBLIC_CATALOG_ENDPOINT,authentication:'none',pricing:'InkRoom official public sale prices; not upstream vendor prices or account authorization.'},
    limits:'No image generation, private account access or task recovery. Catalog and search errors never trigger optimization or another provider.',
  };
}

function catalogEndpoint(value) {
  let url;
  try { url = new URL(value); } catch { throw new PromptError('invalid_origin','Invalid public MCP catalog address.'); }
  const local = ['localhost','127.0.0.1','[::1]'].includes(url.hostname);
  if ((url.protocol !== 'https:' && !(local && url.protocol === 'http:')) || url.username || url.password || url.search || url.hash)
    throw new PromptError('invalid_origin','Public MCP catalog must use HTTPS without credentials, a query or fragment. HTTP is allowed only for localhost.');
  return url.href;
}

function rpcValue(value, id) {
  if (!value || value.jsonrpc !== '2.0' || value.id !== id) return null;
  if (value.error) throw new PromptError('mcp_error',typeof value.error.message === 'string' ? value.error.message.slice(0,2048) : 'Public MCP returned a protocol error.');
  if (!value.result || typeof value.result !== 'object' || Array.isArray(value.result))
    throw new PromptError('invalid_response','Public MCP returned an invalid result.');
  return value.result;
}

async function readRPC(response, id) {
  const type = response.headers.get('content-type')?.toLowerCase() || '';
  if (!type.includes('application/json') && !type.includes('text/event-stream')) {
    await response.body?.cancel(); throw new PromptError('invalid_response','Expected JSON or an MCP event stream from the public catalog.');
  }
  const reader = response.body?.getReader();
  if (!reader) throw new PromptError('invalid_response','Empty public MCP response.');
  let size = 0; let text = ''; const decoder = new TextDecoder();
  const parse = (source) => {
    try { return JSON.parse(source); }
    catch { throw new PromptError('invalid_response','Public MCP returned malformed JSON.'); }
  };
  try {
    while (true) {
      const {done,value} = await reader.read();
      if (value) {
        size += value.byteLength;
        if (size > MAX_RESPONSE_BYTES) throw new PromptError('response_too_large','Public MCP catalog response exceeds 512 KiB.');
        text += decoder.decode(value,{stream:!done});
      }
      if (type.includes('text/event-stream')) {
        text = text.replace(/\r\n/g,'\n');
        let boundary;
        while ((boundary = text.indexOf('\n\n')) >= 0) {
          const event = text.slice(0,boundary); text = text.slice(boundary+2);
          const data = event.split('\n').filter(line => line.startsWith('data:')).map(line => line.slice(5).replace(/^ /,'')).join('\n');
          if (!data) continue;
          const result = rpcValue(parse(data),id);
          if (result) return result;
        }
        if (done) throw new PromptError('invalid_response','Public MCP event stream ended without the requested result.');
      } else if (done) {
        const result = rpcValue(parse(text),id);
        if (!result) throw new PromptError('invalid_response','Public MCP returned a mismatched response ID.');
        return result;
      }
    }
  } catch (error) {
    if (error instanceof PromptError) throw error;
    throw new PromptError('network_error','Public MCP response was interrupted. No retry or optimization was attempted.');
  } finally { await reader.cancel().catch(() => {}); reader.releaseLock(); }
}

export class PublicCatalogClient {
  constructor({endpoint = PUBLIC_CATALOG_ENDPOINT,fetchImpl = globalThis.fetch,timeoutMs = 15000} = {}) {
    this.endpoint = catalogEndpoint(endpoint); this.fetch = fetchImpl; this.timeoutMs = timeoutMs;
  }
  async post(message,{signal,session,protocol} = {}) {
    let response;
    try {
      response = await this.fetch(this.endpoint,{
        method:'POST',redirect:'error',credentials:'omit',signal,
        headers:{'Accept':'application/json, text/event-stream','Content-Type':'application/json',
          ...(session ? {'Mcp-Session-Id':session} : {}), ...(protocol ? {'MCP-Protocol-Version':protocol} : {})},
        body:JSON.stringify(message),
      });
    } catch {
      throw new PromptError(signal?.aborted ? 'timeout_or_cancelled' : 'network_error','Public InkRoom catalog did not respond. No retry or optimization was attempted.');
    }
    if (!response.ok) {
      const retry = response.headers.get('retry-after');
      const retryAfter = retry && /^\d+$/.test(retry) ? Number(retry) : null;
      await response.body?.cancel();
      const errors = {
        401:['public_catalog_unavailable','The public catalog endpoint still requires authentication. Public access must be enabled by the operator; no Token is requested or retried.'],
        403:['public_catalog_forbidden','The public catalog request was denied. No credentials or alternate provider were tried.'],
        404:['service_not_released','The public InkRoom catalog endpoint has not been released.'],
        429:['rate_limited','Public catalog usage limit reached. Respect Retry-After; no retry or optimization was attempted.'],
        503:['unavailable','The public InkRoom catalog is temporarily unavailable.'],
      };
      const [code,message] = errors[response.status] || ['service_error',`Public InkRoom catalog returned HTTP ${response.status}.`];
      throw new PromptError(code,message,retryAfter);
    }
    return response;
  }
  async models({signal} = {}) {
    const timeout = AbortSignal.timeout(this.timeoutMs);
    const combined = signal ? AbortSignal.any([signal,timeout]) : timeout;
    const initialized = await this.post({jsonrpc:'2.0',id:1,method:'initialize',params:{protocolVersion:PROTOCOL_VERSION,capabilities:{},clientInfo:{name:'inkroom-prompts-public-catalog',version:'1.0.4'}}},{signal:combined});
    const session = initialized.headers.get('mcp-session-id');
    const info = await readRPC(initialized,1);
    if (typeof info.protocolVersion !== 'string' || !info.serverInfo || !info.capabilities)
      throw new PromptError('invalid_response','Public MCP initialization did not return protocol and server capabilities.');
    const options = {signal:combined,session,protocol:info.protocolVersion};
    const notice = await this.post({jsonrpc:'2.0',method:'notifications/initialized'},options);
    await notice.body?.cancel();
    const response = await this.post({jsonrpc:'2.0',id:2,method:'tools/call',params:{name:'list_models',arguments:{includeUnavailable:false}}},options);
    const tool = await readRPC(response,2);
    if (tool.isError) throw new PromptError('catalog_error','Public InkRoom catalog tool reported an error. No retry or optimization was attempted.');
    let value = tool.structuredContent;
    if (!value && Array.isArray(tool.content)) {
      const text = tool.content.find(item => item.type === 'text' && typeof item.text === 'string')?.text;
      try { value = JSON.parse(text); } catch { /* Reject a non-structured catalog below. */ }
    }
    if (!value || !Array.isArray(value.models) || !value.models.every(model => model && typeof model.id === 'string'))
      throw new PromptError('invalid_response','Public MCP did not return a model catalog.');
    return value;
  }
}
