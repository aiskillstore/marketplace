/**
 * live_hud_studio.js
 * Deterministic Multi-Platform Livestream Chrome, Popup Queue, PK Battle Bar,
 * and Bezier Heart Fountain State Machine (Douyin, Kuaishou, Instagram Live, X Live, TikTok Live).
 */

(function () {
  const PLATFORMS = {
    douyin: {
      name: "抖音直播间",
      accent: "#FE2C55",
      hostName: "阿泽 Live",
      hostSub: "本场点赞 18.6万",
      followText: "关注",
      showFollow: true,
      showTopGifters: true,
      showLivePill: false,
      storyRing: false,
      viewerText: "24.8K",
      subRankChips: ["🔥 人气榜 No.3", "小时榜", "🎁 福袋 01:28"],
      composerText: "说点什么…",
      chatRowMode: "bubble",
      badgeColor: "#3B82F6",
      badgePrefix: "钻粉 Lv.",
      joinSamples: [
        "✨ [钻粉 Lv.16] 星河舰长 来了",
        "✨ [守护] 芝士小猫 乘坐星光进场",
        "✨ [粉丝团] 夜猫子07 来了"
      ],
      giftMeta: { sender: "星河舰长", name: "璀璨星舰", icon: "🚀" },
      commerce: { badge: "讲解中", title: "1号链接 · 限量盲盒礼盒", price: "¥39.9", cta: "抢" },
      pkLeftColor: "linear-gradient(90deg, #ff1744, #fe2c55)",
      pkRightColor: "#25f4ee",
      heartColors: ["#FE2C55", "#FB7185", "#F43F5E", "#FDA4AF"],
      seedComments: [
        { user: "前排课代表", text: "前排打卡！这第一视角太稳了", lv: 14 },
        { user: "芝士小猫", text: "家人们注意看背景哈哈哈哈", lv: 9 },
        { user: "不吃香菜", text: "手掌托底对焦好真实！！", lv: 18 },
        { user: "切片组就位", text: "录屏了录屏了，名场面预定！", lv: 26 }
      ]
    },
    kuaishou: {
      name: "快手直播间",
      accent: "#FF5000",
      hostName: "老铁实测间",
      hostSub: "红心热力 9.8万",
      followText: "+ 关注",
      showFollow: true,
      showTopGifters: true,
      showLivePill: false,
      storyRing: false,
      viewerText: "3.2万老铁",
      subRankChips: ["🔥 红心热力榜", "🧧 快币红包 00:45"],
      composerText: "聊一聊…",
      chatRowMode: "bubble",
      badgeColor: "#F97316",
      badgePrefix: "铁粉 ",
      joinSamples: [
        "🔥 [铁粉] 榜一大哥 点亮了 ❤️",
        "🔥 [老铁] 东北小辣椒 点亮了 ❤️",
        "🔥 [守护] 可乐加冰 加入了直播间"
      ],
      giftMeta: { sender: "榜一大哥", name: "黄金穿云箭", icon: "🏹" },
      commerce: { badge: "小黄车秒杀", title: "源头直供 · 福利秒杀装", price: "¥19.9", cta: "去抢" },
      pkLeftColor: "linear-gradient(90deg, #ff5000, #fb923c)",
      pkRightColor: "#1890ff",
      heartColors: ["#FF5000", "#EF4444", "#FACC15", "#FB923C"],
      seedComments: [
        { user: "老铁666", text: "太实在了老铁，全屏扣666！", lv: 12, combo: 18 },
        { user: "北方汉子", text: "点亮了 ❤️❤️❤️", lv: 8 },
        { user: "测评达人", text: "小黄车1号链接还有库存吗？", lv: 15 },
        { user: "夜班保安", text: "哈哈哈哈这波绝对没剧本！", lv: 22, combo: 6 }
      ]
    },
    instagram: {
      name: "Instagram Live",
      accent: "#E1306C",
      hostName: "kaya.studio ⌄",
      hostSub: "Live Broadcast",
      followText: "",
      showFollow: false,
      showTopGifters: false,
      showLivePill: true,
      livePillBg: "linear-gradient(90deg, #E1306C, #FF0069)",
      storyRing: true,
      viewerText: "👁 14.2K",
      subRankChips: [],
      composerText: "Add a comment…",
      chatRowMode: "borderless-ig",
      badgeColor: "#E1306C",
      badgePrefix: "Badge ",
      joinSamples: [
        "👋 mina.design joined · Wave",
        "👋 pixel_kai joined · Wave",
        "👋 studio.sora joined · Wave"
      ],
      giftMeta: { sender: "mina.design", name: "Live Badges", icon: "💎" },
      commerce: { badge: "PINNED", title: "Studio Ring-Light Kit", price: "$29", cta: "View" },
      pkLeftColor: "linear-gradient(90deg, #E1306C, #FD1D1D)",
      pkRightColor: "#833AB4",
      heartColors: ["#E1306C", "#FD1D1D", "#C13584", "#FF6EA0"],
      seedComments: [
        { user: "📌 kaya.studio", text: "Welcome!! Drop your questions in the Q&A box below ✨", lv: 0 },
        { user: "lens_nerd", text: "that 18mm selfie angle feels 100% real", lv: 0 },
        { user: "momo_rblx", text: "WAIT LOOK BEHIND YOUR SHOULDER 👀", lv: 0 },
        { user: "vod_clipper", text: "no gibberish text at all, super clean!!", lv: 0 }
      ]
    },
    x: {
      name: "X / Periscope Live",
      accent: "#F91880",
      hostName: "@dev_mika",
      hostSub: "Broadcasting live",
      followText: "Follow",
      showFollow: true,
      showTopGifters: false,
      showLivePill: true,
      livePillBg: "#EF4444",
      storyRing: false,
      viewerText: "18.4K watching",
      subRankChips: ["📡 RAW CAMERA FEED · LOW LATENCY"],
      composerText: "Say something…",
      chatRowMode: "x-glass",
      badgeColor: "#35B1D1",
      badgePrefix: "",
      joinSamples: [
        "@alex_ai joined & reposted",
        "@periscope_vet tapped 12 hearts",
        "@shader_cat tuned in live"
      ],
      giftMeta: { sender: "@dev_pulse", name: "Super Heart Boost", icon: "⚡" },
      commerce: { badge: "FEATURED", title: "Open-Source Skill Repo", price: "MIT", cta: "Open" },
      pkLeftColor: "linear-gradient(90deg, #F91880, #EF4444)",
      pkRightColor: "#1D9BF0",
      // Exact 6 Periscope viewer-assigned colors
      heartColors: ["#fce473", "#f68b39", "#ed6c63", "#847bb9", "#97cd76", "#35b1d1"],
      seedComments: [
        { user: "@shader_cat", text: "2:00 AM desk stream vibes are immaculate", tint: "#fce473" },
        { user: "@frame_hunter", text: "wait are those ginger cat ears behind the chair?!", tint: "#35b1d1" },
        { user: "@zero_chill", text: "DO NOT LET THE CAT STEP ON ENTER 💀", tint: "#ed6c63" },
        { user: "@clip_archive", text: "instant classic broadcast moment", tint: "#97cd76" }
      ]
    },
    tiktok: {
      name: "TikTok Live",
      accent: "#FE2C55",
      hostName: "BloxyKai",
      hostSub: "Likes 42.1K",
      followText: "+ Follow",
      showFollow: true,
      showTopGifters: true,
      showLivePill: false,
      storyRing: false,
      viewerText: "19.6K",
      subRankChips: ["🏆 Weekly Rank #5", "🎁 Treasure 00:58"],
      composerText: "Add comment…",
      chatRowMode: "bubble",
      badgeColor: "#14B8A6",
      badgePrefix: "Gifter Lv.",
      joinSamples: [
        "🌟 [Gifter Lv.24] pixel_kai joined",
        "🌟 [Sub] obby_master joined",
        "🌟 [Top 1] neon_whale joined"
      ],
      giftMeta: { sender: "pixel_kai", name: "Galaxy Rose", icon: "🌹" },
      commerce: { badge: "PINNED", title: "Blocky Streamer Hoodie", price: "$24.00", cta: "Shop" },
      pkLeftColor: "linear-gradient(90deg, #FE2C55, #FF5E7E)",
      pkRightColor: "#25F4EE",
      heartColors: ["#FE2C55", "#25F4EE", "#FB7185", "#A855F7"],
      seedComments: [
        { user: "obby_master", text: "NO WAY ZERO DEATH STAGE 99?!", lv: 16 },
        { user: "chat_jinx", text: "watch the red killbrick right before flag 😭", lv: 9 },
        { user: "clip_that", text: "BRO HIS TOE BARELY CLIPPED IT LMAO", lv: 28 },
        { user: "stage1_club", text: "BACK TO STAGE 1 RIP KEYBOARD 💀💀", lv: 19 }
      ]
    }
  };

  const state = {
    platform: "douyin",
    scene: "studio-irl",
    chromaMode: "none",
    giftComboCount: 1,
    joinCursor: 0,
    pkVisible: false,
    pkLeftRatio: 54,
    pipVisible: false,
    afVisible: false,
    safeZoneVisible: false,
    commerceVisible: false,
    qaVisible: false
  };

  const els = {
    stage: document.getElementById("phone-stage"),
    hudChrome: document.getElementById("hud-chrome"),
    topScrim: document.getElementById("top-scrim"),
    bottomScrim: document.getElementById("bottom-scrim"),
    hostAvatar: document.getElementById("host-avatar"),
    hostName: document.getElementById("host-name"),
    hostLikes: document.getElementById("host-likes"),
    followPill: document.getElementById("follow-pill"),
    liveStatusPill: document.getElementById("live-status-pill"),
    topGifters: document.getElementById("top-gifters"),
    viewerCountPill: document.getElementById("viewer-count-pill"),
    subrankRow: document.getElementById("subrank-row"),
    joinRibbon: document.getElementById("join-ribbon"),
    chatStack: document.getElementById("chat-feed-stack"),
    composerPlaceholder: document.getElementById("composer-placeholder"),
    giftSlots: document.getElementById("gift-slots"),
    commerceCard: document.getElementById("commerce-card"),
    commerceBadge: document.getElementById("commerce-badge"),
    commerceTitle: document.getElementById("commerce-title"),
    commercePrice: document.getElementById("commerce-price"),
    commerceCta: document.getElementById("commerce-cta"),
    igQaCard: document.getElementById("ig-qa-card"),
    heartsFountain: document.getElementById("hearts-fountain"),
    pkStage: document.getElementById("pk-stage"),
    pkBarFill: document.getElementById("pk-bar-fill"),
    pkBarTrack: document.getElementById("pk-bar-track"),
    pkScoreLeft: document.getElementById("pk-score-left"),
    pkScoreRight: document.getElementById("pk-score-right"),
    pipBox: document.getElementById("pip-box"),
    afBox: document.getElementById("af-box"),
    safeZoneGuides: document.getElementById("safe-zone-guides"),
    cleanPlateBg: document.getElementById("clean-plate-bg"),
    plateCanvas: document.getElementById("live-plate-canvas"),
    pipCanvas: document.getElementById("pip-canvas"),
    videoPlate: document.getElementById("custom-video-plate"),
    telemetry: document.getElementById("telemetry-box"),
    chatInput: document.getElementById("custom-chat-input")
  };

  function updateTelemetry() {
    els.telemetry.textContent = `platform=${state.platform} | scene=${state.scene} | pk=${state.pkVisible} (${state.pkLeftRatio}%) | pip=${state.pipVisible} | combo=x${state.giftComboCount} | commerce=${state.commerceVisible}`;
  }

  function appendChatRow(item, cfg) {
    const row = document.createElement("div");
    row.className = "chat-row";
    if (cfg.chatRowMode === "borderless-ig") row.classList.add("borderless-ig");
    if (cfg.chatRowMode === "x-glass") {
      row.classList.add("x-glass");
      if (item.tint) row.style.borderLeftColor = item.tint;
    }

    if (item.lv && cfg.badgePrefix) {
      const badge = document.createElement("span");
      badge.className = "fan-badge";
      badge.style.background = cfg.badgeColor;
      badge.textContent = `${cfg.badgePrefix}${item.lv}`;
      row.appendChild(badge);
    }

    const userSpan = document.createElement("span");
    userSpan.className = "chat-user";
    if (item.tint) userSpan.style.color = item.tint;
    if (cfg.chatRowMode === "borderless-ig") userSpan.style.color = "#ffffff";
    userSpan.textContent = item.user;
    row.appendChild(userSpan);

    const textNode = document.createTextNode(item.text);
    row.appendChild(textNode);

    if (item.combo) {
      const combo = document.createElement("span");
      combo.className = "combo-pill";
      combo.textContent = `×${item.combo}`;
      row.appendChild(combo);
    }

    els.chatStack.appendChild(row);
    while (els.chatStack.children.length > 5) {
      els.chatStack.removeChild(els.chatStack.firstChild);
    }
  }

  function setPlatform(platformId) {
    state.platform = platformId;
    els.stage.dataset.platform = platformId;

    document.querySelectorAll("[data-set-platform]").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.setPlatform === platformId);
    });

    if (platformId === "clean") {
      els.hudChrome.classList.add("clean-hidden");
      els.topScrim.style.display = "none";
      els.bottomScrim.style.display = "none";
      els.giftSlots.innerHTML = "";
      els.commerceCard.classList.remove("visible");
      els.igQaCard.classList.remove("visible");
      updateTelemetry();
      return;
    }

    els.hudChrome.classList.remove("clean-hidden");
    els.topScrim.style.display = "block";
    els.bottomScrim.style.display = "block";

    const cfg = PLATFORMS[platformId] || PLATFORMS.douyin;
    document.documentElement.style.setProperty("--accent", cfg.accent);

    els.hostAvatar.textContent = cfg.hostName.replace(/^@/, "").slice(0, 1).toUpperCase();
    els.hostAvatar.classList.toggle("story-ring", Boolean(cfg.storyRing));
    els.hostName.textContent = cfg.hostName;
    els.hostLikes.textContent = cfg.hostSub;
    els.followPill.textContent = cfg.followText;
    els.followPill.style.display = cfg.showFollow ? "inline-block" : "none";

    els.liveStatusPill.style.display = cfg.showLivePill ? "inline-block" : "none";
    if (cfg.livePillBg) els.liveStatusPill.style.background = cfg.livePillBg;
    els.topGifters.style.display = cfg.showTopGifters ? "flex" : "none";
    els.viewerCountPill.textContent = cfg.viewerText;
    els.composerPlaceholder.textContent = cfg.composerText;

    els.subrankRow.innerHTML = "";
    cfg.subRankChips.forEach((txt) => {
      const chip = document.createElement("span");
      chip.className = "subrank-chip";
      chip.textContent = txt;
      els.subrankRow.appendChild(chip);
    });

    els.joinRibbon.textContent = cfg.joinSamples[0];
    els.commerceBadge.textContent = cfg.commerce.badge;
    els.commerceTitle.textContent = cfg.commerce.title;
    els.commercePrice.textContent = cfg.commerce.price;
    els.commerceCta.textContent = cfg.commerce.cta;

    els.pkBarFill.style.background = cfg.pkLeftColor;
    els.pkBarTrack.style.background = cfg.pkRightColor;

    els.chatStack.innerHTML = "";
    cfg.seedComments.forEach((c) => appendChatRow(c, cfg));
    updateTelemetry();
  }

  function triggerJoinBanner() {
    if (state.platform === "clean") return;
    const cfg = PLATFORMS[state.platform] || PLATFORMS.douyin;
    state.joinCursor = (state.joinCursor + 1) % cfg.joinSamples.length;
    els.joinRibbon.style.animation = "none";
    void els.joinRibbon.offsetWidth;
    els.joinRibbon.textContent = cfg.joinSamples[state.joinCursor];
    els.joinRibbon.style.animation = "slideGiftIn 0.24s ease";
    updateTelemetry();
  }

  function triggerGiftCombo() {
    if (state.platform === "clean") return;
    const cfg = PLATFORMS[state.platform] || PLATFORMS.douyin;
    let banner = els.giftSlots.querySelector(".gift-banner");
    if (!banner) {
      state.giftComboCount = 1;
      banner = document.createElement("div");
      banner.className = "gift-banner";
      banner.innerHTML = `
        <div class="gift-avatar">${cfg.giftMeta.icon}</div>
        <div class="gift-copy">
          <div class="gift-sender">${cfg.giftMeta.sender}</div>
          <div class="gift-title">送出 ${cfg.giftMeta.name}</div>
        </div>
        <div class="gift-combo-num">×1</div>
      `;
      els.giftSlots.appendChild(banner);
    } else {
      state.giftComboCount += state.giftComboCount < 10 ? 5 : 22;
      const numEl = banner.querySelector(".gift-combo-num");
      numEl.textContent = `×${state.giftComboCount}`;
      numEl.classList.add("pop");
      setTimeout(() => numEl.classList.remove("pop"), 150);
    }
    spawnHeartBurst(6);
    updateTelemetry();
  }

  function spawnHeartBurst(count = 8) {
    if (state.platform === "clean") return;
    const cfg = PLATFORMS[state.platform] || PLATFORMS.douyin;
    const flows = ["flowOne", "flowTwo", "flowThree"];
    for (let i = 0; i < count; i++) {
      setTimeout(() => {
        const h = document.createElement("div");
        h.className = "floating-heart";
        h.textContent = "❤";
        const color = cfg.heartColors[i % cfg.heartColors.length];
        const flow = flows[i % flows.length];
        const dur = (1.25 + (i % 4) * 0.14).toFixed(2);
        h.style.color = color;
        h.style.left = `${18 + (i % 3) * 14}px`;
        h.style.fontSize = `${20 + (i % 4) * 5}px`;
        h.style.animation = `${flow} ${dur}s linear forwards`;
        els.heartsFountain.appendChild(h);
        setTimeout(() => h.remove(), Number(dur) * 1000 + 80);
      }, i * 75);
    }
  }

  // Bind buttons
  document.querySelectorAll("[data-set-platform]").forEach((btn) => {
    btn.addEventListener("click", () => setPlatform(btn.dataset.setPlatform));
  });

  document.getElementById("btn-join").addEventListener("click", triggerJoinBanner);
  document.getElementById("btn-gift").addEventListener("click", triggerGiftCombo);
  document.getElementById("btn-hearts").addEventListener("click", () => spawnHeartBurst(10));

  document.getElementById("btn-commerce").addEventListener("click", () => {
    state.commerceVisible = !state.commerceVisible;
    els.commerceCard.classList.toggle("visible", state.commerceVisible);
    updateTelemetry();
  });

  document.getElementById("btn-qa").addEventListener("click", () => {
    state.qaVisible = !state.qaVisible;
    els.igQaCard.classList.toggle("visible", state.qaVisible);
    updateTelemetry();
  });

  document.getElementById("btn-pk").addEventListener("click", () => {
    state.pkVisible = !state.pkVisible;
    els.pkStage.classList.toggle("visible", state.pkVisible);
    document.documentElement.style.setProperty("--chat-max-height", state.pkVisible ? "152px" : "196px");
    updateTelemetry();
  });

  document.getElementById("btn-pk-flip").addEventListener("click", () => {
    if (!state.pkVisible) {
      state.pkVisible = true;
      els.pkStage.classList.add("visible");
    }
    state.pkLeftRatio = state.pkLeftRatio > 50 ? 16 : 84;
    els.pkBarFill.style.width = `${state.pkLeftRatio}%`;
    els.pkScoreLeft.textContent = state.pkLeftRatio > 50 ? "128,900" : "19,400";
    els.pkScoreRight.textContent = state.pkLeftRatio > 50 ? "24,100" : "142,800";
    spawnHeartBurst(8);
    updateTelemetry();
  });

  document.getElementById("btn-pip").addEventListener("click", () => {
    state.pipVisible = !state.pipVisible;
    els.pipBox.classList.toggle("visible", state.pipVisible);
    updateTelemetry();
  });

  document.getElementById("btn-af").addEventListener("click", () => {
    state.afVisible = !state.afVisible;
    els.afBox.classList.toggle("visible", state.afVisible);
    updateTelemetry();
  });

  document.getElementById("btn-safezone").addEventListener("click", () => {
    state.safeZoneVisible = !state.safeZoneVisible;
    els.safeZoneGuides.classList.toggle("visible", state.safeZoneVisible);
    updateTelemetry();
  });

  document.getElementById("btn-send-chat").addEventListener("click", () => {
    const val = (els.chatInput.value || "").trim();
    if (!val || state.platform === "clean") return;
    const cfg = PLATFORMS[state.platform] || PLATFORMS.douyin;
    appendChatRow({ user: state.platform === "x" ? "@you_live" : "直播间观众", text: val, lv: 20, tint: "#35b1d1" }, cfg);
    els.chatInput.value = "";
    spawnHeartBurst(3);
  });

  document.getElementById("video-file-input").addEventListener("change", (ev) => {
    const file = ev.target.files && ev.target.files[0];
    if (!file) return;
    state.chromaMode = "video";
    els.cleanPlateBg.className = "clean-plate-bg";
    els.plateCanvas.style.display = "none";
    els.videoPlate.src = URL.createObjectURL(file);
    els.videoPlate.style.display = "block";
    els.videoPlate.play();
    updateTelemetry();
  });

  function setScene(sceneId) {
    state.scene = sceneId;
    state.chromaMode = "none";
    els.cleanPlateBg.className = "clean-plate-bg";
    els.videoPlate.style.display = "none";
    els.plateCanvas.style.display = "block";
    document.querySelectorAll("[data-set-scene]").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.setScene === sceneId);
    });
    if (sceneId === "roblox-obby" && !state.pipVisible) {
      state.pipVisible = true;
      els.pipBox.classList.add("visible");
    }
    updateTelemetry();
  }

  document.querySelectorAll("[data-set-scene]").forEach((btn) => {
    btn.addEventListener("click", () => setScene(btn.dataset.setScene));
  });

  document.getElementById("btn-bg-green").addEventListener("click", () => {
    state.chromaMode = "green";
    els.cleanPlateBg.className = "clean-plate-bg chroma-green";
    els.plateCanvas.style.display = "none";
    els.videoPlate.style.display = "none";
    document.querySelectorAll("[data-set-scene]").forEach((b) => b.classList.remove("active"));
    updateTelemetry();
  });

  document.getElementById("btn-bg-checker").addEventListener("click", () => {
    state.chromaMode = "checker";
    els.cleanPlateBg.className = "clean-plate-bg chroma-checker";
    els.plateCanvas.style.display = "none";
    els.videoPlate.style.display = "none";
    document.querySelectorAll("[data-set-scene]").forEach((b) => b.classList.remove("active"));
    updateTelemetry();
  });

  // Procedural Clean-Plate Live Camera Viewport Renderer (Studio IRL / Wuxia Sword / Roblox Obby + Synced PiP)
  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, r);
    ctx.closePath();
  }

  function renderLivePlates(ts) {
    const t = (ts || 0) * 0.001;
    if (state.chromaMode === "none" && els.plateCanvas) {
      const ctx = els.plateCanvas.getContext("2d");
      const W = 390, H = 844;
      ctx.clearRect(0, 0, W, H);

      if (state.scene === "wuxia-sword") {
        const gSky = ctx.createLinearGradient(0, 0, 0, H);
        gSky.addColorStop(0, "#0284c7");
        gSky.addColorStop(0.58, "#7dd3fc");
        gSky.addColorStop(1, "#fef3c7");
        ctx.fillStyle = gSky;
        ctx.fillRect(0, 0, W, H);

        // Drifting golden-white clouds
        for (let i = 0; i < 4; i++) {
          const cx = ((i * 130 + t * (28 + i * 9)) % (W + 180)) - 90;
          const cy = 500 + i * 52;
          ctx.fillStyle = i % 2 === 0 ? "rgba(255,255,255,0.85)" : "rgba(254,243,199,0.82)";
          roundRect(ctx, cx, cy, 150, 38, 19);
          ctx.fill();
        }

        // Hovering cyan rune sword underfoot
        const bob = Math.sin(t * 2.6) * 6;
        ctx.save();
        ctx.translate(W / 2, 548 + bob);
        ctx.fillStyle = "#2dd4bf";
        ctx.shadowColor = "#2dd4bf";
        ctx.shadowBlur = 18;
        roundRect(ctx, -28, -8, 56, 140, 12);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.fillStyle = "#facc15";
        roundRect(ctx, -46, -12, 92, 16, 6);
        ctx.fill();
        ctx.restore();

        // Spirit crane gliding across upper-right
        const craneX = W + 60 - ((t * 55) % (W + 140));
        const craneY = 235 + Math.sin(t * 5) * 8;
        ctx.fillStyle = "#ffffff";
        roundRect(ctx, craneX - 24, craneY - 10, 48, 20, 10);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(craneX - 22, craneY - 18, 8, 8, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#ef4444";
        ctx.beginPath();
        ctx.arc(craneX - 22, craneY - 25, 4, 0, Math.PI * 2);
        ctx.fill();

        // Swordsman streamer in azure robes + topknot holding 18mm selfie angle
        const sy = 340 + bob;
        ctx.fillStyle = "#bae6fd";
        roundRect(ctx, W / 2 - 66, sy + 52, 132, 146, 28);
        ctx.fill();
        ctx.fillStyle = "#f8fafc";
        ctx.fillRect(W / 2 - 18, sy + 52, 36, 146);
        // Extended right arm toward selfie camera
        ctx.fillStyle = "#7dd3fc";
        roundRect(ctx, W / 2 + 48, sy + 36, 68, 34, 16);
        ctx.fill();
        // Head + hair + jade topknot
        ctx.fillStyle = "#1e293b";
        ctx.beginPath();
        ctx.arc(W / 2, sy - 6, 52, 0, Math.PI * 2);
        ctx.fill();
        roundRect(ctx, W / 2 - 16, sy - 74, 32, 22, 9);
        ctx.fill();
        ctx.fillStyle = "#38bdf8";
        roundRect(ctx, W / 2 - 20, sy - 56, 40, 7, 3);
        ctx.fill();
        ctx.fillStyle = "#fde0c4";
        ctx.beginPath();
        ctx.ellipse(W / 2, sy + 4, 44, 48, 0, 0, Math.PI * 2);
        ctx.fill();
        // Eyes + confident grin
        ctx.fillStyle = "#0f172a";
        ctx.beginPath();
        ctx.arc(W / 2 - 15, sy + 2, 5.5, 0, Math.PI * 2);
        ctx.arc(W / 2 + 15, sy + 2, 5.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.arc(W / 2 - 15, sy + 2, 2.6, 0, Math.PI * 2);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(W / 2 + 15, sy + 2, 2.6, 0, Math.PI * 2);
        ctx.stroke();
        ctx.strokeStyle = "#0f172a";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(W / 2, sy + 18, 10, 0.15, Math.PI - 0.15);
        ctx.stroke();
      } else if (state.scene === "roblox-obby") {
        const gSky = ctx.createLinearGradient(0, 0, 0, H);
        gSky.addColorStop(0, "#0e7490");
        gSky.addColorStop(1, "#bae6fd");
        ctx.fillStyle = gSky;
        ctx.fillRect(0, 0, W, H);

        // Floating SmoothPlastic Obby Pads + Glowing Red Killbrick
        ctx.fillStyle = "#f472b6";
        roundRect(ctx, 34, 540, 142, 26, 7);
        ctx.fill();
        ctx.fillStyle = "#34d399";
        roundRect(ctx, 214, 512, 146, 26, 7);
        ctx.fill();
        ctx.fillStyle = "#ff2438";
        ctx.shadowColor = "#ff2438";
        ctx.shadowBlur = 14;
        roundRect(ctx, 182, 520, 26, 18, 5);
        ctx.fill();
        ctx.shadowBlur = 0;

        // Canonical Roblox R6 Blocky Runner (2x2x1 torso + flush 1x2x1 limbs + 1:1 barrel head)
        const jumpPhase = (t * 0.75) % 1;
        const rx = 95 + Math.sin(jumpPhase * Math.PI) * 115;
        const ry = 372 - Math.sin(jumpPhase * Math.PI) * 78;
        ctx.save();
        ctx.translate(rx, ry);
        // Flush 1x2x1 Legs
        ctx.fillStyle = "#1e293b";
        roundRect(ctx, -38, 66, 37, 68, 5);
        ctx.fill();
        roundRect(ctx, 1, 66, 37, 68, 5);
        ctx.fill();
        // Solid 1x2x1 Fingerless Block Arms
        ctx.fillStyle = "#fde68a";
        roundRect(ctx, -74, -4, 34, 72, 6);
        ctx.fill();
        roundRect(ctx, 40, -16, 34, 72, 6);
        ctx.fill();
        // 2x2x1 Torso + Geometric Triangle Emblem
        ctx.fillStyle = "#0ea5e9";
        roundRect(ctx, -38, -6, 76, 72, 7);
        ctx.fill();
        ctx.fillStyle = "#f8fafc";
        ctx.beginPath();
        ctx.moveTo(0, 10);
        ctx.lineTo(16, 40);
        ctx.lineTo(-16, 40);
        ctx.closePath();
        ctx.fill();
        // 1:1 Studless Barrel Head + 2D Decal
        ctx.fillStyle = "#facc15";
        roundRect(ctx, -26, -58, 52, 50, 15);
        ctx.fill();
        ctx.fillStyle = "#0f172a";
        ctx.beginPath();
        ctx.arc(-9, -35, 3.5, 0, Math.PI * 2);
        ctx.arc(9, -35, 3.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#0f172a";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(0, -24, 8, 0.15, Math.PI - 0.15);
        ctx.stroke();
        ctx.restore();
      } else {
        // Default: Realistic 24mm Studio Streamer Rig (RGB Wall + Ring-Light Catchlights + 0°/15° Glance + Left Boom Mic)
        const gRoom = ctx.createLinearGradient(0, 0, 0, H);
        gRoom.addColorStop(0, "#0f172a");
        gRoom.addColorStop(0.6, "#1e1b4b");
        gRoom.addColorStop(1, "#090d16");
        ctx.fillStyle = gRoom;
        ctx.fillRect(0, 0, W, H);

        // RGB Wall Neon Strips
        ctx.strokeStyle = "#fe2c55";
        ctx.lineWidth = 6;
        ctx.shadowColor = "#fe2c55";
        ctx.shadowBlur = 16;
        ctx.beginPath();
        ctx.moveTo(52, 165);
        ctx.lineTo(52, 370);
        ctx.stroke();

        ctx.strokeStyle = "#25f4ee";
        ctx.shadowColor = "#25f4ee";
        ctx.beginPath();
        ctx.moveTo(338, 175);
        ctx.lineTo(338, 380);
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Studio Desk + RGB Keyboard Glow
        ctx.fillStyle = "#334155";
        roundRect(ctx, 20, 505, W - 40, 120, 14);
        ctx.fill();
        ctx.fillStyle = "rgba(56, 189, 248, 0.35)";
        roundRect(ctx, 110, 514, 170, 16, 6);
        ctx.fill();

        // Streamer Torso + White Tee + Wireless Lavalier Mic
        const breathe = Math.sin(t * 2.2) * 3.5;
        const sy = 325 + breathe;
        ctx.fillStyle = "#2563eb";
        roundRect(ctx, W / 2 - 86, sy + 64, 172, 148, 36);
        ctx.fill();
        ctx.fillStyle = "#f8fafc";
        roundRect(ctx, W / 2 - 24, sy + 64, 48, 130, 8);
        ctx.fill();
        ctx.fillStyle = "#0f172a";
        roundRect(ctx, W / 2 + 18, sy + 82, 14, 20, 4);
        ctx.fill();

        // Neck + Sculpted Hair + Over-Ear Headphones + Ellipsoid Face
        ctx.fillStyle = "#f5cba7";
        roundRect(ctx, W / 2 - 18, sy + 38, 36, 36, 12);
        ctx.fill();

        // Headphone arch
        ctx.strokeStyle = "#a855f7";
        ctx.lineWidth = 11;
        ctx.beginPath();
        ctx.arc(W / 2, sy - 2, 58, Math.PI, 0);
        ctx.stroke();
        ctx.fillStyle = "#38bdf8";
        roundRect(ctx, W / 2 - 66, sy - 14, 16, 38, 8);
        ctx.fill();
        roundRect(ctx, W / 2 + 50, sy - 14, 16, 38, 8);
        ctx.fill();

        ctx.fillStyle = "#1e293b";
        ctx.beginPath();
        ctx.arc(W / 2, sy - 12, 52, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "#fde0c4";
        ctx.beginPath();
        ctx.ellipse(W / 2, sy + 2, 46, 54, 0, 0, Math.PI * 2);
        ctx.fill();

        // Bangs
        ctx.fillStyle = "#1e293b";
        ctx.beginPath();
        ctx.ellipse(W / 2, sy - 38, 46, 20, 0, Math.PI, Math.PI * 2);
        ctx.fill();

        // 0° Direct Lens vs 15° Off-Axis Chat-Monitor Eye Glance!
        const glanceChat = (t % 5.0) > 3.6;
        const eyeShiftX = glanceChat ? 5.5 : 0;
        for (const ex of [W / 2 - 17, W / 2 + 17]) {
          ctx.fillStyle = "#0f172a";
          ctx.beginPath();
          ctx.arc(ex + eyeShiftX, sy - 2, 7.2, 0, Math.PI * 2);
          ctx.fill();
          // Circular LED Ring-Light Catchlight!
          ctx.strokeStyle = "#ffffff";
          ctx.lineWidth = 2.1;
          ctx.beginPath();
          ctx.arc(ex + eyeShiftX, sy - 2, 3.6, 0, Math.PI * 2);
          ctx.stroke();
        }
        ctx.strokeStyle = "#0f172a";
        ctx.lineWidth = 3.2;
        ctx.beginPath();
        ctx.arc(W / 2 + eyeShiftX * 0.4, sy + 20, 11, 0.15, Math.PI - 0.15);
        ctx.stroke();

        // Locked Screen-Left Condenser Boom Mic + Pop Filter
        ctx.strokeStyle = "#475569";
        ctx.lineWidth = 10;
        ctx.lineCap = "round";
        ctx.beginPath();
        ctx.moveTo(12, 525);
        ctx.lineTo(122, 428);
        ctx.stroke();
        ctx.fillStyle = "#1e293b";
        roundRect(ctx, 110, 396, 34, 52, 16);
        ctx.fill();
      }
    }

    // Render synced Corner PiP Streamer Reaction Canvas when visible
    if (state.pipVisible && els.pipCanvas) {
      const pctx = els.pipCanvas.getContext("2d");
      pctx.fillStyle = "#1e1b4b";
      pctx.fillRect(0, 0, 104, 138);
      const bob = Math.sin(t * 4) * 2;
      pctx.fillStyle = "#0ea5e9";
      roundRect(pctx, 20, 76 + bob, 64, 48, 8);
      pctx.fill();
      pctx.fillStyle = "#a855f7";
      roundRect(pctx, 24, 24 + bob, 56, 12, 6);
      pctx.fill();
      pctx.fillStyle = "#facc15";
      roundRect(pctx, 28, 30 + bob, 48, 44, 13);
      pctx.fill();
      pctx.fillStyle = "#0f172a";
      pctx.beginPath();
      pctx.arc(44, 50 + bob, 3.5, 0, Math.PI * 2);
      pctx.arc(60, 50 + bob, 3.5, 0, Math.PI * 2);
      pctx.fill();
      pctx.fillStyle = "rgba(2,6,23,0.82)";
      roundRect(pctx, 8, 116, 88, 16, 6);
      pctx.fill();
      pctx.fillStyle = "#7dd3fc";
      pctx.font = "bold 9px monospace";
      pctx.fillText("PiP · R6 CAM", 18, 127);
    }

    requestAnimationFrame(renderLivePlates);
  }

  // Initialize default Douyin state + live canvas + initial heart burst
  setPlatform("douyin");
  spawnHeartBurst(5);
  requestAnimationFrame(renderLivePlates);
})();
