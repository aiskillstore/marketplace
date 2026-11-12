---
name: cloud-computer-task
description: Hand a long web task (scan job boards, fill forms, collect a lead list, book an appointment) to your own cloud computer and get the result back. Use when a task needs a real browser for a long time.
---

# Cloud computer task

MyClawn gives an assistant its own cloud computer: a browser that stays signed in, its own email address and files. A task runs there, can outlast the chat, and comes back with the answer, a screenshot of the final screen and a link to a screen recording.

## Setup (once, by the user)

Connect the MyClawn Computer server with the user's own MyClawn account (OAuth sign-in): https://www.myclawn.com/mcp/desktop
Claude Code: `claude mcp add --transport http myclawn https://www.myclawn.com/mcp/desktop`, then `/mcp` and choose myclawn to sign in. Other clients: https://github.com/20vision/myclawn-computer-mcp
A new account gets a free 24-hour computer on its first task. Plans and details: https://www.myclawn.com/docs/connectors?utm_source=agent-skills&utm_medium=probe

## Steps

1. Only use it for work that needs a real browser over time: scanning job boards, filling forms, building a lead list, booking an appointment, work behind a login. For anything a plain web search answers, do not use it.
2. Write the task in plain words with the goal, the sites, what the result must look like (a table, a list, a confirmation) and what must not be done. Show it to the user before sending anything that submits a form or books something.
3. Send it with the connector's task tool, wait for the result, and report the answer, the screenshot and the recording link.
4. If the connector is not signed in, tell the user to do the sign-in; do not try to create accounts for them.
