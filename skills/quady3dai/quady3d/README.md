# Quady3D Agent Skill

[Official setup and examples](https://quady3d.com/integrations/agent-skill) · [MCP installation](https://quady3d.com/integrations/mcp) · [Developer API](https://quady3d.com/developers)

This Skill guides an agent through generating a 3D asset, recovering its original task and saving the result into the requested project. It requires the Quady3D MCP server and an account with the appropriate credits and download access. The Skill itself does not provide cloud access.

Install this repository's `quady3d` Skill with your host's supported Skill installer. For hosts supported by the skills CLI:

```sh
npx skills add quady3dai/quady3d-tools --skill quady3d
```

Or download `quady3d-skill-0.1.2.zip` from the versioned [release](https://github.com/quady3dai/quady3d-tools/releases/tag/v0.1.2) and install the contained `quady3d` folder into your host's Skill directory. Install MCP separately; see the official setup page above.

Only the documented standalone Codex workflow has been verified. Claude remains pending verification. Read-only account/model checks do not generate a paid task; creation requires the user's authorized credit limit. Uninstall the Skill through the host or remove only its own folder. Remove the MCP connection and revoke the API key separately when disconnecting.

Client license: MIT. Hosted services and generated assets have their own terms.
