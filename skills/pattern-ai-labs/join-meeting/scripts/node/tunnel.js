/**
 * Tunnel client — proxies HTTP/WS from AgentCall to localhost.
 */

import WebSocket from 'ws';
import http from 'http';

export class TunnelClient {
  constructor(tunnelWSURL, tunnelId, tunnelAccessKey, localPort = 3000) {
    this.tunnelWSURL = tunnelWSURL;
    this.tunnelId = tunnelId;
    this.tunnelAccessKey = tunnelAccessKey;
    this.localPort = localPort;
    this.ws = null;
    this.running = false;
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.running = true;
      this.ws = new WebSocket(this.tunnelWSURL);

      this.ws.on('open', () => {
        // Register.
        this.ws.send(JSON.stringify({
          type: 'tunnel.register',
          payload: {
            tunnel_id: this.tunnelId,
            tunnel_access_key: this.tunnelAccessKey,
          },
        }));
        console.error(`[tunnel] connected: ${this.tunnelId}`);
        resolve();
      });

      this.ws.on('error', reject);
      this.ws.on('message', (data) => this._handleMessage(JSON.parse(data.toString())));

      this.ws.on('close', () => {
        if (this.running) {
          console.error('[tunnel] disconnected, reconnecting...');
          this._reconnect();
        }
      });

      // Heartbeat.
      this._heartbeatInterval = setInterval(() => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.ping();
        }
      }, 30000);
    });
  }

  _handleMessage(msg) {
    const type = msg.type;

    if (type === 'http.request') {
      this._handleHTTPRequest(msg.payload || msg);
    }
  }

  _handleHTTPRequest(payload) {
    const requestId = payload.request_id;
    const method = payload.method || 'GET';
    const path = payload.path || '/';
    const headers = payload.headers || {};

    const options = {
      hostname: 'localhost',
      port: this.localPort,
      path,
      method,
      headers,
    };

    const body = payload.body || '';

    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        const respHeaders = {};
        for (const [k, v] of Object.entries(res.headers)) {
          respHeaders[k] = Array.isArray(v) ? v[0] : v;
        }
        this.ws.send(JSON.stringify({
          type: 'http.response',
          request_id: requestId,
          payload: {
            request_id: requestId,
            status: res.statusCode,
            headers: respHeaders,
            body,
          },
        }));
      });
    });

    req.on('error', (err) => {
      this.ws.send(JSON.stringify({
        type: 'http.response',
        request_id: requestId,
        payload: {
          request_id: requestId,
          status: 502,
          headers: { 'Content-Type': 'text/plain' },
          body: `Local server error: ${err.message}`,
        },
      }));
    });

    if (body) {
      req.write(body);
    }
    req.end();
  }

  async _reconnect() {
    const delays = [1000, 2000, 4000, 8000, 16000];
    for (const delay of delays) {
      await new Promise((r) => setTimeout(r, delay));
      try {
        await this.connect();
        return;
      } catch (e) {
        console.error(`[tunnel] reconnect failed: ${e.message}`);
      }
    }
    console.error('[tunnel] reconnect failed after all retries');
  }

  close() {
    this.running = false;
    clearInterval(this._heartbeatInterval);
    if (this.ws) this.ws.close();
  }
}
