// ---
// name: omniailab-motion-demo-input-morphs-into-logo
// description: input-morphs-into-logo —— slack-promo 40–41s
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// input-morphs-into-logo —— slack-promo 40–41s
// 消息输入框（一行文字 + 发送键）点击发送：文字飞走，输入框收缩变形成
// 圆角胶囊；上方依次落下 圆、胶囊、小圆，四粒元素集结排成抽象 logo
// 单瓣（泪滴 + 胶囊的抽象组合，非真 Slack logo），落定呼吸。
import React from 'react';
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from 'remotion';

const BG = '#3d1f47'; // 深梅紫
const CX = 960;
const CY = 560;

// 落定后的抽象单瓣布局（横向胶囊在中，上方泪滴圆、右侧胶囊、下方小圆）
// 单瓣 = 主胶囊(输入框变) + 大圆 + 竖胶囊 + 小圆 集结成花瓣角
const FINAL = {
  mainPill: { x: CX - 150, y: CY + 10, w: 300, h: 108, r: 54 }, // 横胶囊
  bigDot: { x: CX - 204, y: CY + 10, d: 108 },                  // 左端圆（与胶囊左帽相切，构成泪滴感）
  vPill: { x: CX + 96, y: CY - 152, w: 108, h: 260, r: 54 },    // 右上竖胶囊
  smallDot: { x: CX + 150, y: CY - 226, d: 76 },                // 竖胶囊顶上的小圆
};

