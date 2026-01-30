"""
Picture Book Wizard 完整配置数据
将 markdown 规则转换为结构化数据
"""

# ============================================================
# 风格配置 (18 种)
# ============================================================
STYLES = {
    # === I. 核心儿童绘本风格 (7种) ===
    "storybook": {
        "name_cn": "经典绘本",
        "category": "core",
        "keywords": "classic children's storybook illustration, soft rounded shapes, friendly character design, warm inviting colors, clear composition, professional picture book style, gentle lighting, age-appropriate aesthetics",
        "best_for": ["传统故事", "教育内容", "角色叙事"],
        "age_rating": 3,
    },
    "watercolor": {
        "name_cn": "水彩",
        "category": "core",
        "keywords": "soft watercolor illustration, gentle color blending, organic paper texture, delicate brushwork, light and airy, natural color flow, transparent layers, watercolor wash effects",
        "best_for": ["自然场景", "温柔叙事", "情感时刻"],
        "age_rating": 3,
    },
    "gouache": {
        "name_cn": "水粉",
        "category": "core",
        "keywords": "opaque gouache illustration, flat color areas, bold soft colors, clear shapes, matte finish, vibrant controlled palette, painterly texture, clean silhouettes",
        "best_for": ["欢快故事", "文化庆典", "活泼场景"],
        "age_rating": 3,
    },
    "crayon": {
        "name_cn": "蜡笔",
        "category": "core",
        "keywords": "naive crayon illustration, childlike hand-drawn strokes, warm waxy texture, playful imperfect lines, authentic children's drawing style, soft crayon marks, friendly accessible aesthetic",
        "best_for": ["童趣表达", "简单故事", "第一人称叙述"],
        "age_rating": 3,
    },
    "colored-pencil": {
        "name_cn": "彩铅",
        "category": "core",
        "keywords": "gentle colored pencil drawing, soft pencil strokes, delicate color layering, subtle cross-hatching, warm intimate texture, hand-drawn organic quality, fine soft details",
        "best_for": ["安静时刻", "细腻自然", "睡前故事"],
        "age_rating": 4,
    },
    "clay": {
        "name_cn": "黏土",
        "category": "core",
        "keywords": "hand-sculpted claymation style, physical clay textures, fingerprint details visible, matte surface, soft edges, warm color grading, tactile touchable quality, 3D sculpted appearance, soft studio lighting",
        "best_for": ["自然场景", "近距离互动", "温馨故事"],
        "age_rating": 3,
    },
    "paper-cut": {
        "name_cn": "剪纸",
        "category": "core",
        "keywords": "Chinese paper-cut art style, layered paper silhouettes, intricate cut-out patterns, bold red and gold colors, symmetrical design, flat graphic style with depth layers, sharp clean edges, traditional Chinese decorative patterns, shadow layers, folk art aesthetic",
        "best_for": ["节日庆典", "文化教育", "图案学习"],
        "age_rating": 3,
    },

    # === II. 氛围增强风格 (5种) ===
    "dreamy": {
        "name_cn": "梦幻",
        "category": "atmospheric",
        "keywords": "soft dreamy illustration, ethereal lighting, gentle blur effects, pastel color washes, floating weightless elements, magical glow, sparkles and light particles, calm peaceful atmosphere",
        "best_for": ["梦境", "睡前故事", "想象场景"],
        "age_rating": 4,
        "usage_percent": "10-15%",
    },
    "fairytale": {
        "name_cn": "童话",
        "category": "atmospheric",
        "keywords": "whimsical fairytale illustration, magical enchanted elements, soft romantic lighting, decorative storybook borders, traditional fairytale aesthetics, gentle fantasy details, storybook charm",
        "best_for": ["经典童话", "魔法时刻", "特殊场景"],
        "age_rating": 4,
        "usage_percent": "15-20%",
    },
    "collage": {
        "name_cn": "拼贴",
        "category": "atmospheric",
        "keywords": "paper collage illustration, layered textures, mixed media elements, visible paper edges, tactile handmade appearance, crafted overlapping layers, playful composition, artistic cut-outs",
        "best_for": ["创意过程", "艺术主题", "记忆场景"],
        "age_rating": 4,
        "usage_percent": "10-15%",
    },
    "fabric": {
        "name_cn": "布艺",
        "category": "atmospheric",
        "keywords": "textile fabric collage, soft material textures, felt and cotton layers, embroidery stitching details, cozy tactile quality, warm handmade aesthetic, fabric pattern overlays",
        "best_for": ["温馨家庭", "祖孙故事", "舒适环境"],
        "age_rating": 3,
        "usage_percent": "10-20%",
    },
    "felt": {
        "name_cn": "毛毡",
        "category": "atmospheric",
        "keywords": "felt handmade illustration, thick soft felt textures, fuzzy material surface, hand-cut felt shapes, layered dimensional craft, warm cozy aesthetic, playful handmade quality",
        "best_for": ["室内场景", "冬季主题", "安全感叙事"],
        "age_rating": 3,
        "usage_percent": "10-15%",
    },

    # === III. 中国文化风格 (5种) ===
    "ink": {
        "name_cn": "水墨",
        "category": "chinese",
        "keywords": "Chinese ink wash painting for children, gentle flowing brush strokes, soft ink gradients, warm ethereal mist, traditional technique with color accents, watercolor blends, artistic poetic composition",
        "best_for": ["自然意境", "诗意故事", "艺术欣赏"],
        "age_rating": 5,
    },
    "ink-line": {
        "name_cn": "白描",
        "category": "chinese",
        "keywords": "traditional Chinese line art, clean black ink outlines, elegant minimal strokes, white background, simple expressive linework, traditional drawing technique, optional light color fills",
        "best_for": ["书法教育", "简洁构图", "传统艺术"],
        "age_rating": 5,
    },
    "nianhua": {
        "name_cn": "年画",
        "category": "chinese",
        "keywords": "Chinese New Year painting for children, vibrant festive colors, bold outlines, flat color fills, symmetrical joyful composition, auspicious symbols, folk art aesthetic, decorative patterns, celebration atmosphere",
        "best_for": ["春节", "传统节日", "吉祥主题", "文化传承"],
        "age_rating": 3,
    },
    "porcelain": {
        "name_cn": "青花瓷",
        "category": "chinese",
        "keywords": "Chinese blue and white porcelain for children, delicate cobalt blue on white, ceramic glaze texture, soft flowing patterns, traditional motifs simplified, elegant refined aesthetic, child-friendly designs",
        "best_for": ["宁静故事", "文化遗产", "艺术欣赏"],
        "age_rating": 5,
    },
    "shadow-puppet": {
        "name_cn": "皮影",
        "category": "chinese",
        "keywords": "Chinese shadow puppet theater for children, translucent friendly silhouettes, warm gentle backlighting, intricate cut-outs, layered depth, amber orange glow, child-friendly traditional designs, theatrical storytelling",
        "best_for": ["戏剧故事", "光影学习", "表演艺术"],
        "age_rating": 4,
    },

    # === IV. 专业风格 (1种) ===
    "tech": {
        "name_cn": "科技",
        "category": "specialized",
        "keywords": "futuristic children's illustration, soft glowing interfaces, friendly robot designs, colorful holographic elements, clean digital aesthetic with warm touches, child-friendly technology",
        "best_for": ["科技主题", "未来探索", "编程教育"],
        "age_rating": 6,
        "warning": "谨慎使用，可能过于抽象",
    },
}

