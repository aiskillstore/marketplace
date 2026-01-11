# Prompt
This is the history of the conversation between the user and the agent. Take it and use it to understand the next user request. Include summarized version of your conversation with the user in the user_prompt_summary field. This way our fork agent has a history of the conversation and can use it to understand the next user request.

## History

'''yaml
- history:
    - user_prompt_summary: User wanted to fork terminal with Gemini CLI fast model to summarize .claude/commands
      agent_response_summary: Debugged fork_terminal - fixed nvm not loading (changed to bash -li), fixed Gemini theme config (set ANSI in project .gemini/settings.json). Fork worked, captured output showing all 21 commands summarized.
    - user_prompt_summary: User asked if captured output is terminal output or actual agent output
      agent_response_summary: Confirmed it's full terminal output (startup noise, errors, profiler metrics + agent response). User wanted clean agent-only output.
    - user_prompt_summary: User wanted 3 separate variables - LOG_TO_FILE (debug, default false), LOG_AGENT_OUTPUT (clean JSON, default true), READ_CAPTURED_OUTPUT (inject to context)
      agent_response_summary: Implemented full refactor of fork_terminal.py - added log_agent_output param, changed log_to_file default to false. Agent output goes to /tmp/fork-agent-*.json, debug to /tmp/fork-debug-*.txt. Updated SKILL.md and all 6 cookbooks with Clean Output Capture sections showing JSON output flags for each CLI.
'''

## Next User Request

Understand this codebase, then write a 20 line summary in the README.
