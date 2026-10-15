// ---
// name: omniailab-motion-demo-voice-waveform-live
// description: 实时声纹胶囊 —— raycast-teams 19.5–26s：
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 实时声纹胶囊 —— raycast-teams 19.5–26s：
// 录音胶囊内实时声纹：细竖条随"说话"起伏（种子随机+相邻插值），
// 说话时中部高耸、停顿缩成点线，波形从右往左滚动；右端提交钮。
// 演：说(0.5–1.9s) → 停(1.9–2.7s) → 说(2.7–4.1s) → 提交(4.1–5s)。
import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';

const mulberry32 = (a: number) => () => {
  let t = (a += 0x6d2b79f5);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

// 值噪声：整数采样点取种子随机值，采样点之间平滑插值
const noiseAt = (x: number) => {
  const i = Math.floor(x);
  const fr = x - i;
  const a = mulberry32(i * 7919 + 13)();
  const b = mulberry32((i + 1) * 7919 + 13)();
  const s = fr * fr * (3 - 2 * fr); // smoothstep
  return a + (b - a) * s;
};

// 说话包络（按"声音发生时刻"计）：说→停→说
const envelope = (t: number) => {
  const seg = (a: number, b: number, rise = 5, fall = 7) =>
    interpolate(t, [a, a + rise, b - fall, b], [0, 1, 1, 0], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
  // 两段说话内部再叠音节起伏
  const talk = Math.max(seg(15, 57), seg(80, 124));
  const syllable = 0.55 + 0.45 * noiseAt(t / 4.5 + 200);
  return talk * syllable;
};

const N_BARS = 64;

export const VoiceWaveformLive: React.FC = () => {
  const f = useCurrentFrame();

  // 提交动作
  const submitAt = 126;
  const submitted = f >= submitAt;
  const btnPress = interpolate(f, [submitAt, submitAt + 3, submitAt + 9], [1, 0.82, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.out(Easing.ease),
  });
  // 提交后波形整体塌缩 + 胶囊微缩离场感
  const collapse = interpolate(f, [submitAt, submitAt + 12], [1, 0.06], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.in(Easing.ease),
  });
  const capsuleScale = interpolate(f, [submitAt, submitAt + 20], [1, 0.96], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.out(Easing.ease),
  });

  // 胶囊入场
  const inOp = interpolate(f, [0, 12], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.out(Easing.ease),
  });
  const inScale = interpolate(f, [0, 14], [1.04, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  const SCROLL = 1.6; // 帧→采样时间比：滚动速度

  const bars = Array.from({ length: N_BARS }).map((_, i) => {
    // 从右往左滚动：最右条是"现在"，越靠左越旧
    const sampleT = f - (N_BARS - 1 - i) * SCROLL;
    const env = sampleT < 0 ? 0 : envelope(sampleT);
    // 空间权重：中部高耸
    const center = Math.pow(Math.sin((i / (N_BARS - 1)) * Math.PI), 0.8);
    const jitter = 0.35 + 0.65 * noiseAt(sampleT * 1.7 + i * 0.13);
    const hRaw = env * center * jitter;
    const h = Math.max(5, hRaw * 235 * collapse); // 静默=5px 点线
    return h;
  });

  const nowEnv = envelope(f);
  const micGlow = submitted ? 0 : nowEnv;

  return (
    <AbsoluteFill style={{ background: '#08080a', overflow: 'hidden' }}>
      {/* 暗场绸缎底光 */}
      <div style={{
        position: 'absolute', left: -300, top: -200, width: 2600, height: 1700,
        background: 'radial-gradient(closest-side, rgba(130,131,140,0.16), rgba(0,0,0,0) 70%)',
        transform: `translate(${f * 0.6}px, ${f * 0.25}px)`,
      }} />

      <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div
          style={{
            width: 1320, height: 300, borderRadius: 150,
            opacity: inOp,
            transform: `scale(${inScale * capsuleScale})`,
            background:
              'linear-gradient(180deg, rgba(255,255,255,0.5), rgba(255,255,255,0.08) 40%, rgba(0,0,0,0.3))',
            padding: 2.5, boxSizing: 'border-box',
          }}
        >
          <div
            style={{
              width: '100%', height: '100%', borderRadius: 148,
              background: 'rgba(24,25,29,0.72)',
              backdropFilter: 'blur(24px)',
              boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.10), 0 40px 100px rgba(0,0,0,0.55)',
              display: 'flex', alignItems: 'center', gap: 36,
              padding: '0 44px', boxSizing: 'border-box',
            }}
          >
            {/* 麦克风圆钮：说话时发亮 */}
            <div
              style={{
                width: 96, height: 96, borderRadius: 48, flexShrink: 0,
                background: `rgba(255,255,255,${0.08 + micGlow * 0.14})`,
                border: '2.5px solid rgba(255,255,255,0.28)',
                boxShadow: `0 0 ${28 * micGlow}px rgba(235,235,245,${micGlow * 0.5})`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 46, filter: 'grayscale(1)', boxSizing: 'border-box',
              }}
            >
              🎙️
            </div>

            {/* 声纹条区 */}
            <div style={{
              flex: 1, height: 244, display: 'flex', alignItems: 'center',
              gap: 6, overflow: 'hidden',
            }}>
              {bars.map((h, i) => (
                <div
                  key={i}
                  style={{
                    flex: 1, height: h, borderRadius: 4,
                    background: `rgba(240,240,248,${0.4 + (h / 235) * 0.6})`,
                  }}
                />
              ))}
            </div>

            {/* 提交钮：白圆 + 上箭头 */}
            <div
              style={{
                width: 96, height: 96, borderRadius: 48, flexShrink: 0,
                background: submitted ? '#ffffff' : 'rgba(255,255,255,0.92)',
                transform: `scale(${btnPress})`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: submitted
                  ? '0 0 60px rgba(255,255,255,0.55)'
                  : '0 8px 24px rgba(0,0,0,0.4)',
              }}
            >
              <svg width="44" height="44" viewBox="0 0 24 24">
                <path
                  d="M12 20V5M12 5l-6.5 6.5M12 5l6.5 6.5"
                  stroke="#111114" strokeWidth="3" strokeLinecap="round"
                  strokeLinejoin="round" fill="none"
                />
              </svg>
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

