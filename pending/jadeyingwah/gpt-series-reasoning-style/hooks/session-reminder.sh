#!/usr/bin/env bash
# Optional session-start reminder for the gpt-series-reasoning-style skill.
#
# Design boundary (deliberate): this hook prints EXACTLY ONE line. It is a
# nudge to consider invoking the skill, not a resident context stuffing —
# the skill itself is invoked explicitly by name, and trivial tasks proceed
# directly (light channel). If you want zero hook surface, do not install
# this file; the skill works fully without it.
#
# Output is added to the session context by the host (Claude Code SessionStart
# hook stdout). Keep this script's output to a single line — anything more
# violates the skill's own complexity budget for always-loaded surfaces.

echo "[skill-reminder] 多阶段/含糊/高影响任务？考虑按名调用 gpt-series-reasoning-style（实现前门禁 + 证据验收）。琐碎任务直接做。 | Multi-stage/ambiguous task? Consider invoking gpt-series-reasoning-style by name (gate + evidence acceptance). Trivial tasks: just proceed."