# ============================================================
# 场景配置 (12 种核心场景)
# ============================================================
SCENES = {
    # === 自然场景 (5种) ===
    "meadow": {
        "name_cn": "草地",
        "category": "nature",
        "elements": "lush green grass meadow, tiny wildflowers scattered, gentle breeze effect, ground-level view, natural daylight, soft grass texture",
        "observable": ["草叶", "野花", "蝴蝶", "露珠", "小石子", "蜜蜂", "蒲公英"],
        "not_observable": ["地下根系", "土壤成分", "地下种子"],
        "characters_cn": ["草", "花", "绿", "地"],
        "mood": "open, fresh, peaceful",
    },
    "pond": {
        "name_cn": "池塘",
        "category": "nature",
        "elements": "crystal clear pond water, mirror-like still water surface, lotus leaves floating, smooth pebbles visible, perfect reflection capability, serene atmosphere",
        "observable": ["水面", "荷叶", "倒影", "小鱼", "蜻蜓", "青蛙", "涟漪"],
        "not_observable": ["深水底部", "水下根系", "鱼卵", "微生物"],
        "characters_cn": ["水", "鱼", "荷", "蛙", "清"],
        "mood": "calm, reflective, serene",
        "special_feature": "reflection",
    },
    "rice-paddy": {
        "name_cn": "稻田",
        "category": "nature",
        "elements": "organized rice paddy rows, green seedlings in shallow water, sky reflections in water, geometric planting pattern, golden hour lighting, agricultural landscape",
        "observable": ["水稻", "田埂", "水面倒影", "白鹭", "农具"],
        "not_observable": ["地下根系", "土壤养分", "种子发芽"],
        "characters_cn": ["田", "稻", "种", "水"],
        "mood": "organized, productive, peaceful",
    },
    "stars": {
        "name_cn": "星空",
        "category": "nature",
        "elements": "deep navy night sky, glowing stars scattered throughout, crescent moon visible, stars at varying depths, magical atmosphere, sense of vastness",
        "observable": ["星星", "月亮", "银河", "流星", "星座轮廓"],
        "not_observable": ["星球表面", "土星环", "星云细节", "遥远星系"],
        "characters_cn": ["星", "月", "天", "夜"],
        "mood": "vast, magical, contemplative",
    },
    "forest": {
        "name_cn": "森林",
        "category": "nature",
        "elements": "giant textured tree trunks, rough bark texture, dappled sunlight filtering through leaves, forest floor details, vertical forest composition, natural woodland atmosphere",
        "observable": ["树皮纹理", "落叶", "蘑菇", "苔藓", "松果", "小鸟", "松鼠"],
        "not_observable": ["年轮(活树)", "内部木纹", "地下根系"],
        "characters_cn": ["树", "林", "叶", "鸟"],
        "mood": "enclosed, natural, mysterious yet safe",
    },

    # === 文化生活场景 (7种) ===
    "kitchen": {
        "name_cn": "厨房",
        "category": "cultural",
        "elements": "warm home kitchen, steaming wok with aromatic food, fresh vegetables on wooden cutting board, traditional Chinese kitchen tools, cozy family cooking atmosphere, warm lighting from above",
        "observable": ["锅碗", "筷子", "蒸汽", "食材", "灶台", "蒸笼", "菜刀"],
        "not_observable": ["食物内部温度", "细菌", "营养成分"],
        "characters_cn": ["锅", "碗", "筷", "饭", "菜", "香"],
        "mood": "warm, familial, aromatic",
    },
    "courtyard": {
        "name_cn": "庭院",
        "category": "cultural",
        "elements": "traditional Chinese courtyard, stone pathways, potted plants, wooden doors, red lanterns, peaceful atmosphere, sky opening above",
        "observable": ["石板路", "花盆", "红灯笼", "木门", "屋檐", "天井"],
        "not_observable": [],
        "characters_cn": ["院", "门", "灯", "家"],
        "mood": "peaceful, culturally rich, intimate",
    },
    "market": {
        "name_cn": "集市",
        "category": "cultural",
        "elements": "bustling Chinese market street, colorful fruit and vegetable stalls, traditional shopfronts, friendly vendors, hanging goods, warm busy atmosphere",
        "observable": ["摊位", "蔬果", "招牌", "人群", "称重器"],
        "not_observable": [],
        "characters_cn": ["买", "卖", "菜", "果"],
        "mood": "bustling, colorful, lively",
    },
    "temple": {
        "name_cn": "寺庙",
        "category": "cultural",
        "elements": "peaceful temple grounds, traditional Chinese architecture, incense smoke, prayer bells, ancient trees, serene spiritual atmosphere",
        "observable": ["香炉", "屋檐", "古树", "石狮", "钟"],
        "not_observable": [],
        "characters_cn": ["庙", "香", "钟", "佛"],
        "mood": "serene, spiritual, ancient",
    },
    "festival": {
        "name_cn": "节庆",
        "category": "cultural",
        "elements": "festive celebration scene, red lanterns everywhere, dragon or lion dance elements, fireworks in sky, happy crowds, traditional decorations, joyful atmosphere",
        "observable": ["灯笼", "烟花", "舞龙舞狮", "对联", "红包"],
        "not_observable": [],
        "characters_cn": ["节", "乐", "红", "福"],
        "mood": "joyful, festive, celebratory",
    },
    "grandma-room": {
        "name_cn": "奶奶房间",
        "category": "cultural",
        "elements": "cozy grandmother's room, wooden furniture, warm lighting, traditional Chinese decor, comfortable bed or chair, family photos, nostalgic warm atmosphere",
        "observable": ["老式家具", "全家福", "针线篮", "茶杯", "老花镜"],
        "not_observable": [],
        "characters_cn": ["奶", "家", "爱", "暖"],
        "mood": "warm, nostalgic, loving",
    },
    "kindergarten": {
        "name_cn": "幼儿园",
        "category": "cultural",
        "elements": "colorful kindergarten classroom, small chairs and tables, children's artwork on walls, toy corners, friendly learning environment, bright cheerful atmosphere",
        "observable": ["小桌椅", "玩具", "画作", "图书角", "滑梯"],
        "not_observable": [],
        "characters_cn": ["学", "玩", "友", "乐"],
        "mood": "cheerful, playful, social",
    },
    "soccer-field": {
        "name_cn": "足球场",
        "category": "cultural",
        "elements": "green grass soccer field, white boundary lines and center circle, goal posts with nets, soccer ball, children in colorful sports uniforms, open sky above, energetic sports atmosphere, dynamic action poses",
        "observable": ["草地", "球门", "足球", "队服", "白线", "球网", "阴影"],
        "not_observable": ["地下灌溉", "草根系统", "球内气压", "肌肉运动"],
        "characters_cn": ["球", "跑", "队", "赢"],
        "mood": "energetic, dynamic, team-oriented",
    },
    "playground": {
        "name_cn": "操场",
        "category": "cultural",
        "elements": "colorful school playground, play equipment with slides and swings, rubber safety ground, children playing together, basketball court lines, school building background, energetic playful atmosphere, bright daylight",
        "observable": ["滑梯", "秋千", "攀爬架", "橡胶地面", "篮球场", "跳绳"],
        "not_observable": ["设备地下固定", "橡胶层结构", "内部安全等级"],
        "characters_cn": ["玩", "友", "乐", "动"],
        "mood": "lively, energetic, social",
    },
}

