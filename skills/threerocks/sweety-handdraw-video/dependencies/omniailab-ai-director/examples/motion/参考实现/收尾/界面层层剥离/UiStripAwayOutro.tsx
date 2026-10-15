// ---
// name: omniailab-motion-demo-ui-strip-away-outro
// description: 界面层层剥离 —— framer-ai 33–36.5s
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 界面层层剥离 —— framer-ai 33–36.5s
// 满屏灰阶"编辑器"里光标点击高亮 Publish 按钮 → UI 层层错峰蒸发退场
// （每层 fade + 轻微位移，从外围到中心）→ 黑场只剩按钮 → 按钮淡出交棒字标。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig, Easing } from 'remotion';
import { G, Card } from '../../_fixtures/Fixtures';

const CLICK = 34; // 点击时刻
// 蒸发层级（点击后延迟，外围先走）
const STRIP = {
  sidebar: CLICK + 4,
  leftPanel: CLICK + 8,
  canvasCards: CLICK + 12,
  topbarEnds: CLICK + 16,
  canvasBg: CLICK + 20,
  toolbarShell: CLICK + 24,
};
const STRIP_DUR = 14;
const BTN_FADE = CLICK + 52;
const LOGO_IN = CLICK + 62;

// 某层的蒸发进度 → {opacity, offset}
const useStrip = (frame: number, start: number, dx: number, dy: number) => {
  const p = interpolate(frame, [start, start + STRIP_DUR], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.in(Easing.quad), // 离场加速
  });
  return {
    opacity: 1 - p,
    transform: `translate(${dx * p}px, ${dy * p}px)`,
  };
};

