#!/usr/bin/env node
/**
 * AgentCall — Smart Note-Taker with LLM Summarization
 *
 * Joins a meeting in audio mode, collects transcripts, then uses an LLM
 * to generate a structured summary with key decisions and action items.
 *
 * Usage:
 *     export AGENTCALL_API_KEY="ak_ac_your_key"
 *     node notetaker.js "https://meet.google.com/abc-def-ghi"
 *
 *     # Optional: customize bot name and output
 *     node notetaker.js "https://meet.google.com/abc-def-ghi" --name "Scribe" --output summary.md
 *
 * Dependencies:
 *     npm install ws
 *
 *     # For LLM summarization, install ONE of:
 *     npm install @anthropic-ai/sdk    # Anthropic (Claude)
 *     npm install openai               # OpenAI (GPT-4o)
 *     npm install @google/generative-ai # Google Gemini
 */

const fs = require("fs");
const path = require("path");
const WebSocket = require("ws");

let _cfg = {};
const _cfgPath = path.join(require("os").homedir(), ".agentcall", "config.json");
if (fs.existsSync(_cfgPath)) {
  try { _cfg = JSON.parse(fs.readFileSync(_cfgPath, "utf-8")); } catch {}
}

const API_BASE = process.env.AGENTCALL_API_URL || _cfg.api_url || "https://api.agentcall.dev";
const API_KEY = process.env.AGENTCALL_API_KEY || _cfg.api_key || "";

if (!API_KEY) {
  console.error("Error: Set AGENTCALL_API_KEY env var or save to ~/.agentcall/config.json");
  process.exit(1);
}

const HEADERS = {
  Authorization: `Bearer ${API_KEY}`,
  "Content-Type": "application/json",
};

// Parse CLI args
const args = process.argv.slice(2);
const meetUrl = args.find((a) => a.startsWith("http"));
const nameIdx = args.indexOf("--name");
const outIdx = args.indexOf("--output");
const botName = nameIdx !== -1 ? args[nameIdx + 1] : "Notetaker";
const outputFile = outIdx !== -1 ? args[outIdx + 1] : null;

if (!meetUrl) {
  console.error(
    "Usage: node notetaker.js <meeting-url> [--name <bot-name>] [--output <file>]"
  );
  process.exit(1);
}

// ──────────────────────────────────────────────────────────────────────────────
// LLM SUMMARIZATION PROMPT
// ──────────────────────────────────────────────────────────────────────────────

const SUMMARY_PROMPT = `You are a meeting summarizer. Given the transcript below, produce a structured summary.

## Instructions
- Write a concise summary (2-4 sentences) of what was discussed
- List key decisions that were made (if any)
- Extract action items with the responsible person and deadline (if mentioned)
- Note any unresolved questions or topics that need follow-up
- Be factual — only include what was actually said, do not infer or assume

## Output Format (use exactly this markdown structure)

## Summary
<2-4 sentence overview>

## Key Decisions
- <decision 1>
- <decision 2>
(or "No explicit decisions were made." if none)

## Action Items
- [ ] <person>: <task> <deadline if mentioned>
- [ ] <person>: <task>
(or "No action items were identified." if none)

## Follow-Up Needed
- <unresolved question or topic>
(or "No follow-ups needed." if none)

## Transcript

{transcript}`;

/**
 * Send the transcript to an LLM for summarization.
 * Uncomment ONE of the options below and add your API key.
 *
 * If no LLM is configured, returns null (raw transcript saved instead).
 */
