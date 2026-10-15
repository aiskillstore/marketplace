// ---
// name: omniailab-motion-demo-fixtures
// description: 标准占位素材包（孵化轮 PLAYBOOK ③）——灰阶卡片组 + 假 dashboard 面板 +
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 标准占位素材包（孵化轮 PLAYBOOK ③）——灰阶卡片组 + 假 dashboard 面板 +
// 标题字块。首轮孵化建一次，之后终身复用。demo 只求把运动演清楚，
// 不求页面质感，全部灰阶。
import React from 'react';

export const G = {
  bg: '#ececea',
  panel: '#f7f7f6',
  line: '#dcdcda',
  bar: '#c2c2c0',
  ink: '#2f2f2f',
  mid: '#8f8f8d',
  card: '#ffffff',
  border: '#d8d8d6',
  side: '#3a3a3a',
  sideBar: '#5a5a58',
};

export const Card: React.FC<{
  w: number; h: number; seed?: number; style?: React.CSSProperties;
}> = ({ w, h, seed = 0, style }) => {
  const titleW = 45 + ((seed * 37) % 40); // 45–85%
  const lines = 2 + (seed % 3);
  return (
    <div style={{
      width: w, height: h, background: G.card, border: `2px solid ${G.border}`,
      borderRadius: 14, padding: 18, boxSizing: 'border-box',
      display: 'flex', flexDirection: 'column', gap: 10,
      boxShadow: '0 2px 8px rgba(0,0,0,0.06)', ...style,
    }}>
      <div style={{ height: 16, width: `${titleW}%`, background: G.bar, borderRadius: 8 }} />
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} style={{ height: 10, width: `${88 - i * 14 - (seed % 5) * 3}%`, background: G.line, borderRadius: 5 }} />
      ))}
      <div style={{ marginTop: 'auto', display: 'flex', gap: 8, alignItems: 'center' }}>
        <div style={{ width: 26, height: 26, borderRadius: 13, background: G.mid }} />
        <div style={{ height: 10, width: 64, background: G.line, borderRadius: 5 }} />
      </div>
    </div>
  );
};

// 假 dashboard 面板：A = 3×2 卡片网格，B = 列表行。1920×1080。
export const FakeDashboard: React.FC<{ variant?: 'A' | 'B' }> = ({ variant = 'A' }) => (
  <div style={{ width: 1920, height: 1080, background: G.bg, display: 'flex' }}>
    <div style={{ width: 220, background: G.side, padding: '28px 22px', boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div style={{ width: 40, height: 40, borderRadius: 10, background: '#777775' }} />
      {Array.from({ length: 7 }).map((_, i) => (
        <div key={i} style={{ height: 12, width: `${60 + ((i * 29) % 35)}%`, background: G.sideBar, borderRadius: 6 }} />
      ))}
    </div>
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <div style={{ height: 72, background: G.panel, borderBottom: `2px solid ${G.line}`, display: 'flex', alignItems: 'center', padding: '0 32px', gap: 20, boxSizing: 'border-box' }}>
        <div style={{ height: 18, width: 180, background: G.bar, borderRadius: 9 }} />
        <div style={{ marginLeft: 'auto', height: 36, width: 320, background: '#fff', border: `2px solid ${G.line}`, borderRadius: 18, boxSizing: 'border-box' }} />
        <div style={{ width: 36, height: 36, borderRadius: 18, background: G.mid }} />
      </div>
      {variant === 'A' ? (
        <div style={{ flex: 1, padding: 36, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gridAutoRows: '1fr', gap: 28, boxSizing: 'border-box' }}>
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} w={0} h={0} seed={i + 1} style={{ width: '100%', height: '100%' }} />
          ))}
        </div>
      ) : (
        <div style={{ flex: 1, padding: 36, display: 'flex', flexDirection: 'column', gap: 20, boxSizing: 'border-box' }}>
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} style={{ flex: 1, background: G.card, border: `2px solid ${G.border}`, borderRadius: 14, display: 'flex', alignItems: 'center', gap: 24, padding: '0 28px', boxSizing: 'border-box' }}>
              <div style={{ width: 44, height: 44, borderRadius: 10, background: G.mid }} />
              <div style={{ height: 14, width: `${30 + ((i * 23) % 25)}%`, background: G.bar, borderRadius: 7 }} />
              <div style={{ marginLeft: 'auto', height: 12, width: 120, background: G.line, borderRadius: 6 }} />
            </div>
          ))}
        </div>
      )}
    </div>
  </div>
);

export const TitleBlock: React.FC<{ text: string; size?: number }> = ({ text, size = 88 }) => (
  <div style={{ fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800, fontSize: size, color: G.ink, letterSpacing: -1 }}>
    {text}
  </div>
);
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

