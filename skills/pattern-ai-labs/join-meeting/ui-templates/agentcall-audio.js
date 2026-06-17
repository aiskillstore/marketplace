/**
 * AgentCall Audio Player — Drop-in audio queue for webpage modes.
 *
 * In webpage modes (webpage-audio, webpage-av, webpage-av-screenshare),
 * audio from GetSun (collaborative voice intelligence) or AgentCall TTS arrives as base64-encoded 24kHz PCM
 * chunks via WebSocket events. This player:
 *
 * 1. Decodes base64 PCM → AudioBuffer
 * 2. Queues chunks for gapless sequential playback
 * 3. On `tts.audio_clear` → stops playback + flushes queue immediately
 * 4. On `transcript.partial` during playback → debounced interruption
 *    (see below). When confirmed, clears audio and fires onInterrupted
 *    with the played and not_played sentence lists.
 *
 * INTERRUPTION DETECTION (direct mode, webpage modes 2-4):
 * FirstCall does NOT transcribe bot audio — transcript.partial always
 * comes from a human participant. But a single partial isn't a
 * reliable interruption signal: STT also fires partials for short
 * fillers ("mhm", "uh"), background noise, mic bumps, and brief
 * acknowledgments that aren't meant to interrupt. A naive "first
 * partial → cut audio" rule cuts the bot off constantly in noisy
 * group meetings.
 *
 * Debounce: on the FIRST partial during playback, the player suspends
 * the AudioContext (pauses the bot's audio output mid-stream — context
 * currentTime stops advancing), starts a 2-second window, and fires
 * onSuspensionStart so the template can flip the avatar to "interrupted"
 * for immediate visual feedback. Partials are incremental (each carries
 * only the new words spoken since the previous partial), so we sum word
 * counts across partials inside the window. Once the total reaches
 * wordThreshold (2) the interrupt is confirmed: audio is cleared and
 * onInterrupted fires. If the window expires below threshold, ctx is
 * resumed and onSuspensionEnd fires so the template can revert to
 * "speaking" — the brief silence is the only visible side effect of a
 * false alarm.
 *
 * CHUNK GATE AFTER CONFIRMATION:
 * Once the interrupt is confirmed, the backend doesn't know yet — its
 * TTS pipeline keeps streaming in-flight chunks for the original
 * utterance for hundreds of ms. Without a gate, those chunks would
 * refill the queue and the bot would resume talking right after we
 * cleared. So _handleInterruption sets this.interrupted = true, which
 * makes playChunk silently drop incoming chunks until the next
 * tts.started event (signaling the agent's new utterance is starting).
 *
 * Collaborative-mode interruption (tts.audio_clear from GetSun) bypasses
 * the debounce — that signal comes from a sophisticated voice
 * intelligence service and is treated as authoritative. It does NOT
 * set the chunk gate because GetSun continues streaming new utterances
 * without an explicit tts.started boundary.
 *
 * SENTENCE TRACKING:
 * Each tts.webpage_audio event can include sentence_index, sentence_text,
 * and duration_ms. On confirmed interruption the player categorizes
 * every queued sentence as either played (fully heard by participants)
 * or not_played (cut mid-way OR queued but never started). The
 * mid-cut sentence goes in not_played because the message wasn't
 * fully delivered.
 *
 * USAGE:
 *   const player = new AgentCallAudio({
 *     onStateChange: (playing) => setState(playing ? "speaking" : "listening"),
 *     onSuspensionStart: () => setState("interrupted"),
 *     onSuspensionEnd:   () => setState("speaking"),
 *     onInterrupted: (info) => {
 *       setState("interrupted");
 *       ws.send(JSON.stringify({ type: 'tts.interrupted', ...info }));
 *     }
 *   });
 *   ws.onmessage = (e) => player.handleEvent(JSON.parse(e.data));
 */

