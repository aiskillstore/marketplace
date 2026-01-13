---
name: voice-system-expert
description: Use when working with Quetrex's voice interface, OpenAI Realtime API, WebRTC, or echo cancellation. Knows Quetrex's specific voice architecture decisions and patterns. CRITICAL - prevents breaking working voice system.
allowed-tools: Read
---

# Quetrex Voice System Expert

## CRITICAL: Read This First

Quetrex's voice system architecture is **extensively documented and battle-tested**. Before making ANY changes to voice-related code, you MUST read:

1. **ADR-001-VOICE-ECHO-CANCELLATION.md** (definitive architectural decision)
2. **docs/architecture/VOICE-SYSTEM.md** (technical implementation)
3. **docs/features/voice-interface.md** (user-facing features)

**Location:** `src/lib/openai-realtime.ts`

## Core Architecture Decision

### ALWAYS-ON MICROPHONE + BROWSER AEC

This is **Decision 4** from VOICE-SYSTEM.md and the definitive approach documented in ADR-001.

```typescript
// ✅ CORRECT: Always-on microphone
const mediaStream = await navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: true,  // CRITICAL - browser handles echo cancellation
    noiseSuppression: true,
    autoGainControl: true,
  },
})

// Microphone track stays ENABLED throughout conversation
// Browser's native AEC prevents feedback loops
// Server-side VAD (Voice Activity Detection) handles turn detection
```

## How It Works

### Audio Pipeline
```
User speaks
    ↓
Microphone (always enabled, echoCancellation: true)
    ↓
WebRTC → OpenAI Realtime API
    ↓
Server-side VAD detects speech
    ↓
OpenAI processes and responds
    ↓
Audio response via WebRTC
    ↓
HTMLAudioElement playback (stays in browser pipeline)
    ↓
Browser AEC compares mic input + speaker output
    ↓
Echo automatically canceled (no feedback loop)
```

### Why This Works

**Browser Echo Cancellation Requirements:**
1. Both microphone input AND speaker output must be in browser's audio graph
2. Audio must flow through browser's WebRTC stack
3. No manual intervention needed (browser handles it)

**This is the industry standard:**
- ChatGPT voice mode
- Google Meet
- Zoom
- Discord
- Microsoft Teams

They ALL use always-on microphone + browser AEC.

## DO NOT DO THESE THINGS

### ❌ DON'T: Toggle Microphone Track

```typescript
// ❌ WRONG - This breaks echo cancellation
async function pauseRecording() {
  microphone.enabled = false // DON'T DO THIS
}

async function resumeRecording() {
  microphone.enabled = true // DON'T DO THIS
}
```

**Why this fails:**
- Not industry standard
- Causes audio glitches
- Can break echo cancellation
- Adds artificial delays
- More complex state management
- No real benefit

### ❌ DON'T: Route Audio Outside Browser

```typescript
// ❌ WRONG - AudioWorklet bypass to native audio
const workletNode = new AudioWorkletNode(audioContext, 'bypass-processor')
workletNode.port.postMessage({ cmd: 'route-to-native' })
```

**Why this fails:**
- Breaks browser AEC (audio leaves browser pipeline)
- Causes echo/feedback loops
- Requires complex native audio handling
- Platform-specific implementations
- Already tried and failed (see abandoned-approaches/)

### ❌ DON'T: Implement Custom Echo Cancellation

```typescript
// ❌ WRONG - Custom AEC implementation
class CustomEchoCanceller {
  cancelEcho(input: AudioBuffer, output: AudioBuffer) {
    // Complex DSP code...
  }
}
```

**Why this fails:**
- Reinventing the wheel
- Browser AEC is battle-tested by billions of users
- Extremely complex to implement correctly
- Requires deep DSP knowledge
- Performance issues
- Platform-specific tuning needed

### ❌ DON'T: Add Artificial Delays

```typescript
// ❌ WRONG - Delays for echo prevention
await new Promise(resolve => setTimeout(resolve, 500))
await playAudio()
await new Promise(resolve => setTimeout(resolve, 500))
resumeRecording()
```

**Why this fails:**
- Not necessary (browser AEC handles it)
- Degrades user experience
- Adds latency
- Still doesn't prevent echo if implementation is wrong

## What You CAN Change

### ✅ DO: Adjust Audio Settings

```typescript
// ✅ Can tweak these settings
const constraints = {
  audio: {
    echoCancellation: true,      // MUST be true
    noiseSuppression: true,       // Can adjust
    autoGainControl: true,        // Can adjust
    sampleRate: 24000,            // Can change for quality
    channelCount: 1,              // Mono is fine for voice
  },
}
```

