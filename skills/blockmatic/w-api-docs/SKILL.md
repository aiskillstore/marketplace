---
name: w-api-docs
description: Refresh API docs from the owning schema source; never edit generated OpenAPI by hand.
disable-model-invocation: true
---

Update API documentation from the source of truth (TypeBox/Fastify routes, or the repo's documented generator). Never edit generated OpenAPI, generated clients, or generated SQL directly.

1. Read the API docs MDX and the generator README. Identify the owning source and the generate script in package.json.
2. Change the owning schema or route, not the generated artifact.
3. Run the documented generate command. Check drift scripts if the repo has them.
4. Update adopter MDX only for behavior that changed. Do not invent auth, rate-limit, or versioning policy.
5. Docs: `/w-docs` if behavior or commands changed.
