// ---
// name: omniailab-motion-demo-oscilloscope-stream-v2
// description: oscilloscope-stream-v2 —— 示波流线 v2（批次 6 "改改再看" 重做）
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// oscilloscope-stream-v2 —— 示波流线 v2（批次 6 "改改再看" 重做）
// 相对 v1 的加码：流速 5.5→8px/f；写入点亮点 1.5×（7→10.5）、余辉 90→160px；
// 流动中途插入一次突发尖峰（振幅 2.2×、持续 ~20 帧写入后随流带走），尖峰经过写入点时
// 卡头实时读数跳大并变琥珀；真图表语境：真标题/真 y 轴刻度/真时间轴/实时读数。
// 刹停逻辑保留：f100–112 out-cubic 刹停，f112 后真静止 48f。
// 帧确定性：波形与尖峰包络都是纯 worldX 函数，无 Math.random / Date.now。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, TitleBlock } from '../../_fixtures/Fixtures';

const AMBER = '#b45309';

const CARD_W = 1080;
const CARD_H = 560;
const CX = (1920 - CARD_W) / 2;
const CY = (1080 - CARD_H) / 2 + 40;
const PAD = 46;
const AXIS_W = 64; // 左侧 y 轴刻度位
const PLOT_X = PAD + AXIS_W;
const PLOT_W = CARD_W - PAD * 2 - AXIS_W; // 924
const PLOT_H = 300;
const PLOT_Y = 158;

const HOLD = 12;
const FREEZE_START = 100;
const FREEZE_END = 112;
const SPEED = 8; // px/frame（v1 5.5 → 8，~240px/s）
const AMP = 0.72; // 基础振幅占半高比例（给尖峰留出头部空间）

// 突发尖峰：worldX ∈ [288, 448]（写入发生在 f48–68，之后随流向左带走）
const SPIKE_X0 = 288;
const SPIKE_W = 160;
const SPIKE_GAIN = 1.2; // 峰值 = 1 + 1.2 = 2.2×

const env = (x: number): number => {
  if (x <= SPIKE_X0 || x >= SPIKE_X0 + SPIKE_W) return 1;
  const p = (x - SPIKE_X0) / SPIKE_W;
  return 1 + SPIKE_GAIN * (0.5 - 0.5 * Math.cos(p * Math.PI * 2));
};

// 有效时间：HOLD 前为 0，之后线性流动，FREEZE 区间 easeOut 刹停为常数
const effTime = (frame: number): number => {
  const t = (f: number) => Math.max(f - HOLD, 0) * SPEED;
  if (frame <= FREEZE_START) return t(frame);
  const brakeDist = (t(FREEZE_END) - t(FREEZE_START)) * 0.45;
  return (
    t(FREEZE_START) +
    interpolate(frame, [FREEZE_START, FREEZE_END], [0, brakeDist], {
      easing: Easing.out(Easing.cubic),
      extrapolateRight: 'clamp',
    })
  );
};

// 波形：四个正弦叠加，x 单位 = 世界像素
const wave = (x: number): number =>
  0.34 * Math.sin(x * 0.021) +
  0.27 * Math.sin(x * 0.052 + 1.7) +
  0.18 * Math.sin(x * 0.013 + 4.2) +
  0.12 * Math.sin(x * 0.087 + 2.3);

const signal = (x: number): number => wave(x) * env(x) * AMP; // ∈ ~[-1.6, 1.6]，常态 [-0.65, 0.65]
const yOf = (x: number): number => PLOT_H / 2 - signal(x) * (PLOT_H / 2);
// 读数映射：绘图区中线 = 1,000 req/s，上下沿 = 2,000 / 0
const valueOf = (x: number): number => Math.round(1000 + signal(x) * 1000);

const fmt = (n: number): string => n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');

const Y_TICKS = ['2.0k', '1.5k', '1.0k', '0.5k', '0'];
const X_TICKS = ['-60s', '-50s', '-40s', '-30s', '-20s', '-10s', 'now'];