# ============================================================
# 角色配置 (4 主角 + 支持角色)
# ============================================================
CHARACTERS = {
    # === 主角 ===
    "yueyue": {
        "name_cn": "悦悦",
        "name_meaning": "悦 (yuè) = 喜悦",
        "age": 5,
        "gender": "girl",
        "personality": ["curious", "gentle", "wonder-filled"],
        "anchor": "a 5-year-old Chinese girl named Yueyue with round face, rosy cheeks, bright expressive eyes",
        "signature": {
            "hair": "two pigtails with bright red satin ribbon bows",
            "top": "sunshine yellow knit sweater with ribbed collar",
            "bottom": "medium-wash denim overalls with metal clip straps",
            "shoes": "white canvas slip-on sneakers",
        },
        "build": "chubby preschooler build 105-110cm",
        "best_for": ["自然探索", "温柔学习", "文化传统", "家庭故事"],
    },
    "xiaoming": {
        "name_cn": "小明",
        "name_meaning": "小明 (xiǎomíng) = 小小的光明",
        "age": 6,
        "gender": "boy",
        "personality": ["adventurous", "energetic", "confident"],
        "anchor": "a 6-year-old Chinese boy named Xiaoming with round face, bright smile, curious eyes",
        "signature": {
            "hair": "short neat black hair (2-3cm) with clean side part on left",
            "top": "bright royal blue cotton t-shirt",
            "bottom": "light tan khaki cotton shorts",
            "shoes": "blue and white canvas sneakers with white laces",
        },
        "build": "active athletic build 115-120cm",
        "best_for": ["冒险探索", "运动活动", "问题解决", "户外活动"],
    },
    "meimei": {
        "name_cn": "美美",
        "name_meaning": "美 (měi) = 美丽",
        "age": 4,
        "gender": "girl",
        "personality": ["creative", "imaginative", "artistic"],
        "anchor": "a 4-year-old Chinese girl named Meimei with heart-shaped face, bright expressive eyes, sweet smile",
        "signature": {
            "hair": "long black hair in high ponytail with rainbow pattern plastic hairclip, straight bangs across forehead",
            "top": "pastel pink cotton dress with short puff sleeves and white Peter Pan collar, daisy flower print",
            "bottom": "",  # dress
            "shoes": "white strappy sandals with pink buckles, white ankle socks with lace trim",
        },
        "build": "delicate graceful 100-105cm",
        "best_for": ["艺术创作", "想象游戏", "音乐舞蹈", "色彩学习"],
    },
    "lele": {
        "name_cn": "乐乐",
        "name_meaning": "乐 (lè) = 快乐",
        "age": 3,
        "gender": "boy",
        "personality": ["cheerful", "innocent", "playful"],
        "anchor": "a 3-year-old Chinese boy named Lele with chubby round face, big sparkling eyes, button nose",
        "signature": {
            "hair": "short fluffy black hair (2cm), natural messy-cute style",
            "top": "red and white horizontal striped cotton t-shirt",
            "bottom": "soft royal blue elastic-waist cotton pants",
            "shoes": "tiny red velcro-strap toddler shoes with white rubber soles",
        },
        "build": "chubby toddler 90-95cm",
        "best_for": ["第一次体验", "简单学习", "家庭关爱", "基础认知"],
    },
}

