// ---
// name: omniailab-motion-demo-sheen-sweep-retry
// description: sheen-sweep-retry —— 单点扫光（高标准重试）
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// sheen-sweep-retry —— 单点扫光（高标准重试）
// 深墨大卡居中，一道 45° 高光带在 40–68f 从左外扫到右外，仅此一次。
// 约束：单点(只扫主角卡)、圆角裁剪(overflow hidden)、扫前扫后完全静止。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

const CARD_W = 760;
const CARD_H = 420;
const SHEEN_W = CARD_W * 1.6; // 1216

export const SheenSweepRetry: React.FC = () => {
  const frame = useCurrentFrame();

  // 扫光：40–68f，从卡左外(-SHEEN_W)扫到卡右外(CARD_W)，inOut(cubic)，只一次
  const sweepActive = frame >= 40 && frame <= 68;
  const x = interpolate(frame, [40, 68], [-SHEEN_W, CARD_W], {
    easing: Easing.inOut(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: G.bg,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'Helvetica, Arial, sans-serif',
      }}
    >
      <div
        style={{
          width: CARD_W,
          height: CARD_H,
          background: G.side,
          borderRadius: 24,
          overflow: 'hidden', // 圆角裁剪：高光带被卡的圆角裁住
          position: 'relative',
          boxShadow: '0 12px 40px rgba(0,0,0,0.22)',
          boxSizing: 'border-box',
          padding: '64px 72px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          gap: 28,
        }}
      >
        <div
          style={{
            fontSize: 130,
            fontWeight: 800,
            color: '#f5f5f3',
            letterSpacing: 2,
            lineHeight: 1,
          }}
        >
          PRO
        </div>
        <div style={{ height: 16, width: 380, background: G.sideBar, borderRadius: 8 }} />
        <div style={{ height: 16, width: 260, background: G.sideBar, borderRadius: 8 }} />

        {/* 高光带：条件挂载，扫完即摘罩，收尾真静止 */}
        {sweepActive && (
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: SHEEN_W,
              height: CARD_H,
              transform: `translateX(${x}px)`,
              background:
                'linear-gradient(115deg, transparent 42%, rgba(255,255,255,0.32) 50%, transparent 58%)',
              pointerEvents: 'none',
            }}
          />
        )}
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

