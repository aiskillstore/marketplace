# Multi-Platform Livestream Chrome & FX — REA Reverse-Engineering Ledger
# 主流直播平台（抖音 / 快手 / Ins / X / TikTok）边框、弹窗与特效逆向复刻台账

This document records the structured **REA (`reverse-engineer-anything`)** investigation, protocol/CSS evidence, `1080×1920` safe-zone geometry, interactive popup state machines, and clean-room design boundaries backing `scripts/hud_presets.mjs`, `scripts/compose_hud.py`, and `studio/index.html`.

---

## 1. Evidence & Verification Ledger (Observed vs. Published Spec vs. Clean-Room Design)

Following REA evidence discipline, every architectural rule separates **cryptographically digested REA observations**, **open wire-protocol / published platform specifications**, and **trademark-clean reconstruction choices**:

| Evidence / Source | Artifact / Digest / REA Evidence ID | Verified Facts Established | Scope & Known Limitations |
| --- | --- | --- | --- |
| **REA Static JS Analysis — Periscope/X Heart Fountain** | `ev_b0cb9e3c7367d554a845d39a207cc90d190d69459e69b8182eaa12fc274c71f7` (`root_artifact_sha256: 89bcc74c...fc23d2`, `Hearts.js` + `Hearts.css`) | Confirms 6 viewer-assigned heart tint classes (`colOne #fce473`, `colTwo #f68b39`, `colThree #ed6c63`, `colFour #847bb9`, `colFive #97cd76`, `colSix #35b1d1`), 3 sinusoidal keyframe trajectories (`flowOne`, `flowTwo`, `flowThree`), `1.2s–1.6s` linear rise duration, and `22px–50px` size jitter. | Static open-source Periscope-style module; does not inspect proprietary X iOS/Android binaries. |
| **Douyin / TikTok Webcast Protobuf Schema** | `TikTok-Webcast-Protobuf/src/slim/v1/webcast.proto` (`blob sha: dd596091...832a32a4`) | Establishes exact room event channels: `WebcastRoomUserSeqMessage` (`topViewers[]`, `viewerCount`), `WebcastChatMessage` (`user.badges`, `PrivilegeLogExtra.level`, `emotes`), `WebcastMemberMessage` (join ribbon), `WebcastGiftMessage` (`giftId`, `repeatCount`, `repeatEnd`, `groupId`), `WebcastLikeMessage` (`likeCount`, `totalLikeCount`), `WebcastLinkMicBattle` & `WebcastLinkMicArmies` (`points`, `battleStatus`), `WebcastHourlyRankMessage`, and `WebcastEnvelopeMessage` (lucky bag/treasure box). | Open community-maintained `.proto` definitions matching Webcast push frames; live authenticated Douyin web rooms were DNS-unreachable from the build container (`capture_browser_scenario` partial observation recorded navigation boundary). |
| **Kuaishou Live Feed Protobuf & Safe-Zone Spec** | `ks.proto` (`blob sha: e33cbea4...0036`) + Kuaishou Open Mini-Play Standard (`open.kuaishou.com/miniPlayDocs/plan/standard.html`) | Establishes `SCWebFeedPush` (`PayloadType = 310`): `displayWatchingCount`, `displayLikeCount`, `commentFeeds` (`fansGroupIntimacyLevel`, `wealthGrade`), `comboCommentFeed` (`content`, `comboCount` for spammed danmaku like `×18`), `likeFeeds` (`"点亮了 ❤️"`), `giftFeeds` (`mergeKey`, `comboCount`, `slotDisplayDuration`, `StyleType.BATCH_STAR_0..6`), `SC_SHOP_OPENED (360)`, `SC_RED_PACK_FEED (330)`, `SC_PK_STATISTIC (381)`. Safe-zone spec locks `1080×1920` layout: **Header `0–340px`**, **Center Stage `340–1300px` (`960px` tall, `880px` safe width)**, **Bottom Comment Zone `1300–1920px` (`620px` tall)**. | Published Kuaishou developer spec + open protobuf schema. |
| **Live Room Scrim & Danmaku Mask CSS Spec** | `live-tiktok-compact.css` (`blob sha: e3acdfae...0c570696b2d`) + Figma Live Streaming UI System | Confirms `pointer-events: none` top scrim (`120px`, `rgba(0,0,0,0.48) → 0`) and bottom scrim (`320px`, `rgba(0,0,0,0.65) → 0`), `Chat_Feed_Stack` width cap (`260–280px` on `390px` viewport = `~68–72%` width so right-side heart fountain & shopping card remain unobstructed), bubble fill `rgba(0,0,0,0.36)` with `12px` radius, top fade `mask-image: linear-gradient(to bottom, transparent 0%, #000 22%)`, and **2-slot (`44px` height) serialized Gift Combo channel**. | Design-system and web-overlay CSS reference. |
| **REA Static & Playwright Runtime Verification of Reconstructed `studio/`** | Static JS Evidence: `ev_2f8fa33e2ba96c4324d0002c44971f998d984b90b3a7c50dc30285492bf02560` (`sha256: e81cf061...ca17c`)<br>Browser Scenario Evidence: `ev_6bcf0f46d070e9ba38f052c48760efab44c0060326de4184099d6c572529e6b6` | Verified all 13 interactive transitions across `douyin`, `kuaishou`, `instagram`, `x`, and `tiktok` presets plus the 3 live `<canvas>` clean-plate camera rigs (`studio-irl`, `wuxia-sword`, `roblox-obby`) in Chromium `157.0.8103.78` with **0 console errors**. | Confirms clean-room studio implementation fidelity and runtime stability. |

---