# === 支持角色 ===
SUPPORTING_CHARACTERS = {
    "grandma": {
        "name_cn": "奶奶",
        "anchor": "a kind elderly Chinese grandmother, silver-gray hair in a bun, warm smile, wearing traditional Chinese jacket",
        "signature": {
            "hair": "silver-gray hair neatly tied in low bun",
            "top": "dark blue traditional Chinese jacket with frog buttons",
            "bottom": "loose black cotton pants",
            "shoes": "black cloth shoes with soft soles",
        },
        "relationship": "慈爱、智慧、传统",
    },
    "grandpa": {
        "name_cn": "爷爷",
        "anchor": "a gentle elderly Chinese grandfather, short gray hair, kind eyes, wearing traditional vest",
        "signature": {
            "hair": "short gray hair, slightly balding",
            "top": "beige traditional Chinese vest over white shirt",
            "bottom": "dark gray cotton pants",
            "shoes": "brown leather shoes",
        },
        "relationship": "慈祥、耐心、故事讲述者",
    },
    "mom": {
        "name_cn": "妈妈",
        "anchor": "a young Chinese mother, shoulder-length black hair, gentle smile, wearing casual comfortable clothes",
        "signature": {
            "hair": "shoulder-length black hair, often tied back",
            "top": "soft pink or cream colored blouse",
            "bottom": "comfortable jeans or skirt",
            "shoes": "simple flats",
        },
        "relationship": "温柔、关爱、照顾",
    },
    "dad": {
        "name_cn": "爸爸",
        "anchor": "a young Chinese father, short black hair, warm smile, wearing casual shirt",
        "signature": {
            "hair": "short neat black hair",
            "top": "light blue or white casual button shirt",
            "bottom": "khaki pants",
            "shoes": "casual brown shoes",
        },
        "relationship": "可靠、有趣、保护",
    },
}

