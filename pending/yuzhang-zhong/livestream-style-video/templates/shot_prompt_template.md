# Single-Shot Clean-Plate + Post-HUD Prompt Template

## Shot `<01>` (`<0.00s–3.50s>`) — `<Role>`

- **First-Frame Keyframe Prompt (EN)**:
  `9:16 vertical static keyframe, <lens & mount>: <subject & style geometry lock>, <starting pose>. <lighting>. Clean raw camera feed, zero UI text or watermarks.`
- **Clean-Plate Motion Prompt (EN)**:
  `<Engine Camera Tag> <lens & mount>. Subject: <subject & style lock>. Action: <ONE primary action>. Eye-line: <0° lens / 15° chat glance>. Camera physics: <mount vibration / walking bob>. Clean raw camera feed, zero burned-in UI text, zero platform watermarks.`
- **视频纯净底片提示词 (ZH)**:
  `9:16竖屏，<机位焦段与架设>。主体：<画风与角色锁定>。单一动作：<单步动作>。互动眼神轴：<0°直视+15°瞥弹幕>。100%纯净无UI文字底片，严禁乱码弹幕与平台水印。`
- **Track-B Corner Facecam Prompt (Optional for `pip-facecam-rig`)**:
  `<Locked 28mm RGB webcam reaction prompt>`
- **Negative Prompt**:
  `<style exclusions>, floating omniscient crane shot, burned-in gibberish chat text, official platform watermarks`
- **Post-HUD Overlay Spec**:
  `platform=<douyin|kuaishou|instagram|x|tiktok> | popup=<join_toast|commerce_card|qa_pinned|gift_combo>`