### ✅ DO: Handle Connection States

```typescript
// ✅ Can manage connection lifecycle
async function connectVoice() {
  // Setup WebRTC connection
  // Start streaming
  // Handle connection events
}

async function disconnectVoice() {
  // Clean up WebRTC connection
  // Stop streaming
  // Release microphone
}
```

### ✅ DO: Add UI Feedback

```typescript
// ✅ Can add visual indicators
function onVoiceActivity(active: boolean) {
  if (active) {
    // Show "listening" indicator
    // Animate microphone icon
  } else {
    // Show "idle" indicator
  }
}
```

### ✅ DO: Handle Errors

```typescript
// ✅ Can improve error handling
try {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
} catch (error) {
  if (error.name === 'NotAllowedError') {
    // Show permission request UI
  } else if (error.name === 'NotFoundError') {
    // Show "no microphone found" error
  }
}
```

## Implementation Location

**Primary file:** `src/lib/openai-realtime.ts`

**Key functions:**
- `setupMediaStream()` - Initializes microphone with correct constraints
- `connectToOpenAI()` - Establishes WebRTC connection
- `handleAudioResponse()` - Plays AI responses via HTMLAudioElement

**DO NOT modify:**
- Microphone enable/disable logic (should stay always-on)
- Echo cancellation settings (must be true)
- Audio routing (must stay in browser pipeline)

**CAN modify:**
- UI feedback and visual indicators
- Error handling and user messages
- Connection retry logic
- Audio quality settings (sample rate, etc.)

## Why This Architecture Was Chosen

From ADR-001:

**Option A: Trust Industry Pattern (CHOSEN)**
- ✅ Used by ChatGPT, Google Meet, Zoom, Discord
- ✅ Browser vendors optimize for this pattern
- ✅ Works across all platforms (macOS, Windows, Linux, mobile)
- ✅ No custom implementation needed
- ✅ Proven reliability

**Options Rejected:**
- ❌ Manual microphone toggling (not industry standard)
- ❌ AudioWorklet native bypass (breaks AEC)
- ❌ Custom echo cancellation (reinventing wheel)
- ❌ Native Rust WebRTC (2-4 weeks work for no benefit)

## Platform Context: Web Application

**IMPORTANT:** Quetrex is now a **pure web application**, not a Tauri desktop app.

**Why this matters for voice:**
- Browser echo cancellation works perfectly in all browsers
- No WKWebView limitations (that was the Tauri problem)
- Universal compatibility (Chrome, Safari, Firefox, Edge)
- No platform-specific audio handling needed
- Just works™️

**The WKWebView Problem (Historical):**
Quetrex was originally a Tauri desktop app. On macOS, Tauri uses WKWebView, which has a bug: **WebRTC audio playback doesn't work**. This forced us to try workarounds (AudioWorklet bypass, native audio routing), which all broke echo cancellation.

**Solution:** Convert to web application. Now echo cancellation works perfectly everywhere.

## Testing Voice Changes

If you must modify voice code:

1. **Test on real browsers** (not just dev tools)
2. **Test the echo scenario:**
   - Turn up speaker volume
   - Start voice conversation
   - Verify no feedback loop/echo
3. **Test across platforms:**
   - Chrome (most common)
   - Safari (macOS, iOS)
   - Firefox
   - Edge
4. **Test edge cases:**
   - Poor network connection
   - Microphone permission denied
   - Mid-conversation disconnect

## When to Consult Documentation

**Before any voice changes, read:**
1. `docs/decisions/ADR-001-VOICE-ECHO-CANCELLATION.md`
2. `docs/architecture/VOICE-SYSTEM.md`
3. `docs/development/abandoned-approaches/`

**If you see mentions of:**
- Tauri → Ignore (Quetrex is web app now)
- WKWebView → Ignore (not relevant anymore)
- AudioWorklet bypass → Don't implement (already tried, failed)
- Manual mic toggling → Don't implement (not industry standard)

## Summary

**The Golden Rule:** Trust browser echo cancellation. Always-on microphone + `echoCancellation: true` + audio in browser pipeline = Perfect echo cancellation.

**DO:**
- Keep microphone enabled throughout conversation
- Use `echoCancellation: true`
- Keep audio in browser (HTMLAudioElement)
- Let OpenAI Realtime API handle VAD
- Trust the industry pattern

**DON'T:**
- Toggle microphone track
- Route audio outside browser
- Implement custom echo cancellation
- Add artificial delays
- Try to "improve" what already works

**If in doubt:** Read ADR-001 and VOICE-SYSTEM.md. The architecture is thoroughly documented for a reason.
