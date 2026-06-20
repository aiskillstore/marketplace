# Telemetry Hook Recipes

These recipes show how Browser, Chrome, IDE, wrapper, or provider-side integrations can call `telemetry-emit` without collecting raw prompts, outputs, transcripts, messages, notes, arguments, or file content.

They are client hook recipes, not proof that a host client is already natively integrated.

## Summary

- Recipe count: `5`
- Native auto-capture integrations claimed: `0`
- Default spool: `.yao/telemetry_spool/external_events.jsonl`

## Recipes

| Client | Command | Event | Outcome | Dry run |
| --- | --- | --- | --- | --- |
| Browser extension | `browser-extension` | `skill_activation` | `accepted` | `python3 scripts/yao.py telemetry-emit . --output-jsonl .yao/telemetry_spool/external_events.jsonl --event skill_activation --activation-type explicit --outcome accepted --failure-type none --command browser-extension --dry-run` |
| Chrome extension | `chrome-extension` | `skill_output` | `edited` | `python3 scripts/yao.py telemetry-emit . --output-jsonl .yao/telemetry_spool/external_events.jsonl --event skill_output --activation-type manual --outcome edited --failure-type none --command chrome-extension --dry-run` |
| VS Code extension | `vscode-extension` | `skill_activation` | `accepted` | `python3 scripts/yao.py telemetry-emit . --output-jsonl .yao/telemetry_spool/external_events.jsonl --event skill_activation --activation-type implicit --outcome accepted --failure-type none --command vscode-extension --dry-run` |
| CLI wrapper | `cli-wrapper` | `script_run` | `unknown` | `python3 scripts/yao.py telemetry-emit . --output-jsonl .yao/telemetry_spool/external_events.jsonl --event script_run --activation-type manual --outcome unknown --failure-type none --command cli-wrapper --dry-run` |
| Provider adapter | `provider-adapter` | `skill_output` | `accepted` | `python3 scripts/yao.py telemetry-emit . --output-jsonl .yao/telemetry_spool/external_events.jsonl --event skill_output --activation-type manual --outcome accepted --failure-type none --command provider-adapter --dry-run` |

## Import

After a client finishes a batch, import the local spool:

```bash
python3 scripts/yao.py telemetry-import . --input-jsonl .yao/telemetry_spool/external_events.jsonl
```

## Privacy Contract

- Allowed fields: `event`, `skill`, `version`, `source`, `command`, `activation_type`, `outcome`, `failure_type`, `timestamp`.
- Blocked raw-content fields: `content, input, inputs, message, messages, note, output, outputs, prompt, raw, text, transcript`.
- Client integrations must map local state to normalized outcome classes before calling the hook.
