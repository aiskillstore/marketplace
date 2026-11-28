#!/usr/bin/env node
/**
 * hud_presets.mjs
 * Zero-dependency Multi-Platform Livestream Chrome, Safe-Zone, Interactive Popup,
 * and Particle FX specification library (Douyin, Kuaishou, Instagram Live, X Live, TikTok Live, Clean).
 *
 * Grounded in REA static/protocol evidence:
 * - Douyin / TikTok Webcast message topology (RoomUserSeq, Chat, Member, Gift combo slots, Like, LinkMicBattle/Armies, Shopping)
 * - Kuaishou SCWebFeedPush topology (CommentFeed, ComboCommentFeed, LikeFeed "点亮了红心", GiftFeed mergeKey, 1080x1920 safe zones)
 * - Instagram Live borderless drop-shadow comment stack, Story-ring LIVE header, Wave join pill, and frosted Live Q&A card
 * - X / Periscope Live dark obsidian glass pills and 6-color viewer-assigned sinusoidal heart fountain (flowOne/flowTwo/flowThree)
 *
 * Trademark-clean design: uses original geometric icons, neutral typography, and color tokens—zero official platform logos.
 */

import fs from "node:fs";
import path from "node:path";

export const PLATFORM_HUD_PRESETS = {
  douyin: {
    id: "douyin",
    labelZh: "抖音直播间风格 (Douyin Live Chrome)",
    labelEn: "Douyin Live Room Chrome & Commerce/Gift HUD",
    accentPrimary: [254, 44, 85],     // #FE2C55 rose-crimson
    accentSecondary: [37, 244, 238],  // #25F4EE electric cyan
    scrimTopAlpha: 0.46,
    scrimBottomAlpha: 0.62,
    safeZone1080x1920: {
      topAvoidPx: 290,
      bottomAvoidPx: 580,
      rightAvoidPx: 148,
      chatWidthRatio: 0.68,
      chatMaxHeightRatio: 0.23
    },
    headerLayout: {
      hostCapsule: true,
      followButtonTextZh: "关注",
      followButtonTextEn: "Follow",
      subRankRowZh: ["人气榜 No.3", "小时榜", "福袋 01:28"],
      subRankRowEn: ["Top #3", "Hourly Rank", "Lucky Bag 01:28"],
      topViewersCount: 3,
      viewerPillFormat: "compact-number"
    },
    commentStyle: {
      bubbleBgRgba: [0, 0, 0, 0.36],
      borderRadiusPx: 12,
      fanBadgeBg: [59, 130, 246],
      wealthBadgeBg: [139, 92, 246],
      nameColor: [147, 197, 253],
      textColor: [255, 255, 255],
      topFadeStop: 0.22
    },
    popups: {
      joinFormatZh: (u) => `✨ [钻粉 Lv.16] ${u} 来了`,
      joinFormatEn: (u) => `✨ [Fan Lv.16] ${u} joined`,
      giftSlots: 2,
      defaultGiftZh: { sender: "星河舰长", gift: "璀璨星舰", combo: 66 },
      defaultGiftEn: { sender: "NovaPilot", gift: "Starlight Cruiser", combo: 66 },
      commerceCard: {
        badgeZh: "讲解中",
        badgeEn: "LIVE DEAL",
        titleZh: "1号链接 · 限量盲盒礼盒",
        titleEn: "Link #1 · Limited Mystery Box",
        price: "¥39.9",
        ctaZh: "抢",
        ctaEn: "Buy"
      },
      pkColors: {
        left: [254, 44, 85],
        right: [37, 244, 238]
      }
    },
    heartPalette: [
      [254, 44, 85],
      [251, 113, 133],
      [244, 63, 94],
      [253, 164, 175]
    ]
  },

  kuaishou: {
    id: "kuaishou",
    labelZh: "快手直播间风格 (Kuaishou Warm-Iron HUD)",
    labelEn: "Kuaishou Live Room HUD (Combo Danmaku & Red-Heart Feed)",
    accentPrimary: [255, 80, 0],      // #FF5000 warm orange-flame
    accentSecondary: [250, 204, 21],  // #FACC15 gold coin accent
    scrimTopAlpha: 0.44,
    scrimBottomAlpha: 0.64,
    safeZone1080x1920: {
      // Exact Kuaishou Mini-Play open spec: top 340px, center 960px, bottom 620px, safe width 880px
      topAvoidPx: 340,
      bottomAvoidPx: 620,
      rightAvoidPx: 156,
      chatWidthRatio: 0.70,
      chatMaxHeightRatio: 0.24
    },
    headerLayout: {
      hostCapsule: true,
      followButtonTextZh: "+ 关注",
      followButtonTextEn: "+ Follow",
      subRankRowZh: ["🔥 红心热力 9.8万", "快币红包 00:45"],
      subRankRowEn: ["🔥 98K Hearts", "Red Packet 00:45"],
      topViewersCount: 3,
      viewerPillFormat: "laotie-count"
    },
    commentStyle: {
      bubbleBgRgba: [12, 10, 8, 0.44],
      borderRadiusPx: 10,
      fanBadgeBg: [249, 115, 22],
      wealthBadgeBg: [234, 179, 8],
      nameColor: [253, 224, 71],
      textColor: [255, 255, 255],
      topFadeStop: 0.20,
      supportsComboComment: true,
      supportsInlineLikeFeed: true
    },
    popups: {
      joinFormatZh: (u) => `🔥 [铁粉] ${u} 点亮了 ❤️`,
      joinFormatEn: (u) => `🔥 [Top Fan] ${u} lit a ❤️`,
      giftSlots: 2,
      defaultGiftZh: { sender: "榜一大哥", gift: "黄金穿云箭", combo: 18 },
      defaultGiftEn: { sender: "IronBro_01", gift: "Golden Sky Arrow", combo: 18 },
      commerceCard: {
        badgeZh: "小黄车热卖",
        badgeEn: "FLASH DROP",
        titleZh: "源头好物 · 秒杀福利款",
        titleEn: "Factory Direct · Flash Bundle",
        price: "¥19.9",
        ctaZh: "去抢购",
        ctaEn: "Grab"
      },
      pkColors: {
        left: [255, 80, 0],
        right: [24, 144, 255]
      }
    },
    heartPalette: [
      [255, 80, 0],
      [239, 68, 68],
      [250, 204, 21],
      [251, 146, 60]
    ]
  },

  instagram: {
    id: "instagram",
    labelZh: "Instagram Live 极简悬浮风格 (Ins Live)",
    labelEn: "Instagram Live Minimal Story-Ring & Q&A HUD",
    accentPrimary: [225, 48, 108],    // #E1306C magenta-rose
    accentSecondary: [247, 119, 55],  // #F77737 sunset story ring
    scrimTopAlpha: 0.36,
    scrimBottomAlpha: 0.52,
    safeZone1080x1920: {
      topAvoidPx: 230,
      bottomAvoidPx: 520,
      rightAvoidPx: 132,
      chatWidthRatio: 0.72,
      chatMaxHeightRatio: 0.22
    },
    headerLayout: {
      hostCapsule: false,
      storyRingAvatar: true,
      liveBadgeText: "LIVE",
      eyeViewerPill: true,
      closeCrossRight: true
    },
    commentStyle: {
      // Characteristic IG Live: ZERO bubble background, pure drop-shadowed white text!
      bubbleBgRgba: [0, 0, 0, 0.0],
      dropShadow: true,
      borderRadiusPx: 0,
      fanBadgeBg: [225, 48, 108],
      nameColor: [248, 250, 252],
      textColor: [241, 245, 249],
      topFadeStop: 0.25
    },
    popups: {
      joinFormatZh: (u) => `👋 ${u} 加入了直播 · 挥手`,
      joinFormatEn: (u) => `👋 ${u} joined · Wave`,
      giftSlots: 1,
      defaultGiftZh: { sender: "kaya.studio", gift: "直播徽章打赏", combo: 3 },
      defaultGiftEn: { sender: "kaya.studio", gift: "Live Badges", combo: 3 },
      qaCard: {
        headerZh: "来自观众的提问 · Q&A",
        headerEn: "Question from @mina.design",
        questionZh: "这套直播机位是怎么做到零乱码的？",
        questionEn: "Wait is this actually happening live right now?!"
      },
      pkColors: {
        left: [225, 48, 108],
        right: [131, 58, 180]
      }
    },
    heartPalette: [
      [225, 48, 108],
      [253, 29, 29],
      [193, 53, 132],
      [255, 110, 160]
    ]
  },

  x: {
    id: "x",
    labelZh: "X / Periscope 极夜多彩飘心风格 (X Live)",
    labelEn: "X / Periscope Dark Glass & 6-Color Heart Fountain HUD",
    accentPrimary: [249, 24, 128],    // #F91880 / coral-crimson LIVE pill
    accentSecondary: [53, 177, 209],  // #35B1D1 Periscope sky-cyan
    scrimTopAlpha: 0.42,
    scrimBottomAlpha: 0.56,
    safeZone1080x1920: {
      topAvoidPx: 220,
      bottomAvoidPx: 490,
      rightAvoidPx: 140,
      chatWidthRatio: 0.68,
      chatMaxHeightRatio: 0.21
    },
    headerLayout: {
      hostCapsule: true,
      liveBadgeText: "LIVE",
      watchingSuffixEn: "watching",
      watchingSuffixZh: "正在观看"
    },
    commentStyle: {
      // Individual dark obsidian rounded cards with viewer-assigned Periscope color avatar strip
      bubbleBgRgba: [15, 20, 25, 0.78],
      borderRadiusPx: 14,
      perViewerTint: true,
      nameColor: [148, 163, 184],
      textColor: [248, 250, 252],
      topFadeStop: 0.20
    },
    popups: {
      joinFormatZh: (u) => `@${u} 加入了直播并转发`,
      joinFormatEn: (u) => `@${u} joined & reposted`,
      giftSlots: 1,
      defaultGiftZh: { sender: "@dev_pulse", gift: "Super Heart Boost", combo: 12 },
      defaultGiftEn: { sender: "@dev_pulse", gift: "Super Heart Boost", combo: 12 },
      topicPin: {
        labelEn: "LIVE BROADCAST · RAW FEED",
        labelZh: "实时直拍信号 · 零延迟互动"
      },
      pkColors: {
        left: [249, 24, 128],
        right: [29, 155, 240]
      }
    },
    // Exact 6 Periscope viewer-assigned colors from REA Evidence ev_b0cb9e3c7367d554a845d39a207cc90d190d69459e69b8182eaa12fc274c71f7
    heartPalette: [
      [252, 228, 115], // #fce473 colOne
      [246, 139, 57],  // #f68b39 colTwo
      [237, 108, 99],  // #ed6c63 colThree
      [132, 123, 185], // #847bb9 colFour
      [151, 205, 118], // #97cd76 colFive
      [53, 177, 209]   // #35b1d1 colSix
    ]
  },

  tiktok: {
    id: "tiktok",
    labelZh: "TikTok Live 国际版直播间风格",
    labelEn: "TikTok Live Global Rose-Combo & Top-Gifter HUD",
    accentPrimary: [254, 44, 85],
    accentSecondary: [37, 244, 238],
    scrimTopAlpha: 0.45,
    scrimBottomAlpha: 0.60,
    safeZone1080x1920: {
      topAvoidPx: 280,
      bottomAvoidPx: 560,
      rightAvoidPx: 144,
      chatWidthRatio: 0.68,
      chatMaxHeightRatio: 0.22
    },
    headerLayout: {
      hostCapsule: true,
      followButtonTextZh: "+ Follow",
      followButtonTextEn: "+ Follow",
      subRankRowZh: ["Weekly Rank #5", "Treasure 00:58"],
      subRankRowEn: ["Weekly Rank #5", "Treasure 00:58"],
      topViewersCount: 3,
      viewerPillFormat: "compact-number"
    },
    commentStyle: {
      bubbleBgRgba: [0, 0, 0, 0.36],
      borderRadiusPx: 12,
      fanBadgeBg: [20, 184, 166],
      wealthBadgeBg: [99, 102, 241],
      nameColor: [186, 230, 253],
      textColor: [255, 255, 255],
      topFadeStop: 0.22
    },
    popups: {
      joinFormatZh: (u) => `🌟 [Gifter Lv.24] ${u} joined`,
      joinFormatEn: (u) => `🌟 [Gifter Lv.24] ${u} joined`,
      giftSlots: 2,
      defaultGiftZh: { sender: "pixel_kai", gift: "Galaxy Rose", combo: 99 },
      defaultGiftEn: { sender: "pixel_kai", gift: "Galaxy Rose", combo: 99 },
      commerceCard: {
        badgeZh: "PINNED",
        badgeEn: "PINNED",
        titleZh: "Creator Desk Kit · #01",
        titleEn: "Creator Desk Kit · #01",
        price: "$24.00",
        ctaZh: "Shop",
        ctaEn: "Shop"
      },
      pkColors: {
        left: [254, 44, 85],
        right: [37, 244, 238]
      }
    },
    heartPalette: [
      [254, 44, 85],
      [37, 244, 238],
      [251, 113, 133],
      [168, 85, 247]
    ]
  },

  clean: {
    id: "clean",
    labelZh: "100% 纯净无框底片 (Clean Diffusion Plate)",
    labelEn: "100% Clean Raw Camera Plate (Zero HUD Overlay)",
    accentPrimary: [148, 163, 184],
    accentSecondary: [100, 116, 139],
    scrimTopAlpha: 0,
    scrimBottomAlpha: 0,
    safeZone1080x1920: {
      topAvoidPx: 0,
      bottomAvoidPx: 0,
      rightAvoidPx: 0,
      chatWidthRatio: 0,
      chatMaxHeightRatio: 0
    },
    headerLayout: { hostCapsule: false },
    commentStyle: { bubbleBgRgba: [0, 0, 0, 0] },
    popups: { giftSlots: 0 },
    heartPalette: []
  }
};

