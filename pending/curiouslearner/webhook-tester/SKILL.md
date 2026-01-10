---
name: webhook-tester
description: Test webhook integrations locally with tunneling, inspection, and debugging tools.
---

# Webhook Tester Skill

Test webhook integrations locally with tunneling, inspection, and debugging tools.

## Instructions

You are a webhook testing expert. When invoked:

1. **Local Webhook Testing**:
   - Set up local webhook receivers
   - Expose localhost to internet using tunnels
   - Capture and inspect webhook payloads
   - Verify webhook signatures
   - Test retry mechanisms

2. **Debugging Webhooks**:
   - Inspect request headers and body
   - Validate webhook signatures
   - Test different payload formats
   - Simulate webhook failures
   - Log and replay webhooks

3. **Integration Testing**:
   - Test webhook delivery
   - Verify idempotency
   - Test retry logic
   - Validate error handling
   - Performance testing

4. **Security Validation**:
   - Verify signature validation
   - Test HTTPS requirements
   - Validate origin checking
   - Test replay attack prevention

## Usage Examples

```
@webhook-tester
@webhook-tester --setup-tunnel
@webhook-tester --inspect
@webhook-tester --verify-signature
@webhook-tester --replay
```

## Tunneling Tools

### ngrok (Most Popular)

#### Basic Setup
```bash
# Install ngrok
# Download from https://ngrok.com/download
# Or use package manager
brew install ngrok/ngrok/ngrok  # macOS
choco install ngrok             # Windows

# Authenticate (get token from ngrok.com)
ngrok config add-authtoken YOUR_TOKEN

# Start tunnel to localhost:3000
ngrok http 3000

# Custom subdomain (requires paid plan)
ngrok http 3000 --subdomain=myapp

# Multiple ports
ngrok http 3000 3001

# Use specific region
ngrok http 3000 --region=us

# Enable inspection UI
ngrok http 3000 --inspect=true
```

#### ngrok Configuration File
```yaml
# ~/.ngrok2/ngrok.yml
version: "2"
authtoken: YOUR_TOKEN

tunnels:
  api:
    addr: 3000
    proto: http
    subdomain: myapi

  webhooks:
    addr: 4000
    proto: http
    subdomain: webhooks

  web:
    addr: 8080
    proto: http
    bind_tls: true

# Start all tunnels
ngrok start --all

# Start specific tunnel
ngrok start api
```

#### ngrok API
```javascript
// Using ngrok programmatically
const ngrok = require('ngrok');

async function startTunnel() {
  const url = await ngrok.connect({
    addr: 3000,
    region: 'us',
    onStatusChange: status => console.log('Status:', status)
  });

  console.log('Tunnel URL:', url);
  // Use this URL as webhook endpoint
  return url;
}

// Cleanup
async function stopTunnel() {
  await ngrok.disconnect();
  await ngrok.kill();
}
```

### Cloudflare Tunnel (Free, No Account Required)

```bash
# Install
brew install cloudflare/cloudflare/cloudflared  # macOS
# Or download from cloudflare.com

# Quick tunnel (no auth required)
cloudflared tunnel --url http://localhost:3000

# Output will be: https://random-words.trycloudflare.com
```

### localtunnel

```bash
# Install
npm install -g localtunnel

# Start tunnel
lt --port 3000

# Custom subdomain (may not be available)
lt --port 3000 --subdomain myapp

# Use localtunnel programmatically
const localtunnel = require('localtunnel');

const tunnel = await localtunnel({ port: 3000 });
console.log('Tunnel URL:', tunnel.url);

tunnel.on('close', () => {
  console.log('Tunnel closed');
});
```

### VS Code Port Forwarding

```bash
# In VS Code with GitHub account
# 1. Open Terminal
# 2. Click "Ports" tab
# 3. Click "Forward a Port"
# 4. Enter port number (e.g., 3000)
# 5. Share the public URL
```

## Webhook Receiver Setup

### Express.js Webhook Endpoint

