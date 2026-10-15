// ---
// name: omniailab-motion-demo-comic-panel-split
// description: comic-panel-split｜漫画分格并列
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// comic-panel-split｜漫画分格并列
// FakeDashboard A（加 KPI 数字块）全屏 20f → 咔咔咔切成 3 个斜线分格
// （12° 斜边，10px 白缝 + 墨线描边），逐格 2f 间隔弹入（3f scale 1.06→1
// + 加深脉冲）。三格 = 同页面三机位：全景 1x / 卡片特写 1.9x / 数字区
// 特写 2.6x。定格 18f 各格缓慢微推近保持活 → 第三格斜边框 12f out-cubic
// 扩张吃掉全屏成为下一镜特写。57f 起摘罩（特写直出、分格结构与缝线
// 全部卸载），57–150f 真静止 93f ≥ 40f。帧确定，无随机源。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';
import { FakeDashboard, G } from '../../_fixtures/Fixtures';

const SPLIT = 20;              // 全屏 A 结束、开始分格
const POP = 3;                 // 每格弹入 3f
const STAGGER = 2;             // 逐格 2f 间隔
const HOLD_END = 45;           // 27f 弹完 + 定格 18f
const EXPAND_END = 57;         // 第三格 12f 扩张结束
// 57–150 真静止 93f

// 斜边 12°：tan(12°)×1080 ≈ 230，顶边比底边右移 230
// 缝 10px（水平半宽 5px）
// 边界1：顶 750 / 底 520；边界2：顶 1405 / 底 1175
const outCubic = Easing.out(Easing.cubic);

// 页面 = FakeDashboard A + 左上卡片内 KPI 数字块（给"数字区特写"一个锚点）
const PageA: React.FC = () => (
  <div style={{ width: 1920, height: 1080, position: 'relative' }}>
    <FakeDashboard variant="A" />
    <div style={{
      position: 'absolute', left: 328, top: 320, width: 380, height: 160,
      background: G.card, borderRadius: 12, display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', gap: 8,
    }}>
      <div style={{ fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800, fontSize: 96, color: G.ink, letterSpacing: -2, lineHeight: 1 }}>
        1,284
      </div>
      <div style={{ height: 10, width: 150, background: G.mid, borderRadius: 5 }} />
    </div>
  </div>
);

type PanelSpec = {
  clip: (f: number) => string; // clip-path polygon
  centroidX: number;           // 弹入缩放原点
  originX: number; originY: number; // 内容变换原点（焦点）
  baseScale: number;           // 机位倍率
  tx: number; ty: number;      // 焦点搬到格中心的位移
  z: number;
};

