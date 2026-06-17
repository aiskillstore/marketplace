#!/usr/bin/env node
/**
 * Main orchestrator — creates a call, starts tunnel, streams events.
 */

import { AgentCallClient } from './agentcall.js';
import { TunnelClient } from './tunnel.js';
import { createInterface } from 'readline';
import { readFileSync, writeFileSync, unlinkSync, existsSync } from 'fs';

const STATE_FILE = '.agentcall-state.json';

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    meetURL: '',
    mode: 'audio',
    voiceStrategy: 'direct',
    botName: 'Agent',
    port: 3000,
    screensharePort: 3001,
    template: '',
    webpageURL: '',
    screenshareURL: '',
    transcription: false,
    triggerWords: '',
    context: '',
    apiURL: 'https://api.agentcall.dev',
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (!arg.startsWith('--') && !opts.meetURL) {
      opts.meetURL = arg;
    } else if (arg === '--mode') opts.mode = args[++i];
    else if (arg === '--voice-strategy') opts.voiceStrategy = args[++i];
    else if (arg === '--bot-name') opts.botName = args[++i];
    else if (arg === '--port') opts.port = parseInt(args[++i]);
    else if (arg === '--screenshare-port') opts.screensharePort = parseInt(args[++i]);
    else if (arg === '--template') opts.template = args[++i];
    else if (arg === '--webpage-url') opts.webpageURL = args[++i];
    else if (arg === '--screenshare-url') opts.screenshareURL = args[++i];
    else if (arg === '--transcription') opts.transcription = true;
    else if (arg === '--trigger-words') opts.triggerWords = args[++i];
    else if (arg === '--context') opts.context = args[++i];
    else if (arg === '--api-url') opts.apiURL = args[++i];
  }

  if (!opts.meetURL) {
    console.error('Usage: join.js <meet-url> [--mode audio] [--voice-strategy direct] ...');
    process.exit(1);
  }

  return opts;
}

function emit(event) {
  console.log(JSON.stringify(event));
}

function checkExistingState() {
  try {
    if (existsSync(STATE_FILE)) {
      const data = JSON.parse(readFileSync(STATE_FILE, 'utf8'));
      // Expire after 24 hours.
      if (data.created_at) {
        const age = Date.now() - new Date(data.created_at).getTime();
        if (age > 86400000) { // 24 hours in ms
          cleanupState();
          return null;
        }
      }
      return data.call_id;
    }
  } catch {}
  return null;
}

function saveState(callId, opts) {
  writeFileSync(STATE_FILE, JSON.stringify({
    call_id: callId,
    meet_url: opts.meetURL,
    mode: opts.mode,
    created_at: new Date().toISOString(),
  }));
}

function cleanupState() {
  try { unlinkSync(STATE_FILE); } catch {}
}

async function main() {
  const opts = parseArgs();
  const apiKey = process.env.AGENTCALL_API_KEY;
  if (!apiKey) {
    console.error('Error: AGENTCALL_API_KEY environment variable required');
    process.exit(1);
  }

  const client = new AgentCallClient(apiKey, opts.apiURL);
  let callId = checkExistingState();

  if (callId) {
    emit({ event: 'recovering', call_id: callId });
    // Verify call is still active.
    try {
      const existing = await client.getCall(callId);
      if (existing.status === 'ended' || existing.status === 'error') {
        emit({ event: 'recovery_failed', reason: `call already ${existing.status}` });
        cleanupState();
        callId = null;
      }
    } catch (e) {
      emit({ event: 'recovery_failed', reason: 'call not found' });
      cleanupState();
      callId = null;
    }
  }

  if (!callId) {
    const params = {
      meet_url: opts.meetURL,
      bot_name: opts.botName,
      mode: opts.mode,
      voice_strategy: opts.voiceStrategy,
      transcription: opts.transcription,
    };

    if (opts.mode !== 'audio' && !opts.template) {
      if (opts.webpageURL) {
        params.webpage_url = opts.webpageURL;
      } else {
        params.ui_port = opts.port;
      }
      if (opts.screenshareURL) {
        params.screenshare_url = opts.screenshareURL;
      } else {
        params.screenshare_port = opts.screensharePort;
      }
    }
    if (opts.template) params.ui_template = opts.template;

    if (opts.voiceStrategy === 'collaborative') {
      params.collaborative = {
        trigger_words: opts.triggerWords.split(',').filter(Boolean),
        context: opts.context,
      };
    }

    try {
      const result = await client.createCall(params);
      callId = result.call_id;
      saveState(callId, opts);
      emit({
        event: 'call.created',
        call_id: callId,
        ws_url: result.ws_url || '',
        tunnel_url: result.tunnel_url || '',
        status: result.status || '',
      });
    } catch (e) {
      emit({ event: 'error', message: e.message });
      process.exit(1);
    }
  }

  // Start tunnel client if needed (not for public URLs or templates).
  let tunnelClient = null;
  if (opts.mode !== 'audio' && !opts.template && !opts.webpageURL) {
    const wsURL = opts.apiURL.replace('https://', 'wss://').replace('http://', 'ws://');
    tunnelClient = new TunnelClient(
      `${wsURL}/internal/tunnel/connect`,
      result.tunnel_id, result.tunnel_access_key, opts.port
    );
    try {
      await tunnelClient.connect();
    } catch (e) {
      emit({ event: 'tunnel.error', message: e.message });
    }
  }

  // Read stdin for commands.
  const rl = createInterface({ input: process.stdin });
  rl.on('line', (line) => {
    try {
      const cmd = JSON.parse(line.trim());
      client.sendCommand(cmd);
    } catch {}
  });

  // Connect WS and stream events.
  try {
    await client.connectWS(callId, (event) => {
      emit(event);
      if (event.event === 'call.ended' || event.type === 'call.ended') {
        cleanup();
      }
    });
  } catch (e) {
    emit({ event: 'ws.error', message: e.message });
  }

  function cleanup() {
    rl.close();
    if (tunnelClient) tunnelClient.close();
    client.close();
    cleanupState();
    process.exit(0);
  }

  process.on('SIGINT', cleanup);
  process.on('SIGTERM', cleanup);
}

main();
