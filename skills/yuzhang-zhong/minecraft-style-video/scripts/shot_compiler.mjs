#!/usr/bin/env node
/**
 * shot_compiler.mjs
 * Zero-dependency CLI storyboard planner and engine-specific I2V/T2V prompt compiler
 * for 9:16 Minecraft-style voxel character, mob, and block/item short videos.
 */

import { fileURLToPath } from "node:url";

const TEMPLATES = {
  "diamond-creeper-ambush": {
    titleZh: "挖到钻石秒遇苦力怕",
    titleEn: "Diamond Cave Creeper Ambush",
    defaultRig: "steve-wide",
    defaultShader: "rtx-emissive",
    featuredObject: "16x16x16 Diamond Ore + 16x16x1 Diamond Pickaxe + Creeper Mob",
    subjectEn:
      "an authentic Minecraft Steve miner (sharp 90-degree 8x8x8 cubic head with +0.5px 3D brown hair layer, 8x12x4 cyan tunic torso, 4x12x4 rectangular prism limbs with fingerless flat 4x4 square hand ends) holding an extruded 16x16x1 pixel-art diamond pickaxe in a torch-lit deepslate cave",
    subjectZh:
      "《我的世界》标准像素矿工Steve（8x8x8锋利直角立方体头、+0.5px立体深棕像素刘海层、8x12x4青色短衫躯干、4x12x4平头正方形截面手臂），握持16x16x1锯齿像素钻石镐身处火把照亮的深板岩矿洞",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn:
          "pivots his rigid right 4x12x4 blocky arm at the shoulder hinge to swing the extruded 16x16x1 pixel-art diamond pickaxe into a glowing cyan 16x16x16 Diamond Ore block, creating dark pixel crack lines across the block face",
        actionZh:
          "右侧4x12x4刚性方柱手臂沿肩部转轴干脆挥落，用16x16x1锯齿像素钻石镐敲击发光的青色16x16x16钻石矿石方块，方块表面浮现黑色像素裂纹",
        faceEn: "excited 8x8 pixel face with sparkling 2x1 pixel eyes and raised pixel eyebrows",
        faceZh: "8x8像素脸呈现惊喜发光的2x1像素眼睛与上扬像素眉",
        cameraEn: "Close-up over-the-shoulder framing on the diamond ore block, rapid dolly push-in with subtle pickaxe impact shake",
        cameraZh: "越肩特写对准发光钻石矿石方块，镜头极速推近并伴随敲击瞬间轻微震动",
        hailuoTag: "[Push in, Shake]",
        sfx: "block.stone.hit + 清脆挖矿敲击声",
        caption: "挖了三小时，终于出钻石了？！"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn:
          "the 16x16x16 Diamond Ore block shatters into square pixel particles and a spinning miniature pixel diamond drop, revealing a green armless quadrupedal Minecraft Creeper standing silently in the gap behind it",
        actionZh:
          "16x16x16钻石矿石啪地碎裂为十几个正方形像素碎屑与一颗旋转悬浮的微型像素钻石，碎裂缺口后方赫然站着一只绿叶迷彩像素纹理的无手臂四足苦力怕",
        faceEn: "miner's 2x1 pixel pupils shrink in shock opposite the Creeper's iconic 8x8 black pixel frowning face",
        faceZh: "矿工像素瞳孔骤然缩小，与苦力怕标志性8x8黑色像素哭丧脸正面对视",
        cameraEn: "Medium rack-focus shot shifting from the floating pixel diamond to the Creeper behind the broken block",
        cameraZh: "中景焦点从悬浮旋转的像素钻石快速切至缺口后方的苦力怕",
        hailuoTag: "[Static shot]",
        sfx: "block.stone.break + entity.item.pickup + 低沉脚步声",
        caption: "等等…石头后面是谁？"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn:
          "the green Minecraft Creeper flashes bright solid white and swells horizontally in boxy voxel scale while the miner's rigid 4x12x4 arms pivot straight up in panic",
        actionZh:
          "苦力怕全身高频闪烁刺眼纯白光并呈方块比例横向膨胀，矿工双侧4x12x4刚性方柱手臂猛地向上举起破防后退",
        faceEn: "miner's 8x8 pixel face switches to oversized 2x2 hollow square panic eyes and vertical cyan pixel tear strips",
        faceZh: "矿工8x8像素脸瞬间切换为2x2空心正方形惊恐眼与蓝色垂直像素流泪条",
        cameraEn: "Low-angle two-shot pulling back slightly with urgent camera vibration synced to the white fuse flash",
        cameraZh: "低角度双人同框微仰拍，伴随苦力怕白光闪烁产生紧迫镜头震动",
        hailuoTag: "[Pull out, Shake]",
        sfx: "entity.creeper.primed (经典 Tsssss... 引信嘶鸣声)",
        caption: "最害怕的一集：嘶——"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn:
          "a cluster of stepped white cubic explosion smoke blocks bursts outward as the miner tips sideways at a rigid 90-degree angle with a crimson Minecraft hurt-flash tint beside his bobbing dropped diamond pickaxe",
        actionZh:
          "数团阶梯状纯白正方体爆炸烟雾方块向四周迸发，矿工全身泛起原版受击红光并保持笔直刚体姿态呈90度侧翻在地，旁侧悬浮旋转着掉落的像素钻石镐",
        faceEn: "dizzy cross-pixel eyes on the sideways 8x8x8 cubic head",
        faceZh: "侧翻的8x8x8立方体头上定格为眩晕像素眼",
        cameraEn: "High-angle 45-degree isometric cave shot matching Shot 1's lighting for seamless loop replay",
        cameraZh: "45度高角度矿洞俯拍定格，光影与首镜衔接形成无缝循环",
        hailuoTag: "[Tilt down, Static shot]",
        sfx: "entity.generic.explode + 经典受击音效",
        caption: "辛辛苦苦三小时，一朝回到重生点"
      }
    ]
  },
  "cozy-lantern-build": {
    titleZh: "治愈系微缩方块木屋建造",
    titleEn: "Cozy Isometric Voxel Cabin & Lantern Build",
    defaultRig: "alex-slim",
    defaultShader: "bsl-sunlight",
    featuredObject: "16x16x16 Grass Block + Crafting Table + 14x14x14 Chest + Voxel Lantern",
    subjectEn:
      "a canonical Minecraft Alex voxel builder (sharp 8x8x8 cubic head with +0.5px 3D ginger side-ponytail and beret shell, 8x12x4 moss-green tunic torso, slim 3x12x4 rectangular prism arms with flat 3x4 square hand ends) on a miniature 5x5x5 Grass Block cutaway diorama",
    subjectZh:
      "《我的世界》森系建筑师Alex像素小人（8x8x8直角立方体头、+0.5px立体橘红侧马尾与贝雷帽皮肤层、8x12x4苔绿上衣、3x12x4纤细平头方手），站在5x5x5微缩草方块剖面景观底座上",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn:
          "uses her flat 3x4 square blocky hands to snap a canonical 16x16x16 Minecraft Crafting Table block cleanly onto an oak plank corner of the grass block diorama",
        actionZh:
          "用3x4平头正方形像素手将一块标准16x16x16像素《我的世界》工作台方块啪嗒一声精准卡入草方块木屋转角槽位",
        faceEn: "warm 8x8 pixel face with curved happy 2x1 pixel eyes and soft pink 1x1 blush texels",
        faceZh: "温暖8x8像素脸呈现弯弯2x1像素笑眼与粉色1x1腮红像素格",
        cameraEn: "45-degree isometric tilt-shift macro shot pushing gently toward the miniature voxel cabin",
        cameraZh: "45度等距移轴微缩模型俯拍，镜头轻柔推向方块小木屋",
        hailuoTag: "[Push in]",
        sfx: "block.wood.place 清脆木方块安放声",
        caption: "在桌面搭一座会发光的微缩方块屋"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn:
          "places a 14x14x14 hinged wooden Minecraft Chest with a protruding 3D silver 2x4 pixel front latch next to the crafting table, and its top lid hinges open 60 degrees with a crisp wooden creak",
        actionZh:
          "在工作台旁安放一只14x14x14像素可开合橡木储物箱（正面带凸起3D银色2x4像素锁扣），箱盖沿转轴向上翻开60度",
        faceEn: "focused 8x8 pixel eyes looking down at the glowing items inside the chest",
        faceZh: "专注的8x8像素眼望向箱内透出的微光",
        cameraEn: "Side-angle macro close-up highlighting the 16x16 pixel grain and 3D silver chest latch",
        cameraZh: "侧面微距特写，清晰展现16x16像素木纹与立体银色箱锁细节",
        hailuoTag: "[Static shot]",
        sfx: "block.chest.open 原版木箱开启吱呀声",
        caption: "强迫症极度舒适的像素对齐"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn:
          "hangs a 6x9x6 voxel Lantern under the oak roof beam; warm golden BSL-shader block light instantly floods across the crisp 16x16 grass and wood pixel textures",
        actionZh:
          "抬起3x12x4细方柱手臂将一盏6x9x6像素铁框灯笼挂上橡木屋檐，温暖的BSL金黄方块光源瞬间铺满周围清晰的16x16草方块与木板纹理",
        faceEn: "sparkling 2x1 pixel eyes illuminated by warm amber lantern light",
        faceZh: "暖黄灯笼光映亮灵动的2x1像素眼睛",
        cameraEn: "Slow dolly arc around the illuminated voxel porch under twilight blue sky",
        cameraZh: "暮色蓝调背景下，镜头缓慢环绕被暖光点亮的方块门廊",
        hailuoTag: "[Pan right]",
        sfx: "block.lantern.place 清脆金属挂钩声 + 治愈风铃",
        caption: "打开光影的那一刻，氛围感拉满"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn:
          "sits on the stepped edge of the 16x16x16 Grass Block swinging her 4x12x4 blocky legs in rhythm beside a pastel-pink voxel Axolotl as red pixel heart particles float upward",
        actionZh:
          "坐在16x16x16草方块边缘轻轻晃动并拢的4x12x4方柱双腿，身旁趴着一只粉色像素美西螈，头顶飘起红色正方形像素爱心粒子",
        faceEn: "peaceful closed-eye happy pixel smile on both Alex and the pink Axolotl",
        faceZh: "建筑师小人与粉色美西螈同时呈现治愈系微笑像素眼",
        cameraEn: "Gentle pull-back to the full 45-degree isometric diorama view matching Shot 1",
        cameraZh: "镜头轻柔拉回开场45度微缩景观全景，实现无缝循环播放",
        hailuoTag: "[Pull out]",
        sfx: "舒缓原版钢琴旋律 + 水滴泡泡声",
        caption: "今日份电子精神角落已建成"
      }
    ]
  },
  "pro-builder-vs-noob-tnt": {
    titleZh: "红石大佬 vs 熊孩子拍TNT",
    titleEn: "Pro Diamond Builder vs. Noob TNT Prank",
    defaultRig: "steve-wide",
    defaultShader: "bare-bones-trailer",
    featuredObject: "16x16x16 TNT Block + 14x14x14 Chest + 3D Diamond Armor",
    subjectEn:
      "two contrasting Minecraft voxel characters side by side: on the left, a Pro Builder wearing a 3D cubic #4AEDD9 Diamond Helmet and Chestplate; on the right, a Classic Steve Noob with fingerless flat 4x4 square hands holding a red-and-white 16x16x16 TNT block",
    subjectZh:
      "同框反差双人《我的世界》像素小人：左侧为穿戴3D立体亮青色钻石头盔与胸甲的建筑大佬，右侧为双手捧着红白16x16x16像素TNT炸药块的呆萌史蒂夫新手",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn:
          "the Diamond-armored Pro proudly gestures with his extruded 16x16x1 diamond sword toward a neat display of chests and diamond blocks, while the Noob stands stiffly holding a 16x16x16 TNT block",
        actionZh:
          "左侧钻石甲大佬挥动16x16x1像素钻石剑自豪展示整齐的储物箱与钻石块展台，右侧新手笔直僵立，平头方手里捧着一块红白16x16x16像素TNT方块",
        faceEn: "confident pixel grin on the Pro; blank unchanging 2x1 pixel stare on the Noob",
        faceZh: "左侧大佬自信挑眉像素脸，右侧新手保持一动不动的呆萌默认像素眼",
        cameraEn: "Fast snap-zoom into a medium two-shot on a clean stone-brick fortress floor",
        cameraZh: "石砖基地中景双人同框快速推镜，高饱和官方宣传片画风",
        hailuoTag: "[Push in]",
        sfx: "entity.experience_orb.pickup 叮咚声 + 呆萌木鱼声",
        caption: "带萌新参观我肝了一周的基地"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn:
          "the Noob rigidly pivots both 4x12x4 arms downward to slam the 16x16x16 red-and-white TNT block directly onto the stone floor between them and flicks a pixel flint-and-steel spark",
        actionZh:
          "右侧新手双侧4x12x4刚性方柱手臂干脆向下挥落，把印有TNT字样的16x16x16炸药方块啪地拍在两人中间的石砖地上并擦出像素火石火花",
        faceEn: "Noob keeps the exact same blank pixel smile; Pro's 2x1 pixel eyes widen in disbelief",
        faceZh: "新手依然保持呆萌像素微笑，左侧大佬的2x1像素眼瞬间瞪大",
        cameraEn: "Low-angle close-up centering the newly placed 16x16x16 TNT block on the floor grid",
        cameraZh: "低角度近景聚焦地面正中央刚放下的16x16x16红白TNT方块",
        hailuoTag: "[Tilt down, Static shot]",
        sfx: "block.grass.place + item.flintandsteel.use 打火石咔嚓声",
        caption: "萌新：「这个红色方块是礼花吗？」"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn:
          "the 16x16x16 TNT block alternates flashing solid bright white and swelling in cubic scale as both characters lean backward at a stiff 30-degree waist angle",
        actionZh:
          "地面上的16x16x16 TNT方块开始高频闪烁刺眼白光并呈正方体比例膨胀，两个像素小人同步保持笔直躯干向后仰倒30度",
        faceEn: "synchronized 2x2 hollow square panic pixel eyes on both avatars",
        faceZh: "两人8x8像素脸同步切换为2x2空心正方形惊恐像素眼",
        cameraEn: "Medium wide static shot with rapid camera shake synced to the pulsing white TNT block",
        cameraZh: "中全景固定机位，配合TNT白光闪烁产生急促镜头震动",
        hailuoTag: "[Shake, Static shot]",
        sfx: "entity.tnt.primed 急促引信嘶鸣声",
        caption: "血压瞬间拉满：别乱按右键啊！！"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn:
          "standing amidst floating cubic white smoke particles in a shallow block crater, both soot-smudged avatars slowly rotate only their 8x8x8 cubic heads 45 degrees to stare deadpan into the lens",
        actionZh:
          "在飘散着正方形白烟粒子的浅方坑里，浑身沾满黑灰像素点的两个小人身体完全静止，仅8x8x8立方体脑袋缓慢转动45度盯向镜头",
        faceEn: "synchronized horizontal line deadpan pixel eyes (-_-) on both soot-covered 8x8 faces",
        faceZh: "两人沾灰的8x8像素脸同步定格为沉默一字死鱼眼(-_-)",
        cameraEn: "Slow dolly pull-back returning to the opening two-shot framing for loop replay",
        cameraZh: "镜头缓慢拉远回到开场双人同框构图实现无缝循环",
        hailuoTag: "[Pull out]",
        sfx: "entity.generic.explode 余音 + 乌鸦飞过音效",
        caption: "友尽现场：已将该玩家移出服务器"
      }
    ]
  },
  "redstone-chain-asmr": {
    titleZh: "强迫症极度舒适红石机关连环",
    titleEn: "Satisfying Redstone & Sticky Piston Chain ASMR",
    defaultRig: "alex-slim",
    defaultShader: "rtx-emissive",
    featuredObject: "16x16x16 Sticky Piston + Redstone Dust + Redstone Lamp",
    subjectEn:
      "a precision Minecraft redstone mechanism built from canonical 16x16x16 cobblestone sticky pistons, glowing crimson redstone dust lines, and warm Redstone Lamps operated by an Alex engineer with flat 3x4 square hands",
    subjectZh:
      "由标准16x16x16像素粘性活塞、自发光红石粉线路与红石灯组成的精密《我的世界》红石机关阵列，由3x4平头方手的Alex工程师触发",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn:
          "a flat 3x4 square pixel hand flips a voxel cobblestone lever 90 degrees, instantly igniting a trail of glowing crimson #EF4444 redstone dust texels with square red spark particles",
        actionZh:
          "3x4平头正方形像素手干脆地扳下90度像素拉杆，地面一排红石粉贴图瞬间亮起#EF4444鲜红自发光并蹦出正方形红色粒子",
        faceEn: "confident pixel wink reflected in the glowing redstone light",
        faceZh: "红石火光映照下自信眨眼的8x8像素脸",
        cameraEn: "Extreme macro close-up following the glowing redstone dust line across the floor grid",
        cameraZh: "微距大特写沿地面像素网格紧随点亮的红石线路推进",
        hailuoTag: "[Push in, Pan right]",
        sfx: "block.lever.click 清脆拉杆咔哒声",
        caption: "当红石线路严丝合缝跑通的那一刻"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn:
          "three 16x16x16 sticky pistons extend their 4-pixel-thick wooden heads in crisp sequential 90-degree steps, snapping three glowing cyan Diamond Blocks into a flush row",
        actionZh:
          "三个16x16x16粘性活塞按节奏依次伸出4像素厚的木质推板，将三块高光亮青色钻石块严丝合缝推成齐平一排",
        faceEn: "focused 2x1 pixel eyes tracking the rhythmic piston motion",
        faceZh: "专注的2x1像素眼睛随活塞节奏轻轻移动",
        cameraEn: "45-degree isometric tracking shot parallel to the extending piston heads",
        cameraZh: "45度等距平行跟拍镜头，展现活塞分步推块的机械美感",
        hailuoTag: "[Pan right]",
        sfx: "block.piston.extend 连续三声清脆活塞机械推拉音",
        caption: "强迫症表示可以盯一整天"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn:
          "the completed diamond block row conducts power into a domino wave of 16x16x16 Redstone Lamps lighting up one by one in warm amber-gold across the dark deepslate wall",
        actionZh:
          "闭合的钻石块阵列导电触发多米诺骨牌效应，深板岩墙面上的16x16x16红石灯由近及远逐格点亮温暖琥珀金光",
        faceEn: "awestruck 8x8 pixel face bathed in cascading golden block light",
        faceZh: "层层亮起的金色方块光洒在惊叹的8x8像素脸上",
        cameraEn: "Low-angle wide dolly shot capturing the cascading wave of glowing Redstone Lamps",
        cameraZh: "低角度广角推镜，完整捕捉红石灯逐格点亮的波浪光影",
        hailuoTag: "[Tilt up, Push in]",
        sfx: "连续递进的清脆音符盒叮咚声 (block.note_block.chime)",
        caption: "这丝滑程度打几分？"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn:
          "a hidden 2x2 flush quartz piston door retracts inward and slides open to reveal a spinning extruded 16x16x1 Enchanted Golden Apple floating on an obsidian pedestal",
        actionZh:
          "隐藏的2x2齐平石英活塞门向内缩回并向两侧滑开，露出黑曜石底座中央悬浮旋转的16x16x1附魔金苹果",
        faceEn: "beaming star-eyed pixel expression",
        faceZh: "闪耀星星眼像素表情",
        cameraEn: "Symmetrical center framing pushing smoothly toward the pedestal to loop back to Shot 1",
        cameraZh: "对称中心构图平滑推向展台，衔接首镜实现无缝循环",
        hailuoTag: "[Push in]",
        sfx: "block.piston.contract + 附魔闪烁音效",
        caption: "红石科技的尽头是仪式感"
      }
    ]
  },
  "enderman-block-heist": {
    titleZh: "末影人半夜偷草方块",
    titleEn: "Enderman Midnight Grass Block Heist",
    defaultRig: "mob-enderman",
    defaultShader: "bsl-sunlight",
    featuredObject: "Enderman Mob + 16x16x16 Grass Block",
    subjectEn:
      "a canonical 3-block-tall jet-black Minecraft Enderman (sharp 8x8x8 cubic head with glowing magenta 3x1 pixel eyes and thin 2x30x2 rectangular stick limbs) standing beside a Steve builder on a moonlit grass lawn",
    subjectZh:
      "3格高纯黑《我的世界》末影人（8x8x8直角立方体头、自发光紫红3x1像素眼、修长2x30x2细方柱四肢），站在月光草坪上的Steve小人身旁",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn:
          "Steve places the final 16x16x16 Grass Block to complete a flat garden lawn while a tall jet-black Enderman with glowing purple 3x1 pixel eyes materializes right behind him in a burst of square purple particles",
        actionZh:
          "Steve刚放好最后一块16x16x16草方块补齐平整草坪，身后紫色正方形粒子一闪，凭空出现一只闪烁紫红3x1像素眼的高大纯黑末影人",
        faceEn: "proud pixel smile on Steve; glowing motionless purple 3x1 pixel eyes on the Enderman",
        faceZh: "Steve满意微笑，身后末影人紫红3x1像素眼一动不动",
        cameraEn: "Medium two-shot under moonlit BSL shader shadows",
        cameraZh: "月光BSL光影下的中景前后反差构图",
        hailuoTag: "[Static shot]",
        sfx: "entity.enderman.teleport 经典末影瞬移低音",
        caption: "刚铺平的草坪，总觉得背后凉飕飕"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn:
          "the Enderman's thin 2x30x2 rectangular stick arms pluck the center 16x16x16 Grass Block straight out of the lawn, leaving a neat 1x1x1 square hole in the ground",
        actionZh:
          "末影人修长的2x30x2细方柱手臂干脆利落地把草坪正中央的那块16x16x16草方块直接拔起抱在怀里，地面留下一个1x1x1方坑",
        faceEn: "Steve's 8x8 pixel head snaps around with wide 2x2 square eyes staring at the missing block hole",
        faceZh: "Steve的8x8像素头猛地转过来，2x2惊愕像素眼死死盯着地面方坑",
        cameraEn: "High-angle shot centering the square hole in the grass grid and the Enderman holding the block",
        cameraZh: "微俯拍居中展现草坪上的正方形缺口与抱方块的末影人",
        hailuoTag: "[Tilt down]",
        sfx: "block.grass.break 清脆拔草方块声",
        caption: "当着我的面扣走一块草皮？！"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn:
          "Steve accidentally looks up into the Enderman's eyes; the Enderman's 8x8x8 black cube head vibrates rapidly and drops its lower cubic jaw open while still clutching the 16x16x16 Grass Block",
        actionZh:
          "Steve不小心抬头与末影人对视，末影人怀里还紧紧抱着那块16x16x16草方块，8x8x8纯黑立方体头壳瞬间高频震动并向下张开方形下颚",
        faceEn: "shaking open cubic jaw on the Enderman; sweating deadpan pixel eyes on Steve",
        faceZh: "末影人张开方形下颚震动，Steve额角浮现像素冷汗",
        cameraEn: "Dramatic low-angle push-in toward the vibrating Enderman head",
        cameraZh: "戏剧性低角度仰拍快速推向震动的末影人头部",
        hailuoTag: "[Push in, Shake]",
        sfx: "entity.enderman.stare 标志性对视低吼音效",
        caption: "坏了，忘记不能看它眼睛了"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn:
          "purple square portal particles pop as the Enderman vanishes and reappears calmly perched on top of Steve's oak cabin roof, still politely holding the stolen 16x16x16 Grass Block",
        actionZh:
          "紫色正方形粒子炸开，末影人瞬间消失又安静地出现在橡木屋顶最高处，怀里依然端端正正抱着那块偷来的16x16x16草方块",
        faceEn: "calm glowing purple 3x1 pixel eyes looking down from the roof",
        faceZh: "屋顶上末影人恢复平静的紫红3x1像素眼低头俯视",
        cameraEn: "Crane tilt-up to the cabin roof matching the moonlit palette of Shot 1",
        cameraZh: "摇镜仰拍屋顶剪影，与首镜月夜色调无缝衔接",
        hailuoTag: "[Tilt up]",
        sfx: "entity.enderman.teleport 瞬移波普声",
        caption: "礼貌怪盗：只拿一块，绝不多拿"
      }
    ]
  },
  "axolotl-rainy-shelter": {
    titleZh: "雨夜收留粉红美西螈",
    titleEn: "Rainy Night Pink Voxel Axolotl Rescue",
    defaultRig: "alex-slim",
    defaultShader: "bsl-sunlight",
    featuredObject: "Pink Voxel Axolotl + Voxel Lantern + Glass Tank Block",
    subjectEn:
      "a cozy Minecraft character in a pastel 3D hoodie skin shell and a tiny leucistic pastel-pink voxel Axolotl with 3D pixel external gill fronds on a rainy cobblestone street",
    subjectZh:
      "穿奶油抹茶3D立体卫衣皮肤层的《我的世界》小人与长着3D像素外鳃羽冠的粉红像素美西螈，身处雨夜圆石街道",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn:
          "vertical blue pixel rain streaks splash into square water droplets around a tiny pastel-pink voxel Axolotl shivering beside a cobblestone step",
        actionZh:
          "垂直落下的蓝色像素雨丝在圆石台阶旁溅起正方形水花粒子，一只小小的粉红像素美西螈缩在角落轻轻抖动外鳃",
        faceEn: "wide teary 1x1 dark pixel eyes on the pink voxel Axolotl",
        faceZh: "粉红美西螈呈现湿漉漉的1x1像素小眼神",
        cameraEn: "Low-angle macro close-up at puddle level with shallow depth of field",
        cameraZh: "贴地水洼高度微距特写，浅景深凸显像素雨滴颗粒",
        hailuoTag: "[Push in]",
        sfx: "weather.rain 柔和像素雨声 + 美西螈轻叫声",
        caption: "雨夜路边捡到一只稀有粉红美西螈"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn:
          "the hoodie avatar kneels with a clean 90-degree blocky knee bend and lowers a glowing warm 6x9x6 voxel Lantern beside the pink Axolotl, casting golden light across the wet 16x16 cobblestone texels",
        actionZh:
          "卫衣小人以干净的90度方块屈膝姿态蹲下，用3x4平头方手将一盏温暖发光的6x9x6像素灯笼放到美西螈身旁，金黄暖光瞬间驱散冷蓝雨色",
        faceEn: "gentle warm 2x1 pixel smile on the hoodie avatar",
        faceZh: "卫衣小人8x8像素脸浮现温柔微笑",
        cameraEn: "Side-profile medium close-up capturing the warm lantern glow meeting the cool rain",
        cameraZh: "侧面中近景，捕捉暖金灯笼光与冷蓝雨夜的冷暖光影交汇",
        hailuoTag: "[Static shot]",
        sfx: "block.lantern.place 温暖金属轻响",
        caption: "别怕，跟我回方块小屋吧"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn:
          "inside a warm oak cabin, the pink voxel Axolotl swims happily inside a 16x16x16 clear pixel-bordered glass aquarium block illuminated by sea lanterns",
        actionZh:
          "温暖的橡木屋内，粉红像素美西螈在海晶灯照亮的16x16x16带像素边框透明玻璃水族箱方块里欢快摆尾游动",
        faceEn: "happy curved pixel smile on the Axolotl as red square heart particles pop above the water",
        faceZh: "美西螈露出开心像素笑脸，水面冒出红色正方形爱心粒子",
        cameraEn: "Front macro tracking shot through the crisp pixel-framed glass block",
        cameraZh: "透过清晰像素边框玻璃方块的正面微距跟拍",
        hailuoTag: "[Pan left]",
        sfx: "entity.axolotl.idle_water 清脆水泡咕噜声",
        caption: "给它搭了一个专属海晶灯生态缸"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn:
          "the hoodie avatar rests her 8x8x8 cubic head on her flat 3x4 square hands at the desk, watching the pink Axolotl float peacefully as rain falls outside the window",
        actionZh:
          "卫衣小人双侧3x4平头方手托着8x8x8立方体脑袋趴在桌前，静静看着水族箱里的粉红美西螈，窗外像素细雨潺潺",
        faceEn: "synchronized relaxed pixel eyes on both the avatar and the Axolotl",
        faceZh: "一人一宠同步呈现放松治愈的像素眼神",
        cameraEn: "Slow pull-back to a cozy isometric window frame for seamless loop replay",
        cameraZh: "缓慢拉远至温馨等距窗景构图，实现无缝循环播放",
        hailuoTag: "[Pull out]",
        sfx: "原版磁带 C418 风格轻柔钢琴尾音",
        caption: "外面的雨再大，小方块里永远温暖"
      }
    ]
  }
};

