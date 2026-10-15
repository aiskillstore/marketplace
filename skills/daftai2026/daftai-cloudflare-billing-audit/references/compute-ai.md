# Containers, Browser Rendering, Workers AI and AI Gateway

Default scope is offline, read-only source review; do not query a live account. Use runtime metrics only if the user separately supplies redacted evidence. Distinguish each biller and operation that starts/stops it. Do not infer a runaway loop from a billing dispute or a binding.

## CF-CONTAINERS-IDLE-RUNTIME — allocated runtime outlives useful work
- Risk conditions: start/sleep/stop logic can leave a container running or allocated after the job has finished, or concurrency/lifetime is unbounded.
- Check: start triggers, idle timeout, sleep/stop paths, allocation sizes, concurrency, logs and egress.
- Mitigation and trade-off: ensure sleep/stop on idle, bound lifetime/concurrency/allocations and clean up unused deployments. Aggressive shutdown can interrupt work.
- Blind spots: ahmetb-moltworker-containers is an expectation-mismatch report, not proof of an idle container. No cited case proves this specific mechanism.
- Evidence: caseId ahmetb-moltworker-containers; guideId sarmaasis-cloudflare-under-five-dollars; official sourceIds CF-DOC-CONTAINERS-PRICING, CF-DOC-CONTAINERS-LIMITS.

## CF-BROWSER-RUN-SESSION-LIFETIME — unclosed or repeated sessions
- Risk conditions: browser session launches repeat, lack a close/finally path, or have no page/session/time/concurrency bound.
- Check: session creation/close paths, retries and trigger fan-out; distinguish Browser Run hours from session concurrency.
- Mitigation and trade-off: always close sessions, cap sessions/pages/time and use plain fetch when JS rendering is unnecessary. This may reduce fidelity or require reconnect/session-state handling.
- Blind spots: loftwah-browser-rendering is a user's correction about unrecognized usage, not proof of an unclosed-session bug.
- Evidence: caseId loftwah-browser-rendering; guideId sarmaasis-cloudflare-under-five-dollars; official sourceIds CF-DOC-BROWSER-PRICING, CF-DOC-BROWSER-LIMITS.

## CF-WORKERS-AI-CALL-AMPLIFICATION — repeated inference calls
- Risk conditions: agent/tool loop or retry path makes unbounded model calls/tokens without per-user quota/output bound.
- Check: call sites, loop exit criteria, retries, model selection, token/output bounds and whether the biller is Workers AI or an upstream BYOK provider.
- Mitigation and trade-off: cache, cap calls/tokens, deduplicate and enforce per-user quotas. Smaller models/caps can reduce quality or abort tasks.
- Blind spots: jason-silberman-ai-billing is an alleged duplicate usage/prepaid mismatch, not evidence of code-loop inference; no cited case establishes runaway AI code.
- Evidence: guideId sarmaasis-cloudflare-under-five-dollars; caseId jason-silberman-ai-billing is attribution context only; official sourceIds CF-DOC-WORKERS-AI-PRICING, CF-DOC-WORKERS-AI-LIMITS.

## CF-AIGW-SPEND-LIMIT-OVERRUN — gateway scope and consistency
- Risk conditions: application relies on an AI Gateway budget as a strict global cap, or costly calls bypass the configured gateway/rule scope.
- Check: gateway identity, model/provider/metadata scope, route path, concurrent calls and BYOK billing destination.
- Mitigation and trade-off: route relevant calls through the intended gateway; combine budget rules with app-level concurrency/quota controls. Blocking or fallback can interrupt or degrade requests.
- Blind spots: gateway accounting is eventually consistent; a burst can briefly overrun. This is a gateway control limitation, not an observed Billflare runaway case.
- Evidence: Billflare case/guide precedent: none cited; official sourceIds CF-DOC-AI-GATEWAY-SPEND, CF-DOC-AI-GATEWAY-PRICING.