## 2. Five-Platform Visual & Interactive Architecture Matrix / 五大平台界面与交互对比

| Component / 组件 | 抖音直播间 (`douyin`) | 快手直播间 (`kuaishou`) | Instagram Live (`instagram`) | X / Periscope (`x`) | TikTok Live (`tiktok`) |
| --- | --- | --- | --- | --- | --- |
| **Primary Accent** | `#FE2C55` Rose + `#25F4EE` Cyan | `#FF5000` Warm Flame + `#FACC15` Gold | `#E1306C → #FF0069` Magenta + Sunset Story Ring | `#EF4444 / #F91880` LIVE + `#0F1419` Obsidian Glass | `#FE2C55` Rose + `#14B8A6` Sub Mint |
| **Top-Left Header** | Rounded black-glass host capsule (`Avatar + Nickname + 本场点赞 + 关注 pill`) + 2nd row `人气榜 / 小时榜 / 福袋` | Rounded host capsule (`+ 关注` orange pill + `红心热力`) + 2nd row `红心热力榜 / 快币红包` | Unboxed Story-ring avatar + `@username ⌄` (clean minimal top bar) | Crisp `LIVE` red badge + `18.4K watching` pill + `@handle` dark glass chip below | Rounded host capsule (`+ Follow` rose pill + `Likes`) + `Weekly Rank / Treasure` |
| **Top-Right Header** | Top 3 coin gifter circles + compact viewer pill (`24.8K`) + `×` close | Top watcher circles + `3.2万` pill + `×` close | Rectangular magenta `LIVE` badge + dark `14.2K` viewer pill + `×` close | Minimal `×` close + share/overflow | Top 3 gifter circles (`1/2/3`) + viewer pill + `×` close |
| **Comment / Danmaku Row** | `rgba(0,0,0,0.36)` rounded `12px` pill + blue/violet `[钻粉 Lv.16]` badge + sky-blue username | `rgba(12,10,8,0.44)` `10px` pill + orange `[铁粉]` badge + gold username + **`×18` combo danmaku pill** | **Zero background bubble** — pure white drop-shadowed text + top `25%` alpha fade | Individual dark glass `14px` cards (`rgba(15,20,25,0.80)`) with **left vertical 3px Periscope viewer color bar** | `rgba(0,0,0,0.36)` `12px` pill + `[Gifter Lv.24]` / `[Sub]` badge |
| **Enter / Join Event** | Blue-gradient slide-in ribbon above chat (`★ [钻粉] xxx 来了`) | Warm orange-gold highlight (`★ [铁粉] xxx 点亮了红心`) | Inline `● username joined · Wave` pill | `@handle joined & reposted` glass toast | `★ [Gifter Lv.24] user joined` ribbon |
| **Gift / Tip Popup** | **2-slot (`44px`) mid-left banner** merging by `groupId`, italic gold `×66` scale-pop (`1.0 → 1.36`) | Warm gold-orange beveled **穿云箭 `×18`** combo banner (`mergeKey` accumulator) | Subtle badge purchase highlight (`bought 3 Badges`) | `Super Heart Boost` highlight card | **2-slot mid-left `Sent Galaxy Rose ×99`** combo banner |
| **Signature Card Popup** | Bottom-right white **小黄车讲解卡** (`讲解中` red tag + thumb + `¥39.9` + `抢` CTA) | Bottom-right **小黄车秒杀卡** (`源头好物 ¥19.9 去抢`) | Centered frosted-glass iOS **Live Q&A Question Card** (`Question from @user`) | Pinned live broadcast topic banner | Pinned Creator Shop product card (`PINNED $24 Shop`) |
| **1v1 PK Split Bar** | Flush at `y=110px` (`390×844` ref): `#FE2C55` left vs `#25F4EE` right + tabular score + `PK` badge | `#FF5000` warm orange left vs `#1890FF` blue right + `PK` spark | Magenta `#E1306C` vs Violet `#833AB4` dual split | `#F91880` vs `#1D9BF0` split bar | `#FE2C55` vs `#25F4EE` `LIVE Match` bar |
| **Heart Fountain FX** | Rose/pink bezier fountain + full-screen double-tap burst | Rapid orange-red-gold heart fountain | Smooth magenta-crimson rising hearts | **6-color Periscope viewer-assigned S-curve fountain** (`#fce473, #f68b39, #ed6c63, #847bb9, #97cd76, #35b1d1`) | Rose + cyan + violet rising heart stream |

---

## 3. Safe-Zone Composition Rules for AI Camera Framing (`1080×1920` 构图防遮挡铁律)

When writing Clean-Plate First-Frame and I2V prompts intended for Post-HUD overlay, keep the streamer's face and held props inside the **Central Safe Stage**:

- **Top Avoid Zone (`0–340px` / top `18%`)**: Reserved for host capsule, rank chips, and PK score bar. Never frame the streamer's eyes in the top `15%` of the `9:16` canvas.
- **Bottom-Left Avoid Zone (`1300–1920px`, left `70%` width)**: Reserved for join ribbons, `Chat_Feed_Stack`, and comment input pill. Place desk surfaces, hands, or secondary environment texture here—never critical facial expressions or tiny clue objects.
- **Bottom-Right Avoid Zone (`right 148px`, bottom `35%`)**: Reserved for Live Shopping (`小黄车`) popup cards and rising heart fountains.
- **Golden Subject Anchor (`y = 340px..1260px` / `22%–65%` from top)**: Ideal vertical zone for the streamer's eyes (`~34–42%` from top), `18cm` autofocus showcase items (`~48–58%` from top), and corner `PiP` facecam (`top-right y = 18%–38%`).
