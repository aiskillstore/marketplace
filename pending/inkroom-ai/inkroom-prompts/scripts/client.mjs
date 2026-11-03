// MIT. Shared by the standalone Skill and the MCP server. No credentials.
export class PromptError extends Error {
  constructor(code, message, retryAfter = null) {
    super(message); this.name = 'PromptError'; this.code = code; this.retryAfter = retryAfter;
  }
}
export function serviceOrigin(value = 'https://prompts.inkroom.ai') {
  const url = new URL(value);
  const local = ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname);
  if ((url.protocol !== 'https:' && !(local && url.protocol === 'http:')) || url.username || url.password || url.search || url.hash || url.pathname !== '/') {
    throw new PromptError('invalid_origin', 'Service address must be an HTTPS origin (HTTP is allowed for localhost).');
  }
  return url.origin;
}
export function queryText(value, max) {
  if (typeof value !== 'string' || !value.trim() || [...value.trim()].length > max) {
    throw new PromptError('invalid_input', `Provide 1–${max} characters of keywords or an image idea.`);
  }
  return value.trim();
}
function publicURL(value, image = false) {
  if (typeof value !== 'string') return null;
  try {
    const url = new URL(value);
    if (url.protocol !== 'https:' || url.username || url.password) return null;
    if (image && (url.hostname !== 'static.inkroom.ai' || url.port || !url.pathname.startsWith('/api/prompt-assets/') || url.search || url.hash)) return null;
    return url.href;
  } catch { return null; }
}
export class PromptClient {
  constructor({origin, fetchImpl = globalThis.fetch, timeoutMs = 35000} = {}) {
    this.origin = serviceOrigin(origin); this.fetch = fetchImpl; this.timeoutMs = timeoutMs;
  }
  async request(path, {body, signal} = {}) {
    const timeout = AbortSignal.timeout(this.timeoutMs);
    const combined = signal ? AbortSignal.any([signal, timeout]) : timeout;
    let response;
    try {
      response = await this.fetch(this.origin + path, {
        method: body ? 'POST' : 'GET', redirect: 'error', credentials: 'omit',
        headers: {'Accept':'application/json', ...(body ? {'Content-Type':'application/json'} : {})},
        ...(body ? {body:JSON.stringify(body)} : {}), signal:combined
      });
    } catch {
      throw new PromptError(combined.aborted ? 'timeout_or_cancelled' : 'network_error', 'InkRoom did not return a result. No automatic retry was made.');
    }
    const retry = response.headers.get('retry-after');
    const retryAfter = retry && /^\d+$/.test(retry) ? Number(retry) : null;
    if (!response.ok) {
      await response.body?.cancel();
      const messages = {
        400:['invalid_input','Check the keywords and input length.'],
        404:['service_not_released','This InkRoom service endpoint has not been released yet. No Key is needed.'],
        429:['rate_limited','Free usage limit reached. Try later; do not create parallel retries.'],
        502:['optimizer_failed','The optimizer did not return a usable result. No image was generated.'],
        503:['unavailable','InkRoom prompt service or its free optimizer is temporarily unavailable. No Key is needed.']
      };
      const [code,message] = messages[response.status] || ['service_error',`InkRoom returned HTTP ${response.status}.`];
      throw new PromptError(code,message,retryAfter);
    }
    if (!response.headers.get('content-type')?.includes('application/json')) {
      await response.body?.cancel(); throw new PromptError('invalid_response','Expected a JSON response from InkRoom.');
    }
    const reader = response.body?.getReader();
    if (!reader) throw new PromptError('invalid_response','Empty InkRoom response.');
    const chunks = []; let size = 0;
    try {
      while (true) {
        const {done,value} = await reader.read(); if (done) break;
        size += value.byteLength;
        if (size > 512 * 1024) { await reader.cancel(); throw new PromptError('response_too_large','InkRoom response exceeds 512 KiB.'); }
        chunks.push(value);
      }
    } catch (error) {
      if (error instanceof PromptError) throw error;
      throw new PromptError('network_error','The response was interrupted. No automatic retry was made.');
    } finally { reader.releaseLock(); }
    const bytes = new Uint8Array(size); let offset = 0;
    for (const chunk of chunks) { bytes.set(chunk,offset); offset += chunk.byteLength; }
    try { return JSON.parse(new TextDecoder().decode(bytes)); }
    catch { throw new PromptError('invalid_response','InkRoom returned invalid JSON.'); }
  }
  async search(query, {limit = 3, signal} = {}) {
    query = queryText(query,200);
    if (!Number.isInteger(limit) || limit < 1 || limit > 5) throw new PromptError('invalid_input','limit must be 1–5.');
    const value = await this.request(`/api/prompts/assistant/search?${new URLSearchParams({query,limit:String(limit)})}`,{signal});
    if (value?.kind !== 'library' || !Array.isArray(value.items) || value.items.length > limit) throw new PromptError('invalid_response','Invalid library response.');
    const items = value.items.map(item => {
      if (!item || typeof item.id !== 'string' || typeof item.prompt !== 'string' || typeof item.title !== 'string' || item.prompt.length > 100000) throw new PromptError('invalid_response','Invalid prompt record.');
      return {id:item.id, title:item.title, prompt:item.prompt,
        tags:Array.isArray(item.tags) ? item.tags.filter(tag => typeof tag === 'string') : [],
        exampleImageUrl:publicURL(item.exampleImageUrl,true), sourceUrl:publicURL(item.sourceUrl)};
    });
    return {kind:'library',query,items,hasMore:value.hasMore === true,optimizationAvailable:value.optimizationAvailable === true};
  }
  async optimize(query, {signal} = {}) {
    const value = await this.request('/api/prompts/assistant/optimize',{body:{query:queryText(query,500)},signal});
    if (value?.kind !== 'optimized' || typeof value.prompt !== 'string' || !value.prompt.trim() || value.prompt.length > 16000) throw new PromptError('invalid_response','Invalid optimized prompt.');
    return {kind:'optimized',prompt:value.prompt,model:typeof value.model === 'string' ? value.model : '',exampleImageUrl:null};
  }
}
