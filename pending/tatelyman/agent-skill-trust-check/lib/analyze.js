export const FINDING_RULES = [
  {
    id: 'shell-execution',
    label: 'Shell or process execution',
    weight: 8,
    pattern: /\b(shell|bash|zsh|powershell|cmd\.exe|child_process|execSync|spawn|subprocess|os\.system)\b/i,
    advice: 'Require exact command allowlists, dry-run mode, and visible permission boundaries before install.',
  },
  {
    id: 'destructive-command',
    label: 'Destructive command pattern',
    weight: 10,
    pattern: /\b(rm\s+-rf|mkfs|dd\s+if=|chmod\s+777|chown\s+-R|sudo\b|curl\s+[^|]+\|\s*(sh|bash))\b/i,
    advice: 'Remove destructive examples or put them behind explicit human confirmation and scoped paths.',
  },
  {
    id: 'secret-access',
    label: 'Secret or credential access',
    weight: 9,
    pattern: /\b(api[_-]?key|auth[_-]?token|password|secret|private[_-]?key|seed phrase|mnemonic|\.env|process\.env|credential)\b/i,
    advice: 'Document what secrets are read, why they are needed, and how outputs avoid logging or exfiltration.',
  },
  {
    id: 'wallet-payment',
    label: 'Wallet or payment action',
    weight: 8,
    pattern: /\b(wallet|sign(ature|ing)?|transaction|transfer|usdc|x402|payment|settle|payTo|eip-3009)\b/i,
    advice: 'Add quoted amount, network, recipient, replay/idempotency, and approval boundaries before any signing flow.',
  },
  {
    id: 'network-exfil',
    label: 'Network or webhook output',
    weight: 6,
    pattern: /\b(fetch|axios|curl|webhook|post\s+to|upload|send\s+to|http:\/\/|https:\/\/)\b/i,
    advice: 'List all remote hosts and the data sent to each host; redact secrets and user identifiers.',
  },
  {
    id: 'persistence',
    label: 'Persistence or background behavior',
    weight: 6,
    pattern: /\b(cron|launchd|systemd|daemon|background|startup|login item|persist|autostart)\b/i,
    advice: 'Make background behavior opt-in and include removal commands.',
  },
  {
    id: 'prompt-boundary',
    label: 'Weak prompt boundary',
    weight: 5,
    pattern: /\b(ignore previous|override instructions|system prompt|developer message|hidden instruction|jailbreak)\b/i,
    advice: 'Separate untrusted content from operational instructions and document prompt-injection handling.',
  },
];

export const POSITIVE_RULES = [
  { id: 'license', pattern: /\blicen[cs]e\b/i },
  { id: 'tests', pattern: /\b(test|spec|ci|github actions)\b/i },
  { id: 'permissions', pattern: /\b(permission|scope|allowlist|denylist)\b/i },
  { id: 'versioning', pattern: /\b(version|release|changelog|semver)\b/i },
  { id: 'source', pattern: /\b(source|repository|github\.com)\b/i },
  { id: 'uninstall', pattern: /\b(uninstall|remove|cleanup|disable)\b/i },
];

export function analyze(text, target = 'stdin') {
  const findings = FINDING_RULES.filter((rule) => rule.pattern.test(text)).map((rule) => ({
    id: rule.id,
    label: rule.label,
    severity: rule.weight >= 9 ? 'high' : rule.weight >= 7 ? 'medium' : 'low',
    advice: rule.advice,
  }));

  const positives = POSITIVE_RULES.filter((rule) => rule.pattern.test(text)).map((rule) => rule.id);
  const missing = POSITIVE_RULES.filter((rule) => !rule.pattern.test(text)).map((rule) => rule.id);
  const riskScore = findings.reduce((sum, finding) => {
    const rule = FINDING_RULES.find((item) => item.id === finding.id);
    return sum + (rule?.weight || 0);
  }, 0);

  let verdict = 'review_before_install';
  if (riskScore >= 24 || findings.some((finding) => finding.severity === 'high')) {
    verdict = 'do_not_install_without_changes';
  } else if (riskScore <= 6 && missing.length <= 2) {
    verdict = 'reasonable_to_trial_in_sandbox';
  }

  return {
    target,
    verdict,
    risk_score: riskScore,
    findings,
    positives,
    missing_signals: missing,
    patch_order: findings.map((finding) => finding.advice),
    next_step: 'For marketplace-grade review, run the paid Agent Skill Trust Check listing or request a private review from Tate Programs.',
  };
}
