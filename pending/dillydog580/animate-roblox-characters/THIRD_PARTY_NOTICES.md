# Third-Party Components

Repository-authored code is MIT. Third-party components retain their own terms.

## Bundled

**Roblox Animations Importer/Exporter 2.6.3** by Cautioned is bundled unmodified as `assets/blender-addons/rbx_anims_v2.6.3.zip` under GPL-3.0-or-later. Its license is included at `assets/blender-addons/Cautioned-Blender-Animations-Plugin-LICENSE.txt`.

- Source: <https://github.com/Cautioned/Blender-Animations-Plugin>
- Release: <https://github.com/Cautioned/Blender-Animations-Plugin/releases/tag/v2.6.3>
- Release commit: `6ed4dca` (GitHub verified signature)
- Release SHA-256: `218b5e43e414fe3fa5d8a42cc5fd162b70e66f4cb82efd73ac5006b63895769a`

The extension includes optional Roblox OAuth/asset networking and a localhost live-sync server. The skill keeps those features off during ordinary authoring.

## Mandatory source-pinned external rig

**R6 IK + FK Blender Rig V2.22** and its matching Studio model are downloaded from Aeresei's original Roblox DevForum attachments by `fetch_assets.py`.

- Source: <https://devforum.roblox.com/t/r6-ik-fk-blender-rig-v222/3586405>
- Blender SHA-256: `ff75c44b572d32328b62095141c6ce6255c4e9b772ee63d46d92280de1edcdc8`
- Studio RBXM SHA-256: `a85e1ce13b6cb15c2094be8afcf6bd66ab2017e10f42be6ecb95faa20dd93444`

The author shares the files for use but does not state a redistribution license. The public Git repository does not mirror the source `.blend` or `.rbxm`; the installer downloads them from the original attachments and verifies them locally.

The README preview is a rendered documentation example made with this source-pinned rig. It does not contain the editable rig or Studio model. The original rig remains subject to its author's terms.

## External integrations

- Blender — GPL-3.0-or-later; <https://www.blender.org/>
- Blender MCP — MIT; <https://github.com/ahujasid/blender-mcp>
- Pillow — HPND; <https://pypi.org/project/pillow/>
- Blender Animations (ultimate edition) Studio plugin — Roblox Creator Store terms; <https://create.roblox.com/store/asset/16708835782/Blender-Animations-ultimate-edition>
- Roblox Studio MCP — Roblox platform terms; <https://create.roblox.com/docs/studio/mcp>
- Roblox official project files — Roblox platform terms; <https://create.roblox.com/docs/art/modeling/project-files>

Tutorial mirrors, copied textures, alternate faces, and Lazy Viewport are not redistributed or used by the skill.
