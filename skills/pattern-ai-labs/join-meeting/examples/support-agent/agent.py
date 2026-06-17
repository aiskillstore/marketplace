#!/usr/bin/env python3
"""
AgentCall — Customer Support Agent (1-on-1)

An AI-powered support agent that joins a call, listens to the customer,
looks up information from a knowledge base, and responds using TTS.
Uses direct mode (no barge-in/interruption handling) for simple
turn-based conversations.

Usage:
    export AGENTCALL_API_KEY="ak_ac_your_key"
    python agent.py "https://meet.google.com/abc-def-ghi"

    # Custom voice and bot name
    python agent.py "https://meet.google.com/abc" --name "Sarah" --voice af_bella

Dependencies:
    pip install requests websockets

NOTE: This is demo code. The LLM integration uses pseudo code — uncomment
one of the LLM options in decide_response() to make it functional.

In production you would:
  - Connect to a real CRM/order database instead of knowledge.json
  - Add conversation memory / session management
  - Implement proper escalation (transfer to human agent)
  - Add error handling and retry logic
  - Log conversations for quality assurance
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import List, Optional

import requests
import websockets

_cfg = {}
_cfg_path = os.path.join(os.path.expanduser("~"), ".agentcall", "config.json")
if os.path.exists(_cfg_path):
    try:
        _cfg = json.loads(open(_cfg_path).read())
    except (json.JSONDecodeError, OSError):
        pass

API_BASE = os.environ.get("AGENTCALL_API_URL", "") or _cfg.get("api_url", "") or "https://api.agentcall.dev"
API_KEY = os.environ.get("AGENTCALL_API_KEY", "") or _cfg.get("api_key", "")

if not API_KEY:
    print("Error: Set AGENTCALL_API_KEY env var or save to ~/.agentcall/config.json")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


# ──────────────────────────────────────────────────────────────────────────────
# KNOWLEDGE BASE
# In production, replace this with a real database, CRM, or API.
# ──────────────────────────────────────────────────────────────────────────────

def load_knowledge(path: str = None) -> dict:
    """Load the knowledge base from JSON file."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "knowledge.json")
    with open(path) as f:
        return json.load(f)


def format_knowledge_for_prompt(kb: dict) -> str:
    """Format the knowledge base into a string for the LLM prompt."""
    parts = [f"Company: {kb['company']}"]

    parts.append("\nProducts:")
    for p in kb["products"]:
        parts.append(f"  - {p['name']} ({p['id']}): ${p['price']} — {p['specs']}")

    parts.append("\nPolicies:")
    for key, val in kb["policies"].items():
        parts.append(f"  - {key.title()}: {val}")

    parts.append("\nFAQs:")
    for faq in kb["faqs"]:
        parts.append(f"  Q: {faq['q']}")
        parts.append(f"  A: {faq['a']}")

    return "\n".join(parts)


# ──────────────────────────────────────────────────────────────────────────────
# LLM DECISION ENGINE
#
# The agent sends the conversation history + knowledge base to an LLM.
# The LLM decides what to say and whether to continue, escalate, or end.
#
# Response format: {"response": "what to say", "action": "respond|escalate|end"}
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """You are a customer support agent for {company}. You are on a live phone call with a customer.

## Your Knowledge Base
{knowledge}

## Rules
- Be helpful, concise, and empathetic
- Keep responses to 1-3 sentences — this is a phone call, not an essay
- Use the knowledge base to answer accurately. Do not make up information.
- If the customer asks something you cannot answer from the knowledge base, set action to "escalate"
- If the customer's issue is resolved and they say goodbye or have no more questions, set action to "end"
- Otherwise set action to "respond" to continue the conversation
- Address the customer's most recent message while keeping full conversation context

## Response Format
Respond with ONLY a JSON object, no markdown, no explanation:
{{"response": "what you say to the customer", "action": "respond|escalate|end"}}"""


def build_llm_messages(kb: dict, conversation: List[dict]) -> List[dict]:
    """Build the message list for the LLM."""
    system = SYSTEM_PROMPT_TEMPLATE.format(
        company=kb["company"],
        knowledge=format_knowledge_for_prompt(kb),
    )

    messages = [{"role": "system", "content": system}]

    for turn in conversation:
        if turn["role"] == "customer":
            messages.append({"role": "user", "content": turn["text"]})
        elif turn["role"] == "agent":
            messages.append({"role": "assistant", "content": json.dumps({
                "response": turn["text"],
                "action": "respond",
            })})

    return messages


