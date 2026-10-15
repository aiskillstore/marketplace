// ---
// name: omniailab-motion-template-root
// description: 成片工程模板——工程/src/Root.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import { Composition } from 'remotion';
import { AiflMain, AIFL_TOTAL } from './demo/Main';

export const Root: React.FC = () => {
  return (
    <Composition
      id="DemoPromo"
      component={AiflMain}
      durationInFrames={AIFL_TOTAL}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

