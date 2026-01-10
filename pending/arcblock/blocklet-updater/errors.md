# Error Reference

## Exit Conditions

All errors below cause immediate exit - do not proceed with bundling.

| Error                     | Message                                                         | Suggestions                                                                    |
| ------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| No blocklet.yml           | "No blocklet.yml found. This is not a blocklet project."        | Run blocklet-converter first or create blocklet.yml manually                   |
| Version bump failed       | "Version bump failed: [ERROR]"                                  | Check blocklet.yml format, ensure version field exists                         |
| Dependency install failed | "Dependency installation failed: [ERROR]"                       | Check package.json, try `pnpm install` manually |
| Build failed              | "Build failed: [ERROR]"                                         | Fix TypeScript/config errors, try `pnpm run build` manually                    |
| No index.html found       | "No index.html found in dist/, build/, out/, public/, or root." | Check build config output path                                                 |
| Meta verification failed  | "Metadata verification failed: [ERROR]"                         | Check blocklet.yml required fields: did, name, version                         |
| Bundle failed             | "Bundle creation failed: [ERROR]"                               | Verify `main` path and `files` array in blocklet.yml                           |
| blocklet CLI missing      | "blocklet command not found"                                    | Install with `npm install -g @blocklet/cli`                                    |
