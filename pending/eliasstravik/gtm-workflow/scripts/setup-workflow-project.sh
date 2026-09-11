#!/usr/bin/env bash
set -euo pipefail

command -v vercel >/dev/null || { echo "Install the Vercel CLI first: https://vercel.com/docs/cli"; exit 1; }
workspace="${1:-$PWD}"
project="${2:-$(basename "$workspace")-workflows}"
workflow_dir="$workspace/workflows"
test -f "$workflow_dir/package.json" || { echo "Run this from a GTM workspace that contains workflows/package.json."; exit 1; }

vercel project add "$project" >/dev/null 2>&1 || true
vercel link --yes --project "$project" --cwd "$workflow_dir"
vercel project update "$project" --root-directory workflows --node-version 22.x --framework other --yes
vercel project protection disable "$project" --sso >/dev/null 2>&1 || true
run_secret="$(openssl rand -hex 32)"
cron_secret="$(openssl rand -hex 32)"
printf '%s' "$run_secret" | vercel env add GTM_RUN_SECRET production,preview --cwd "$workflow_dir" --force
printf '%s' "$cron_secret" | vercel env add CRON_SECRET production,preview --cwd "$workflow_dir" --force

project_json="$workflow_dir/.vercel/project.json"
project_id="$(node -p "require(process.argv[1]).projectId" "$project_json")"
team_id="$(node -p "require(process.argv[1]).orgId" "$project_json")"
echo "Project: $project"
echo "Project ID: $project_id"
echo "Team ID: $team_id"
echo "Run secret: $run_secret"
echo "Next: connect Turso in Vercel Marketplace, enable System Environment Variables, deploy, and record the production URL in workflows/package.json gtm.vercel."
