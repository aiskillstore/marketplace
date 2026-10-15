// ---
// name: omniailab-motion-demo-halation-bloom
// description: halation-bloom —— 高光晕染
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// halation-bloom —— 高光晕染
// 深灰底大白字 "10x" crash-zoom 急停入场（2.4→1，7f in-quad + 2f 回弹）。
// 撞停帧起：底层复制文字（blur+提亮的白色晕层）猛涨一圈（scale 1→1.3，6f out-cubic 扩散），
// 再 20f 线性回落到 0.35 驻留柔晕（扩散/消散解耦判例），随后 15f 缓收到 0.22 稳态。
// 深底白字：白底上提亮不可见判例。收尾真静止 ≥40f。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';

const BG = '#2a2a28';
const WHITE = '#f7f7f5';
const MID = '#8f8f8d';

// —— 时间轴（30fps）——
const ZOOM_START = 8; // 入场起始
const IMPACT = 15; // 撞停帧（7f 急速缩入）
const REBOUND_END = 17; // 2f 回弹
const POP_END = IMPACT + 6; // 晕层猛涨 6f → f21
const FALL_END = POP_END + 20; // 20f 线性回落 → f41
const SETTLE_END = FALL_END + 15; // 15f 缓收 → f56，此后全静止
// 总时长 145f → 静止 89f ≥ 40f

const TextBlock: React.FC<{ color: string }> = ({ color }) => (
  <div
    style={{
      fontFamily: 'Helvetica, Arial, sans-serif',
      fontSize: 260,
      fontWeight: 800,
      color,
      letterSpacing: '-0.02em',
      lineHeight: 1,
      whiteSpace: 'nowrap',
    }}
  >
    10x
  </div>
);

export const HalationBloom: React.FC = () => {
  const frame = useCurrentFrame();

  // —— crash-zoom 入场：scale 2.4 → 0.94（7f in-quad 加速撞停）→ 1（2f 回弹）——
  const zoomIn = interpolate(frame, [ZOOM_START, IMPACT], [2.4, 0.94], {
    easing: Easing.in(Easing.quad),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const rebound = interpolate(frame, [IMPACT, REBOUND_END], [0.94, 1], {
    easing: Easing.out(Easing.quad),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const textScale = frame < IMPACT ? zoomIn : rebound;
  const textOpacity = interpolate(frame, [ZOOM_START, ZOOM_START + 3], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // —— 晕层：撞停帧起条件挂载 ——
  // 扩散（scale）：out-cubic，6f 猛涨 1 → 1.3
  const bloomScale = interpolate(frame, [IMPACT, POP_END], [1, 1.3], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // 消散（opacity）：与扩散解耦——猛涨段保持全亮，随后 20f 线性回落到 0.35
  const bloomFall = interpolate(frame, [POP_END, FALL_END], [1, 0.35], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // 驻留晕 15f 缓收到 0.22 稳态
  const bloomSettle = interpolate(frame, [FALL_END, SETTLE_END], [0.35, 0.22], {
    easing: Easing.out(Easing.quad),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const bloomOpacity = frame < FALL_END ? bloomFall : bloomSettle;

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: BG,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* 小标签，全程静态 */}
      <div
        style={{
          position: 'absolute',
          top: 110,
          width: '100%',
          textAlign: 'center',
          fontFamily: 'Helvetica, Arial, sans-serif',
          fontSize: 30,
          fontWeight: 700,
          letterSpacing: '0.35em',
          color: MID,
        }}
      >
        HALATION BLOOM
      </div>

      {/* 晕层：文字复制底层，blur + 提亮，撞停帧起条件挂载 */}
      {frame >= IMPACT && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: `scale(${bloomScale})`,
            opacity: bloomOpacity,
            filter: 'blur(22px) brightness(1.8)',
          }}
        >
          <TextBlock color={WHITE} />
        </div>
      )}

      {/* 本体文字：crash-zoom 急停 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transform: `scale(${textScale})`,
          opacity: textOpacity,
        }}
      >
        <TextBlock color={WHITE} />
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