const SHADER_TAIL_EN = {
  "bsl-sunlight":
    "Minecraft BSL / Complementary Shaders volumetric lighting, warm block-light bounce, crisp unfiltered nearest-neighbor 16x16 pixel textures, sharp 90-degree voxel corners",
  "bare-bones-trailer":
    "Official Minecraft Trailer and Bare Bones texture pack look, vibrant clean 16x16 pixel blocks, Fresh Animations expressive pixel eyes, bright global illumination",
  "vanilla-crisp":
    "authentic Vanilla Minecraft Java Edition look, unfiltered nearest-neighbor 16x16 pixel-art textures, crisp directional block-face shading",
  "rtx-emissive":
    "Minecraft RTX path-traced voxel lighting, emissive glowing ore and torch light reflecting on crisp 16x16 nearest-neighbor pixel blocks"
};

const SHADER_TAIL_ZH = {
  "bsl-sunlight":
    "Minecraft BSL体积光影渲染，温暖方块光源漫反射，清晰无模糊的16x16邻近采样像素贴图，90度锋利直角体素边缘",
  "bare-bones-trailer":
    "Minecraft官方宣传片Bare Bones高饱和纯净像素画风，Fresh Animations灵动像素眼，明亮全局光照",
  "vanilla-crisp":
    "纯正《我的世界》Java原版渲染质感，无滤镜16x16邻近采样像素贴图，经典方块六面明暗阶梯",
  "rtx-emissive":
    "Minecraft RTX光线追踪体素光影，矿石与火把自发光照亮清晰的16x16像素方格表面"
};

