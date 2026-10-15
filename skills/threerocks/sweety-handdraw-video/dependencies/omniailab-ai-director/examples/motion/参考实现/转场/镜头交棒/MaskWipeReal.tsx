// ---
// name: omniailab-motion-demo-mask-wipe-real
// description: mask-wipe 元素遮罩擦除（轮 D）——真实项目卡（card4-hires）放大成
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// mask-wipe 元素遮罩擦除（轮 D）——真实项目卡（card4-hires）放大成
// 全屏窗口，projects 全景从窗内长出接管："点开一张卡进入它的世界"。
// 节拍：0–40 全景 hold → 40–85 卡放大成窗（窗内新景反向补偿）→ 85–120 hold。
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, Easing } from 'remotion';
import layout from '../../_textures/live-layout.json';

export const MASKWIPE_DUR = 120;

const C4 = layout.projects.cards[3]; // 页面空间 x=781,y=616,w=357,h=312
const VIEW_Y = 180; // 全景观察窗：页面 y=180 起

export const MaskWipeReal: React.FC = () => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [40, 85], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.bezier(0.5, 0, 0.2, 1),
  });
  // 卡在屏幕空间的初始 geometry（全景视口下）
  const g0 = { x: C4.x, y: C4.y - VIEW_Y, w: C4.w, h: C4.h, r: 12 };
  const x = interpolate(t, [0, 1], [g0.x, 0]);
  const y = interpolate(t, [0, 1], [g0.y, 0]);
  const w = interpolate(t, [0, 1], [g0.w, 1920]);
  const h = interpolate(t, [0, 1], [g0.h, 1080]);
  const r = interpolate(t, [0, 1], [g0.r, 0]);
  // 窗内新景（detail 视角用 papers 页顶部模拟）：从 0.42 缩放反向长到 1
  const innerScale = interpolate(t, [0, 1], [0.42, 1]);
  return (
    <AbsoluteFill style={{ backgroundColor: '#f9f6f1', overflow: 'hidden' }}>
      {/* 背景：projects 全景 */}
      <Img
        src={staticFile('textures/live/projects-full.png')}
        style={{ position: 'absolute', left: 0, top: -VIEW_Y, width: 1920 }}
      />
      {/* 卡片即窗口 */}
      <div
        style={{
          position: 'absolute', left: x, top: y, width: w, height: h,
          borderRadius: r, overflow: 'hidden',
          boxShadow: t > 0 && t < 1 ? '0 16px 56px rgba(31,28,23,0.25)' : 'none',
        }}
      >
        {/* 窗内新景：projects 页深部（detail 语义），反向补偿铺满 */}
        <div
          style={{
            position: 'absolute', width: 1920, height: 1080,
            left: '50%', top: '50%',
            transform: `translate(-50%, -50%) scale(${innerScale})`,
            overflow: 'hidden', background: '#f9f6f1',
          }}
        >
          <Img
            src={staticFile('textures/live/projects-full.png')}
            style={{ position: 'absolute', left: 0, top: -846, width: 1920 }}
          />
        </div>
        {/* 卡片脸：随放大渐隐露出窗内景 */}
        <Img
          src={staticFile('textures/live/card4-hires.png')}
          style={{
            position: 'absolute', inset: 0, width: '100%', height: '100%',
            opacity: Math.max(0, 1 - t * 2.2),
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

