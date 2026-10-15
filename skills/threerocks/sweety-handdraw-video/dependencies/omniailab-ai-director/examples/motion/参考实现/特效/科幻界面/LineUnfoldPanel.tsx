// ---
// name: omniailab-motion-demo-line-unfold-panel
// description: line-unfold-panel —— 一线展面（Jarvis/FUI 母题）
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// line-unfold-panel —— 一线展面（Jarvis/FUI 母题）
// 暗底。入场两拍：3px 细线从中点向两侧极快抽出（5f）→ 定宽后纵向
// 撑开成 Card 面板（9f，out 缓动）→ 内容延迟淡入。
// 静置展示后反向退场：压扁成线（7f）→ 线缩成点 → 熄灭，像老 CRT 关机。
// f0–12 空场静置；入场 f12–34；持面板至 f78；退场 f78–98；末静止 ≥42f（140f）。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, Card } from '../../_fixtures/Fixtures';

const PANEL_W = 760;
const PANEL_H = 460;
const CX = 960;
const CY = 540;

// —— 入场时间表 ——
const T0 = 12; // 点亮起点
const LINE_END = T0 + 5; // 线抽出完成 f17
const UNFOLD_END = LINE_END + 9; // 面板撑开完成 f26
const CONTENT_END = UNFOLD_END + 8; // 内容淡入完成 f34

// —— 退场时间表 ——
const OUT0 = 78; // 开始压扁
const COLLAPSE_END = OUT0 + 7; // 压成线 f85
const SHRINK_END = COLLAPSE_END + 6; // 线缩成点 f91
const OFF = SHRINK_END + 4; // 点熄灭 f95

const clamp = { extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const };

export const LineUnfoldPanel: React.FC = () => {
  const frame = useCurrentFrame();

  // 入场：scaleX（线抽出）快进快停，入场后保持 1
  const inSX = interpolate(frame, [T0, LINE_END], [0.004, 1], {
    easing: Easing.out(Easing.poly(4)),
    ...clamp,
  });
  // 入场：scaleY（纵向撑开），线阶段压在 3px
  const inSY = interpolate(frame, [LINE_END, UNFOLD_END], [3 / PANEL_H, 1], {
    easing: Easing.out(Easing.cubic),
    ...clamp,
  });
  // 内容淡入（面板撑开过半才开始）
  const contentOp = interpolate(frame, [UNFOLD_END - 3, CONTENT_END], [0, 1], {
    easing: Easing.out(Easing.quad),
    ...clamp,
  });

  // 退场：先压 Y 回线，再缩 X 回点
  const outSY = interpolate(frame, [OUT0, COLLAPSE_END], [1, 3 / PANEL_H], {
    easing: Easing.in(Easing.cubic),
    ...clamp,
  });
  const outSX = interpolate(frame, [COLLAPSE_END, SHRINK_END], [1, 0.004], {
    easing: Easing.in(Easing.poly(4)),
    ...clamp,
  });
  // 内容在压扁前先撤
  const contentOutOp = interpolate(frame, [OUT0 - 4, OUT0 + 2], [1, 0], clamp);

  const sx = frame < OUT0 ? inSX : outSX;
  const sy = frame < OUT0 ? inSY : outSY;

  // 末点熄灭：opacity 快落。f >= OFF 后整个元素条件卸载 → 真静止
  const dotOp = interpolate(frame, [SHRINK_END, OFF], [1, 0], {
    easing: Easing.in(Easing.quad),
    ...clamp,
  });

  const alive = frame >= T0 && frame < OFF;
  // 面板阶段（sy 足够大）显示卡片内容；线/点阶段显示发光条
  const isPanel = sy > 0.15;

  return (
    <div style={{ width: 1920, height: 1080, background: '#1c1c1b', overflow: 'hidden', position: 'relative' }}>
      <div
        style={{
          position: 'absolute',
          top: 120,
          width: '100%',
          textAlign: 'center',
          fontFamily: 'Helvetica, Arial, sans-serif',
          fontWeight: 800,
          fontSize: 52,
          color: G.mid,
          letterSpacing: 2,
        }}
      >
        LINE UNFOLD PANEL
      </div>
      {alive && (
        <div
          style={{
            position: 'absolute',
            left: CX - PANEL_W / 2,
            top: CY - PANEL_H / 2,
            width: PANEL_W,
            height: PANEL_H,
            transform: `scaleX(${sx}) scaleY(${sy})`,
            transformOrigin: '50% 50%',
            opacity: dotOp,
          }}
        >
          {isPanel ? (
            <>
              <Card w={PANEL_W} h={PANEL_H} seed={3} style={{ border: `2px solid ${G.mid}`, boxShadow: '0 0 40px rgba(255,255,255,0.18)' }} />
              {/* 内容层单独控 opacity：盖一层暗板模拟"内容未亮" */}
              <div
                style={{
                  position: 'absolute',
                  inset: 2,
                  borderRadius: 12,
                  background: G.card,
                  opacity: 1 - Math.min(contentOp, contentOutOp),
                }}
              />
            </>
          ) : (
            // 线/点阶段：白色发光条填满整个盒（被 scale 压成线）
            <div style={{ width: '100%', height: '100%', background: '#ffffff', boxShadow: '0 0 60px rgba(255,255,255,0.9)', borderRadius: 2 }} />
          )}
        </div>
      )}
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