const NEGATIVE_EN =
  "human fingers, five fingers, realistic human hands, blurry bilinear textures, smudged pixel art, Roblox cylindrical barrel head, Lego top head studs, Lego C-shaped claw hands, smooth cylindrical metal sword/pickaxe, 3D protruding human nose, rubbery noodle limbs, watermark";

const NEGATIVE_ZH =
  "人类五指，真实人手，贴图模糊涂抹，双线性插值糊化，Roblox圆桶头，乐高头顶圆凸粒，乐高C型夹爪手，圆滑金属剑刃与圆棍镐柄，3D凸起真人鼻子，橡胶面条状弯曲四肢，水印";

function printHelp() {
  console.log(`Usage: node scripts/shot_compiler.mjs [options]

Compile a 9:16 Minecraft-style voxel storyboard and model-specific I2V/T2V prompts.

Options:
  --template <id>    Story template: diamond-creeper-ambush | cozy-lantern-build |
                     pro-builder-vs-noob-tnt | redstone-chain-asmr |
                     enderman-block-heist | axolotl-rainy-shelter (default: diamond-creeper-ambush)
  --duration <sec>   15 (4 shots) or 30 (8 shots) (default: 15)
  --engine <id>      Target model: kling | seedance | hailuo | wan | sora | runway (default: kling)
  --rig <id>         Rig override: steve-wide | alex-slim | mob-quadruped | mob-enderman
  --shader <id>      Shader override: bsl-sunlight | bare-bones-trailer | vanilla-crisp | rtx-emissive
  --lang <code>      Output language: en | zh | zh-tw | ja | ko | es | fr | de | pt | ru | zh-en (default: en)
  --json             Output structured JSON
  --help             Show this help message`);
}