export const OscilloscopeStreamV2: React.FC = () => {
  const frame = useCurrentFrame();
  const T = effTime(frame);

  const N = 270;
  const pts: string[] = [];
  for (let i = 0; i <= N; i++) {
    const px = (i / N) * PLOT_W;
    const worldX = T - (PLOT_W - px);
    pts.push(`${px.toFixed(2)},${yOf(worldX).toFixed(2)}`);
  }
  const headY = yOf(T);

  const frozen = frame >= FREEZE_END;
  const glowOp = interpolate(frame, [FREEZE_START, FREEZE_END], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 余辉段：头部往回 160px（v1 90 → 160）
  const TAIL = 160;
  const tailPts: string[] = [];
  if (!frozen) {
    for (let i = 0; i <= 40; i++) {
      const px = PLOT_W - TAIL + (i / 40) * TAIL;
      const worldX = T - (PLOT_W - px);
      tailPts.push(`${px.toFixed(2)},${yOf(worldX).toFixed(2)}`);
    }
  }

  // 实时读数：尖峰经过写入点时跳大 + 变琥珀
  const spikeK = Math.min(Math.max((env(T) - 1) / SPIKE_GAIN, 0), 1);
  const hot = spikeK > 0.22;
  const readout = fmt(valueOf(T));
  const readScale = 1 + 0.32 * spikeK;
  const dotColor = spikeK > 0.15 ? AMBER : G.ink;

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: 110, width: '100%', textAlign: 'center' }}>
        <TitleBlock text="OSCILLOSCOPE STREAM V2" size={72} />
      </div>

      <div
        style={{
          position: 'absolute',
          left: CX,
          top: CY,
          width: CARD_W,
          height: CARD_H,
          background: G.card,
          border: `2px solid ${G.border}`,
          borderRadius: 14,
          boxSizing: 'border-box',
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
        }}
      >
        {/* 真卡头：标题 + 副题 + 实时读数 */}
        <div style={{ position: 'absolute', left: PAD, top: 38, fontFamily: 'Helvetica, Arial, sans-serif' }}>
          <div style={{ fontSize: 30, fontWeight: 700, color: G.ink }}>Requests per second</div>
          <div style={{ fontSize: 20, fontWeight: 500, color: G.mid, marginTop: 8 }}>api-gateway · production · last 60 s</div>
        </div>
        <div
          style={{
            position: 'absolute',
            right: PAD,
            top: 36,
            textAlign: 'right',
            fontFamily: 'Helvetica, Arial, sans-serif',
            transform: `scale(${readScale.toFixed(4)})`,
            transformOrigin: 'right top',
          }}
        >
          <div style={{ fontSize: 46, fontWeight: 800, color: hot ? AMBER : G.ink, fontVariantNumeric: 'tabular-nums', letterSpacing: -1 }}>
            {readout}
          </div>
          <div style={{ fontSize: 18, fontWeight: 600, color: hot ? AMBER : G.mid, marginTop: 2 }}>req/s · live</div>
        </div>

        {/* y 轴真刻度 */}
        {Y_TICKS.map((t, i) => (
          <div
            key={`yt${i}`}
            style={{
              position: 'absolute',
              left: PAD - 6,
              top: PLOT_Y + (PLOT_H / 4) * i - 11,
              width: AXIS_W - 8,
              textAlign: 'right',
              fontFamily: 'Helvetica, Arial, sans-serif',
              fontSize: 20,
              fontWeight: 600,
              color: G.mid,
            }}
          >
            {t}
          </div>
        ))}

        <div style={{ position: 'absolute', left: PLOT_X, top: PLOT_Y, width: PLOT_W, height: PLOT_H }}>
          {/* 网格 */}
          {[0, 1, 2, 3, 4].map((i) => (
            <div key={`h${i}`} style={{ position: 'absolute', left: 0, right: 0, top: (PLOT_H / 4) * i, height: 2, background: G.line, opacity: 0.7 }} />
          ))}
          {[0, 1, 2, 3, 4, 5, 6].map((i) => (
            <div key={`v${i}`} style={{ position: 'absolute', top: 0, bottom: 0, left: (PLOT_W / 6) * i, width: 2, background: G.line, opacity: 0.45 }} />
          ))}

          <svg width={PLOT_W} height={PLOT_H} style={{ position: 'absolute', inset: 0, overflow: 'visible' }}>
            <polyline points={pts.join(' ')} fill="none" stroke={G.ink} strokeWidth={5} strokeLinejoin="round" strokeLinecap="round" />
            {!frozen && glowOp > 0 && (
              <polyline
                points={tailPts.join(' ')}
                fill="none"
                stroke="#6a6a68"
                strokeWidth={9}
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity={0.55 * glowOp}
                style={{ filter: 'blur(2px)' }}
              />
            )}
            {/* 写入点亮点（1.5×） */}
            {!frozen && glowOp > 0 && (
              <>
                <circle cx={PLOT_W} cy={headY} r={24} fill={spikeK > 0.15 ? AMBER : '#8f8f8d'} opacity={0.35 * glowOp} style={{ filter: 'blur(5px)' }} />
                <circle cx={PLOT_W} cy={headY} r={10.5} fill={dotColor} opacity={glowOp} />
              </>
            )}
          </svg>
        </div>

        {/* x 轴真时间刻度 */}
        <div style={{ position: 'absolute', left: PLOT_X, top: PLOT_Y + PLOT_H + 14, width: PLOT_W }}>
          {X_TICKS.map((t, i) => (
            <div
              key={`xt${i}`}
              style={{
                position: 'absolute',
                left: (PLOT_W / 6) * i - 40,
                width: 80,
                textAlign: 'center',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontSize: 19,
                fontWeight: 600,
                color: G.mid,
              }}
            >
              {t}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