# === 动物伙伴 ===
ANIMAL_COMPANIONS = {
    "cat": {
        "name_cn": "小猫",
        "anchor": "a small fluffy orange tabby cat, bright green eyes, pink nose, white paws",
        "signature": {
            "fur": "soft orange tabby fur with darker stripes",
            "eyes": "bright curious green eyes",
            "features": "pink nose, white chest and paws, fluffy tail",
        },
    },
    "dog": {
        "name_cn": "小狗",
        "anchor": "a friendly golden retriever puppy, fluffy golden fur, happy expression, wagging tail",
        "signature": {
            "fur": "soft fluffy golden fur",
            "eyes": "warm brown eyes",
            "features": "floppy ears, black nose, constantly wagging tail",
        },
    },
    "rabbit": {
        "name_cn": "小兔",
        "anchor": "a cute white rabbit with long ears, pink eyes, fluffy cotton tail",
        "signature": {
            "fur": "soft white fluffy fur",
            "eyes": "pink or red gentle eyes",
            "features": "long upright ears, twitching nose, cotton ball tail",
        },
    },
    "chick": {
        "name_cn": "小鸡",
        "anchor": "a tiny yellow chick, fluffy down feathers, small orange beak",
        "signature": {
            "fur": "soft fluffy yellow down",
            "eyes": "small black bead eyes",
            "features": "tiny orange beak and feet",
        },
    },
}