def decide_response(kb: dict, conversation: List[dict]) -> dict:
    """
    Ask an LLM what to say next.
    Uncomment ONE of the options below and set the appropriate API key.

    Returns: {"response": "...", "action": "respond|escalate|end"}
    """

    messages = build_llm_messages(kb, conversation)

    # ──────────────────────────────────────────────────────────────────
    # OPTION A: Anthropic (Claude)
    #
    # pip install anthropic
    # export ANTHROPIC_API_KEY="sk-ant-..."
    # ──────────────────────────────────────────────────────────────────
    # from anthropic import Anthropic
    #
    # client = Anthropic()
    # system_msg = messages[0]["content"]
    # chat_msgs = messages[1:]
    # response = client.messages.create(
    #     model="claude-sonnet-4-20250514",
    #     max_tokens=256,
    #     system=system_msg,
    #     messages=chat_msgs,
    # )
    # return json.loads(response.content[0].text)

    # ──────────────────────────────────────────────────────────────────
    # OPTION B: OpenAI (GPT-4o)
    #
    # pip install openai
    # export OPENAI_API_KEY="sk-..."
    # ──────────────────────────────────────────────────────────────────
    # from openai import OpenAI
    #
    # client = OpenAI()
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=messages,
    #     response_format={"type": "json_object"},
    # )
    # return json.loads(response.choices[0].message.content)

    # ──────────────────────────────────────────────────────────────────
    # OPTION C: Google Gemini
    #
    # pip install google-generativeai
    # export GOOGLE_API_KEY="..."
    # ──────────────────────────────────────────────────────────────────
    # import google.generativeai as genai
    #
    # genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    # model = genai.GenerativeModel("gemini-2.0-flash")
    # # Flatten messages into a single prompt for Gemini
    # prompt = messages[0]["content"] + "\n\n## Conversation\n"
    # for m in messages[1:]:
    #     role = "Customer" if m["role"] == "user" else "Agent"
    #     prompt += f"{role}: {m['content']}\n"
    # prompt += "\nAgent (respond with JSON):"
    # response = model.generate_content(prompt)
    # return json.loads(response.text)

    # ──────────────────────────────────────────────────────────────────
    # OPTION D: Any OpenAI-compatible API (Ollama, Together, Groq)
    # ──────────────────────────────────────────────────────────────────
    # from openai import OpenAI
    #
    # client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    # response = client.chat.completions.create(
    #     model="llama3",
    #     messages=messages,
    # )
    # return json.loads(response.choices[0].message.content)

    # ──────────────────────────────────────────────────────────────────
    # NO LLM CONFIGURED — simple echo fallback for testing
    # ──────────────────────────────────────────────────────────────────
    last_msg = conversation[-1]["text"] if conversation else ""
    print("  [!] No LLM configured. Using echo fallback.")
    print("  [!] Uncomment one of the options in decide_response() for real conversations.\n")
    return {
        "response": f"I heard you say: {last_msg}. Please configure an LLM in agent.py for real support responses.",
        "action": "respond",
    }


# ──────────────────────────────────────────────────────────────────────────────
# AGENTCALL API
# ──────────────────────────────────────────────────────────────────────────────

def create_call(meet_url: str, bot_name: str) -> dict:
    resp = requests.post(
        f"{API_BASE}/v1/calls",
        headers=HEADERS,
        json={
            "meet_url": meet_url,
            "bot_name": bot_name,
            "mode": "audio",
            "voice_strategy": "direct",
            "transcription": True,
        },
    )
    resp.raise_for_status()
    return resp.json()


def save_call_log(call_id: str, conversation: List[dict], end_reason: str, output_file: Optional[str]):
    """Save the conversation log and summary."""
    now = datetime.now()
    filename = output_file or f"support-log-{now.strftime('%Y-%m-%d-%H%M')}.md"

    with open(filename, "w") as f:
        f.write(f"# Support Call Log — {now.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**Call ID:** {call_id}  \n")
        f.write(f"**End reason:** {end_reason}  \n")
        f.write(f"**Turns:** {len(conversation)}  \n\n")
        f.write("---\n\n")
        f.write("## Conversation\n\n")
        for turn in conversation:
            role = "Customer" if turn["role"] == "customer" else "Agent"
            icon = "👤" if turn["role"] == "customer" else "🤖"
            f.write(f"{icon} **{role}:** {turn['text']}  \n\n")

        f.write("---\n\n")
        f.write("## Post-Call Actions\n\n")
        f.write("```\n")
        f.write("# TODO: Integrate with your ticketing system\n")
        f.write("#\n")
        f.write("# Example: Create a Zendesk ticket\n")
        f.write("# zendesk.tickets.create(\n")
        f.write(f"#     subject='Support call {call_id}',\n")
        f.write("#     description=conversation_summary,\n")
        f.write("#     priority='normal',\n")
        f.write("# )\n")
        f.write("#\n")
        f.write("# Example: Log to CRM\n")
        f.write("# crm.activities.create(\n")
        f.write(f"#     call_id='{call_id}',\n")
        f.write("#     type='support_call',\n")
        f.write("#     notes=conversation_summary,\n")
        f.write("# )\n")
        f.write("```\n")

    print(f"\nCall log saved to: {filename}")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN LOOP