```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();

// Raw body parser for signature verification
app.use(express.json({
  verify: (req, res, buf) => {
    req.rawBody = buf.toString();
  }
}));

// Webhook endpoint
app.post('/webhooks/github', (req, res) => {
  console.log('Received webhook from GitHub');
  console.log('Headers:', req.headers);
  console.log('Body:', req.body);

  // Verify signature
  const signature = req.headers['x-hub-signature-256'];
  const secret = process.env.WEBHOOK_SECRET;

  if (!verifyGitHubSignature(req.rawBody, signature, secret)) {
    console.error('Invalid signature');
    return res.status(401).send('Invalid signature');
  }

  // Process webhook
  const event = req.headers['x-github-event'];
  handleGitHubEvent(event, req.body);

  // Always respond quickly (GitHub expects response within 10s)
  res.status(200).send('OK');
});

function verifyGitHubSignature(payload, signature, secret) {
  if (!signature) return false;

  const hmac = crypto.createHmac('sha256', secret);
  const digest = 'sha256=' + hmac.update(payload).digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(digest)
  );
}

function handleGitHubEvent(event, payload) {
  switch (event) {
    case 'push':
      console.log('Push event:', payload.ref);
      break;
    case 'pull_request':
      console.log('PR event:', payload.action);
      break;
    default:
      console.log('Unhandled event:', event);
  }
}

// Stripe webhook
app.post('/webhooks/stripe', (req, res) => {
  const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
  const sig = req.headers['stripe-signature'];

  let event;
  try {
    event = stripe.webhooks.constructEvent(
      req.rawBody,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Handle the event
  switch (event.type) {
    case 'payment_intent.succeeded':
      const paymentIntent = event.data.object;
      console.log('PaymentIntent succeeded:', paymentIntent.id);
      break;
    case 'payment_intent.failed':
      console.log('PaymentIntent failed');
      break;
    default:
      console.log(`Unhandled event type ${event.type}`);
  }

  res.json({ received: true });
});

// Generic webhook logger
app.post('/webhooks/:service', (req, res) => {
  const { service } = req.params;

  console.log(`\n${'='.repeat(50)}`);
  console.log(`Webhook received: ${service}`);
  console.log(`Timestamp: ${new Date().toISOString()}`);
  console.log(`${'='.repeat(50)}`);

  console.log('\nHeaders:');
  Object.entries(req.headers).forEach(([key, value]) => {
    console.log(`  ${key}: ${value}`);
  });

  console.log('\nBody:');
  console.log(JSON.stringify(req.body, null, 2));

  console.log(`${'='.repeat(50)}\n`);

  res.status(200).json({ received: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Webhook receiver listening on port ${PORT}`);
});
```

### Python Flask Webhook Receiver

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import os

app = Flask(__name__)

@app.route('/webhooks/github', methods=['POST'])
def github_webhook():
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    secret = os.getenv('WEBHOOK_SECRET')

    if not verify_github_signature(request.data, signature, secret):
        return 'Invalid signature', 401

    event = request.headers.get('X-GitHub-Event')
    payload = request.json

    print(f'Received {event} event')
    print(f'Payload: {payload}')

    # Process event
    handle_github_event(event, payload)

    return 'OK', 200

def verify_github_signature(payload, signature, secret):
    if not signature:
        return False

    mac = hmac.new(
        secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    )
    expected = 'sha256=' + mac.hexdigest()

    return hmac.compare_digest(expected, signature)

def handle_github_event(event, payload):
    if event == 'push':
        print(f"Push to {payload['ref']}")
    elif event == 'pull_request':
        print(f"PR {payload['action']}")

@app.route('/webhooks/<service>', methods=['POST'])
def generic_webhook(service):
    print(f'\n{"=" * 50}')
    print(f'Webhook received: {service}')
    print(f'{"=" * 50}')

    print('\nHeaders:')
    for key, value in request.headers:
        print(f'  {key}: {value}')

    print('\nBody:')
    print(request.get_data(as_text=True))

    return jsonify({'received': True}), 200

if __name__ == '__main__':
    app.run(port=3000)
```

## Webhook Testing Tools

### webhook.site (Online Tool)

```bash
# 1. Visit https://webhook.site
# 2. Get unique URL (e.g., https://webhook.site/abc-123)
# 3. Use this URL as webhook endpoint
# 4. View all incoming requests in real-time

# Features:
# - Unique URL per session
# - View request headers and body
# - Custom response configuration
# - Request history
# - Share URL with team
```

### Postman

```javascript
// 1. Create Mock Server in Postman
// 2. Add webhook endpoint
// 3. Configure response
// 4. Use mock URL as webhook endpoint

// Example Mock Server Response
{
  "statusCode": 200,
  "body": {
    "received": true,
    "timestamp": "{{$timestamp}}"
  }
}
```

### Webhook Testing CLI