export function resolvePlatformPreset(platformId = "douyin") {
  const key = String(platformId || "douyin").toLowerCase().trim();
  if (key === "ins" || key === "ig" || key === "ig-live") return PLATFORM_HUD_PRESETS.instagram;
  if (key === "twitter" || key === "periscope" || key === "x-live") return PLATFORM_HUD_PRESETS.x;
  if (key === "ks") return PLATFORM_HUD_PRESETS.kuaishou;
  if (key === "dy") return PLATFORM_HUD_PRESETS.douyin;
  if (key === "tt") return PLATFORM_HUD_PRESETS.tiktok;
  if (key === "off" || key === "none") return PLATFORM_HUD_PRESETS.clean;
  return PLATFORM_HUD_PRESETS[key] || PLATFORM_HUD_PRESETS.douyin;
}

/**
 * Compute deterministic per-shot HUD event state for any shot index (0..N-1) and normalized phase (0..1),
 * driving scrolling danmaku, viewer counter spikes, join banners, gift combo bounces, shopping popups,
 * Q&A cards, PK tug-of-war bars, and bezier heart particles.
 */
const EPISODE_DANMAKU_PACKS = {
  irl_night_market_selfie: {
    commerceZh: "秘制十倍辣烤串",
    commerceEn: "10x Chili Skewers",
    zh: [
      [
        { user: "吃货雷达", text: "十倍变态辣？主播别逞强啊", lv: 14 },
        { user: "夜市老饕", text: "这摊红油闻着就冲鼻梁！", lv: 9 },
        { user: "前排围观", text: "立帖为证，三秒内必破防", lv: 21 }
      ],
      [
        { user: "镜头考据党", text: "手掌托底对焦绝了，辣椒籽好清", lv: 18 },
        { user: "夜猫子07", text: "看着都斯哈斯哈流口水", lv: 11 },
        { user: "不吃香菜", text: "小黄车1号同款辣酱已拍", lv: 15, combo: 6 }
      ],
      [
        { user: "全场课代表", text: "哈哈哈哈脸瞬间红温石化了！！", lv: 26, combo: 23 },
        { user: "可乐加冰", text: "自拍杆都在发抖笑死我了", lv: 16 },
        { user: "切片组就位", text: "嘴硬王者光速翻车名场面", lv: 30 }
      ],
      [
        { user: "满屏问号", text: "吨吨吨狂炫冰柠檬茶救命", lv: 19, combo: 66 },
        { user: "早八特种兵", text: "榜一快刷个火箭送去医院哈哈", lv: 12 },
        { user: "榜一随缘", text: "敬你是条汉子，星舰安排！", lv: 36 }
      ]
    ],
    en: [
      [
        { user: "spice_king", text: "10x ghost chili?? bold move", lv: 14 },
        { user: "night_bites", text: "that neon market vibe is fire", lv: 9 },
        { user: "chat_bet", text: "giving him 3 seconds max lol", lv: 21 }
      ],
      [
        { user: "lens_nerd", text: "clean palm autofocus on the spice!", lv: 18 },
        { user: "hungry_rn", text: "sizzling oil looks unreal", lv: 11 },
        { user: "clip_bot", text: "chat brace yourselves", lv: 15, combo: 6 }
      ],
      [
        { user: "vod_hunter", text: "BRO TURNED BRIGHT RED INSTANTLY", lv: 26, combo: 23 },
        { user: "iced_tea", text: "EVEN THE SELFIE ARM IS SHAKING", lv: 16 },
        { user: "zero_chill", text: "instant regret in 4K lmao", lv: 30 }
      ],
      [
        { user: "laugh_riot", text: "CHUGGING THAT LEMON TEA FOR LIFE", lv: 19, combo: 66 },
        { user: "top_gifter", text: "take a Starlight Cruiser champ", lv: 36 },
        { user: "chat_wins", text: "chat undefeated once again", lv: 12 }
      ]
    ]
  },
  desk_unboxing_autofocus: {
    commerceZh: "全金属解压机关盒",
    commerceEn: "Mystery Spring Box",
    zh: [
      [
        { user: "数码老铁", text: "终于等到这款断货王实测了！", lv: 16 },
        { user: "手工耿迷弟", text: "听说里面机关很邪乎小心点", lv: 10 },
        { user: "前排蹲链接", text: "快开快开，好用直接秒", lv: 19 }
      ],
      [
        { user: "微距控", text: "手掌托底秒锁焦，金属拉丝绝了", lv: 22 },
        { user: "买买买君", text: "小黄车库存只剩最后50件了", lv: 14, combo: 8 },
        { user: "细节狂魔", text: "这红按钮看着就想按下去！", lv: 11 }
      ],
      [
        { user: "弹幕护体", text: "卧槽！！弹簧直接怼麦上了哈哈", lv: 28, combo: 18 },
        { user: "耳机党阵亡", text: "主播吓得连人带椅往后飞", lv: 15 },
        { user: "快手课代表", text: "年度最佳带货工伤现场666", lv: 24, combo: 12 }
      ],
      [
        { user: "榜一大哥", text: "表情管理彻底下线哈哈哈哈", lv: 38, combo: 66 },
        { user: "解压协会", text: "反向测评最为致命，已下单！", lv: 17 },
        { user: "录屏小能手", text: "穿云箭走起，赔主播精神损失", lv: 29 }
      ]
    ],
    en: [
      [
        { user: "tech_bro", text: "finally testing the viral cube!", lv: 16 },
        { user: "desk_setup", text: "left boom mic framing is crisp", lv: 10 },
        { user: "unbox_fan", text: "press the red button!!", lv: 19 }
      ],
      [
        { user: "af_master", text: "AF-C palm lock is buttery smooth", lv: 22 },
        { user: "gear_head", text: "machined aluminum edges look clean", lv: 14, combo: 8 },
        { user: "deal_watch", text: "grabbed Link #1 before sellout", lv: 11 }
      ],
      [
        { user: "jump_scare", text: "YO IT LAUNCHED INTO THE MIC!!", lv: 28, combo: 18 },
        { user: "chair_gang", text: "THE CHAIR RECOIL LMAO", lv: 15 },
        { user: "clip_king", text: "100% UNSCRIPTED GOLD", lv: 24, combo: 12 }
      ],
      [
        { user: "IronBro_01", text: "sending Golden Sky Arrows lol", lv: 38, combo: 66 },
        { user: "sold_out", text: "best accidental ad ever, bought 2", lv: 17 },
        { user: "chat_roast", text: "hazard pay needed immediately", lv: 29 }
      ]
    ]
  },
  midnight_corridor_fpv_live: {
    qaZh: "404木门外面明明插着门闩，千万别进去！",
    qaEn: "Wait isn't Room 404 bolted from the outside?!",
    zh: [
      [
        { user: "深夜壮胆团", text: "第一视角呼吸声听着后背发凉", lv: 15 },
        { user: "建筑考据", text: "左手看弹幕右手照路，真一个人？", lv: 9 },
        { user: "高能预警", text: "404铜牌反光有点诡异啊", lv: 21 }
      ],
      [
        { user: "显微镜观众", text: "刚才手挥过去确实没钓鱼线！", lv: 18 },
        { user: "胆小鬼勿入", text: "头顶灯泡是不是闪了一下？？", lv: 12 },
        { user: "夜班保安", text: "快退后两步，门轴在响！", lv: 25 }
      ],
      [
        { user: "满屏护体", text: "卧槽门自己开了！！快跑啊！！", lv: 30 },
        { user: "心跳180", text: "手电筒抖成筛子了别回头！！", lv: 19 },
        { user: "实况见证", text: "真没剧本，鸡皮疙瘩起来了", lv: 27 }
      ],
      [
        { user: "百米飞人", text: "主播这转身冲刺速度破纪录了", lv: 22 },
        { user: "安全出口", text: "看到绿牌EXIT终于松一口气", lv: 14 },
        { user: "打赏压惊", text: "徽章刷一波给主播买新鞋！", lv: 32 }
      ]
    ],
    en: [
      [
        { user: "urbex_kai", text: "chest POV makes my palms sweat", lv: 15 },
        { user: "mina.design", text: "checking chat on left phone is wild", lv: 9 },
        { user: "night_watch", text: "do NOT knock on Room 404", lv: 21 }
      ],
      [
        { user: "skeptic_01", text: "okay zero wires confirmed...", lv: 18 },
        { user: "audio_head", text: "WAIT DID THE BULB JUST FLICKER", lv: 12 },
        { user: "run_now", text: "bro back away from the frame!!", lv: 25 }
      ],
      [
        { user: "panic_chat", text: "IT OPENED BY ITSELF RUNNN!!", lv: 30 },
        { user: "flashlight", text: "LOOK HOW HARD HIS HAND SHAKES", lv: 19 },
        { user: "live_proof", text: "nah I'm watching with lights on", lv: 27 }
      ],
      [
        { user: "sprint_pro", text: "fastest 180 toward EXIT in history", lv: 22 },
        { user: "kaya.studio", text: "badges sent for emotional damage", lv: 32 },
        { user: "saved_vod", text: "legendary IG Live moment", lv: 14 }
      ]
    ]
  },
  late_night_study_webcam: {
    zh: [
      [
        { user: "考研夜航船", text: "凌晨两点陪伴直播，键盘声好治愈", lv: 12 },
        { user: "全栈打工人", text: "青轴麻将音听着效率拉满", lv: 18 },
        { user: "咖啡续命", text: "改完这版PPT就能睡了吧", lv: 9 }
      ],
      [
        { user: "列文虎克", text: "等等！椅子后面冒出两只橘猫耳朵！", lv: 24 },
        { user: "云吸猫协会", text: "主播完全没发现身后有刺客哈哈", lv: 15 },
        { user: "运维老哥", text: "快锁键盘！主子准备起跳了！！", lv: 29 }
      ],
      [
        { user: "生产环境危", text: "完了！！橘猫两爪精准踩中回车！！", lv: 31 },
        { user: "代码审计", text: "未测试分支直接推线上库了？？", lv: 22 },
        { user: "眼镜反光", text: "从镜片里看到了绝望的弹窗白光", lv: 19 }
      ],
      [
        { user: "名画诞生", text: "一人一猫同步抬头盯摄像头神同步", lv: 35 },
        { user: "橘猫无罪", text: "猫猫：我帮铲屎官提前下班喵~", lv: 17 },
        { user: "热搜预定", text: "千万别删回放，太经典了哈哈", lv: 28 }
      ]
    ],
    en: [
      [
        { user: "@shader_cat", text: "2:00 AM co-working vibes are elite", lv: 12 },
        { user: "@rust_acean", text: "thocky keyboard switches sound clean", lv: 18 },
        { user: "@night_dev", text: "almost done with the release!", lv: 9 }
      ],
      [
        { user: "@eagle_eye", text: "WAIT ORANGE CAT EARS BEHIND CHAIR", lv: 24 },
        { user: "@feline_ops", text: "he has zero clue what's coming", lv: 15 },
        { user: "@sre_oncall", text: "LOCK YOUR TERMINAL RIGHT NOW", lv: 29 }
      ],
      [
        { user: "@prod_down", text: "THE CAT STEPPED DIRECTLY ON ENTER", lv: 31 },
        { user: "@git_push", text: "force-pushed straight to main 💀", lv: 22 },
        { user: "@webcam_shake", text: "even the monitor cam shook lmao", lv: 19 }
      ],
      [
        { user: "@cinema_irl", text: "synchronized cat + human 0° stare", lv: 35 },
        { user: "@dev_pulse", text: "Super Heart Boost for severance pay", lv: 28 },
        { user: "@clip_archive", text: "cat looks proud of the deploy too", lv: 17 }
      ]
    ]
  },
  wuxia_sword_flight_live: {
    commerceZh: "二阶青霜飞剑法器",
    commerceEn: "Tier-2 Azure Sword",
    zh: [
      [
        { user: "蜀山早八人", text: "御剑三环又堵？师兄走云海辅路啊", lv: 15 },
        { user: "炼器阁主", text: "这传音玉简前置画质够稳的！", lv: 21 },
        { user: "丹修摸鱼", text: "高空风这么大发带都没吹飞", lv: 10 }
      ],
      [
        { user: "剑道发烧友", text: "下摇看剑身符文太帅了！求链接", lv: 19 },
        { user: "百公里两灵石", text: "比宗门灵舟省钱多了，已拍小黄车", lv: 14, combo: 9 },
        { user: "御剑交警", text: "注意！右后方有只大仙鹤没打转向符", lv: 26 }
      ],
      [
        { user: "护体剑罡", text: "卧槽仙鹤贴脸加塞！！险些坠剑！！", lv: 30, combo: 24 },
        { user: "丹顶鹤车主", text: "仙鹤尾流把镜头晃歪12度哈哈", lv: 18 },
        { user: "修真切片组", text: "全修真界都看到师兄劈叉稳剑了", lv: 27 }
      ],
      [
        { user: "发髻歪了", text: "道冠歪成斜塔还强装淡定笑死", lv: 23, combo: 66 },
        { user: "青云掌门", text: "御剑期间禁止看弹幕扣分！", lv: 40 },
        { user: "榜一剑仙", text: "刷艘星舰赔师兄的发型管理费", lv: 34 }
      ]
    ],
    en: [
      [
        { user: "cloud_rider", text: "rush hour on the sword lane again?!", lv: 15 },
        { user: "jade_cam", text: "18mm jade-slip selfie cam goes hard", lv: 21 },
        { user: "sect_junior", text: "bro streaming at 10,000 feet", lv: 10 }
      ],
      [
        { user: "rune_smith", text: "those cyan sword runes underfoot!!", lv: 19 },
        { user: "spirit_stone", text: "2 stones per 100km? instant cop", lv: 14, combo: 9 },
        { user: "sky_radar", text: "WATCH RIGHT SHOULDER SPIRIT CRANE!!", lv: 26 }
      ],
      [
        { user: "turbulence", text: "WHITE CRANE CUT HIM OFF MID-AIR", lv: 30, combo: 24 },
        { user: "wing_gust", text: "12-degree camera roll panic lmao", lv: 18 },
        { user: "xianxia_vod", text: "road rage in the immortal realm", lv: 27 }
      ],
      [
        { user: "crooked_bun", text: "THE TILTED HAIR CROWN DEADPAN 💀", lv: 23, combo: 66 },
        { user: "sect_elder", text: "eyes on the skyway young disciple!", lv: 40 },
        { user: "NovaPilot", text: "gifting Starlight Cruiser for aura", lv: 34 }
      ]
    ]
  },
  roblox_obby_rage_pip: {
    commerceZh: "跑酷加速弹簧通行证",
    commerceEn: "Speed-Coil Gamepass",
    zh: [
      [
        { user: "跑酷见证人", text: "第99关零失误？右上角主播嘴角压不住了", lv: 16 },
        { user: "毒奶协会", text: "半场开香槟最为致命哈哈", lv: 11 },
        { user: "R6死忠粉", text: "猫耳耳机小窗同步率满分！", lv: 20 }
      ],
      [
        { user: "屏住呼吸", text: "最后一跳了！！千万别按早空格！", lv: 18 },
        { user: "细节放大镜", text: "主播脸都快贴进显示器蓝光里了", lv: 14 },
        { user: "终点旗招手", text: "稳住这把破世界纪录了！！", lv: 25 }
      ],
      [
        { user: "红砖杀手", text: "卧槽脚尖擦了0.1毫米红砖直接没了？！", lv: 32, combo: 28 },
        { user: "O_O表情包", text: "右上角小窗震惊圆圈眼截图了！！", lv: 21 },
        { user: "Oof经典咏流传", text: "差半步拿旗，血压直接拉满", lv: 27 }
      ],
      [
        { user: "喜提第一关", text: "双手刚性拍桌+瀑布宽条眼泪笑疯", lv: 29, combo: 99 },
        { user: "键盘侠心疼", text: "桌子：我承受了不该承受的痛", lv: 15 },
        { user: "pixel_kai", text: "99朵银河玫瑰安慰重开主播！", lv: 36 }
      ]
    ],
    en: [
      [
        { user: "obby_master", text: "Stage 99 zero-death flag planted 👀", lv: 16 },
        { user: "jinx_squad", text: "never flex before the green pad lol", lv: 11 },
        { user: "r6_purist", text: "smug PiP facecam smirk is crazy", lv: 20 }
      ],
      [
        { user: "spacebar_pro", text: "ONE LAST JUMP HOLD YOUR BREATH", lv: 18 },
        { user: "sweat_drop", text: "bro leaning 2 inches from monitor", lv: 14 },
        { user: "wr_pace", text: "SO CLOSE TO THE FINISH FLAG!!", lv: 25 }
      ],
      [
        { user: "killbrick_rip", text: "HIS BLOCKY TOE GRAZED RED BRICK?!", lv: 32, combo: 28 },
        { user: "clip_that", text: "LOOK AT THE O_O FACECAM REACTION", lv: 21 },
        { user: "oof_moment", text: "generational choke right on live", lv: 27 }
      ],
      [
        { user: "stage1_club", text: "BACK TO STAGE 1 WATERFALL TEARS 💀", lv: 29, combo: 99 },
        { user: "desk_check", text: "RIP desk after that double block slam", lv: 15 },
        { user: "pixel_kai", text: "99x Galaxy Rose for the rebuild", lv: 36 }
      ]
    ]
  },
  roblox_doors_irl_selfie: {
    qaZh: "壁灯闪了两下！快找木衣柜躲进去别看后面！",
    qaEn: "LIGHTS FLICKERED TWICE — HIDE IN THE CLOSET NOW!!",
    zh: [
      [
        { user: "酒店老房客", text: "050号铜牌门单排自拍？主播胆子真肥", lv: 14 },
        { user: "耳机音量警告", text: "这木地板脚步声听着心里发毛", lv: 9 },
        { user: "前排护体", text: "握紧手电筒注意听电流声！", lv: 19 }
      ],
      [
        { user: "满屏快躲", text: "灯闪了灯闪了！！别低头看弹幕快躲！", lv: 26 },
        { user: "衣柜指路党", text: "右手边就有百叶木柜快进去！！", lv: 17 },
        { user: "急死观众", text: "主播还在问为什么刷HIDE？？", lv: 22 }
      ],
      [
        { user: "左肩高能", text: "自拍屏幕里左肩膀后面亮起一对白眼！！", lv: 34 },
        { user: "瞳孔地震", text: "不用回头直接从前置镜头对视上了！", lv: 24 },
        { user: "吓飞手机", text: "18mm超广角自拍恐怖感直接翻倍", lv: 29 }
      ],
      [
        { user: "百叶窗视角", text: "躲进木柜只靠手机屏冷光照明绝了", lv: 25 },
        { user: "静音大军", text: "别刷大声特效礼物会把怪引过来哈哈", lv: 18 },
        { user: "kaya.studio", text: "瀑布泪贴图太真实了，徽章压惊", lv: 31 }
      ]
    ],
    en: [
      [
        { user: "doors_vet", text: "streaming Door 050 on selfie stick?!", lv: 14 },
        { user: "wood_creak", text: "dark hotel corridor looks so eerie", lv: 9 },
        { user: "stay_alert", text: "watch the brass sconces closely", lv: 19 }
      ],
      [
        { user: "spam_hide", text: "HIDE HIDE HIDE LIGHTS JUST FLASHED!!", lv: 26 },
        { user: "closet_now", text: "STOP READING CHAT GET IN WARDROBE", lv: 17 },
        { user: "mina.design", text: "something is coming down the hall!", lv: 22 }
      ],
      [
        { user: "behind_left", text: "GLOWING WHITE EYES OVER LEFT SHOULDER", lv: 34 },
        { user: "selfie_scare", text: "SPOTTED IT IN THE FRONT CAM PREVIEW!", lv: 24 },
        { user: "heart_rate", text: "O_O decal switch was instant", lv: 29 }
      ],
      [
        { user: "closet_gang", text: "peeking through wooden slats crying 💀", lv: 25 },
        { user: "shhh_chat", text: "nobody breathe until red glow passes", lv: 18 },
        { user: "kaya.studio", text: "3 Badges for surviving Door 050!", lv: 31 }
      ]
    ]
  },
  roblox_pet_hatch_pk: {
    commerceZh: "神宠盲盒幸运孵化蛋",
    commerceEn: "Mythic Hatch Egg",
    zh: [
      [
        { user: "氪金观察员", text: "左屏金色VIP蛋 vs 右屏新手斑点蛋哈哈", lv: 16 },
        { user: "PK吃瓜群众", text: "开局血条78%比22%，新手拿头赢？", lv: 12, combo: 6 },
        { user: "黄皮信仰", text: "别小看经典Noob的玄学微笑！", lv: 23 }
      ],
      [
        { user: "同步敲蛋", text: "两边同时亮金裂纹了！！谁出金？？", lv: 19 },
        { user: "心跳开奖", text: "小黄车同款盲盒蛋先拍一单沾喜气", lv: 14 },
        { user: "欧气检定", text: "三二一开壳见真章！！", lv: 25, combo: 12 }
      ],
      [
        { user: "全服播报", text: "卧槽0.01%青金传说神龙给新手孵出来了？！", lv: 35, combo: 38 },
        { user: "PK条极限反杀", text: "左边开出灰石头当场石化哈哈哈哈", lv: 22 },
        { user: "微笑战神", text: "Noob爆出神龙连表情都不变一下太帅了", lv: 29, combo: 18 }
      ],
      [
        { user: "当场改名", text: "左屏90度刚体扑桌自闭 vs 右屏淡定喝可乐", lv: 31, combo: 88 },
        { user: "榜一大哥", text: "穿云箭全刷给右屏欧皇老铁！！", lv: 42 },
        { user: "节目效果拉满", text: "年度最具戏剧性连麦PK没有之一", lv: 26 }
      ]
    ],
    en: [
      [
        { user: "whale_watch", text: "Golden VIP Egg vs Starter Egg PK lol", lv: 16 },
        { user: "odds_maker", text: "78% PK lead already, poor Noob", lv: 12, combo: 6 },
        { user: "noob_believer", text: "never doubt the Default Smile aura", lv: 23 }
      ],
      [
        { user: "crack_hype", text: "BOTH EGGS GLOWING AT ONCE!!", lv: 19 },
        { user: "rng_gods", text: "please let the starter egg cook", lv: 14 },
        { user: "drumroll", text: "3... 2... 1... HATCH!!", lv: 25, combo: 12 }
      ],
      [
        { user: "server_alert", text: "0.01% MYTHIC NEON DRAGON ON STARTER EGG?!", lv: 35, combo: 38 },
        { user: "pebble_rip", text: "Y2K QUEEN GOT A GRAY ROCK LMAO", lv: 22 },
        { user: "pk_comeback", text: "PK BAR INSTANTLY FLIPPED TO 84%!!", lv: 29, combo: 18 }
      ],
      [
        { user: "bloxy_toast", text: "90° desk faceplant vs calm Bloxy Cola sip", lv: 31, combo: 88 },
        { user: "IronBro_01", text: "Golden Sky Arrows for ClassicNoob!!", lv: 42 },
        { user: "gg_ez", text: "default smile stays undefeated", lv: 26 }
      ]
    ]
  }
};