const SUPPORTED_LANGS = new Set(["en", "zh", "zh-tw", "ja", "ko", "es", "fr", "de", "pt", "ru", "zh-en"]);

function normalizeLang(code = "en") {
  const clean = String(code || "en").toLowerCase().trim();
  if (clean === "zh-cn") return "zh";
  if (clean === "pt-br") return "pt";
  return SUPPORTED_LANGS.has(clean) ? clean : "en";
}

const STORY_HEADERS = {
  en: "9:16 Minecraft Storyboard",
  zh: "9:16 Minecraft 竖屏分镜表",
  "zh-tw": "9:16 Minecraft 直式分鏡表",
  ja: "9:16 Minecraft ショート動画絵コンテ",
  ko: "9:16 Minecraft 쇼츠 스토리보드",
  es: "Storyboard Vertical 9:16 de Minecraft",
  fr: "Storyboard Vertical 9:16 Minecraft",
  de: "9:16 Minecraft-Kurzvideo-Storyboard",
  pt: "Storyboard Vertical 9:16 de Minecraft",
  ru: "Раскадровка 9:16 для Minecraft-видео",
  "zh-en": "9:16 Minecraft Storyboard / 竖屏分镜表"
};

export function parseArgs(argv) {
  const opts = {
    template: "diamond-creeper-ambush",
    duration: 15,
    engine: "kling",
    rig: "",
    shader: "",
    lang: "en",
    json: false,
    help: false
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--help" || arg === "-h") opts.help = true;
    else if (arg === "--json") opts.json = true;
    else if (arg === "--template" && argv[i + 1]) opts.template = argv[++i];
    else if (arg === "--duration" && argv[i + 1]) opts.duration = Number(argv[++i]) || 15;
    else if (arg === "--engine" && argv[i + 1]) opts.engine = argv[++i].toLowerCase();
    else if (arg === "--rig" && argv[i + 1]) opts.rig = argv[++i];
    else if (arg === "--shader" && argv[i + 1]) opts.shader = argv[++i];
    else if (arg === "--lang" && argv[i + 1]) opts.lang = normalizeLang(argv[++i]);
  }
  return opts;
}