# ============================================================
# 年龄系统
# ============================================================
AGE_SYSTEM = {
    (3, 4): {
        "label": "低龄段",
        "label_en": "Early Childhood",
        "pages": (1, 3),
        "default_pages": 3,
        "sentence_cn": (5, 8),
        "sentence_en": (5, 10),
        "complexity": "simple",
        "learning": ["基础认知", "颜色形状", "感官体验", "安全卫生"],
        "emotions": ["happy", "sad", "surprised"],
        "default_character": "lele",
        "hsk_level": 1,
    },
    (5, 6): {
        "label": "学龄前",
        "label_en": "Preschool",
        "pages": (3, 5),
        "default_pages": 4,
        "sentence_cn": (8, 12),
        "sentence_en": (10, 15),
        "complexity": "simple_narrative",
        "learning": ["基础科学", "基础数学", "社交技能", "情感认知"],
        "emotions": ["happy", "sad", "surprised", "proud", "shy", "curious"],
        "default_character": "yueyue",
        "hsk_level": 2,
    },
    (7, 8): {
        "label": "小学低年级",
        "label_en": "Early Elementary",
        "pages": (5, 7),
        "default_pages": 5,
        "sentence_cn": (12, 15),
        "sentence_en": (15, 20),
        "complexity": "narrative_arc",
        "learning": ["科学方法", "数学逻辑", "历史文化", "品德教育"],
        "emotions": ["complex", "mixed", "empathy"],
        "default_character": "xiaoming",
        "hsk_level": 3,
    },
    (9, 10): {
        "label": "小学高年级",
        "label_en": "Late Elementary",
        "pages": (7, 10),
        "default_pages": 7,
        "sentence_cn": (15, 20),
        "sentence_en": (20, 25),
        "complexity": "complex",
        "learning": ["高级科学", "心理学", "哲学思考", "跨学科"],
        "emotions": ["nuanced", "reflective"],
        "default_character": "xiaoming",
        "hsk_level": 4,
    },
    (11, 12): {
        "label": "初中低年级",
        "label_en": "Early Middle School",
        "pages": (10, 15),
        "default_pages": 10,
        "sentence_cn": (20, 25),
        "sentence_en": (25, 30),
        "complexity": "advanced",
        "learning": ["深度科学", "社会学", "批判思维", "自我认知"],
        "emotions": ["sophisticated"],
        "default_character": "xiaoming",
        "hsk_level": 5,
    },
}

# ============================================================
# 水印防护
# ============================================================
WATERMARK_PREVENTION = {
    "level1": "no watermark, no text, clean image",
    "level2": "clean professional children's book illustration, publication-ready quality, pristine unmarked image, full bleed composition, no watermark, no text overlays, no signatures, no artist marks, no logos, no branding, no copyright symbols, no website URLs, clean professional image",
}

