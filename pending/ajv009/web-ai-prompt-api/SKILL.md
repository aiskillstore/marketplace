---
name: web-ai-prompt-api
description: Chrome's built-in Prompt API implementation guide. Use Gemini Nano locally in browser for AI features - session management, multimodal input, structured output, streaming, Chrome Extensions. Reference for all Prompt API development.
---

# Chrome Prompt API Reference

Complete implementation guide for Chrome's built-in Prompt API using Gemini Nano.

## Hardware & OS Requirements

**OS:** Windows 10/11, macOS 13+ (Ventura+), Linux, ChromeOS (Platform 16389.0.0+) on Chromebook Plus
**Storage:** 22 GB free (model downloaded separately)
**GPU:** >4 GB VRAM OR **CPU:** 16 GB RAM + 4 cores
**Network:** Unmetered connection for download
**Chrome:** 138+ (Extensions in stable, Web in origin trial)

**Not supported:** Mobile (Android, iOS), non-Chromebook Plus ChromeOS

Check model size: `chrome://on-device-internals`
Model removed if storage <10 GB after download.

## Language Support

From Chrome 140: English, Spanish, Japanese (input/output)

## Availability Check

```javascript
const availability = await LanguageModel.availability();
// Returns: "unavailable" | "downloadable" | "downloading" | "available"
```

**CRITICAL:** Always pass same options to `availability()` as you use in `create()`. Some models don't support certain modalities/languages.

## Model Parameters

```javascript
await LanguageModel.params();
// { defaultTopK: 3, maxTopK: 128, defaultTemperature: 1, maxTemperature: 2 }
```

## Session Creation

### Basic Session

```javascript
const session = await LanguageModel.create();
```

### With Custom Parameters

```javascript
const params = await LanguageModel.params();
const session = await LanguageModel.create({
  temperature: Math.min(params.defaultTemperature * 1.2, 2.0),
  topK: params.defaultTopK
});
```

### With Download Monitoring

```javascript
const session = await LanguageModel.create({
  monitor(m) {
    m.addEventListener('downloadprogress', (e) => {
      console.log(`Downloaded ${e.loaded * 100}%`);
    });
  }
});
```

### With AbortSignal

```javascript
const controller = new AbortController();
stopButton.onclick = () => controller.abort();

const session = await LanguageModel.create({
  signal: controller.signal
});
```

## Initial Prompts (Context Setting)

```javascript
const session = await LanguageModel.create({
  initialPrompts: [
    { role: 'system', content: 'You are a helpful assistant.' },
    { role: 'user', content: 'What is the capital of Italy?' },
    { role: 'assistant', content: 'The capital of Italy is Rome.' },
    { role: 'user', content: 'What language is spoken there?' },
    { role: 'assistant', content: 'The official language is Italian.' }
  ]
});
```

**Use cases:**
- Resume stored sessions after browser restart
- N-shot prompting
- Set assistant personality/tone
- Provide conversation history

## Multimodal Input (Origin Trial)

### expectedInputs & expectedOutputs

```javascript
const session = await LanguageModel.create({
  expectedInputs: [
    {
      type: "text",  // or "image", "audio"
      languages: ["en" /* system */, "ja" /* user prompt */]
    }
  ],
  expectedOutputs: [
    { type: "text", languages: ["ja"] }
  ]
});
```

**Input types:** text, image, audio
**Output types:** text only

Throws `NotSupportedError` if unsupported modality.

### Using with Images/Audio

```javascript
const session = await LanguageModel.create({
  initialPrompts: [{
    role: 'system',
    content: 'Analyze images for patterns.'
  }],
  expectedInputs: [{ type: 'image' }]
});

// Append image
await session.append([{
  role: 'user',
  content: [
    { type: 'text', value: 'Analyze this image' },
    { type: 'image', value: fileInput.files[0] }
  ]
}]);
```

## Prompting Methods

### Non-Streaming (Short Responses)

```javascript
const result = await session.prompt('Write me a haiku!');
console.log(result);
```

### Streaming (Long Responses)

```javascript
const stream = session.promptStreaming('Write me a long poem!');
for await (const chunk of stream) {
  console.log(chunk);  // Partial results as they arrive
}
```

### With AbortSignal

```javascript
const controller = new AbortController();
stopButton.onclick = () => controller.abort();

const result = await session.prompt('Write a poem', {
  signal: controller.signal
});
```

## Response Constraints (Structured Output)

Pass JSON Schema to get predictable JSON responses:

```javascript
const schema = {
  type: "object",
  properties: {
    hashtags: {
      type: "array",
      maxItems: 3,
      items: {
        type: "string",
        pattern: "^#[^\\s#]+$"
      }
    }
  },
  required: ["hashtags"],
  additionalProperties: false
};

const result = await session.prompt(
  `Generate hashtags for: ${post}`,
  { responseConstraint: schema }
);

const data = JSON.parse(result);  // Guaranteed valid JSON
```

**Simple boolean example:**

```javascript
const schema = { "type": "boolean" };
const result = await session.prompt(
  `Is this about pottery?\n\n${text}`,
  { responseConstraint: schema }
);
console.log(JSON.parse(result));  // true or false
```

**Measure input quota usage:**