function buildEnginePrompts(shot, tpl, engine, shaderKey) {
  const shEn = SHADER_TAIL_EN[shaderKey] || SHADER_TAIL_EN["bsl-sunlight"];
  const shZh = SHADER_TAIL_ZH[shaderKey] || SHADER_TAIL_ZH["bsl-sunlight"];

  const firstFrameEn = `9:16 vertical keyframe. ${tpl.subjectEn}. Scene & action setup: ${shot.actionEn}. Expression: ${shot.faceEn}. Framing: ${shot.cameraEn}. Style lock: ${shEn}, fingerless flat square pixel-block hands, no human fingers, no Roblox cylinder head, no Lego studs.`;
  const firstFrameZh = `9:16竖屏首帧定格图。${tpl.subjectZh}。画面定格：${shot.actionZh}。面部贴图：${shot.faceZh}。机位：${shot.cameraZh}。画风锁定：${shZh}，平头正方形像素手截面（无人类五指、无Roblox圆桶头、无乐高凸粒）。`;

  let i2vPromptEn = "";
  let i2vPromptZh = "";

  if (engine === "hailuo") {
    i2vPromptEn = `${shot.hailuoTag} ${tpl.subjectEn} ${shot.actionEn}. Facial detail: ${shot.faceEn}. Rigid mechanical shoulder/hip pivots, ${shEn}, no human fingers, no blurry textures.`;
    i2vPromptZh = `${shot.hailuoTag} 【海螺Director I2V】${tpl.subjectZh}，${shot.actionZh}。面部表现：${shot.faceZh}。刚性转轴摆动，${shZh}，严禁人类手指与贴图糊化。`;
  } else if (engine === "seedance" || engine === "jimeng") {
    i2vPromptEn = `[Seedance/Jimeng I2V] ${shot.cameraEn}. ${tpl.subjectEn} ${shot.actionEn}, ${shot.faceEn}. Crisp cubic voxel motion, ${shEn}.`;
    i2vPromptZh = `【即梦Seedance I2V】${shZh}，${shot.cameraZh}。画面中${tpl.subjectZh}，${shot.actionZh}，${shot.faceZh}。动作干脆利落有积木定格感，保持16x16清晰像素网格。`;
  } else if (engine === "wan") {
    i2vPromptEn = `9:16 vertical video, ${shEn}. ${tpl.subjectEn} ${shot.actionEn}. ${shot.faceEn}. Camera: ${shot.cameraEn}. Rigid blocky limbs, fingerless flat square hands.`;
    i2vPromptZh = `【通义万相Wan I2V】9:16竖屏，${shZh}。${tpl.subjectZh}，${shot.actionZh}，${shot.faceZh}。运镜：${shot.cameraZh}。保持刚性方柱四肢与平头正方形像素手。`;
  } else if (engine === "sora" || engine === "runway") {
    i2vPromptEn = `Camera: ${shot.cameraEn}. Subject: ${tpl.subjectEn}. Action: ${shot.actionEn}; ${shot.faceEn}. Constraint: ${shEn}; limbs remain strictly rectangular prisms with mechanical hinge pivots and zero soft-body bending.`;
    i2vPromptZh = `【${engine.toUpperCase()} I2V】机位：${shot.cameraZh}。主体：${tpl.subjectZh}。动作：${shot.actionZh}；${shot.faceZh}。约束：${shZh}，四肢严格保持长方体刚性转轴运动。`;
  } else {
    // Default: Kling (可灵)
    i2vPromptEn = `[Kling I2V] ${tpl.subjectEn}, ${shot.actionEn}. Face: ${shot.faceEn}. Camera: ${shot.cameraEn}. Rigid blocky joints, ${shEn}, no human fingers, no Lego studs.`;
    i2vPromptZh = `【可灵Kling I2V】${tpl.subjectZh}，${shot.actionZh}，${shot.faceZh}。运镜：${shot.cameraZh}。刚性方块关节，${shZh}，严禁长出真人手指或出现贴图模糊。`;
  }

  return { firstFrameEn, firstFrameZh, i2vPromptEn, i2vPromptZh };
}