export function buildShotHudTimeline(shot = {}, shotIdx = 0, totalShots = 4, platformId = "douyin", episodeSlug = "") {
  const preset = resolvePlatformPreset(platformId);
  if (preset.id === "clean") {
    return { platform: "clean", enabled: false, events: [] };
  }

  const baseViewers = shot.baseViewers || 12400 + shotIdx * 6800;
  const peakMultiplier = shotIdx === totalShots - 1 ? 2.4 : shotIdx === totalShots - 2 ? 1.85 : 1.15;
  const viewerCount = Math.round(baseViewers * peakMultiplier);

  const pack = EPISODE_DANMAKU_PACKS[episodeSlug] || EPISODE_DANMAKU_PACKS.irl_night_market_selfie;
  const cIdx = Math.min(3, shotIdx % 4);
  const commentsZh = shot.hudCommentsZh || pack.zh[cIdx];
  const commentsEn = shot.hudCommentsEn || pack.en[cIdx];

  const activePopup =
    shot.hudPopup ||
    (shotIdx === 0
      ? "join_toast"
      : shotIdx === 1
      ? preset.id === "instagram"
        ? "qa_pinned"
        : "commerce_card"
      : shotIdx === 2
      ? "gift_combo"
      : "gift_combo_peak");

  return {
    platform: preset.id,
    enabled: true,
    viewerCount,
    safeZone1080x1920: preset.safeZone1080x1920,
    activePopup,
    commentsZh,
    commentsEn,
    commerceItemZh: shot.commerceItemZh || pack.commerceZh || "1号福利链接",
    commerceItemEn: shot.commerceItemEn || pack.commerceEn || "Link #1 Deal",
    qaQuestionZh: shot.qaQuestionZh || pack.qaZh || "等等！刚才是真的自己在动吗？？",
    qaQuestionEn: shot.qaQuestionEn || pack.qaEn || "Wait did that actually move on live?!",
    giftZh: shot.hudGiftZh || preset.popups.defaultGiftZh,
    giftEn: shot.hudGiftEn || preset.popups.defaultGiftEn,
    pkScoreRatio: shot.pkScoreRatio ?? (shotIdx < 2 ? 0.52 : shotIdx === 2 ? 0.28 : 0.14),
    heartBurstIntensity: shotIdx >= 2 ? "high" : "normal"
  };
}

const isMain = process.argv[1] && path.resolve(process.argv[1]).endsWith("hud_presets.mjs");
if (isMain) {
  const argPlatform = process.argv.includes("--platform")
    ? process.argv[process.argv.indexOf("--platform") + 1]
    : "all";
  const payload =
    argPlatform === "all"
      ? PLATFORM_HUD_PRESETS
      : resolvePlatformPreset(argPlatform);
  const outIdx = process.argv.indexOf("--out");
  const text = JSON.stringify(payload, null, 2) + "\n";
  if (outIdx !== -1 && process.argv[outIdx + 1]) {
    const abs = path.resolve(process.argv[outIdx + 1]);
    fs.mkdirSync(path.dirname(abs), { recursive: true });
    fs.writeFileSync(abs, text, "utf8");
    console.log(`Wrote HUD preset spec to ${abs}`);
  } else {
    process.stdout.write(text);
  }
}