export const ComicPanelSplit: React.FC = () => {
  const frame = useCurrentFrame();

  // ===== 摘罩：扩张完成后特写直出，分格结构 / 缝线全部卸载 =====
  if (frame >= EXPAND_END) {
    return (
      <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
        <div style={{
          width: 1920, height: 1080,
          transform: 'translate(442px, 140px) scale(2.6)',
          transformOrigin: '518px 400px',
        }}>
          <PageA />
        </div>
      </AbsoluteFill>
    );
  }

  // ===== 阶段 1：全屏 A =====
  if (frame < SPLIT) {
    return (
      <AbsoluteFill style={{ background: G.bg }}>
        <PageA />
      </AbsoluteFill>
    );
  }

  // ===== 阶段 2/3：分格 + 第三格扩张 =====
  // 定格期微推近（27–45f 线性，很缓）
  const push = interpolate(frame, [SPLIT + 2 * STAGGER + POP, HOLD_END], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  // 第三格扩张进度（扩散用 out-cubic）
  const ex = interpolate(frame, [HOLD_END, EXPAND_END], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: outCubic,
  });

  // 第三格左斜边（= 边界2 吃屏轨迹）
  const e3Top = 1410 + ex * (-60 - 1410);    // 1410 → -60
  const e3Bot = 1180 + ex * (-290 - 1180);   // 1180 → -290

  const panels: PanelSpec[] = [
    { // 全景 1x
      clip: () => 'polygon(0px 0px, 745px 0px, 515px 1080px, 0px 1080px)',
      centroidX: 315, originX: 960, originY: 540,
      baseScale: 1 + push * 0.03, tx: 0, ty: 0, z: 1,
    },
    { // 卡片特写 1.9x（中上卡片）
      clip: () => 'polygon(755px 0px, 1400px 0px, 1170px 1080px, 525px 1080px)',
      centroidX: 962, originX: 1070, originY: 371,
      baseScale: 1.9 + push * 0.055, tx: -108, ty: 169, z: 1,
    },
    { // 数字区特写 2.6x（KPI 块），扩张时焦点从格中心搬到屏中心
      clip: () => `polygon(${e3Top}px 0px, 1920px 0px, 1920px 1080px, ${e3Bot}px 1080px)`,
      centroidX: 1607, originX: 518, originY: 400,
      // 扩张时 push 增量退掉，scale 收敛回 2.6（与摘罩帧完全一致）
      baseScale: 2.6 + push * 0.08 * (1 - ex), tx: 1089 + ex * (442 - 1089), ty: 140, z: 3,
    },
  ];

  // 缝线透明度：边界1 随第 2 格弹入出现、扩张期被吃前线性淡出；
  // 边界2 随第 3 格弹入出现、扩张末 4f 线性淡出（消散用线性）
  const seam1O = Math.min(
    interpolate(frame, [SPLIT + STAGGER, SPLIT + STAGGER + 2], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }),
    interpolate(frame, [HOLD_END, HOLD_END + 3], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }),
  );
  const seam2O = Math.min(
    interpolate(frame, [SPLIT + 2 * STAGGER, SPLIT + 2 * STAGGER + 2], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }),
    interpolate(frame, [EXPAND_END - 4, EXPAND_END], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }),
  );

  return (
    <AbsoluteFill style={{ background: '#ffffff' }}>
      {panels.map((p, i) => {
        const start = SPLIT + i * STAGGER;
        if (frame < start) return null; // 未弹入不渲染
        // 弹入：3f scale 1.06→1 + 加深脉冲
        const pop = interpolate(frame, [start, start + POP], [0, 1], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: outCubic,
        });
        const popScale = 1.06 - 0.06 * pop;
        const pulse = 0.3 * (1 - pop);
        return (
          <div key={i} style={{
            position: 'absolute', inset: 0, zIndex: p.z,
            clipPath: p.clip(frame),
            transform: `scale(${popScale})`,
            transformOrigin: `${p.centroidX}px 540px`,
          }}>
            <div style={{
              width: 1920, height: 1080,
              transform: `translate(${p.tx}px, ${p.ty}px) scale(${p.baseScale})`,
              transformOrigin: `${p.originX}px ${p.originY}px`,
            }}>
              <PageA />
            </div>
            {pulse > 0.005 && (
              <div style={{ position: 'absolute', inset: 0, background: `rgba(0,0,0,${pulse})` }} />
            )}
          </div>
        );
      })}
      {/* 斜缝：白缝命门 + 墨线描边（暗 16 下、白 10 上 → 两侧各 3px 墨边） */}
      {(seam1O > 0.005 || seam2O > 0.005) && (
        <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0, zIndex: 5, pointerEvents: 'none' }}>
          {seam1O > 0.005 && (
            <g opacity={seam1O}>
              <line x1={750} y1={-10} x2={520} y2={1090} stroke="#2f2f2f" strokeWidth={16} />
              <line x1={750} y1={-10} x2={520} y2={1090} stroke="#ffffff" strokeWidth={10} />
            </g>
          )}
          {seam2O > 0.005 && (
            <g opacity={seam2O}>
              <line x1={e3Top - 5} y1={-10} x2={e3Bot - 5} y2={1090} stroke="#2f2f2f" strokeWidth={16} />
              <line x1={e3Top - 5} y1={-10} x2={e3Bot - 5} y2={1090} stroke="#ffffff" strokeWidth={10} />
            </g>
          )}
        </svg>
      )}
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

