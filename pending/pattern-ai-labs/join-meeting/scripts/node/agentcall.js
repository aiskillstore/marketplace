/**
 * AgentCall API client for Node.js.
 */

import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import WebSocket from 'ws';

const CONFIG_PATH = join(homedir(), '.agentcall', 'config.json');

function loadConfig() {
  if (existsSync(CONFIG_PATH)) {
    try {
      return JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));
    } catch { /* ignore */ }
  }
  return {};
}

export class AgentCallClient {
  constructor(apiKey, baseURL) {
    const cfg = loadConfig();
    this.apiKey = apiKey || process.env.AGENTCALL_API_KEY || cfg.api_key || '';
    this.baseURL = baseURL || process.env.AGENTCALL_API_URL || cfg.api_url || 'https://api.agentcall.dev';
    this.ws = null;
  }

  async _fetch(method, path, body) {
    const url = `${this.baseURL}${path}`;
    const opts = {
      method,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
    };
    if (body) opts.body = JSON.stringify(body);
    const resp = await fetch(url, opts);
    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`API error ${resp.status}: ${text}`);
    }
    return resp.json();
  }

  // --- Call Management ---

  async createCall(params) {
    return this._fetch('POST', '/v1/calls', params);
  }

  async getCall(callId) {
    return this._fetch('GET', `/v1/calls/${callId}`);
  }

  async endCall(callId) {
    return this._fetch('DELETE', `/v1/calls/${callId}`);
  }

  async listCalls() {
    return this._fetch('GET', '/v1/calls');
  }

  async getTranscript(callId, format = 'json') {
    return this._fetch('GET', `/v1/calls/${callId}/transcript?format=${format}`);
  }

  // --- WebSocket ---

  connectWS(callId, onEvent) {
    const wsURL = this.baseURL.replace('https://', 'wss://').replace('http://', 'ws://');
    const uri = `${wsURL}/v1/calls/${callId}/ws?api_key=${this.apiKey}`;

    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(uri);

      this.ws.on('open', () => resolve());
      this.ws.on('error', (err) => reject(err));
      this.ws.on('message', (data) => {
        const event = JSON.parse(data.toString());
        onEvent(event);
      });
      this.ws.on('close', () => {
        onEvent({ event: 'ws.closed' });
      });
    });
  }

  sendCommand(command) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(command));
    }
  }

  close() {
    if (this.ws) this.ws.close();
  }

  // --- TTS ---

  async ttsGenerate(text, voice = 'af_heart', speed = 1.0) {
    return this._fetch('POST', '/v1/tts/generate', { text, voice, speed });
  }

  async ttsVoices() {
    return this._fetch('GET', '/v1/tts/voices');
  }
}
