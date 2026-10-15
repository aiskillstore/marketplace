// ---
// name: omniailab-motion-component-camera
// description: origin: 模板片源仓库 helpers
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// origin: 模板片源仓库 helpers
import { useThree, useFrame } from '@react-three/fiber';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import * as THREE from 'three';
import { handheld } from './shake';

export type CamKeyframe = {
  frame: number;
  pos: [number, number, number];
  look: [number, number, number];
  fov?: number;
};

const easeInOut = Easing.bezier(0.4, 0.0, 0.2, 1.0);

/**
 * Animates the default camera through keyframes (frames relative to the
 * enclosing Sequence). Position/look are eased segment by segment.
 * `shake` adds deterministic hand-held drift (world units).
 */
export const Rig: React.FC<{
  keyframes: CamKeyframe[];
  easing?: (t: number) => number;
  shake?: number;
}> = ({ keyframes, easing = easeInOut, shake = 0 }) => {
  const frame = useCurrentFrame();
  const { camera } = useThree();

  let a = keyframes[0];
  let b = keyframes[keyframes.length - 1];
  for (let i = 0; i < keyframes.length - 1; i++) {
    if (frame >= keyframes[i].frame && frame <= keyframes[i + 1].frame) {
      a = keyframes[i];
      b = keyframes[i + 1];
      break;
    }
  }
  const t =
    a.frame === b.frame
      ? 1
      : interpolate(frame, [a.frame, b.frame], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing,
        });

  const lerp3 = (p: [number, number, number], q: [number, number, number]): THREE.Vector3 =>
    new THREE.Vector3(
      p[0] + (q[0] - p[0]) * t,
      p[1] + (q[1] - p[1]) * t,
      p[2] + (q[2] - p[2]) * t
    );

  const pos = lerp3(a.pos, b.pos);
  const look = lerp3(a.look, b.look);
  const fov = (a.fov ?? 36) + ((b.fov ?? 36) - (a.fov ?? 36)) * t;

  useFrame(() => {
    if (shake > 0) {
      const [dx, dy] = handheld(frame, shake);
      pos.x += dx;
      pos.y += dy;
      look.x += dx * 0.6;
      look.y += dy * 0.6;
    }
    camera.position.copy(pos);
    camera.lookAt(look);
    if (camera instanceof THREE.PerspectiveCamera) {
      camera.fov = fov;
      camera.updateProjectionMatrix();
    }
  });

  return null;
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