```javascript
const usage = session.measureInputUsage({ responseConstraint: schema });
```

**Omit schema from input quota:**

```javascript
const result = await session.prompt(
  `Summarize as JSON { rating } with 0-5 number:`,
  {
    responseConstraint: schema,
    omitResponseConstraintInput: true
  }
);
```

## Response Prefixes

Guide model output format by prefilling assistant response:

```javascript
const result = await session.prompt([
  { role: 'user', content: 'Create a TOML character sheet' },
  { role: 'assistant', content: '```toml\n', prefix: true }
]);
// Model continues from "```toml\n"
```

## append() Method

Add messages to session without immediate response (useful for multimodal):

```javascript
await session.append([
  {
    role: 'user',
    content: [
      { type: 'text', value: 'First context message' },
      { type: 'image', value: imageFile }
    ]
  }
]);

// Later, prompt with accumulated context
const result = await session.prompt('Analyze the images');
```

Promise fulfills when validated and appended.

## Session Management

### Check Quota

```javascript
console.log(`${session.inputUsage}/${session.inputQuota}`);
const remaining = session.inputQuota - session.inputUsage;
```

When quota exceeded, oldest messages lost from context.

### Clone Session

Clones inherit parameters, initial prompts, and history:

```javascript
const mainSession = await LanguageModel.create({
  initialPrompts: [{ role: 'system', content: 'Speak like a pirate' }]
});

const clone1 = await mainSession.clone();
const clone2 = await mainSession.clone({ signal: controller.signal });

// Independent conversations with same setup
await clone1.prompt('Tell me a joke about parrots');
await clone2.prompt('Tell me a joke about treasure');
```

**Use for:** Parallel conversations, "what if" scenarios, resource efficiency

### Restore Session from localStorage

```javascript
let sessionData = getFromLocalStorage(uuid) || {
  initialPrompts: [],
  topK: (await LanguageModel.params()).defaultTopK,
  temperature: (await LanguageModel.params()).defaultTemperature
};

const session = await LanguageModel.create(sessionData);

// Track conversation
const stream = session.promptStreaming(prompt);
let result = '';
for await (const chunk of stream) {
  result = chunk;
}

sessionData.initialPrompts.push(
  { role: 'user', content: prompt },
  { role: 'assistant', content: result }
);

localStorage.setItem(uuid, JSON.stringify(sessionData));
```

### Destroy Session

```javascript
session.destroy();
// Frees resources, aborts ongoing execution
// Session unusable after destroy
```

**Best practice:** Keep one empty session alive to keep model loaded. Destroy only when truly done.

## User Activation Requirement

Model download requires user interaction:

```javascript
if (navigator.userActivation.isActive) {
  const session = await LanguageModel.create();
}
```

**Sticky activation events:** click, tap, keydown, mousedown

## Permission Policy & iframes

**Default:** Top-level windows + same-origin iframes only

**Grant cross-origin iframe access:**

```html
<iframe src="https://cross-origin.example.com/"
        allow="language-model">
</iframe>
```

**Not available in Web Workers** (permission policy complexity)

## Local Development (localhost)

1. Go to `chrome://flags/#prompt-api-for-gemini-nano-multimodal-input`
2. Select **Enabled**
3. Relaunch Chrome
4. Open DevTools, type: `await LanguageModel.availability();`
5. Should return `"available"`

**Troubleshoot:**
- Restart Chrome
- Check `chrome://on-device-internals` → Model Status tab
- Wait for model download to complete

## Chrome Extensions

Available in Chrome 138+ stable for extensions.

**Remove expired origin trial permissions:**

```json
{
  "permissions": ["aiLanguageModelOriginTrial"]  // REMOVE THIS
}
```

Register for current origin trial if needed.

## Best Practices

**Session management:**
- Clone sessions to preserve initial prompts
- Use AbortController to let users stop responses
- Track inputUsage to warn before quota exceeded
- Destroy unused sessions to free memory
- Keep one empty session alive to keep model ready

**Performance:**
- Use streaming for long responses
- append() messages in advance for multimodal
- Monitor download progress, inform users
- Check availability before creating sessions

**Structured output:**
- Use JSON Schema for predictable responses
- LLMs good at generating schemas from descriptions
- Validate with JSON Schema validators
- Use prefix for format guidance

**Context preservation:**
- Store conversation in localStorage for restoration
- Use initialPrompts for session context
- Clone for parallel conversations with same context

## Error Handling

```javascript
try {
  const session = await LanguageModel.create();
  const result = await session.prompt('Hello');
} catch (err) {
  if (err.name === 'AbortError') {
    // User stopped generation
  } else if (err.name === 'NotSupportedError') {
    // Unsupported modality/language
  } else {
    console.error(err.name, err.message);
  }
}
```

## Key Limitations

- Desktop only (no mobile)
- 22 GB storage required
- Unmetered network for download
- No Web Workers support
- Output is text-only (input can be multimodal)
- Context window has token limits
- Model removed if storage <10 GB after download

## Use Cases

- AI-powered search on page content
- Content classification/filtering
- Event extraction from pages
- Contact information extraction
- Chatbots with conversation memory
- Offline AI features
- Privacy-sensitive data processing
- Content summarization
- Translation assistance
- Image/audio analysis (multimodal)
