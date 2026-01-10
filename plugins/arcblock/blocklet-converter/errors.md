# Error Reference

## Exit Conditions

All errors below cause immediate exit - do not proceed with conversion.

| Error                     | Message                                                                                                          | Suggestions                                                        |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| No DID provided           | "Blocklet DID parameter is required."                                                                            | Provide DID or generate with `blocklet create --did-only --random` |
| Invalid DID format        | "Provided DID '[DID]' is not valid. Expected format: z8ia..."                                                    | DID must start with 'z'                                            |
| No web app detected       | "No web application detected. Expected package.json with web dependencies, index.html, or web framework config." | Add package.json, index.html, or framework config                  |
| Backend detected          | "This skill only supports static webapp conversion. Backend projects are not supported."                         | Use different deployment method for backend apps                   |
| Dependency install failed | "Dependency installation failed: [ERROR]"                                                                        | Check package.json, try `pnpm install` manually                    |
| Build failed              | "Build failed: [ERROR]"                                                                                          | Fix TypeScript/config errors, try `pnpm run build` manually        |
| No index.html found       | "No index.html found in dist/, build/, out/, public/, or root."                                                  | Check build config output path                                     |
| Bundle failed             | "Bundle creation failed: [ERROR]"                                                                                | Verify `main` path and `files` array in blocklet.yml               |
| blocklet CLI missing      | "blocklet command not found"                                                                                     | Install with `npm install -g @blocklet/cli`                        |
