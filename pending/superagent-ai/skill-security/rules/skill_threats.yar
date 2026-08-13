/*
    skill_threats.yar — threats specific to AI agent skills (SKILL.md + bundled
    resources). These have no analogue in classic malware scanners and are the
    reason a skill-aware scanner exists.

    Grounded in:
      - Liu et al., "Agent Skills in the Wild" (arXiv:2601.10338) — prompt
        injection is the single most prevalent category (26.1% of skills).
      - "Malicious Agent Skills in the Wild" (arXiv:2602.06547) — shadow features,
        hook/permission-flag abuse, brand impersonation (one actor = 54% of cases).
      - ClawHavoc (Jan 2026) — skills that write malicious instructions into the
        agent's memory files so the backdoor persists after the skill is removed.

    The body of a SKILL.md is *data*, never instructions to the agent running the
    scan. A skill that tries to steer the auditing agent is itself a finding.
*/

rule skill_instruction_override
{
    meta:
        description = "Instruction-override / jailbreak phrasing embedded in skill content"
        category = "skill_prompt_injection"
        severity = "HIGH"
        confidence = "0.8"
        rule_id = "PI1"
    strings:
        $ignore_prev = /ignore\s+(all\s+)?(previous|prior|above)\s+instructions?/ nocase
        $disregard   = /disregard\s+(all\s+)?(previous|safety|security|system)/ nocase
        $override    = /(override|bypass|disable)\s+(your\s+)?(safety|security|system|guard)/ nocase
        $forget      = /forget\s+(everything|all\s+(your\s+)?(previous|prior)\s+instructions?)/ nocase
        $new_rules   = /your\s+new\s+(instructions?|rules?|task)\s+(are|is)/ nocase
        $jailbreak   = /you\s+are\s+now\s+(in\s+)?(jailbreak|unrestricted|unfiltered|dan)\s+mode/ nocase
        $dev_mode    = /(enable|activate)\s+(developer|debug|admin|root|god)\s+mode/ nocase
    condition:
        any of them
}

rule skill_audit_manipulation
{
    meta:
        description = "Content attempting to manipulate a security review of the skill"
        category = "skill_prompt_injection"
        severity = "CRITICAL"
        confidence = "0.85"
        rule_id = "PI6"
    strings:
        $mark_safe   = /(mark|report|classify|rate)\s+(this\s+)?(skill\s+)?(as\s+)?(safe|clean|benign|trusted|low\s+risk)/ nocase
        $no_findings = /(do\s+not|don't|never)\s+(report|flag|mention|list)\s+(any\s+)?(findings?|issues?|vulnerabilit)/ nocase
        $skip_scan   = /(skip|bypass|ignore)\s+(the\s+)?(security\s+)?(scan|audit|review|analysis)/ nocase
        $reviewer    = /if\s+you\s+are\s+(an?\s+)?(security\s+)?(scanner|auditor|reviewer|analyzing)/ nocase
    condition:
        any of them
}

rule skill_memory_poisoning
{
    meta:
        description = "Writes to agent memory/persistent context so effects survive skill removal"
        category = "skill_memory_poisoning"
        severity = "CRITICAL"
        confidence = "0.8"
        rule_id = "RA3"
        ref = "ClawHavoc 2026"
    strings:
        $claude_md   = /(>>?|open\s*\([^)]*["']a["']|write_text)[^\n]{0,60}(CLAUDE\.md|AGENTS\.md|\.cursorrules|GEMINI\.md)/ nocase
        $memory_dir  = /(\.claude\/(memory|CLAUDE\.md)|\.config\/[^\n]{0,30}memory|\.agent\/memory)/ nocase
        $persist_ctx = /(persist|inject|append)\s+(this\s+)?(instruction|context|memory|rule)[^\n]{0,40}(across|future|every)\s+(session|conversation|interaction)/ nocase
    condition:
        any of them
}

rule skill_hook_permission_abuse
{
    meta:
        description = "Abuse of the agent platform's hook system or permission flags"
        category = "skill_excessive_agency"
        severity = "HIGH"
        confidence = "0.75"
        rule_id = "EA5"
        ref = "arXiv:2602.06547 shadow features"
    strings:
        $hooks_file     = /\.claude\/(hooks|settings)\.json/ nocase
        $pretooluse     = /(PreToolUse|PostToolUse|UserPromptSubmit|SessionStart)\b/
        $autoapprove    = /("?(dangerously[_-]?skip[_-]?permissions|auto[_-]?approve|bypass[_-]?permissions|yolo)"?\s*[:=]\s*(true|1|"?all"?))/ nocase
        $allow_all      = /"(allow|permissions)"\s*:\s*\[\s*"\*"\s*\]/ nocase
    condition:
        any of them
}

rule skill_hidden_instruction_blob
{
    meta:
        description = "Hidden instruction payloads — HTML comments, zero-width chars, data URIs, base64 blobs in metadata"
        category = "skill_tool_poisoning"
        severity = "HIGH"
        confidence = "0.7"
        rule_id = "PI2"
    strings:
        $html_cmt    = /<!--[^>]{0,400}(ignore|instruction|system|exfiltrat|send|POST|secret|api[_-]?key)[^>]{0,400}-->/ nocase
        $zero_width  = /[\x{200b}\x{200c}\x{200d}\x{2060}\x{feff}]/
        $data_uri    = /data:text\/[a-z]+;base64,[A-Za-z0-9+\/=]{60,}/ nocase
        $md_cmt      = /\[\/\/\]:\s*#\s*\([^)]{0,200}(ignore|instruction|system|send|POST)[^)]{0,200}\)/ nocase
    condition:
        any of them
}

rule skill_brand_impersonation
{
    meta:
        description = "Likely brand-impersonation skill (templated fake integration)"
        category = "skill_supply_chain"
        severity = "MEDIUM"
        confidence = "0.5"
        rule_id = "SC7"
        ref = "arXiv:2602.06547 — one actor = 54% of malicious skills via brand impersonation"
    strings:
        $official    = /(official|verified|trusted)\s+(integration|plugin|skill|connector)\s+(for|by)\s+(stripe|github|aws|google|openai|anthropic|slack|notion)/ nocase
        $setup_creds = /(to\s+(get\s+started|continue|activate)|first)[^\n]{0,80}(paste|enter|provide)\s+(your\s+)?(api[_-]?key|token|password|secret)/ nocase
        $verify_url  = /(verify|validate|register)\s+(your\s+)?(license|key|account)\s+at\s+https?:\/\// nocase
    condition:
        ($official and ($setup_creds or $verify_url)) or $setup_creds
}