class AgentCallAudio {
  constructor(options = {}) {
    this.sampleRate = options.sampleRate || 24000;
    this.ctx = null;
    this.queue = [];
    this.nextTime = 0;
    this.playing = false;
    this.onStateChange = options.onStateChange || null;
    this.onInterrupted = options.onInterrupted || null;
    this.onSuspensionStart = options.onSuspensionStart || null;
    this.onSuspensionEnd = options.onSuspensionEnd || null;

    // Sentence tracking
    this.sentences = [];       // [{index, text, duration_ms, startTime}]
    this.currentSentence = -1;
    this.playbackStartTime = 0;

    // Interruption debounce — see header comment.
    // On the 1st partial during playback we suspend the AudioContext
    // (pauses output mid-stream) and start a 2s window. We sum the
    // word count across incremental partials inside the window; once
    // the total reaches wordThreshold the interrupt is confirmed.
    // Otherwise we resume — the brief silence is the only side effect.
    this.partialPending = false;
    this.wordCount = 0;
    this.partialWindowTimer = null;
    this.wordThreshold = 2;          // total spoken words in window to confirm
    this.partialWindowMs = 2000;     // window length in ms

    // Chunk gate. Set true after _handleInterruption clears the queue;
    // makes playChunk drop incoming chunks until the next tts.started
    // event opens the gate. Prevents in-flight backend chunks from
    // resuming bot audio after a confirmed interrupt.
    this.interrupted = false;
  }

  /**
   * Handle a WebSocket event. Call this for every message.
   * Handles tts.webpage_audio, tts.audio_clear, tts.started, and
   * transcript.partial.
   */
  handleEvent(msg) {
    const eventType = msg.event || msg.type;

    if (eventType === 'tts.webpage_audio' && msg.data) {
      this.playChunk(msg.data, {
        sentenceIndex: msg.sentence_index,
        sentenceText: msg.sentence_text,
        durationMs: msg.duration_ms,
      });
    }

    if (eventType === 'tts.audio_clear') {
      // Authoritative clear (e.g., GetSun audio.interrupted in collaborative
      // mode). Bypass the partial-debounce — this signal is trusted.
      this.clear();
    }

    if (eventType === 'tts.started') {
      // New utterance from the backend — open the chunk gate so the
      // agent's response audio can play.
      this.interrupted = false;
    }

    if (eventType === 'transcript.partial' && this.playing) {
      this._onPartialDuringPlayback(msg.text || '');
    }
  }

  /**
   * Drive the partial-debounce state machine. Partials are incremental
   * (each carries only the new words spoken since the last partial), so
   * we sum word counts across partials inside the 2s window.
   *
   * 1st partial → suspend audio + start 2s window + fire
   *               onSuspensionStart (template flips to "interrupted")
   * Subsequent partials → add their words to the running total
   * Total ≥ wordThreshold → confirm interrupt
   * Window expiry (handled by _resumeAfterTimeout) → resume audio +
   *               fire onSuspensionEnd (template flips back to "speaking")
   */
  _onPartialDuringPlayback(text) {
    const n = (text || '').trim().split(/\s+/).filter(Boolean).length;

    if (!this.partialPending) {
      this.partialPending = true;
      this.wordCount = n;
      if (this.ctx) {
        this.ctx.suspend();
      }
      this.partialWindowTimer = setTimeout(
        () => this._resumeAfterTimeout(),
        this.partialWindowMs
      );
      if (this.onSuspensionStart) {
        this.onSuspensionStart();
      }
    } else {
      this.wordCount += n;
    }

    if (this.wordCount >= this.wordThreshold) {
      // Confirmed interruption — cancel the window, fire interrupt.
      if (this.partialWindowTimer) {
        clearTimeout(this.partialWindowTimer);
        this.partialWindowTimer = null;
      }
      this.partialPending = false;
      this.wordCount = 0;
      this._handleInterruption('user_speaking');
      // Resume context AFTER clearing sources so future audio works
      // (clear() in _handleInterruption stops all queued sources, even
      // on a suspended context). The chunk gate set by _handleInterruption
      // keeps in-flight chunks from refilling the queue.
      if (this.ctx) {
        this.ctx.resume();
      }
    }
  }