export const InputMorphsIntoLogo: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();

  // —— 时间轴 ——
  const CLICK = 22;      // 光标按下发送
  const FLY = 26;        // 文字飞走
  const MORPH = 34;      // 输入框开始收缩变形
  const DROPS = [56, 70, 84]; // 大圆 / 竖胶囊 / 小圆 依次落下
  const SETTLE = 108;    // 全部落定，开始呼吸

  // 输入框初始几何
  const box0 = { x: CX - 430, y: CY - 60, w: 860, h: 120, r: 26 };

  // 光标移入 + 点击
  const cursorX = interpolate(f, [0, CLICK], [1500, box0.x + box0.w - 60], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic),
  });
  const cursorY = interpolate(f, [0, CLICK], [900, box0.y + 60], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic),
  });
  const press = f >= CLICK && f <= CLICK + 4 ? 0.82 : 1;
  const cursorGone = interpolate(f, [FLY + 4, FLY + 12], [1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // 发送键按下反馈
  const btnFlash = f >= CLICK && f <= CLICK + 6 ? 1 : 0;

  // 文字飞走：整行向右上飞出 + 加速
  const flyT = interpolate(f, [FLY, FLY + 12], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic),
  });

  // 输入框 → 主胶囊 morph（几何插值，带一点弹性落定）
  const m = spring({ frame: f - MORPH, fps, config: { damping: 13, stiffness: 90, mass: 0.9 } });
  const bx = interpolate(m, [0, 1], [box0.x, FINAL.mainPill.x]);
  const by = interpolate(m, [0, 1], [box0.y, FINAL.mainPill.y - FINAL.mainPill.h / 2 + 60 - 60]);
  const bw = interpolate(m, [0, 1], [box0.w, FINAL.mainPill.w]);
  const bh = interpolate(m, [0, 1], [box0.h, FINAL.mainPill.h]);
  const br = interpolate(m, [0, 1], [box0.r, FINAL.mainPill.r]);
  const bColor = m; // 边框白框 → 实心暖白

  // 三粒元素依次从画外上方落下（spring 落定，带轻微过冲）
  const dropSpring = (i: number) =>
    spring({ frame: f - DROPS[i], fps, config: { damping: 12, stiffness: 110, mass: 0.85 } });

  // 落定呼吸：整瓣轻微 scale 脉动
  const breathe = f >= SETTLE ? 1 + 0.03 * Math.sin((f - SETTLE) * 0.18) : 1;

  const dropY = (finalY: number, s: number) => interpolate(s, [0, 1], [-260, finalY]);

  const s0 = dropSpring(0);
  const s1 = dropSpring(1);
  const s2 = dropSpring(2);

  const WHITE = '#fdf6ee';

  return (
    <AbsoluteFill style={{ background: BG, fontFamily: 'Helvetica, Arial, sans-serif', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `scale(${breathe})`, transformOrigin: `${CX}px ${CY - 40}px` }}>
        {/* 主体：输入框 → 主胶囊 */}
        <div
          style={{
            position: 'absolute',
            left: bx,
            top: by,
            width: bw,
            height: bh,
            borderRadius: br,
            border: `4px solid ${WHITE}`,
            background: `rgba(253,246,238,${bColor})`,
            boxSizing: 'border-box',
            display: 'flex',
            alignItems: 'center',
            padding: '0 34px',
            boxShadow: m > 0.6 ? '0 0 60px rgba(253,246,238,0.25)' : 'none',
          }}
        >
          {/* 一行文字（发送后飞走） */}
          <div
            style={{
              fontSize: 44,
              color: WHITE,
              whiteSpace: 'nowrap',
              opacity: (1 - flyT) * (1 - m),
              transform: `translate(${flyT * 700}px, ${-flyT * 380}px) rotate(${-flyT * 10}deg)`,
            }}
          >
            Ready, set, go!
            {/* 光标闪烁 */}
            <span style={{ opacity: Math.floor(f / 8) % 2 === 0 && f < FLY ? 1 : 0 }}>|</span>
          </div>
          {/* 发送键 */}
          <div
            style={{
              marginLeft: 'auto',
              width: 72,
              height: 72,
              borderRadius: 18,
              background: btnFlash ? '#ffffff' : 'rgba(253,246,238,0.9)',
              opacity: 1 - m,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transform: `scale(${press})`,
              flexShrink: 0,
            }}
          >
            {/* 纸飞机三角 */}
            <svg width={34} height={34} viewBox="0 0 34 34">
              <path d="M3 17 L31 4 L20 30 L15 19 Z" fill={BG} />
            </svg>
          </div>
        </div>

        {/* 大圆（第一粒，落在主胶囊左端形成泪滴组合） */}
        {f >= DROPS[0] && (
          <div
            style={{
              position: 'absolute',
              left: FINAL.bigDot.x - FINAL.bigDot.d / 2,
              top: dropY(FINAL.bigDot.y - FINAL.bigDot.d / 2, s0),
              width: FINAL.bigDot.d,
              height: FINAL.bigDot.d,
              borderRadius: '50%',
              background: WHITE,
              boxShadow: '0 0 40px rgba(253,246,238,0.2)',
            }}
          />
        )}

        {/* 竖胶囊（第二粒） */}
        {f >= DROPS[1] && (
          <div
            style={{
              position: 'absolute',
              left: FINAL.vPill.x - FINAL.vPill.w / 2,
              top: dropY(FINAL.vPill.y - FINAL.vPill.h / 2, s1),
              width: FINAL.vPill.w,
              height: FINAL.vPill.h,
              borderRadius: FINAL.vPill.r,
              background: WHITE,
              boxShadow: '0 0 40px rgba(253,246,238,0.2)',
            }}
          />
        )}

        {/* 小圆（第三粒，压在竖胶囊顶端旁） */}
        {f >= DROPS[2] && (
          <div
            style={{
              position: 'absolute',
              left: FINAL.smallDot.x - FINAL.smallDot.d / 2,
              top: dropY(FINAL.smallDot.y - FINAL.smallDot.d / 2, s2),
              width: FINAL.smallDot.d,
              height: FINAL.smallDot.d,
              borderRadius: '50%',
              background: '#e8b84b',
              boxShadow: '0 0 40px rgba(232,184,75,0.35)',
            }}
          />
        )}
      </AbsoluteFill>

      {/* 光标 */}
      <div
        style={{
          position: 'absolute',
          left: cursorX,
          top: cursorY,
          opacity: cursorGone,
          transform: `scale(${press})`,
          zIndex: 50,
        }}
      >
        <svg width={40} height={44} viewBox="0 0 40 44">
          <path
            d="M4 2 L4 34 L13 26 L19 40 L26 37 L20 23 L32 22 Z"
            fill="#ffffff"
            stroke={BG}
            strokeWidth={2}
          />
        </svg>
      </div>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

