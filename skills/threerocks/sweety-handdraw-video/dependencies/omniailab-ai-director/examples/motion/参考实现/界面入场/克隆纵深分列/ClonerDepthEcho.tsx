// ---
// name: omniailab-motion-demo-cloner-depth-echo
// description: 克隆纵深分列 —— 克隆纵队
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 克隆纵深分列 —— 克隆纵队
// 一张主卡瞬间"复印"出 7 个克隆体沿 Z 轴向后等距排开（间隔 120px、
// opacity 100%→20% 衰减、整队 8° rotateY 侧视），12f 错峰弹出；停 25f；
// 全部克隆加速吸回本体合一（10f ease-in），合体瞬间本体弹 1.08x。
// 收尾 f120 后真静止 40f。全部 frame 派生。
import React from 'react';
import { useCurrentFrame, interpolate, spring, Easing } from 'remotion';
import { G, Card, TitleBlock } from '../../_fixtures/Fixtures';

const FPS = 30;
const N = 7; // 克隆数
const GAP_Z = 120;

const SPREAD_START = 18; // 排开起始帧
const HOLD_END = 18 + 12 + 25; // f55：停留结束
const MERGE_DUR = 10; // 吸回时长

export const ClonerDepthEcho: React.FC = () => {
  const frame = useCurrentFrame();

  // 吸回进度（全体同步，ease-in 加速）
  const merge = interpolate(frame, [HOLD_END, HOLD_END + MERGE_DUR], [0, 1], {
    easing: Easing.in(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 合体瞬间本体弹一下
  const popS = spring({
    frame: frame - (HOLD_END + MERGE_DUR),
    fps: FPS,
    config: { damping: 11, stiffness: 200, mass: 0.7 },
    durationInFrames: 18,
  });
  const heroScale = frame >= HOLD_END + MERGE_DUR ? 1 + 0.08 * Math.sin(popS * Math.PI) : 1;

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, overflow: 'hidden', position: 'relative' }}>
      <div style={{ position: 'absolute', top: 100, width: '100%', textAlign: 'center' }}>
        <TitleBlock text="CLONER DEPTH ECHO" size={72} />
      </div>

      <div style={{ position: 'absolute', inset: 0, perspective: 1600, perspectiveOrigin: '58% 46%' }}>
        <div
          style={{
            position: 'absolute',
            left: 960 - 260,
            top: 540 - 170 + 40,
            transformStyle: 'preserve-3d',
            transform: 'rotateY(16deg)',
          }}
        >
          {/* 克隆队列：从后往前渲染保证遮挡正确 */}
          {Array.from({ length: N }, (_, k) => N - k).map((idx) => {
            // idx 1..N，idx 越大越靠后
            const spread = spring({
              frame: frame - SPREAD_START - (idx - 1) * 1.6,
              fps: FPS,
              config: { damping: 14, stiffness: 160, mass: 0.8 },
              durationInFrames: 16,
            });
            const p = spread * (1 - merge);
            const z = -GAP_Z * idx * p;
            // 斜向错位让纵队肉眼可见（像侧看一列纵队）
            const dx = 64 * idx * p;
            const dy = -34 * idx * p;
            const op = (1 - (idx / N) * 0.8) * spread * (1 - merge);
            if (op <= 0.005) return null;
            return (
              <div
                key={idx}
                style={{
                  position: 'absolute',
                  transform: `translate3d(${dx.toFixed(2)}px, ${dy.toFixed(2)}px, ${z.toFixed(2)}px)`,
                  opacity: op,
                }}
              >
                <Card w={520} h={340} seed={3} />
              </div>
            );
          })}
          {/* 本体 */}
          <div style={{ position: 'absolute', transform: `translateZ(0px) scale(${heroScale.toFixed(4)})` }}>
            <Card w={520} h={340} seed={3} style={{ boxShadow: '0 10px 36px rgba(31,28,23,0.22)' }} />
          </div>
        </div>
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