export const UiStripAwayOutro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 背景：编辑器灰底 → 黑场（随 canvasBg 层蒸发压黑）
  const bgDark = interpolate(frame, [STRIP.canvasBg, STRIP.canvasBg + STRIP_DUR + 6], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.quad),
  });

  const sidebar = useStrip(frame, STRIP.sidebar, -140, 0);
  const leftPanel = useStrip(frame, STRIP.leftPanel, -90, 20);
  const topLeft = useStrip(frame, STRIP.topbarEnds, -80, -60);
  const topRight = useStrip(frame, STRIP.topbarEnds, 80, -60);
  const toolbarShell = useStrip(frame, STRIP.toolbarShell, 0, -50);
  const canvasFrame = useStrip(frame, STRIP.canvasBg, 0, 40);

  // 画布卡片错峰蒸发
  const cardStrip = (i: number) => useStripStatic(frame, STRIP.canvasCards + i * 3, (i % 2 ? 70 : -70), 50 + i * 10);

  // 按钮：点击脉冲 + 最后淡出
  const press = spring({ frame: frame - CLICK, fps, config: { damping: 12, stiffness: 220 } });
  const pressScale = frame < CLICK ? 1 : 1 - 0.12 * Math.sin(Math.min(1, press) * Math.PI);
  const btnOp = interpolate(frame, [BTN_FADE, BTN_FADE + 12], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // 蒸发期间按钮从工具条位置滑向屏幕中心，独占黑场
  const btnCenter = interpolate(frame, [STRIP.toolbarShell, STRIP.toolbarShell + 18], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const btnX = 1560 + (960 - 88 - 1560) * btnCenter;
  const btnY = 30 + (540 - 30 - 30) * btnCenter;
  const btnScale = 1 + 0.5 * btnCenter;

  // 字标接棒
  const logoP = spring({ frame: frame - LOGO_IN, fps, config: { damping: 14, stiffness: 90 } });

  // 光标移向按钮
  const curX = interpolate(frame, [4, CLICK - 2], [820, 1636], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.quad),
  });
  const curY = interpolate(frame, [4, CLICK - 2], [640, 64], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.quad),
  });
  const curOp = interpolate(frame, [CLICK + 6, CLICK + 16], [1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ background: '#111110', overflow: 'hidden' }}>
      {/* 编辑器灰底（作为一层可蒸发的背景） */}
      <AbsoluteFill style={{ background: G.bg, opacity: 1 - bgDark }} />

      {/* 左侧栏（图层面板） */}
      <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: 240, background: G.side, padding: '90px 24px', boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 20, ...sidebar }}>
        {Array.from({ length: 9 }).map((_, i) => (
          <div key={i} style={{ height: 13, width: `${55 + ((i * 31) % 40)}%`, background: G.sideBar, borderRadius: 6 }} />
        ))}
      </div>

      {/* 右侧属性面板 */}
      <div style={{ position: 'absolute', right: 0, top: 60, bottom: 0, width: 300, background: G.panel, borderLeft: `2px solid ${G.line}`, padding: 28, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 18, ...leftPanel }}>
        {Array.from({ length: 4 }).map((_, i) => (
          <React.Fragment key={i}>
            <div style={{ height: 12, width: '45%', background: G.bar, borderRadius: 6 }} />
            <div style={{ height: 34, background: '#fff', border: `2px solid ${G.line}`, borderRadius: 8, boxSizing: 'border-box' }} />
          </React.Fragment>
        ))}
      </div>

      {/* 顶部工具条左半（logo + 工具 chips） */}
      <div style={{ position: 'absolute', left: 0, top: 0, width: 760, height: 60, background: G.panel, borderBottom: `2px solid ${G.line}`, display: 'flex', alignItems: 'center', gap: 16, padding: '0 24px', boxSizing: 'border-box', ...topLeft }}>
        <div style={{ width: 32, height: 32, borderRadius: 8, background: G.mid }} />
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} style={{ width: 30, height: 30, borderRadius: 8, background: G.line }} />
        ))}
      </div>
      {/* 顶部工具条中段（标题） */}
      <div style={{ position: 'absolute', left: 760, top: 0, right: 400, height: 60, background: G.panel, borderBottom: `2px solid ${G.line}`, display: 'flex', alignItems: 'center', justifyContent: 'center', boxSizing: 'border-box', ...toolbarShell }}>
        <div style={{ height: 14, width: 220, background: G.bar, borderRadius: 7 }} />
      </div>
      {/* 顶部工具条右段底板（Invite 假按钮；Publish 单独渲染在最上层） */}
      <div style={{ position: 'absolute', right: 0, top: 0, width: 400, height: 60, background: G.panel, borderBottom: `2px solid ${G.line}`, display: 'flex', alignItems: 'center', justifyContent: 'flex-start', gap: 14, padding: '0 24px', boxSizing: 'border-box', ...topRight }}>
        <div style={{ height: 36, width: 100, borderRadius: 18, border: `2px solid ${G.bar}`, boxSizing: 'border-box' }} />
      </div>

      {/* 画布区：一张浏览器式大卡 + 两张小卡 */}
      <div style={{ position: 'absolute', left: 320, top: 130, width: 1180, height: 850, ...canvasFrame }}>
        <div style={{ position: 'absolute', inset: 0, background: G.card, border: `2px solid ${G.border}`, borderRadius: 18, boxShadow: '0 10px 40px rgba(0,0,0,0.08)' }}>
          <div style={{ height: 46, borderBottom: `2px solid ${G.line}`, display: 'flex', alignItems: 'center', gap: 8, padding: '0 18px' }}>
            {[0, 1, 2].map((i) => (
              <div key={i} style={{ width: 14, height: 14, borderRadius: 7, background: G.line }} />
            ))}
            <div style={{ marginLeft: 16, height: 20, width: 380, background: G.bg, borderRadius: 10 }} />
          </div>
        </div>
        {[0, 1, 2, 3].map((i) => {
          const s = cardStrip(i);
          return (
            <div key={i} style={{ position: 'absolute', left: 70 + (i % 2) * 560, top: 120 + Math.floor(i / 2) * 340, ...s }}>
              <Card w={480} h={280} seed={i + 2} />
            </div>
          );
        })}
      </div>

      {/* Publish 按钮（高亮层，最后退场） */}
      <div
        style={{
          position: 'absolute',
          left: btnX,
          top: btnY,
          width: 176,
          height: 44,
          opacity: btnOp,
          transform: `scale(${pressScale})`,
          zIndex: 30,
        }}
      >
        <div
          style={{
            width: 176 * btnScale,
            height: 44 * btnScale,
            marginLeft: -((176 * btnScale - 176) / 2),
            marginTop: -((44 * btnScale - 44) / 2),
            borderRadius: 22 * btnScale,
            background: '#f2f2f0',
            boxShadow: `0 0 ${30 + 40 * btnCenter}px rgba(255,255,255,${0.25 + 0.3 * btnCenter * bgDark})`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: 'Helvetica, Arial, sans-serif',
            fontWeight: 700,
            fontSize: 20 * btnScale,
            color: '#161615',
          }}
        >
          Publish
        </div>
      </div>

      {/* 字标接棒 */}
      {frame >= LOGO_IN && (
        <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center' }}>
          <div
            style={{
              opacity: logoP,
              transform: `scale(${0.86 + 0.14 * logoP})`,
              fontFamily: 'Helvetica, Arial, sans-serif',
              fontWeight: 800,
              fontSize: 110,
              letterSpacing: 6,
              color: '#f2f2f0',
            }}
          >
            WORDMARK
          </div>
        </AbsoluteFill>
      )}

      {/* 光标 */}
      <svg width={40} height={44} viewBox="0 0 20 22" style={{ position: 'absolute', left: curX, top: curY, opacity: curOp, zIndex: 40 }}>
        <path d="M2 1 L2 17 L6.5 13.2 L9.4 20 L12.4 18.7 L9.5 12 L15 11.6 Z" fill={G.ink} stroke="#fff" strokeWidth="1.4" />
      </svg>
    </AbsoluteFill>
  );
};

// hook 规则外的静态版本（供 map 内调用）
const useStripStatic = (frame: number, start: number, dx: number, dy: number) => {
  const p = interpolate(frame, [start, start + STRIP_DUR], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.in(Easing.quad),
  });
  return {
    opacity: 1 - p,
    transform: `translate(${dx * p}px, ${dy * p}px)`,
  };
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

