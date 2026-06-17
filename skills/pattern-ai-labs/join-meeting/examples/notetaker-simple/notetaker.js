#!/usr/bin/env node
/**
 * AgentCall — Simple Note-Taker Bot
 *
 * Joins a meeting in audio mode, collects transcripts in real-time,
 * and saves the full transcript to a markdown file when the meeting ends.
 *
 * Usage:
 *     export AGENTCALL_API_KEY="ak_ac_your_key"
 *     node notetaker.js "https://meet.google.com/abc-def-ghi"
 *
 *     # Optional: customize bot name
 *     node notetaker.js "https://meet.google.com/abc-def-ghi" --name "Scribe"
 *
 * Dependencies:
 *     npm install ws
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
const nameFlag = args.indexOf("--name");
const botName = nameFlag !== -1 ? args[nameFlag + 1] : "Notetaker";

if (!meetUrl) {
  console.error("Usage: node notetaker.js <meeting-url> [--name <bot-name>]");
  process.exit(1);
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
  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`Failed to create call: ${resp.status} ${err}`);
  }
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

function saveNotes(callId, participants, transcriptLines, duration, endReason) {
  const now = new Date();
  const dateStr = now.toISOString().slice(0, 16).replace("T", "-").replace(":", "");
  const filename = `meeting-notes-${dateStr}.md`;

  let content = `# Meeting Notes — ${now.toISOString().slice(0, 16).replace("T", " ")}\n\n`;

  content += "## Participants\n";
  for (const p of [...participants].sort()) {
    content += `- ${p}\n`;
  }
  content += "\n";

  content += "## Transcript\n";
  for (const line of transcriptLines) {
    const timeStr = (line.timestamp || "").slice(11, 19) || "";
    content += `[${timeStr}] ${line.speaker}: ${line.text}\n`;
  }
  content += "\n";

  content += "## Meeting Info\n";
  content += `- Call ID: ${callId}\n`;
  content += `- Duration: ${duration}\n`;
  content += `- End reason: ${endReason}\n`;
  content += `- Total utterances: ${transcriptLines.length}\n`;

  fs.writeFileSync(filename, content);
  console.log(`\nNotes saved to: ${filename}`);
  return filename;
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

    ws.on("open", () => {
      console.log("Connected. Waiting for events...\n");
    });

    ws.on("message", (data) => {
      const event = JSON.parse(data.toString());
      const eventType = event.event || event.type || "";

      if (eventType === "call.bot_ready") {
        console.log("Bot is in the meeting. Listening for transcripts...\n");
      } else if (eventType === "participant.joined") {
        const name = event.name || "Unknown";
        participants.add(name);
        console.log(`  + ${name} joined`);
      } else if (eventType === "participant.left") {
        const name = event.name || "Unknown";
        console.log(`  - ${name} left`);
      } else if (eventType === "transcript.final") {
        const speaker = event.speaker || "Unknown";
        const text = event.text || "";
        const timestamp = event.timestamp || "";
        participants.add(speaker);
        transcriptLines.push({ speaker, text, timestamp });
        console.log(`  [${speaker}] ${text}`);
      } else if (eventType === "call.ended") {
        endReason = event.reason || "unknown";
        console.log(`\nCall ended: ${endReason}`);
        ws.close();
      }
    });

    ws.on("close", async () => {
      let duration = `${transcriptLines.length} utterances captured`;

      // Try fetching the full transcript from the API
      console.log("\nFetching full transcript from API...");
      const full = await fetchTranscript(callId);
      if (full && full.entries) {
        transcriptLines.length = 0;
        for (const e of full.entries) {
          const speaker =
            typeof e.speaker === "object" ? e.speaker.name || "Unknown" : String(e.speaker || "Unknown");
          transcriptLines.push({
            speaker,
            text: e.text || "",
            timestamp: e.timestamp || "",
          });
        }
        duration = `${full.duration_minutes || 0} minutes`;
        console.log(`  Got ${transcriptLines.length} entries (${duration})`);
      } else {
        console.log("  Full transcript not available yet, using real-time captures");
      }

      saveNotes(callId, participants, transcriptLines, duration, endReason);
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

async function main() {
  console.log(`Creating call for: ${meetUrl}`);
  console.log(`Bot name: ${botName}\n`);

  const call = await createCall(meetUrl, botName);
  console.log(`Call created: ${call.call_id}`);
  console.log(`Status: ${call.status}\n`);

  await listen(call);
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

main().catch(console.error);