```javascript
// webhook-cli.js
const express = require('express');
const chalk = require('chalk');

class WebhookTester {
  constructor(port = 3000) {
    this.app = express();
    this.port = port;
    this.requests = [];

    this.setupMiddleware();
    this.setupRoutes();
  }

  setupMiddleware() {
    this.app.use(express.json({
      verify: (req, res, buf) => {
        req.rawBody = buf.toString();
      }
    }));
  }

  setupRoutes() {
    // Catch all webhook requests
    this.app.all('/webhooks/*', (req, res) => {
      const webhook = {
        timestamp: new Date().toISOString(),
        method: req.method,
        path: req.path,
        headers: req.headers,
        body: req.body,
        query: req.query
      };

      this.requests.push(webhook);
      this.logWebhook(webhook);

      res.status(200).json({ received: true });
    });
  }

  logWebhook(webhook) {
    console.log(chalk.blue('\n' + '='.repeat(60)));
    console.log(chalk.green('Webhook Received'));
    console.log(chalk.blue('='.repeat(60)));

    console.log(chalk.yellow('\nTimestamp:'), webhook.timestamp);
    console.log(chalk.yellow('Method:'), webhook.method);
    console.log(chalk.yellow('Path:'), webhook.path);

    console.log(chalk.yellow('\nHeaders:'));
    Object.entries(webhook.headers).forEach(([key, value]) => {
      console.log(`  ${chalk.gray(key)}: ${value}`);
    });

    if (Object.keys(webhook.query).length > 0) {
      console.log(chalk.yellow('\nQuery:'));
      console.log(JSON.stringify(webhook.query, null, 2));
    }

    console.log(chalk.yellow('\nBody:'));
    console.log(JSON.stringify(webhook.body, null, 2));

    console.log(chalk.blue('='.repeat(60) + '\n'));
  }

  start() {
    this.app.listen(this.port, () => {
      console.log(chalk.green(`\nWebhook tester running on http://localhost:${this.port}`));
      console.log(chalk.gray('Waiting for webhooks...\n'));
    });
  }

  getHistory() {
    return this.requests;
  }

  clearHistory() {
    this.requests = [];
    console.log(chalk.yellow('History cleared'));
  }
}

// Usage
const tester = new WebhookTester(3000);
tester.start();
```

## Testing Webhook Signatures

### GitHub Webhook Signature

```javascript
const crypto = require('crypto');

function verifyGitHubWebhook(payload, signature, secret) {
  if (!signature || !signature.startsWith('sha256=')) {
    return false;
  }

  const hmac = crypto.createHmac('sha256', secret);
  const digest = 'sha256=' + hmac.update(payload).digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(digest)
  );
}

// Test
const payload = JSON.stringify({ test: 'data' });
const secret = 'my-webhook-secret';
const signature = 'sha256=' + crypto
  .createHmac('sha256', secret)
  .update(payload)
  .digest('hex');

console.log('Valid:', verifyGitHubWebhook(payload, signature, secret));
```

### Stripe Webhook Signature

```javascript
const stripe = require('stripe')('sk_test_...');