async function summarizeWithLLM(transcriptText) {
  const prompt = SUMMARY_PROMPT.replace("{transcript}", transcriptText);

  // ──────────────────────────────────────────────────────────────────────
  // OPTION A: Anthropic (Claude)
  //
  // npm install @anthropic-ai/sdk
  // export ANTHROPIC_API_KEY="sk-ant-..."
  // ──────────────────────────────────────────────────────────────────────
  // const Anthropic = require("@anthropic-ai/sdk");
  // const client = new Anthropic();
  // const response = await client.messages.create({
  //   model: "claude-sonnet-4-20250514",
  //   max_tokens: 2048,
  //   messages: [{ role: "user", content: prompt }],
  // });
  // return response.content[0].text;

  // ──────────────────────────────────────────────────────────────────────
  // OPTION B: OpenAI (GPT-4o)
  //
  // npm install openai
  // export OPENAI_API_KEY="sk-..."
  // ──────────────────────────────────────────────────────────────────────
  // const OpenAI = require("openai");
  // const client = new OpenAI();
  // const response = await client.chat.completions.create({
  //   model: "gpt-4o",
  //   messages: [{ role: "user", content: prompt }],
  // });
  // return response.choices[0].message.content;

  // ──────────────────────────────────────────────────────────────────────
  // OPTION C: Google Gemini
  //
  // npm install @google/generative-ai
  // export GOOGLE_API_KEY="..."
  // ──────────────────────────────────────────────────────────────────────
  // const { GoogleGenerativeAI } = require("@google/generative-ai");
  // const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
  // const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
  // const result = await model.generateContent(prompt);
  // return result.response.text();

  // ──────────────────────────────────────────────────────────────────────
  // OPTION D: Any OpenAI-compatible API (Ollama, Together, Groq, etc.)
  //
  // npm install openai
  // ──────────────────────────────────────────────────────────────────────
  // const OpenAI = require("openai");
  // const client = new OpenAI({
  //   baseURL: "http://localhost:11434/v1",  // Ollama
  //   apiKey: "ollama",
  // });
  // const response = await client.chat.completions.create({
  //   model: "llama3",
  //   messages: [{ role: "user", content: prompt }],
  // });
  // return response.choices[0].message.content;

  // ──────────────────────────────────────────────────────────────────────
  // NO LLM CONFIGURED
  // ──────────────────────────────────────────────────────────────────────
  console.log(
    "\n  [!] No LLM configured. Uncomment one of the options in summarizeWithLLM()."
  );
  console.log("  [!] Saving raw transcript without summary.\n");
  return null;
}

async function createCall(meetUrl, botName) {
  const resp = await fetch(`${API_BASE}/v1/calls`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({
      meet_url: meetUrl,
      bot_name: botName,
      mode: "audio",
      voice_strategy: "direct",
      transcription: true,
    }),
  });
  if (!resp.ok) throw new Error(`Create call failed: ${resp.status}`);
  return resp.json();
}

async function fetchTranscript(callId) {
  const resp = await fetch(
    `${API_BASE}/v1/calls/${callId}/transcript?format=json`,
    { headers: HEADERS }
  );
  if (resp.ok) return resp.json();
  return null;
}

function formatTranscript(lines) {
  return lines
    .map((l) => {
      const ts = (l.timestamp || "").slice(11, 19) || "";
      return `[${ts}] ${l.speaker}: ${l.text}`;
    })
    .join("\n");
}

function saveSummary(
  callId,
  participants,
  transcriptLines,
  duration,
  endReason,
  summary
) {
  const now = new Date();
  const dateStr = now
    .toISOString()
    .slice(0, 16)
    .replace("T", "-")
    .replace(":", "");
  const filename = outputFile || `meeting-summary-${dateStr}.md`;

  let content = `# Meeting Summary — ${now.toISOString().slice(0, 16).replace("T", " ")}\n\n`;
  content += `**Call ID:** ${callId}  \n`;
  content += `**Duration:** ${duration}  \n`;
  content += `**Participants:** ${[...participants].sort().join(", ")}  \n`;
  content += `**End reason:** ${endReason}  \n\n`;
  content += "---\n\n";

  if (summary) {
    content += summary + "\n\n";
  } else {
    content += "## Summary\n*LLM summarization not configured. See the raw transcript below.*\n\n";
    content += "## Key Decisions\n*Not available*\n\n";
    content += "## Action Items\n*Not available*\n\n";
  }

  content += "---\n\n## Full Transcript\n\n";
  for (const line of transcriptLines) {
    const ts = (line.timestamp || "").slice(11, 19) || "";
    content += `[${ts}] **${line.speaker}**: ${line.text}  \n`;
  }

  fs.writeFileSync(filename, content);
  console.log(`\nSummary saved to: ${filename}`);
}