  _resumeAfterTimeout() {
    // Window expired without reaching the word threshold → false alarm.
    // Resume audio — bot continues from where it paused.
    this.partialWindowTimer = null;
    this.partialPending = false;
    this.wordCount = 0;
    if (this.ctx) {
      this.ctx.resume();
    }
    if (this.onSuspensionEnd) {
      this.onSuspensionEnd();
    }
  }

  _resetPartialState() {
    if (this.partialWindowTimer) {
      clearTimeout(this.partialWindowTimer);
      this.partialWindowTimer = null;
    }
    this.partialPending = false;
    this.wordCount = 0;
  }

  /**
   * Split text on sentence terminators followed by whitespace. Simple
   * heuristic — over-splits on abbreviations ("Mr. Smith") and decimals
   * ("3.14"); accepted limitation since the per-sentence agent pattern
   * (one sentence per tts.speak) bypasses this path entirely.
   */
  _splitSentences(text) {
    return (text || '').split(/(?<=[.!?])\s+/).map(s => s.trim()).filter(s => s.length > 0);
  }

  /**
   * Push one or N virtual sentence entries into this.sentences[].
   * Single-sentence text  → one entry, full duration (exact categorization).
   * Multi-sentence text   → N entries, duration allocated by word-count ratio
   *                         (~10-20% margin per boundary; documented).
   * duration_ms missing or <=0 → single entry, no split. Without this guard
   * every virtual entry would have startTime+0 <= ctx.currentTime and
   * categorize as "played" on interrupt — silent wrong-answer bug.
   */
  _pushSentenceEntries(metadata, scheduleStart) {
    const sentences = this._splitSentences(metadata.sentenceText || '');
    if (!metadata.durationMs || metadata.durationMs <= 0 || sentences.length <= 1) {
      this.sentences.push({
        index: metadata.sentenceIndex,
        text: sentences[0] || (metadata.sentenceText || ''),
        duration_ms: metadata.durationMs || 0,
        startTime: scheduleStart,
      });
      return;
    }
    const wordCounts = sentences.map(s => s.split(/\s+/).filter(Boolean).length);
    const totalWords = wordCounts.reduce((a, b) => a + b, 0) || 1;
    let runningStart = scheduleStart;
    for (let i = 0; i < sentences.length; i++) {
      const portion = wordCounts[i] / totalWords;
      const subDurationMs = metadata.durationMs * portion;
      this.sentences.push({
        index: metadata.sentenceIndex,
        text: sentences[i],
        duration_ms: subDurationMs,
        startTime: runningStart,
      });
      runningStart += subDurationMs / 1000;
    }
  }

