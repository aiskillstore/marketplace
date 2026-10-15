// ---
// name: omniailab-motion-demo-grid-wave-flip
// description: 参考实现——参考实现/界面入场/整墙批量入场/GridWaveFlip.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { Card, G } from '../../_fixtures/Fixtures';

// grid-wave-flip〔入场退场〕：3×3 灰背卡片墙沿对角线波前依次 rotateX 翻转 180°，
// 灰背翻成正面内容卡；波浪约一秒扫完全屏，最后一张落定带轻微过冲。
// 结构：hold 20f → delay=(row+col)*6f、每张 14f bezier(0.35,0,0.25,1) → 尾张过冲回弹 → 静止收尾。

const COLS = 3;
const ROWS = 3;
const CELL_W = 520;
const CELL_H = 280;
const GAP = 36;
const HOLD = 20; // 开头建立
const STAGGER = 6; // 对角线波前步进
const FLIP = 14; // 单张翻转时长

const flipEase = Easing.bezier(0.35, 0, 0.25, 1);

// 单张卡的翻转角度：普通卡 0→180；最后一张（波前最末）过冲到 ~190 再回落 180
const angleAt = (frame: number, row: number, col: number): number => {
  const delay = HOLD + (row + col) * STAGGER;
  const isLast = row === ROWS - 1 && col === COLS - 1;
  if (!isLast) {
    return interpolate(frame, [delay, delay + FLIP], [0, 180], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: flipEase,
    });
  }
  // 过冲：14f 冲到 190°，再 8f 弹回 180°
  const main = interpolate(frame, [delay, delay + FLIP], [0, 190], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: flipEase,
  });
  const settle = interpolate(frame, [delay + FLIP, delay + FLIP + 8], [0, -10], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  return main + settle;
};

export const GridWaveFlip: React.FC = () => {
  const frame = useCurrentFrame();
  const wallW = COLS * CELL_W + (COLS - 1) * GAP;
  const wallH = ROWS * CELL_H + (ROWS - 1) * GAP;

  return (
    <AbsoluteFill
      style={{
        background: G.bg,
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      {/* 卡片墙：共享 perspective 1200px 容器，整墙一个消失点 */}
      <div
        style={{
          width: wallW,
          height: wallH,
          perspective: 1200,
          perspectiveOrigin: '50% 50%',
          display: 'grid',
          gridTemplateColumns: `repeat(${COLS}, ${CELL_W}px)`,
          gridTemplateRows: `repeat(${ROWS}, ${CELL_H}px)`,
          gap: GAP,
        }}
      >
        {Array.from({ length: ROWS * COLS }).map((_, i) => {
          const row = Math.floor(i / COLS);
          const col = i % COLS;
          const angle = angleAt(frame, row, col);
          // 高光线：翻到 90°（最薄处）时最亮，位置随角度从上缘扫向下缘
          const glow = Math.max(0, 1 - Math.abs(angle - 90) / 45);
          const glowTop = interpolate(angle, [45, 135], [8, 92], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          // 翻转中抬起阴影，落定后收回
          const lift = Math.sin(Math.min(Math.max(angle, 0), 180) * (Math.PI / 180));
          return (
            <div key={i} style={{ width: CELL_W, height: CELL_H, position: 'relative' }}>
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  transformStyle: 'preserve-3d',
                  transform: `rotateX(${angle}deg)`,
                  boxShadow: `0 ${4 + lift * 22}px ${10 + lift * 40}px rgba(0,0,0,${0.08 + lift * 0.16})`,
                  borderRadius: 14,
                }}
              >
                {/* 灰背面（初始朝外） */}
                <div
                  style={{
                    position: 'absolute',
                    inset: 0,
                    backfaceVisibility: 'hidden',
                    WebkitBackfaceVisibility: 'hidden',
                    background: '#c7c7c5',
                    border: `2px solid ${G.bar}`,
                    borderRadius: 14,
                    boxSizing: 'border-box',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                  }}
                >
                  {/* 背面只留一个哑光圆点标记，强调"灰背" */}
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: 22,
                      background: G.mid,
                      opacity: 0.55,
                    }}
                  />
                </div>
                {/* 正面内容卡（预转 180°，翻过来正好朝外） */}
                <div
                  style={{
                    position: 'absolute',
                    inset: 0,
                    backfaceVisibility: 'hidden',
                    WebkitBackfaceVisibility: 'hidden',
                    transform: 'rotateX(180deg)',
                    borderRadius: 14,
                  }}
                >
                  <Card w={CELL_W} h={CELL_H} seed={i + 1} style={{ width: '100%', height: '100%' }} />
                </div>
              </div>
              {/* 最薄处高光线：不随卡旋转，贴在格位上随角度纵向移动 */}
              {glow > 0.01 && (
                <div
                  style={{
                    position: 'absolute',
                    left: '4%',
                    width: '92%',
                    top: `${glowTop}%`,
                    height: 4,
                    borderRadius: 2,
                    background:
                      'linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.95) 50%, rgba(255,255,255,0) 100%)',
                    boxShadow: '0 0 14px rgba(255,255,255,0.8)',
                    opacity: glow,
                    pointerEvents: 'none',
                  }}
                />
              )}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

