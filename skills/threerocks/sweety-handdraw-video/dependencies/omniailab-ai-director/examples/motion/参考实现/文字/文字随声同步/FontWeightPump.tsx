// ---
// name: omniailab-motion-demo-font-weight-pump
// description: 字重脉冲（font-weight-pump）——标题笔画随节拍变粗又弹回，像文字跟着低音鼓蹦迪。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 字重脉冲（font-weight-pump）——标题笔画随节拍变粗又弹回，像文字跟着低音鼓蹦迪。
// 节拍每 20f 一拍：帧 30/50/70/90/110 命中。命中瞬间 -webkit-text-stroke 0→10px
// 跳满，随后 10f 幂衰减 (1-t/10)^0.8 弹回 0；fontWeight 在命中窗口 400→900 离散跳变
// （env>0.15），配合 stroke 连续衰减读作"连续变粗"。第 3、5 拍（帧 70/110）为重音，
// 额外 scaleX 1→1.08 同衰减（transform 缩放不改排版）。底部 5 个节拍点作节拍参照。
// 结构：0–29f 静止 hold；30–119f 五拍脉冲；120–139f 真静止收尾（20f，110+10=120 无残留）。
import React from 'react';
import { useCurrentFrame } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

const BEATS = [30, 50, 70, 90, 110];
const ACCENTS = new Set([2, 4]); // 第 3、5 拍重音
const DECAY = 10; // 衰减帧数

// 命中后 10f 幂衰减包络：t=0 → 1，t>=10 → 精确 0（保证结尾真静止）
const envAt = (frame: number, beat: number) => {
  const t = frame - beat;
  if (t < 0 || t >= DECAY) return 0;
  return Math.pow(1 - t / DECAY, 0.8);
};

export const FontWeightPump: React.FC = () => {
  const frame = useCurrentFrame();

  // 只可能有一个活跃拍（拍距 20f > 衰减 10f），取最大包络及其拍序号
  let env = 0;
  let activeBeat = -1;
  BEATS.forEach((b, i) => {
    const e = envAt(frame, b);
    if (e > env) {
      env = e;
      activeBeat = i;
    }
  });

  const strokeW = 10 * env; // 笔画粗细连续衰减
  const weight = env > 0.15 ? 900 : 400; // 命中窗口离散跳字重
  const accent = activeBeat >= 0 && ACCENTS.has(activeBeat);
  const scaleX = accent ? 1 + 0.08 * env : 1; // 重音拍变宽一挡

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: G.bg,
        position: 'relative',
        overflow: 'hidden',
        fontFamily: 'Helvetica, Arial, sans-serif',
      }}
    >
      {/* 定宽居中容器，transform 缩放不改排版 */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: 1920,
          height: 1080,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            fontSize: 150,
            fontWeight: weight,
            color: G.ink,
            letterSpacing: 6,
            whiteSpace: 'nowrap',
            WebkitTextStroke: `${strokeW}px ${G.ink}`,
            transform: `scaleX(${scaleX})`,
            transformOrigin: 'center center',
          }}
        >
          PUMP IT UP
        </div>
      </div>

      {/* 底部节拍点：5 个，命中哪拍哪个点闪 ink 并放大 */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          bottom: 130,
          width: 1920,
          display: 'flex',
          justifyContent: 'center',
          gap: 56,
        }}
      >
        {BEATS.map((b, i) => {
          const e = envAt(frame, b);
          const dotOpacity = e > 0.02 ? Math.min(1, 0.3 + e * 1.2) : 0;
          const dotScale = 1 + 0.8 * e;
          return (
            <div
              key={i}
              style={{
                width: 26,
                height: 26,
                borderRadius: 13,
                background: G.line,
                position: 'relative',
                transform: `scale(${dotScale})`,
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  borderRadius: 13,
                  background: G.ink,
                  opacity: dotOpacity,
                }}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

