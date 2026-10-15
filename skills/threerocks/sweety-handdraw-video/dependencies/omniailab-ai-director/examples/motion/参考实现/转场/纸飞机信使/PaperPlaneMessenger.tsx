// ---
// name: omniailab-motion-demo-paper-plane-messenger
// description: 纸飞机信使 —— pitch-app 77–82s（2.5D 简化）
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 纸飞机信使 —— pitch-app 77–82s（2.5D 简化）
// 点击"发送"后镜头拉远脱离窗口 A，折纸飞机从窗口飞出沿弧线飞行
// （俯仰角跟随切线），镜头伴飞穿过多层视差漂浮的灰阶道具，
// 飞抵窗口 B 前落定，窗口 B 放大接管全屏。发送语义实体化成转场信使。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';
import { Card, G } from '../../_fixtures/Fixtures';

const mulberry32 = (a: number) => () => {
  let t = (a += 0x6d2b79f5);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

// ---- 世界坐标 ----
const AX = 520, AY = 560;   // 窗口 A 中心
const BX = 3200, BY = 600;  // 窗口 B 中心
const WIN_W = 760, WIN_H = 500;

// 飞机三次贝塞尔弧线：A 的发送按钮 → 高抛 → B 门前
const P0 = { x: AX + 300, y: AY + 150 };
const P1 = { x: 1250, y: -80 };
const P2 = { x: 2500, y: 300 };
const P3 = { x: BX - 470, y: BY + 20 };
const bez = (t: number) => {
  const u = 1 - t;
  return {
    x: u * u * u * P0.x + 3 * u * u * t * P1.x + 3 * u * t * t * P2.x + t * t * t * P3.x,
    y: u * u * u * P0.y + 3 * u * u * t * P1.y + 3 * u * t * t * P2.y + t * t * t * P3.y,
  };
};

// ---- 时间轴（150f）----
const CLICK = 12;        // 点击发送
const ZOOM_OUT = [16, 42] as const; // 镜头拉远
const FLY = [34, 104] as const;     // 飞行
const TAKEOVER = [112, 146] as const; // 窗口 B 接管

// 视差道具（圆环/方块），depth: 0.45 远 / 0.75 中 / 1.3 近
type Prop = { x: number; y: number; size: number; ring: boolean; depth: number; drift: number };
const PROPS: Prop[] = (() => {
  const rng = mulberry32(42);
  const out: Prop[] = [];
  const depths = [0.45, 0.75, 1.3];
  for (let i = 0; i < 16; i++) {
    const depth = depths[i % 3];
    out.push({
      x: 500 + rng() * 2800,
      y: -150 + rng() * 1350,
      size: depth < 0.6 ? 60 + rng() * 70 : depth < 1 ? 110 + rng() * 100 : 220 + rng() * 160,
      ring: rng() > 0.45,
      depth,
      drift: rng() * Math.PI * 2,
    });
  }
  return out;
})();

const Window: React.FC<{ cx: number; cy: number; seed: number; sendBtn?: boolean; btnPulse?: number }> = ({ cx, cy, seed, sendBtn, btnPulse = 0 }) => (
  <div style={{ position: 'absolute', left: cx - WIN_W / 2, top: cy - WIN_H / 2, width: WIN_W, height: WIN_H, borderRadius: 18, background: '#fff', border: `2px solid ${G.border}`, boxShadow: '0 40px 100px rgba(0,0,0,0.30)', boxSizing: 'border-box', overflow: 'hidden' }}>
    <div style={{ height: 54, background: '#f2f2f0', borderBottom: `2px solid ${G.line}`, display: 'flex', alignItems: 'center', gap: 10, padding: '0 20px', boxSizing: 'border-box' }}>
      {[0, 1, 2].map((i) => <div key={i} style={{ width: 15, height: 15, borderRadius: 8, background: G.bar }} />)}
      <div style={{ marginLeft: 14, height: 13, width: 200, background: G.bar, borderRadius: 7 }} />
    </div>
    <div style={{ padding: 26, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <Card w={WIN_W - 56} h={250} seed={seed} style={{ boxShadow: 'none' }} />
      {sendBtn && (
        <div style={{ alignSelf: 'flex-end', transform: `scale(${1 + btnPulse * 0.22})`, padding: '16px 46px', borderRadius: 12, background: G.ink, color: '#fff', fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800, fontSize: 30, boxShadow: btnPulse > 0 ? `0 0 0 ${btnPulse * 22}px rgba(47,47,47,0.18)` : 'none' }}>
          Send ➤
        </div>
      )}
    </div>
  </div>
);

const Plane: React.FC<{ x: number; y: number; angle: number; scale: number; opacity: number }> = ({ x, y, angle, scale, opacity }) => (
  <svg width={180} height={110} viewBox="0 0 180 110" style={{ position: 'absolute', left: x - 90, top: y - 55, transform: `rotate(${angle}deg) scale(${scale})`, overflow: 'visible', opacity }}>
    {/* 折纸飞机：三块折面，灰阶深浅示折痕 */}
    <polygon points="176,30 6,4 62,66" fill="#ffffff" stroke="#b8b8b6" strokeWidth={3} />
    <polygon points="176,30 62,66 78,102" fill="#d4d4d2" stroke="#b8b8b6" strokeWidth={3} />
    <polygon points="176,30 6,4 50,44" fill="#efefed" stroke="#c6c6c4" strokeWidth={2} />
  </svg>
);

export const PaperPlaneMessenger: React.FC = () => {
  const frame = useCurrentFrame();

  // 飞行进度（整体 ease-in-out：起飞加速、落定减速）
  const tFly = interpolate(frame, [FLY[0], FLY[1]], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.bezier(0.45, 0.05, 0.25, 1),
  });
  const pos = bez(tFly);
  const posNext = bez(Math.min(tFly + 0.012, 1));
  const angle = Math.atan2(posNext.y - pos.y, posNext.x - pos.x) * (180 / Math.PI);

  // ---- 镜头 ----
  const zoomOutP = interpolate(frame, [ZOOM_OUT[0], ZOOM_OUT[1]], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic),
  });
  const takeP = interpolate(frame, [TAKEOVER[0], TAKEOVER[1]], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic),
  });
  // 镜头中心：A → 跟飞机 → B
  const followW = interpolate(frame, [ZOOM_OUT[0], ZOOM_OUT[1]], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  let cx = AX + (pos.x - AX) * followW;
  let cy = (AY + (pos.y - AY) * followW) * (1 - takeP) + 0; // 占位，下一行合成
  cy = AY + (Math.max(pos.y, 150) - AY) * followW;
  cx = cx * (1 - takeP) + BX * takeP;
  cy = cy * (1 - takeP) + BY * takeP;
  // 变焦：1.55（贴脸 A）→ 0.62（拉远伴飞）→ 2.6（B 接管全屏）
  const zBase = 1.55 + (0.62 - 1.55) * zoomOutP;
  const zTake = 0.62 + (3.1 - 0.62) * takeP;
  const z = frame < TAKEOVER[0] ? zBase : zTake;

  const camX = (wx: number, d: number) => 960 + (wx - cx) * z * d;
  const camY = (wy: number, d: number) => 540 + (wy - cy) * z * d;

  const btnPulse = interpolate(frame, [CLICK, CLICK + 3, CLICK + 12], [0, 1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.quad),
  });
  const planeVisible = frame >= FLY[0] - 2;
  // 飞行途中放大到 1.7 增强可读性，落定收回 1.1
  const flightBoost = interpolate(tFly, [0, 0.25, 0.75, 1], [1, 1.7, 1.7, 1.1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const planeScale = interpolate(frame, [FLY[0] - 2, FLY[0] + 8], [0.3, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.back(1.6)),
  }) * flightBoost;
  // 窗口 B 接管时飞机淡出，不留残影
  const planeOpacity = interpolate(takeP, [0, 0.35], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ background: 'linear-gradient(160deg, #e9e9e7 0%, #dcdcda 100%)', overflow: 'hidden' }}>
      {/* 视差道具：远层 / 中层（世界层之下） */}
      {PROPS.filter((p) => p.depth < 1).map((p, i) => {
        const wob = Math.sin(frame * 0.035 + p.drift) * 14;
        const x = camX(p.x, p.depth) + wob;
        const y = camY(p.y, p.depth) + Math.cos(frame * 0.03 + p.drift) * 10;
        const s = p.size * z * p.depth;
        const fade = interpolate(takeP, [0.3, 0.9], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        return (
          <div key={i} style={{
            position: 'absolute', left: x - s / 2, top: y - s / 2, width: s, height: s,
            opacity: (p.depth < 0.6 ? 0.5 : 0.75) * fade,
            borderRadius: p.ring ? '50%' : 14,
            background: p.ring ? 'transparent' : '#c9c9c7',
            border: p.ring ? `${Math.max(s * 0.13, 4)}px solid #bfbfbd` : 'none',
            filter: p.depth < 0.6 ? 'blur(3px)' : 'none',
            boxSizing: 'border-box',
          }} />
        );
      })}

      {/* 世界层（depth=1）：窗口 A / B + 飞机 */}
      <div style={{ position: 'absolute', left: 0, top: 0, transformOrigin: '0 0', transform: `translate(${960 - cx * z}px, ${540 - cy * z}px) scale(${z})` }}>
        <Window cx={AX} cy={AY} seed={3} sendBtn btnPulse={btnPulse} />
        <Window cx={BX} cy={BY} seed={6} />
        {planeVisible && planeOpacity > 0.01 && <Plane x={pos.x} y={pos.y} angle={angle} scale={planeScale} opacity={planeOpacity} />}
      </div>

      {/* 近景道具（世界层之上，焦外大件） */}
      {PROPS.filter((p) => p.depth >= 1).map((p, i) => {
        const wob = Math.sin(frame * 0.04 + p.drift) * 20;
        const x = camX(p.x, p.depth) + wob;
        const y = camY(p.y, p.depth) + Math.cos(frame * 0.033 + p.drift) * 16;
        const s = p.size * z * p.depth;
        const fade = interpolate(takeP, [0.2, 0.7], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        return (
          <div key={i} style={{
            position: 'absolute', left: x - s / 2, top: y - s / 2, width: s, height: s,
            opacity: 0.55 * fade,
            borderRadius: p.ring ? '50%' : 22,
            background: p.ring ? 'transparent' : '#b5b5b3',
            border: p.ring ? `${Math.max(s * 0.12, 6)}px solid #adadab` : 'none',
            filter: 'blur(8px)', boxSizing: 'border-box',
          }} />
        );
      })}
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