export function compileStoryboard(rawOpts = {}) {
  const tplKey = TEMPLATES[rawOpts.template] ? rawOpts.template : "diamond-creeper-ambush";
  const tpl = TEMPLATES[tplKey];
  const duration = rawOpts.duration === 30 ? 30 : 15;
  const engine = rawOpts.engine || "kling";
  const rig = rawOpts.rig || tpl.defaultRig;
  const shader = rawOpts.shader || tpl.defaultShader;

  const baseShots = tpl.shots;
  const expanded = duration === 30 ? [...baseShots, ...baseShots] : baseShots;
  const stepSec = duration / expanded.length;

  const shots = expanded.map((sh, idx) => {
    const t0 = (idx * stepSec).toFixed(1);
    const t1 = ((idx + 1) * stepSec).toFixed(1);
    const prompts = buildEnginePrompts(sh, tpl, engine, shader);
    return {
      index: idx + 1,
      timeWindow: `${t0}s–${t1}s`,
      role: sh.role,
      actionEn: sh.actionEn,
      actionZh: sh.actionZh,
      faceEn: sh.faceEn,
      faceZh: sh.faceZh,
      cameraEn: sh.cameraEn,
      cameraZh: sh.cameraZh,
      sfx: sh.sfx,
      caption: sh.caption,
      ...prompts,
      negativePromptEn: NEGATIVE_EN,
      negativePromptZh: NEGATIVE_ZH
    };
  });

  return {
    template: tplKey,
    titleZh: tpl.titleZh,
    titleEn: tpl.titleEn,
    duration,
    aspectRatio: "9:16",
    engine,
    rig,
    shader,
    featuredObject: tpl.featuredObject,
    shotCount: shots.length,
    shots
  };
}

