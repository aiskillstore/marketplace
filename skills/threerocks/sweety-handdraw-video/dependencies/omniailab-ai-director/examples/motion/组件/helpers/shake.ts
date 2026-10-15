// ---
// name: omniailab-motion-component-shake
// description: origin: 模板片源仓库 helpers
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// origin: 模板片源仓库 helpers
/**
 * Deterministic hand-held camera noise. Layered sines at incommensurate
 * frequencies read as organic drift; amplitude in world units.
 */
export const handheld = (frame: number, amp = 0.012): [number, number, number] => [
  amp * (Math.sin(frame * 0.31) + 0.6 * Math.sin(frame * 0.83 + 1.7)),
  amp * (Math.sin(frame * 0.47 + 0.9) + 0.5 * Math.sin(frame * 1.13 + 3.1)),
  0,
];
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