# ──────────────────────────────────────────────────────────────────────────────

async def run_agent(call: dict, voice: str, output_file: Optional[str]):
    """Main agent loop: listen → think → speak → repeat."""
    call_id = call["call_id"]
    ws_url = call["ws_url"]
    if ws_url.startswith("https://"):
        ws_url = ws_url.replace("https://", "wss://")

    kb = load_knowledge()
    conversation = []
    end_reason = "unknown"
    is_speaking = False

    print(f"Connecting to WebSocket: {ws_url}")

    async with websockets.connect(ws_url) as ws:
        print("Connected. Waiting for bot to join...\n")

        async for msg in ws:
            event = json.loads(msg)
            event_type = event.get("event", event.get("type", ""))

            # ── Bot joined the meeting ──
            if event_type == "call.bot_ready":
                print("Bot is in the meeting.\n")

                # Greet the customer
                greeting = kb.get("greeting", "Hello! How can I help you today?")
                print(f"  Agent: {greeting}")
                conversation.append({"role": "agent", "text": greeting})
                await ws.send(json.dumps({
                    "command": "tts.speak",
                    "text": greeting,
                    "voice": voice,
                }))

            # ── TTS started/finished ──
            elif event_type == "tts.started":
                is_speaking = True
            elif event_type == "tts.done":
                is_speaking = False

            # ── Customer spoke ──
            elif event_type == "transcript.final":
                speaker = event.get("speaker", "Customer")
                text = event.get("text", "").strip()
                if not text:
                    continue

                # Skip if it's the bot's own speech being transcribed
                # (In direct mode, the bot's TTS audio is injected into the meeting
                #  and may be picked up by STT. Simple heuristic: skip if we're speaking.)
                if is_speaking:
                    continue

                print(f"  Customer ({speaker}): {text}")
                conversation.append({"role": "customer", "text": text})

                # Ask LLM what to do
                print("  [thinking...]")
                decision = decide_response(kb, conversation)
                response_text = decision.get("response", "")
                action = decision.get("action", "respond")

                if action == "escalate":
                    # Escalate to human
                    escalation_msg = kb.get("escalation_message",
                        "Let me connect you with a specialist who can help further.")
                    print(f"  Agent (escalating): {escalation_msg}")
                    conversation.append({"role": "agent", "text": escalation_msg})
                    await ws.send(json.dumps({
                        "command": "tts.speak",
                        "text": escalation_msg,
                        "voice": voice,
                    }))
                    # Wait for TTS to finish, then leave
                    await asyncio.sleep(5)
                    await ws.send(json.dumps({"command": "meeting.leave"}))
                    end_reason = "escalated"
                    break

                elif action == "end":
                    # Wrap up the call
                    farewell = response_text or kb.get("farewell",
                        "Thanks for contacting us! Have a great day.")
                    print(f"  Agent (closing): {farewell}")
                    conversation.append({"role": "agent", "text": farewell})
                    await ws.send(json.dumps({
                        "command": "tts.speak",
                        "text": farewell,
                        "voice": voice,
                    }))
                    # Wait for TTS to finish, then leave
                    await asyncio.sleep(5)
                    await ws.send(json.dumps({"command": "meeting.leave"}))
                    end_reason = "resolved"
                    break

                else:
                    # Normal response
                    print(f"  Agent: {response_text}")
                    conversation.append({"role": "agent", "text": response_text})
                    await ws.send(json.dumps({
                        "command": "tts.speak",
                        "text": response_text,
                        "voice": voice,
                    }))

            # ── Call ended externally ──
            elif event_type == "call.ended":
                end_reason = event.get("reason", "unknown")
                print(f"\nCall ended: {end_reason}")
                break

    # Save conversation log
    save_call_log(call_id, conversation, end_reason, output_file)


def main():
    parser = argparse.ArgumentParser(
        description="AgentCall Customer Support Agent (1-on-1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py "https://meet.google.com/abc-def-ghi"
  python agent.py "https://meet.google.com/abc" --name "Sarah" --voice af_bella
  python agent.py "https://meet.google.com/abc" --output call-log.md
        """,
    )
    parser.add_argument("meet_url", help="Meeting URL (Google Meet, Zoom, or Teams)")
    parser.add_argument("--name", default="Support Agent", help="Bot name (default: Support Agent)")
    parser.add_argument("--voice", default="af_heart", help="TTS voice ID (default: af_heart)")
    parser.add_argument("--output", default=None, help="Output filename (default: support-log-DATE.md)")
    args = parser.parse_args()

    print(f"Creating support call for: {args.meet_url}")
    print(f"Bot name: {args.name}")
    print(f"Voice: {args.voice}\n")

    call = create_call(args.meet_url, args.name)
    print(f"Call created: {call['call_id']}")
    print(f"Status: {call['status']}\n")

    asyncio.run(run_agent(call, args.voice, args.output))


if __name__ == "__main__":
    main()
