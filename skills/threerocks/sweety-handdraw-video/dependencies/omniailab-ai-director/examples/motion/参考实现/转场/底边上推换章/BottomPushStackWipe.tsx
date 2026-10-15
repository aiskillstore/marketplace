// ---
// name: omniailab-motion-demo-bottom-push-stack-wipe
// description: 底边上推换章 —— slack-promo 22–27s
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 底边上推换章 —— slack-promo 22–27s
// 换章手法：新场景连底色整屏从底边向上推入，把旧场景顶出画外，
// 连推三章（三种饱和底色，每章中央钉一张灰阶窗口卡随底色走）。
// 推入用重 ease-out（快进慢停）。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';
import { Card, G } from '../../_fixtures/Fixtures';

const H = 1080;

// 章节定义：底色 + 卡片种子。第 0 章是起始灰阶场景。
const CHAPTERS = [
  { color: G.bg, label: 0 },
  { color: '#2bac76', label: 1 }, // 绿
  { color: '#36c5f0', label: 2 }, // 蓝
  { color: '#e01e5a', label: 3 }, // 粉红
];

// 每章推入的起始帧；约 32 帧完成一次推入，随后 hold
const PUSH_STARTS = [18, 55, 92];
const PUSH_DUR = 30;

const heavyEaseOut = Easing.bezier(0.12, 0.9, 0.2, 1); // 快进慢停

const ChapterScene: React.FC<{ chapter: number }> = ({ chapter }) => {
  const c = CHAPTERS[chapter];
  return (
    <AbsoluteFill style={{ background: c.color, justifyContent: 'center', alignItems: 'center' }}>
      {/* 底色上的淡装饰条，让"底色也在动"更可读 */}
      {chapter > 0 && (
        <>
          <div style={{ position: 'absolute', top: 90, left: 120, width: 500, height: 26, borderRadius: 13, background: 'rgba(255,255,255,0.28)' }} />
          <div style={{ position: 'absolute', bottom: 110, right: 140, width: 340, height: 26, borderRadius: 13, background: 'rgba(255,255,255,0.22)' }} />
          <div style={{ position: 'absolute', top: 160, right: 220, width: 90, height: 90, borderRadius: '50%', background: 'rgba(255,255,255,0.18)' }} />
        </>
      )}
      {/* 中央钉住的灰阶窗口卡 */}
      <div style={{ boxShadow: '0 30px 80px rgba(0,0,0,0.28)', borderRadius: 18 }}>
        <div style={{ width: 860, background: '#f2f2f0', borderRadius: '18px 18px 0 0', height: 52, display: 'flex', alignItems: 'center', gap: 10, padding: '0 22px', boxSizing: 'border-box', border: `2px solid ${G.border}`, borderBottom: 'none' }}>
          {['#e0605a', '#e8b93e', '#67bb5a'].map((dot, i) => (
            <div key={i} style={{ width: 16, height: 16, borderRadius: 8, background: dot }} />
          ))}
          <div style={{ marginLeft: 18, height: 14, width: 220, background: G.bar, borderRadius: 7 }} />
        </div>
        <Card w={860} h={430} seed={chapter + 2} style={{ borderRadius: '0 0 18px 18px', padding: 34 }} />
      </div>
    </AbsoluteFill>
  );
};

export const BottomPushStackWipe: React.FC = () => {
  const frame = useCurrentFrame();
  // 每章的推入进度
  const progress = PUSH_STARTS.map((s) =>
    interpolate(frame, [s, s + PUSH_DUR], [0, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: heavyEaseOut,
    })
  );
  return (
    <AbsoluteFill style={{ overflow: 'hidden', background: G.bg }}>
      {CHAPTERS.map((_, i) => {
        // 第 i 章的位移 = 自己被推入的进度 + 被后续章顶出的进度
        const pushedIn = i === 0 ? 1 : progress[i - 1]; // 自己进入
        const pushedOut = i < CHAPTERS.length - 1 ? progress[i] : 0; // 被下一章顶出
        const y = (1 - pushedIn) * H - pushedOut * H;
        if (y <= -H || y >= H) return null;
        return (
          <AbsoluteFill key={i} style={{ transform: `translateY(${y}px)` }}>
            <ChapterScene chapter={i} />
            {/* 推入时上缘接缝阴影，强化"顶出"的物理感 */}
            {i > 0 && (
              <div style={{ position: 'absolute', top: -40, left: 0, right: 0, height: 40, background: 'linear-gradient(to top, rgba(0,0,0,0.30), rgba(0,0,0,0))', opacity: pushedIn < 1 ? 1 : 0 }} />
            )}
          </AbsoluteFill>
        );
      })}
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

