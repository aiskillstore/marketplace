// ---
// name: omniailab-motion-demo-whip-pan-real
// description: E 式基本款 whip-pan——真实整页冻结纹理（参考实现/_textures/）。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// E 式基本款 whip-pan——真实整页冻结纹理（参考实现/_textures/）。
// 世界：projects-full 顶部 section（A 景）与同页底部 section（B 景）横向并排
// ——模拟"功能段之间的区块交棒"，相机 8f 甩 2880px（峰值 ~540px/f），
// blur 只包甩动段。节拍：0–35 A hold → 35–43 甩（糊）→ 43–120 B hold（真静止）。
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, Easing } from 'remotion';
import { CameraMotionBlur } from '@remotion/motion-blur';

export const WHIPPAN_DUR = 120;

const SWING = 2880; // 1.5 屏
// 观察窗都对准 cards 网格区（页面空间 y≈247 起），viewport 顶对 y=180
const VIEW_Y = -180;

const Scene: React.FC = () => {
  const frame = useCurrentFrame();
  const dx = interpolate(frame, [35, 43], [0, SWING], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.6, 0, 0.4, 1),
  });
  return (
    <AbsoluteFill style={{ backgroundColor: '#f9f6f1', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', transform: `translateX(${-dx}px)` }}>
        {/* A 景：项目板全满 */}
        <Img
          src={staticFile('textures/live/projects-full.png')}
          style={{ position: 'absolute', left: 0, top: VIEW_Y, width: 1920 }}
        />
        {/* 缝隙纸色空场 960px——甩动中段一晃而过，全糊 */}
        {/* B 景：同页底部 section（PERCEPTION & SENSING 区），换景可辨且内容饱满 */}
        <Img
          src={staticFile('textures/live/projects-full.png')}
          style={{ position: 'absolute', left: SWING, top: -666, width: 1920 }}
        />
      </div>
    </AbsoluteFill>
  );
};

export const WhipPanReal: React.FC = () => (
  // 峰值 ~540px/f：采样按"回波间距 ≤ 字高"配，20 samples 拖影连续
  <CameraMotionBlur shutterAngle={200} samples={20}>
    <Scene />
  </CameraMotionBlur>
);
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