function formatStoryboardMarkdown(plan, rawLang) {
  const lang = normalizeLang(rawLang);
  const useZh = lang === "zh" || lang === "zh-tw" || lang === "zh-en";
  const useEn = lang !== "zh";
  const hdr = STORY_HEADERS[lang] || STORY_HEADERS.en;
  const lines = [];
  lines.push(`# ${hdr}: ${useZh ? `${plan.titleZh} (${plan.titleEn})` : plan.titleEn}`);
  lines.push("");
  lines.push(
    `- **Template**: \`${plan.template}\` · **Engine**: \`${plan.engine}\` · **Duration**: \`${plan.duration}s\` (\`${plan.shotCount}\` shots, \`${plan.aspectRatio}\`)`
  );
  lines.push(`- **Pixel Rig**: \`${plan.rig}\` · **Shader**: \`${plan.shader}\` · **Featured Voxel Objects**: \`${plan.featuredObject}\``);
  lines.push("");
  lines.push("| Shot | Time | Role | Single Voxel Action | Audio & Caption |");
  lines.push("| :---: | :---: | --- | --- | --- |");
  for (const s of plan.shots) {
    const act = useZh ? s.actionZh : s.actionEn;
    lines.push(`| 0${s.index} | \`${s.timeWindow}\` | ${s.role} | ${act} | ${s.sfx} · ${s.caption} |`);
  }
  lines.push("");

  for (const s of plan.shots) {
    lines.push(`## Shot 0${s.index} (${s.timeWindow}) · ${s.role}`);
    lines.push("");
    if (useEn) {
      lines.push("- **First-Frame Prompt (EN)**:");
      lines.push(`  \`${s.firstFrameEn}\``);
      lines.push("- **Motion Prompt (EN)**:");
      lines.push(`  \`${s.i2vPromptEn}\``);
    }
    if (useZh) {
      lines.push("- **首帧画面提示词 (ZH)**:");
      lines.push(`  \`${s.firstFrameZh}\``);
      lines.push("- **图生视频动态词 (ZH)**:");
      lines.push(`  \`${s.i2vPromptZh}\``);
    }
    lines.push(`- **Negative Prompt**: \`${lang === "zh" ? s.negativePromptZh : s.negativePromptEn}\``);
    lines.push("");
  }

  return lines.join("\n");
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1];
if (isMain) {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) {
    printHelp();
    process.exit(0);
  }
  const plan = compileStoryboard(opts);
  if (opts.json) {
    console.log(JSON.stringify(plan, null, 2));
  } else {
    console.log(formatStoryboardMarkdown(plan, opts.lang));
  }
}