# ============================================================
# 灵魂元素 (Soul)
# ============================================================
SOUL_ELEMENTS = {
    "emotions": {
        "joyful": {"cn": "欢乐", "colors": ["warm-bright", "vibrant"]},
        "calm": {"cn": "平静", "colors": ["serene", "fresh"]},
        "curious": {"cn": "好奇", "colors": ["fresh", "vibrant"]},
        "brave": {"cn": "勇敢", "colors": ["warm-bright", "vibrant"]},
        "warm": {"cn": "温馨", "colors": ["warm-bright", "dreamy"]},
        "wonder": {"cn": "惊奇", "colors": ["dreamy", "vibrant"]},
        "reflective": {"cn": "沉思", "colors": ["serene", "dreamy"]},
    },
    "themes": {
        "growth": {"cn": "成长", "narratives": ["journey", "transform"]},
        "friendship": {"cn": "友谊", "narratives": ["journey", "problem"]},
        "nature": {"cn": "自然", "narratives": ["cycle", "journey"]},
        "family": {"cn": "家庭", "narratives": ["cycle", "problem"]},
        "courage": {"cn": "勇气", "narratives": ["quest", "problem"]},
        "creativity": {"cn": "创意", "narratives": ["transform", "journey"]},
        "discovery": {"cn": "发现", "narratives": ["journey", "quest"]},
    },
    "narratives": {
        "journey": {"cn": "旅程", "pages_min": 3},
        "problem": {"cn": "问题解决", "pages_min": 3},
        "cycle": {"cn": "循环", "pages_min": 3},
        "transform": {"cn": "蜕变", "pages_min": 5},
        "quest": {"cn": "探索", "pages_min": 5},
    },
    "pacing": ["gentle", "lively", "building", "varied"],
    "colors": {
        "warm-bright": {"cn": "温暖明亮", "hex": "#FFD700, #FF6B6B, #FFA500"},
        "fresh": {"cn": "清新", "hex": "#90EE90, #87CEEB, #98FB98"},
        "dreamy": {"cn": "梦幻", "hex": "#DDA0DD, #E6E6FA, #FFB6C1"},
        "vibrant": {"cn": "活力", "hex": "#FF4500, #00CED1, #FFD700"},
        "serene": {"cn": "宁静", "hex": "#B0C4DE, #E0FFFF, #F0FFF0"},
    },
}

# ============================================================
# 故事结构
# ============================================================
STORY_STRUCTURES = {
    3: {
        "name": "Beginning-Middle-End",
        "name_cn": "开始-发展-结束",
        "pages": ["开篇/Setup", "发展/Development", "结局/Resolution"],
    },
    5: {
        "name": "Full Arc",
        "name_cn": "完整弧线",
        "pages": ["引入/Hook", "发现/Discovery", "挑战/Challenge", "成长/Growth", "结局/Resolution"],
    },
    7: {
        "name": "Extended Journey",
        "name_cn": "扩展旅程",
        "pages": ["引入", "探索", "发现", "困难", "尝试", "成功", "总结"],
    },
}

# ============================================================
# CCLP 配置
# ============================================================
CCLP_CONFIG = {
    "version": "4.0",
    "levels": {
        "strict": {
            "name": "严格模式",
            "description": "100% 外观一致，仅表情姿势变化",
            "default": True,
        },
        "moderate": {
            "name": "适度模式",
            "description": "固定面部/发型，服装可根据场景调整",
        },
        "flexible": {
            "name": "灵活模式",
            "description": "仅保留签名特征，允许时间/主题变化",
        },
    },
    "markers": {
        "lock": "[LOCK ESTABLISHED - Page 1]\n[CCLP 4.0 STRICT MODE ACTIVE]",
        "reference": "[CONSISTENCY REFERENCE - Matches Page 1 Lock]\n[CCLP 4.0 STRICT MODE]",
    },
}
