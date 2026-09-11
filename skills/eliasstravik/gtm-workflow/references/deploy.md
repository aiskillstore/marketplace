# Deploy

The workspace needs a pushable `origin`. When absent, repository setup is a separate card before deployment.

## Scripted path

1. Run `scripts/setup-workflow-project.sh` from the workspace checkout. Its one approval creates and configures the workflow project.
2. Paste workflow-specific provider keys that the verification card names.
3. Confirm the Git commit author is a member of the Vercel team.

Set `AI_GATEWAY_API_KEY` on the workflow project unless the deployment already authenticates to AI Gateway with OIDC; if the one-row hosted test fails with an authentication error, the key is the fix. A locally tested AI step switches to the hosted Gateway model after deployment, and the one-row hosted test proves that path.

## Dashboard path

1. Vercel → Add New → Project → import the workspace repository.
2. Set Root Directory to `workflows`.
3. Settings → General → Node.js Version → 22.x.
4. Storage → Marketplace → Turso → connect the database.
5. Settings → Environment Variables → add `GTM_RUN_SECRET`.
6. Add `CRON_SECRET` and, unless OIDC Gateway auth is confirmed, `AI_GATEWAY_API_KEY`.
7. Add provider keys named by `gtm verify --url`.
8. Settings → Deployment → enable System Environment Variables.
9. Settings → Deployment Protection → turn protection off for Production.
10. Record team, project, and production URL under `gtm.vercel` in `package.json`, then redeploy.

The Diagram and Runs links require a Vercel login. Data requires a Turso login. A deploy that does not become live in eight minutes reports: `Saved, but the hosted copy did not come live in 8 minutes. Ask whoever set this up to check the Vercel build.`
