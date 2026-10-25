# Worked examples

Paired examples for the decisions authors get wrong most often: step shape, guidance fading, checkpoints, objective wording, and the shape of an audit hand-back.

## Table of Contents

- [1. Step shape](#1-step-shape)
- [2. Guidance fading](#2-guidance-fading)
- [3. Checkpoints](#3-checkpoints)
- [4. Objective wording](#4-objective-wording)
- [5. Audit hand-back](#5-audit-hand-back)

## 1. Step shape

### Bad

> ## Step 3: Set up the database
>
> Now configure your database connection. Depending on whether you're using Postgres or MySQL, install the appropriate driver and set your connection string. You may also want to configure a connection pool - see the configuration reference for the available options. Then run the migration.

Four defects:

- Two new concepts (driver, pooling).
- A branch the learner must resolve.
- No code.
- No observable output.

A learner who gets an error here cannot tell which decision caused it.

### Good

> ## Step 3: Connect to the database
>
> Create `db.js` with the connection:
>
> ```js
> import postgres from "postgres";
>
> export const sql = postgres("postgres://localhost:5432/tasks_tutorial");
> ```
>
> Check the connection:
>
> ```bash
> node -e "import('./db.js').then(({sql}) => sql\`select 1 as ok\`).then(console.log)"
> ```
>
> Expected output:
>
> ```
> Result(1) [ { ok: 1 } ]
> ```
>
> Connection refused? The database isn't running - see [Troubleshooting](#connection-refused).

One concept, one path, one command, real output, one fail branch. Pooling is a link in the next-steps section, not a decision on the critical path.

## 2. Guidance fading

The same tutorial at step 2, step 5 and step 8. What changes is how much the learner produces.

### Step 2 - full worked example

> Create `routes/tasks.js`:
>
> ```js
> import { Router } from "express";
> import { sql } from "../db.js";
>
> const router = Router();
>
> router.get("/", async (req, res) => {
>   const tasks = await sql`select * from tasks order by id`;
>   res.json(tasks);
> });
>
> export default router;
> ```

Complete, imports included, runs as pasted. A novice needs the whole thing - building it unaided at this stage costs attention the concept needs.

### Step 5 - diff-shaped, insertion point named

> In `routes/tasks.js`, add a filter above the existing handler:
>
> ```js
> // routes/tasks.js - add above router.get("/")
> const parseStatus = (value) =>
>   ["open", "done"].includes(value) ? value : null;
> ```
>
> Then use it inside the handler you wrote in step 2:
>
> ```js
> const status = parseStatus(req.query.status);
> const tasks = status
>   ? await sql`select * from tasks where status = ${status} order by id`
>   : await sql`select * from tasks order by id`;
> ```

The learner places the code themselves and reuses the shape they already know. The file is named and the insertion point is explicit, so placement is unambiguous without being automatic.

### Step 8 - requirement plus expected output

> Add pagination to the same endpoint. A request to `/tasks?limit=2&offset=2` should return the third and fourth tasks:
>
> ```json
> [
>   { "id": 3, "title": "Buy milk" },
>   { "id": 4, "title": "Call Ana" }
> ]
> ```
>
> Reject a `limit` above 100 with a 400. Stuck? [See one solution](#solution-pagination).

Same pattern the learner has now written twice, applied without a template. This is the step that produces criterion 5 of the pass threshold - the learner performing the skill unaided. Skipping it leaves them with a working app and nothing transferable.

### Negative example - no fading

Step 8 written like step 2, a full file to paste. It is faster to write, faster to complete, and teaches nothing: the learner never once produced the pattern.

## 3. Checkpoints

### Bad

> ## Checkpoint
>
> At this point everything should be working. If not, double-check the previous steps.

No command, no output, no recovery. "Double-check the previous steps" is what the learner was already going to do, and it is why they abandon here.

### Good

> ## Checkpoint: the API returns your tasks
>
> Start the server:
>
> ```bash
> npm start
> ```
>
> In a second terminal:
>
> ```bash
> curl -s localhost:3000/tasks
> ```
>
> Expected output:
>
> ```json
> [{ "id": 1, "title": "Write tutorial", "status": "open" }]
> ```
>
> You now have a running API reading from your own database.
>
> Empty array? The seed didn't run - `npm run seed`, then retry.
> Want to start fresh here tomorrow? `git checkout step-4` in the companion repo.
>
> **Optional:** before running the next step, predict what `curl -s "localhost:3000/tasks?status=done"` returns today. [Answer](#checkpoint-4-answer).

Verifiable state, a stated capability, two recovery routes, and an optional retrieval-practice prompt with the answer available - difficulty placed after the checkpoint passes, never on the critical path.

## 4. Objective wording

| Weak                      | Strong                                                           |
| ------------------------- | ---------------------------------------------------------------- |
| Understand authentication | Protect an endpoint so unauthenticated requests get a 401        |
| Learn about our SDK       | Stream a model response into a terminal UI with the SDK          |
| Explore webhooks          | Receive a webhook, verify its signature, and reject a forged one |
| Understand pagination     | Add server-side pagination to a REST endpoint                    |

The strong column is testable: at the end you can ask the learner to do it on a variation and see whether they can. The weak column can only be asked about, never demonstrated - which is why tutorials written from it drift into feature tours.

## 5. Audit hand-back

The request was "nobody finishes our webhooks tutorial".

### Bad

> I read through the tutorial. Overall it's solid but a bit long, and the tone could be friendlier. Step 4 is probably where people get lost - the signature verification part is complex and could use more explanation. I'd also suggest adding screenshots and breaking up the longer paragraphs. Happy to draft a revision.

Nothing here is falsifiable. "Probably where people get lost" is a guess from reading, which is exactly the input the verification protocol exists to replace, and "more explanation" pushes the page toward the one thing Diátaxis says blocks learning. An author can act on none of it without redoing the diagnosis themselves.

### Good

> Two cold runs, both matching the declared level (backend engineers, no prior use of the product). Both stopped inside step 4. Ordered by learners blocked:
>
> | Step | Event               | What happened                                                                                                                                                         | Fix                                                                                            |
> | ---- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
> | 4    | Defect              | `verify(payload, sig)` documented as returning a boolean; the published SDK 3.x returns an object. Both runners hit a false negative and assumed their key was wrong. | Regenerate the block from a real run against 3.x; add the return shape to the expected output. |
> | 2    | Hidden prerequisite | Tunnelling tool never mentioned; both runners stalled ~6 min before finding one.                                                                                      | Add to "Before you begin" with a check command.                                                |
> | 4    | Concept gap         | Both completed the step and neither could say what the signature protected against. Step 4 introduces the header, the secret and the comparison at once.              | Split into 4a (read the header) and 4b (compare the digest), one output each.                  |
> | 6    | Friction            | "Add the handler to your app" - no file named. Both scrolled back to step 2 to guess.                                                                                 | Name the file and the insertion point.                                                         |
>
> Not defects: the missing screenshots, the paragraph length. Neither runner hesitated at either.
>
> Rewriting steps 2 and 4 first covers both blocked runs. Sending the revision back through one more cold run before publishing.

Every row is an observation with an owner, and the last block matters as much as the table: it stops the author from spending the rewrite on cosmetics nobody stumbled over.
