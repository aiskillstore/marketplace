// ---
// name: omniailab-motion-demo-speed-ramp-real
// description: speed-ramp 变速（轮 C）——真实卡片流帧号 remap：快(斜率2.2) →
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// speed-ramp 变速（轮 C）——真实卡片流帧号 remap：快(斜率2.2) →
// 0.2x 慢速展示窗 → 快。慢速窗中目标卡（card4-hires）清晰滑过屏中。
// blur 联动速率：快段包 blur、慢段不包，反差即"凝视感"。
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { CameraMotionBlur } from '@remotion/motion-blur';
import layout from '../../_textures/live-layout.json';

export const SPEEDRAMP_DUR = 135;

const CARD_W = 460;
const GAP = 60;
const RAIL = layout.projects.cards.slice(0, 9);
const TARGET_I = 5;

const Scene: React.FC = () => {
  const frame = useCurrentFrame();
  // remap：0–40f 走 88 源帧（快），40–85f 走 9 源帧（0.2x），85–135f 走 110（快）
  const src = interpolate(frame, [0, 40, 85, 135], [0, 88, 97, 207], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const dx = src * 28;
  return (
    <AbsoluteFill style={{ backgroundColor: '#f9f6f1', overflow: 'hidden' }}>
      {/* 偏移 717：让慢速窗中点（src≈92.4，dx≈2587）时目标卡 k=5 中心落屏中 */}
      <div style={{ position: 'absolute', top: 360, transform: `translateX(${-dx + 717}px)` }}>
        {Array.from({ length: 16 }).map((_, k) => {
          const c = RAIL[k % RAIL.length];
          const isTarget = k === TARGET_I;
          return (
            <Img
              key={k}
              src={staticFile(`textures/live/${isTarget ? 'card4-hires.png' : c.file}`)}
              style={{
                position: 'absolute', left: k * (CARD_W + GAP), top: isTarget ? -16 : 0,
                width: CARD_W, borderRadius: 12,
                boxShadow: isTarget
                  ? '0 10px 32px rgba(31,28,23,0.18)'
                  : '0 4px 16px rgba(31,28,23,0.10)',
              }}
            />
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const SpeedRampReal: React.FC = () => {
  const frame = useCurrentFrame();
  const fast = frame < 42 || frame > 83;
  return fast ? (
    <CameraMotionBlur shutterAngle={200} samples={20}>
      <Scene />
    </CameraMotionBlur>
  ) : (
    <Scene />
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

