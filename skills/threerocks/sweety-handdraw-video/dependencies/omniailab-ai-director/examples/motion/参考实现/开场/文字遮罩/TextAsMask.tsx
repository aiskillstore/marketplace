// ---
// name: omniailab-motion-demo-text-as-mask
// description: 文字视频遮罩（文字遮罩）——kinetische typografie
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 文字视频遮罩（文字遮罩）——kinetische typografie
// 深底上超粗大字 "SCALE"，字形内部用 CSS alpha mask 套住 FakeDashboard：
// 0–20f hold 读布景；20–100f dashboard 在字内匀速 translateX +110→-110（scale 1.15）；
// 100–130f 单段 bezier：mask 层 scale 1→26 放大溢出（内容层用 1/S 反向抵消不畸变），
// 同时无遮罩全屏层淡入接管，dashboard 1.15→1.0 归位；130–150f 全屏静止收尾。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { FakeDashboard, G } from '../../_fixtures/Fixtures';

const MASK_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080"><text x="960" y="666" font-family="Helvetica, Arial, sans-serif" font-size="360" font-weight="900" letter-spacing="-8" text-anchor="middle" fill="white">SCALE</text></svg>`;
const MASK_URL = `url("data:image/svg+xml,${encodeURIComponent(MASK_SVG)}")`;
// mask 放大原点：取字母 L 的竖笔位置（约 61.5% 处），保证放大时原点落在实心笔画内
const ORIGIN = '61.5% 50%';

export const TextAsMask: React.FC = () => {
  const f = useCurrentFrame();
  const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

  // 结尾撤场进度：100–130f 单段 bezier
  const endT = interpolate(f, [100, 130], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.4, 0, 0.2, 1),
  });

  // dashboard 内容运动：20–100f 匀速漂移，100–130f 归位到全屏
  const driftX = interpolate(f, [20, 100], [110, -110], clamp);
  const dx = f < 100 ? driftX : interpolate(endT, [0, 1], [-110, 0]);
  const dashS = interpolate(endT, [0, 1], [1.15, 1]);

  // mask 层放大（内容层反向抵消，dashboard 不跟着几何畸变）
  const maskS = interpolate(endT, [0, 1], [1, 26]);
  // 无遮罩全屏层淡入，保证接管彻底
  const cover = interpolate(endT, [0.25, 0.9], [0, 1], clamp);
  // 底部小注释：撤场时淡出
  const caption = interpolate(f, [100, 114], [1, 0], clamp);

  const dashMotion: React.CSSProperties = {
    position: 'absolute',
    inset: 0,
    transform: `translateX(${dx}px) scale(${dashS})`,
    transformOrigin: '50% 50%',
  };

  return (
    <div style={{ width: 1920, height: 1080, background: G.ink, position: 'relative', overflow: 'hidden' }}>
      {/* 遮罩层：wrapper 负责 mask + 放大；inner 用 1/S 反向缩放抵消内容形变 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `scale(${maskS})`,
          transformOrigin: ORIGIN,
          WebkitMaskImage: MASK_URL,
          maskImage: MASK_URL,
          WebkitMaskRepeat: 'no-repeat',
          maskRepeat: 'no-repeat',
          WebkitMaskSize: '1920px 1080px',
          maskSize: '1920px 1080px',
        }}
      >
        <div style={{ position: 'absolute', inset: 0, transform: `scale(${1 / maskS})`, transformOrigin: ORIGIN }}>
          <div style={dashMotion}>
            <FakeDashboard variant="A" />
          </div>
        </div>
      </div>

      {/* 接管层：同一运动变换的全屏 dashboard，撤场时淡入到 1 */}
      <div style={{ position: 'absolute', inset: 0, opacity: cover }}>
        <div style={dashMotion}>
          <FakeDashboard variant="A" />
        </div>
      </div>

      {/* 底部小注释 */}
      <div
        style={{
          position: 'absolute',
          bottom: 90,
          width: '100%',
          textAlign: 'center',
          fontFamily: 'Helvetica, Arial, sans-serif',
          fontWeight: 700,
          fontSize: 30,
          letterSpacing: 10,
          color: G.mid,
          opacity: caption,
        }}
      >
        TEXT AS MASK
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