app.post('/webhooks/stripe', async (req, res) => {
  const sig = req.headers['stripe-signature'];
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  let event;

  try {
    event = stripe.webhooks.constructEvent(
      req.rawBody,
      sig,
      webhookSecret
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Process the event
  console.log('Event:', event.type);
  res.json({ received: true });
});
```

### Shopify HMAC Verification

```javascript
const crypto = require('crypto');

function verifyShopifyWebhook(body, hmacHeader, secret) {
  const hash = crypto
    .createHmac('sha256', secret)
    .update(body, 'utf8')
    .digest('base64');

  return crypto.timingSafeEqual(
    Buffer.from(hash),
    Buffer.from(hmacHeader)
  );
}

app.post('/webhooks/shopify', (req, res) => {
  const hmac = req.headers['x-shopify-hmac-sha256'];
  const secret = process.env.SHOPIFY_SECRET;

  if (!verifyShopifyWebhook(req.rawBody, hmac, secret)) {
    return res.status(401).send('Invalid signature');
  }

  res.status(200).send('OK');
});
```

## Automated Webhook Testing

### Jest Tests

```javascript
const request = require('supertest');
const app = require('./app');
const crypto = require('crypto');

describe('Webhook Tests', () => {
  const webhookSecret = 'test-secret';

  function generateSignature(payload) {
    return 'sha256=' + crypto
      .createHmac('sha256', webhookSecret)
      .update(JSON.stringify(payload))
      .digest('hex');
  }

  describe('POST /webhooks/github', () => {
    test('should accept valid webhook', async () => {
      const payload = {
        ref: 'refs/heads/main',
        commits: []
      };

      const signature = generateSignature(payload);

      const response = await request(app)
        .post('/webhooks/github')
        .set('X-Hub-Signature-256', signature)
        .set('X-GitHub-Event', 'push')
        .send(payload);

      expect(response.status).toBe(200);
    });

    test('should reject invalid signature', async () => {
      const payload = { test: 'data' };

      const response = await request(app)
        .post('/webhooks/github')
        .set('X-Hub-Signature-256', 'invalid')
        .set('X-GitHub-Event', 'push')
        .send(payload);

      expect(response.status).toBe(401);
    });

    test('should reject missing signature', async () => {
      const payload = { test: 'data' };

      const response = await request(app)
        .post('/webhooks/github')
        .set('X-GitHub-Event', 'push')
        .send(payload);

      expect(response.status).toBe(401);
    });
  });
});
```

## Webhook Replay and Debugging

### Request Storage

```javascript
const fs = require('fs').promises;
const path = require('path');

class WebhookStorage {
  constructor(storageDir = './webhooks') {
    this.storageDir = storageDir;
  }

  async saveWebhook(webhook) {
    const filename = `${Date.now()}-${webhook.path.replace(/\//g, '-')}.json`;
    const filepath = path.join(this.storageDir, filename);

    await fs.mkdir(this.storageDir, { recursive: true });
    await fs.writeFile(filepath, JSON.stringify(webhook, null, 2));

    console.log('Webhook saved:', filepath);
  }

  async loadWebhook(filename) {
    const filepath = path.join(this.storageDir, filename);
    const content = await fs.readFile(filepath, 'utf8');
    return JSON.parse(content);
  }

  async replayWebhook(filename) {
    const webhook = await this.loadWebhook(filename);

    const response = await fetch(`http://localhost:3000${webhook.path}`, {
      method: webhook.method,
      headers: webhook.headers,
      body: JSON.stringify(webhook.body)
    });

    console.log('Replayed webhook:', filename);
    console.log('Response:', response.status);
  }
}
```

## Webhook Retry Testing

### Retry Simulation

```javascript
app.post('/webhooks/test-retry', async (req, res) => {
  const attemptNumber = parseInt(req.headers['x-attempt'] || '1');
  const maxAttempts = 3;

  console.log(`Attempt ${attemptNumber}/${maxAttempts}`);

  // Fail first 2 attempts
  if (attemptNumber < maxAttempts) {
    console.log('Simulating failure');
    return res.status(500).send('Temporary error');
  }

  console.log('Success on final attempt');
  res.status(200).send('OK');
});

// Retry logic (sender side)
async function sendWebhookWithRetry(url, payload, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Attempt': attempt.toString()
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        console.log(`Webhook delivered on attempt ${attempt}`);
        return response;
      }

      console.log(`Attempt ${attempt} failed: ${response.status}`);
    } catch (error) {
      console.log(`Attempt ${attempt} error:`, error.message);
    }

    // Exponential backoff
    if (attempt < maxRetries) {
      const delay = Math.pow(2, attempt) * 1000;
      console.log(`Waiting ${delay}ms before retry...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw new Error('All webhook delivery attempts failed');
}
```

## Best Practices

### Webhook Receiver
- Respond quickly (within 10 seconds)
- Always return 200 for valid requests
- Process webhooks asynchronously
- Implement idempotency
- Verify signatures
- Log all webhooks for debugging

### Security
- Always verify webhook signatures
- Use HTTPS endpoints
- Validate webhook origin
- Implement rate limiting
- Store secrets securely
- Check for replay attacks

### Error Handling
- Handle missing/invalid signatures gracefully
- Log all errors
- Implement retry logic with exponential backoff
- Alert on repeated failures
- Monitor webhook health

### Testing
- Test signature verification
- Simulate failures and retries
- Test idempotency
- Verify error handling
- Load test webhook endpoints
- Test with real payloads

## Common Webhook Providers

### GitHub
```
Signature Header: X-Hub-Signature-256
Event Header: X-GitHub-Event
Algorithm: HMAC SHA-256
```

### Stripe
```
Signature Header: Stripe-Signature
Algorithm: HMAC SHA-256 (special format)
Test Mode: Use Stripe CLI
```

### Shopify
```
Signature Header: X-Shopify-Hmac-SHA256
Algorithm: HMAC SHA-256 (base64)
Topic Header: X-Shopify-Topic
```

### Twilio
```
Signature Header: X-Twilio-Signature
Algorithm: HMAC SHA-1
Validation: Special URL + params
```

### Slack
```
Signature Header: X-Slack-Signature
Timestamp Header: X-Slack-Request-Timestamp
Algorithm: HMAC SHA-256
```

## Notes

- Use tunneling tools (ngrok, cloudflared) for local testing
- Always verify webhook signatures in production
- Respond to webhooks quickly (< 10s)
- Process webhooks asynchronously
- Implement idempotency using webhook IDs
- Log all webhooks for debugging
- Test retry mechanisms
- Monitor webhook delivery failures
- Use webhook testing tools during development
- Store webhook secrets securely
- Implement proper error handling
- Test with real payloads from providers
