# Screens (Olbrain staff)

Only verified @olbrain.com accounts have the screen tools; nobody else does. A screen is a
front end on screens.olbrain.com that calls the organisation's agents. You write its code;
Alchemist creates it, builds its agents, connects them, uploads and publishes. Making one
public, unpublishing, archiving and deleting stay in Studio at https://studio.olbrain.com/screens.

To build one end to end, in this order:

1. Agree with the user what it shows and does, and which agents it needs. Each agent is a
   role: a chat agent is `conversational`, an automatic job is `workflow`. Connecting agents
   (step 7) needs an owner, super admin or admin of the active organisation: check the
   user's role with `list_members` first, and if they aren't one, stop before creating
   anything and say an admin has to connect the agents.
2. `alchemist_screen_create` reserves it in the active organisation and returns its `app_id`.
   It takes a `name`, a one-line `tagline`, an `icon` from Noesis's icon set (like
   `briefcase`) and the `department_id` it sits under (like `sales` or `finance`): agree the
   department with the user. First name the active organisation (`whoami`) and let the user
   confirm it: a screen can't move to another organisation later.
3. Write it in olbrain-noesis-apps (`gh repo clone Olbrain/olbrain-noesis-apps` if it isn't
   here); its README is the contract. `cp -r starter apps/<folder>`; in `app.json` set `"id"`
   to the `app_id`, keep `"host": "screens"`, list the roles in `agent_roles` as
   `{ "key", "label", "required", "runtime" }`. Import only what `shared-screens.json` lists;
   reach agents through `useScreen().bindings` and `agents()` from `screens/host`
   (`apps/screens_check` is the smallest example). `npm ci` once, then `npm test -- <folder>`.
4. Build each role's agent with `alchemist` as any build, cards included, and publish it; or
   use an agent the organisation already has. Keep each `agent_id`.
5. Commit on a branch, push, and open a PR for review: the upload needs the commit's URL. Merge
   that PR with a merge commit, not a squash, so the commit each version records stays in
   main's history.
6. Upload and publish as below. Publishing v1 of a screen the user asked for is part of the build.
7. `alchemist_screen_roles` with `{role key: agent_id}` connects them, then finish everything
   left in `setup_missing`. A bare `<role key>` is a required role with no agent yet: connect
   one. `<role key>:calendly` means that role's agent hasn't signed in to Calendly: add the
   Calendly connector to that agent with `alchemist` (its card takes the sign-in in the
   browser), or connect Calendly on the agent in Studio.
8. Give the user the screen's `url`; only organisations that have the screen see it, which for a
   new one is the active organisation alone.

Upload and publish:

- `alchemist_screens` finds a screen's `id`; its `last_version` counts failed and deleted
  uploads too.
- `npm run package -- <folder>` writes `dist/<id>.zip`. Push the build's commit first: the
  upload needs `https://github.com/Olbrain/<repo>/commit/<sha>`.
- Upload in three steps: `alchemist_screen_upload` with `app_id`; then
  `curl -sf -X PUT -H "Content-Type: <content_type>" --data-binary @dist/<id>.zip "<url>"`
  with `put` from that reply; then `alchemist_screen_upload` again with `upload_id` and
  `source_commit_url`. The URL is a 30-minute write link: run it, don't show it. An expired
  upload starts over from the first step.
- `passed: false` lists every failed check: show them all, fix them, and upload again.
- After the first version, `alchemist_screen_publish` only when the user asks; it changes the
  screen for every organisation that has it, and an older version rolls back. On
  `needs_confirmation`, show `role_changes` and `installs` in full and resend with
  `confirm: true` only on the user's own yes, in auto mode too. Then give the user the
  screen's `url`.
