// ---
// name: omniailab-motion-demo-whip-brake-real
// description: E 式急刹款 whip-brake——真实卡片切片横向长廊，甩过 9 张卡后
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// E 式急刹款 whip-brake——真实卡片切片横向长廊，甩过 9 张卡后
// 在目标卡（card4-hires，高清纹理）前急刹长尾滑入。
// 速率：前 70% 路程用 12f（糊），后 30% 路程 ease-out 48f 长尾。
// 节拍：0–30 起点 hold → 30–42 全速甩 → 42–90 急刹滑入 → 90–130 真静止。
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, Easing } from 'remotion';
import { CameraMotionBlur } from '@remotion/motion-blur';
import layout from '../../_textures/live-layout.json';

export const WHIPBRAKE_DUR = 130;

const RAIL = layout.projects.cards.slice(0, 9); // 9 张真实卡依次排开
const GAP = 60;
const CARD_W = 460;
const TARGET_I = 9; // 第 10 位：card4-hires 目标卡
const TOTAL = (TARGET_I + 1) * (CARD_W + GAP);
// 终点：目标卡居中（120 = 导轨起始偏移）
const END = 120 + TARGET_I * (CARD_W + GAP) + CARD_W / 2 - 960;

const Scene: React.FC = () => {
  const frame = useCurrentFrame();
  // 前 70% 路程 12f，后 30% 路程 48f ease-out 长尾
  const dx = interpolate(frame, [30, 42, 90], [0, END * 0.7, END], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  return (
    <AbsoluteFill style={{ backgroundColor: '#f9f6f1', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: 340, transform: `translateX(${-dx}px)` }}>
        {RAIL.map((c, k) => (
          <Img
            key={c.file + k}
            src={staticFile(`textures/live/${c.file}`)}
            style={{
              position: 'absolute', left: 120 + k * (CARD_W + GAP), top: 0,
              width: CARD_W, borderRadius: 12,
              boxShadow: '0 4px 16px rgba(31,28,23,0.10)',
            }}
          />
        ))}
        {/* 目标卡：高清纹理，急刹落点 */}
        <Img
          src={staticFile('textures/live/card4-hires.png')}
          style={{
            position: 'absolute', left: 120 + TARGET_I * (CARD_W + GAP), top: -20,
            width: CARD_W, borderRadius: 12,
            boxShadow: '0 10px 32px rgba(31,28,23,0.18)',
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

export const WhipBrakeReal: React.FC = () => (
  // 峰值 ~710px/f：采样密度按"回波间距 ≤ 字高"配，20 samples 拖影连续
  <CameraMotionBlur shutterAngle={200} samples={20}>
    <Scene />
  </CameraMotionBlur>
);
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

