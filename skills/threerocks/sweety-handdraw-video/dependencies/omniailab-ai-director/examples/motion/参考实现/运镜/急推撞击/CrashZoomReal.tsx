// ---
// name: omniailab-motion-demo-crash-zoom-real
// description: crash-zoom 急推——真实 projects 页全景一拍推到 card4（高清纹理槽位）。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// crash-zoom 急推——真实 projects 页全景一拍推到 card4（高清纹理槽位）。
// 节拍：0–40 全景 hold → 40–46 急推 6f（ease-in，峰值放大 2.6x）→
// 46–51 过冲回弹（2.6→2.45）→ 51–120 特写 hold 真静止。
// blur 只包 40–46 急推段（轮 A 规律：极速段 samples 20）。
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, Easing } from 'remotion';
import { CameraMotionBlur } from '@remotion/motion-blur';
import layout from '../../_textures/live-layout.json';

export const CRASHZOOM_DUR = 120;

// card4 中心（页面空间）：x=781+357/2≈960, y=616+312/2=772
const TARGET = { cx: 960, cy: 772 };
const VIEW_Y = 180; // 全景观察窗顶（页面 y）

const Scene: React.FC = () => {
  const frame = useCurrentFrame();
  const zoom = interpolate(frame, [40, 46, 51], [1, 2.6, 2.45], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.bezier(0.55, 0, 0.7, 1),
  });
  const cx = interpolate(frame, [40, 46], [960, TARGET.cx], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.quad),
  });
  const cy = interpolate(frame, [40, 46], [VIEW_Y + 540, TARGET.cy], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.quad),
  });
  return (
    <AbsoluteFill style={{ backgroundColor: '#f9f6f1', overflow: 'hidden' }}>
      <div
        style={{
          position: 'absolute', width: 1920, height: layout.projects.pageH,
          transform: `translate(${960 - cx * zoom}px, ${540 - cy * zoom}px) scale(${zoom})`,
          transformOrigin: '0 0',
        }}
      >
        <Img src={staticFile('textures/live/projects-full.png')} style={{ position: 'absolute', width: 1920 }} />
        {/* 高清目标卡覆盖原位，放大后文字仍锐（Q2） */}
        <Img
          src={staticFile('textures/live/card4-hires.png')}
          style={{
            position: 'absolute',
            left: layout.projects.cards[3].x, top: layout.projects.cards[3].y,
            width: layout.projects.cards[3].w, height: layout.projects.cards[3].h,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

export const CrashZoomReal: React.FC = () => {
  const frame = useCurrentFrame();
  return frame >= 38 && frame <= 48 ? (
    <CameraMotionBlur shutterAngle={200} samples={20}>
      <Scene />
    </CameraMotionBlur>
  ) : (
    <Scene />
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