async function listen(call) {
  const callId = call.call_id;
  let wsUrl = call.ws_url;
  if (wsUrl.startsWith("https://")) wsUrl = wsUrl.replace("https://", "wss://");

  const transcriptLines = [];
  const participants = new Set();
  let endReason = "unknown";

  console.log(`Connecting to WebSocket: ${wsUrl}`);

  return new Promise((resolve) => {
    const ws = new WebSocket(wsUrl);

    ws.on("open", () => console.log("Connected. Waiting for events...\n"));

    ws.on("message", (data) => {
      const event = JSON.parse(data.toString());
      const eventType = event.event || event.type || "";

      if (eventType === "call.bot_ready") {
        console.log("Bot is in the meeting. Listening for transcripts...\n");
      } else if (eventType === "participant.joined") {
        participants.add(event.name || "Unknown");
        console.log(`  + ${event.name || "Unknown"} joined`);
      } else if (eventType === "participant.left") {
        console.log(`  - ${event.name || "Unknown"} left`);
      } else if (eventType === "transcript.final") {
        const speaker = event.speaker || "Unknown";
        participants.add(speaker);
        transcriptLines.push({
          speaker,
          text: event.text || "",
          timestamp: event.timestamp || "",
        });
        console.log(`  [${speaker}] ${event.text}`);
      } else if (eventType === "call.ended") {
        endReason = event.reason || "unknown";
        console.log(`\nCall ended: ${endReason}`);
        ws.close();
      }
    });

    ws.on("close", async () => {
      let duration = `${transcriptLines.length} utterances captured`;

      // Fetch full transcript
      console.log("\nFetching full transcript from API...");
      const full = await fetchTranscript(callId);
      if (full && full.entries) {
        transcriptLines.length = 0;
        for (const e of full.entries) {
          transcriptLines.push({
            speaker:
              typeof e.speaker === "object"
                ? e.speaker.name || "Unknown"
                : String(e.speaker || "Unknown"),
            text: e.text || "",
            timestamp: e.timestamp || "",
          });
        }
        duration = `${full.duration_minutes || 0} minutes`;
        console.log(`  Got ${transcriptLines.length} entries (${duration})`);
      } else {
        console.log(
          "  Full transcript not available yet, using real-time captures"
        );
      }

      // Summarize with LLM
      console.log("\nGenerating summary with LLM...");
      const transcriptText = formatTranscript(transcriptLines);
      const summary = await summarizeWithLLM(transcriptText);

      saveSummary(
        callId,
        participants,
        transcriptLines,
        duration,
        endReason,
        summary
      );
      resolve();
    });

    ws.on("error", (err) => {
      console.error("WebSocket error:", err.message);
      cleanup(callId).then(resolve);
    });

    // End call on Ctrl+C
    process.on("SIGINT", () => {
      console.log("\nInterrupted — ending call...");
      cleanup(callId).then(() => process.exit(0));
    });
  });
}

// Cleanup: always end the call to stop billing
async function cleanup(callId) {
  try {
    await fetch(`${API_BASE}/calls/${callId}`, { method: "DELETE", headers: HEADERS });
    console.log("Call ended (cleanup)");
  } catch (e) {
    console.error("Cleanup failed:", e.message);
  }
}

async function main() {
  console.log(`Creating call for: ${meetUrl}`);
  console.log(`Bot name: ${botName}\n`);

  const call = await createCall(meetUrl, botName);
  console.log(`Call created: ${call.call_id}`);
  console.log(`Status: ${call.status}\n`);

  await listen(call);
}

main().catch(console.error);
