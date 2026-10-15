// ---
// name: omniailab-motion-demo-clock-wipe
// description: clock-wipe｜时钟扫描擦除
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// clock-wipe｜时钟扫描擦除
// FakeDashboard A → B。30–90f 一根隐形雷达指针从 12 点方向顺时针扫一圈，
// B 页在上层用大扇形 clip-path polygon 逐帧张开；扫描沿带亮线（白核+暗描边+柔光）。
// 90–96f 亮线淡出，96f 起摘罩（B 直接满屏、无 clip-path、亮线卸载），
// 96–150f 真静止 54f ≥ 40f。帧确定，无随机。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';
import { FakeDashboard } from '../../_fixtures/Fixtures';

const CX = 960;
const CY = 540;
const R = 1400; // 大于中心到角的距离 ~1101，扇形完全盖角
const SEGS = 72; // 顶点数固定且够密，避免锯齿跳变

// 12 点方向为 0°，顺时针（屏幕坐标 y 向下）
const polar = (deg: number, r: number): [number, number] => {
  const a = (deg * Math.PI) / 180;
  return [CX + r * Math.sin(a), CY - r * Math.cos(a)];
};

const fanClip = (theta: number): string => {
  const pts: string[] = [`${CX}px ${CY}px`];
  for (let i = 0; i <= SEGS; i++) {
    const [x, y] = polar((theta * i) / SEGS, R);
    pts.push(`${x.toFixed(1)}px ${y.toFixed(1)}px`);
  }
  return `polygon(${pts.join(', ')})`;
};

export const ClockWipe: React.FC = () => {
  const frame = useCurrentFrame();

  // 30–90f 指针 0→360°，linear（时钟扫描要匀速才像雷达）
  const theta = interpolate(frame, [30, 90], [0, 360], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const wipeDone = frame >= 90;

  // 亮线：扫描期间常亮，90–96f 线性淡出，96f 起条件卸载（摘罩判例）
  const lineOpacity = interpolate(frame, [90, 96], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const lineMounted = frame >= 30 && frame < 96;

  const [x2, y2] = polar(theta, R);

  return (
    <AbsoluteFill style={{ background: '#ececea' }}>
      {/* 底层：A 页。擦完后卸载（上层 B 已满屏） */}
      {!wipeDone && (
        <AbsoluteFill>
          <FakeDashboard variant="A" />
        </AbsoluteFill>
      )}

      {/* 上层：B 页。扫描期挂扇形 clip-path，擦完后摘罩直出 */}
      {frame >= 30 && (
        <AbsoluteFill style={wipeDone ? undefined : { clipPath: fanClip(theta) }}>
          <FakeDashboard variant="B" />
        </AbsoluteFill>
      )}

      {/* 扫描亮线：柔光 + 暗描边 + 白核，从屏心指向当前角度 */}
      {lineMounted && (
        <svg
          width={1920}
          height={1080}
          style={{ position: 'absolute', inset: 0, opacity: lineOpacity, pointerEvents: 'none' }}
        >
          {/* 柔光带（QA 后加码 1.5x：白底看不清就加深+加宽） */}
          <line x1={CX} y1={CY} x2={x2} y2={y2} stroke="rgba(255,255,255,0.35)" strokeWidth={26} strokeLinecap="round" />
          <line x1={CX} y1={CY} x2={x2} y2={y2} stroke="rgba(255,255,255,0.60)" strokeWidth={13} strokeLinecap="round" />
          {/* 暗描边：白底上"提亮"不可见，加深保证浅色区也读得出指针 */}
          <line x1={CX} y1={CY} x2={x2} y2={y2} stroke="rgba(0,0,0,0.55)" strokeWidth={9} strokeLinecap="round" />
          {/* 白核 */}
          <line x1={CX} y1={CY} x2={x2} y2={y2} stroke="rgba(255,255,255,0.95)" strokeWidth={4} strokeLinecap="round" />
        </svg>
      )}
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

