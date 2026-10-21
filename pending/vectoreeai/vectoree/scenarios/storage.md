# Storage

Use this playbook for **S30–S33** and **C05**. Parent skill: `SKILL.md` in this folder (or https://raw.githubusercontent.com/VectoreeAI/vectoree-skills/main/skills/vectoree/SKILL.md)

Need a project API key first (`scenarios/connect.md`). List buckets before creating. Say public vs private out loud.

---

## S30: which buckets?

```bash
npx @vectoree/cli storage buckets list
```

---

## S31: create a public uploads / avatars bucket

```bash
npx @vectoree/cli storage buckets create uploads --public
```

`--public` means world-readable. Omit it for private (the default).

---

## S32: upload this file

```bash
npx @vectoree/cli storage upload uploads ./photo.png
npx @vectoree/cli storage upload uploads ./photo.png --key avatars/me.png
npx @vectoree/cli storage ls uploads
npx @vectoree/cli storage ls uploads avatars/
```

CLI prints `Uploaded … → bucket/key`.

---

## S33 / C05: content page that can upload images

1. Connect if needed (`scenarios/connect.md`).
2. Create a table if the page stores posts (`scenarios/database.md`, e.g. `posts`).
3. Create a public or private bucket (S31). Public is simpler for a first demo; private needs auth later.
4. Probe upload with S32 so `storage ls` shows a file.
5. Wire the frontend with `npx @vectoree/cli docs get storage-sdk`. Keep the project API key on the server.

Signed download URLs (`storage url`) and `storage download` are **not** in the launch CLI. Do not invent those commands. If the user needs a signed URL, say so and point at Dashboard / `docs get storage-sdk`.

C05 done when the bucket exists, `storage ls` shows a file, and the page can pick an image.
