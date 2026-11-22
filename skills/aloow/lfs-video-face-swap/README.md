# Live Face Swap Agent Skill

Use this Skill with Live Face Swap to get a credit estimate, start an approved face swap on a prerecorded MP4, and retrieve the result. You need a Live Face Swap account and a client that supports Streamable HTTP, OAuth with PKCE, and dynamic client registration.

## Install and connect in Codex

1. In your project, create `.agents/skills/lfs-video-face-swap/` and put both `SKILL.md` and `README.md` in that folder.
2. Add this server to your Codex `config.toml`.

   ```toml
   [mcp_servers.live-face-swap]
   url = "https://live-face-swap.net/api/mcp"
   scopes = ["video_swap"]
   ```

3. Run `codex mcp login live-face-swap --oauth-client-registration dcr`. Sign in and approve the connection in the browser, then start a new Codex chat in your project and invoke `$lfs-video-face-swap`.

For another compatible assistant, install the folder using that client's Agent Skills instructions and add Live Face Swap as a remote MCP server using the URL and OAuth scope above. See the [Live Face Swap MCP guide](https://live-face-swap.net/mcp).

## Try it

**Estimate only**

> $lfs-video-face-swap Estimate the credits for a 10-second video. I only need the price right now.

The assistant returns an estimate. An exact quote is available after you prepare the actual files on the site.

**Prepare, confirm, and download**

1. Ask “$lfs-video-face-swap 帮我估算一段 10 秒 MP4 的换脸费用，再给我一个准备素材的链接。”
2. Open the private link. Select your MP4 and an authorized portrait, then review and approve the exact quote.
3. Tell the assistant “我已在网页确认报价，请开始换脸。完成后把下载页发给我。”
4. Open the private result page to preview and download the completed MP4.

**Resume an existing task**

> $lfs-video-face-swap Check my Live Face Swap task again using the task ID I provide.