  /**
   * Decode and queue a base64 PCM audio chunk for playback.
   * Optionally tracks sentence metadata for interruption reporting.
   * Silently drops chunks while the post-interruption gate is closed.
   */
  playChunk(base64Data, metadata = {}) {
    if (this.interrupted) {
      // Gate closed after a confirmed interrupt. Stale in-flight chunks
      // from the original utterance are discarded until tts.started.
      return;
    }

    if (!this.ctx) {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: this.sampleRate
      });
    }

    // Decode base64 → PCM bytes → Float32 samples.
    const bytes = Uint8Array.from(atob(base64Data), c => c.charCodeAt(0));
    const samples = new Float32Array(bytes.length / 2);
    const view = new DataView(bytes.buffer);
    for (let i = 0; i < samples.length; i++) {
      samples[i] = view.getInt16(i * 2, true) / 32768.0;
    }

    // Create AudioBuffer.
    const buffer = this.ctx.createBuffer(1, samples.length, this.sampleRate);
    buffer.getChannelData(0).set(samples);

    // Create source node.
    const source = this.ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(this.ctx.destination);

    // Schedule: play immediately if queue is empty, or right after the last chunk.
    const now = this.ctx.currentTime;
    if (this.nextTime < now) {
      this.nextTime = now;
    }

    // Track sentence metadata. Pushes one or N virtual entries depending on
    // whether sentenceText is single- or multi-sentence — see
    // _pushSentenceEntries above. Capture this.nextTime as the schedule start
    // BEFORE the `+= buffer.duration` below advances it.
    if (metadata.sentenceIndex !== undefined) {
      this._pushSentenceEntries(metadata, this.nextTime);
      this.currentSentence = metadata.sentenceIndex;
    }

    source.start(this.nextTime);
    this.nextTime += buffer.duration;

    // Track for clearing.
    this.queue.push(source);
    source.onended = () => {
      const idx = this.queue.indexOf(source);
      if (idx !== -1) this.queue.splice(idx, 1);
      if (this.queue.length === 0) {
        this.playing = false;
        this.sentences = [];
        this.currentSentence = -1;
        // Bot finished naturally — reset partial debounce so next
        // utterance starts fresh.
        this._resetPartialState();
        if (this.onStateChange) this.onStateChange(false);
      }
    };

    if (!this.playing) {
      this.playing = true;
      this.playbackStartTime = now;
      if (this.onStateChange) this.onStateChange(true);
    }
  }

  /**
   * Handle confirmed interruption: categorize sentences, clear audio,
   * close the chunk gate, fire onInterrupted with played + not_played
   * lists.
   *
   * Categorization uses ctx.currentTime as the cutoff. Since the context
   * was suspended at the first partial, currentTime equals "the moment
   * the user started speaking" — what participants actually heard up to.
   *
   *   played:     sentence end time <= now (heard in full)
   *   not_played: sentence start time > now (never started) OR
   *               sentence start time <= now < end time (cut mid-way)
   *
   * The mid-cut sentence goes in not_played because the message wasn't
   * fully delivered.
   */
  _handleInterruption(reason) {
    if (!this.playing) return;

    const played = [];
    const notPlayed = [];
    if (this.ctx && this.sentences.length > 0) {
      const now = this.ctx.currentTime;
      for (const s of this.sentences) {
        const endTime = s.startTime + (s.duration_ms / 1000);
        if (endTime <= now) {
          played.push(s.text);
        } else {
          notPlayed.push(s.text);
        }
      }
    }

    // Suppress the listening-flash from clear()'s onStateChange — the
    // template already showed "interrupted" via onSuspensionStart, and
    // onInterrupted below will re-affirm it.
    this.clear({ suppressStateChange: true });
    // Close the chunk gate so the backend's in-flight chunks for the
    // interrupted utterance are dropped until tts.started.
    this.interrupted = true;

    if (this.onInterrupted) {
      this.onInterrupted({
        reason: reason,
        played: played,
        not_played: notPlayed,
      });
    }
  }

  /**
   * Stop all playback immediately and flush the queue.
   * Called by _handleInterruption (debounced direct-mode interruption,
   * with suppressStateChange=true) and by tts.audio_clear (collaborative-
   * mode interruption from GetSun, default opts).
   */
  clear(opts = {}) {
    for (const source of this.queue) {
      try { source.stop(); } catch (e) { /* already stopped */ }
    }
    this.queue = [];
    this.nextTime = 0;
    this.playing = false;
    this.sentences = [];
    this.currentSentence = -1;
    this._resetPartialState();
    if (this.onStateChange && !opts.suppressStateChange) {
      this.onStateChange(false);
    }
  }

  /**
   * Returns true if audio is currently playing.
   */
  isPlaying() {
    return this.playing;
  }
}

// Export for module usage.
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AgentCallAudio;
}
