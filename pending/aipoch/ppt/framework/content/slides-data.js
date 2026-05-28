/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                              ║
 * ║   📝 幻灯片内容配置文件                                                        ║
 * ║   修改演示内容请编辑此文件！                                                    ║
 * ║                                                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * 基本配置：
 * - badge: 顶部徽章 { icon, text }
 * - title: 标题 { text, gradient? }
 * - subtitle: 副标题（可选）
 * - clickHint: 底部提示文字（可选）
 * - defaultAnimation: 本页所有元素的默认动画（可选）
 * - elements: 内容元素数组，每个元素需要指定 step 和 type
 * 
 * 可用组件类型：
 * - comparison: 对比卡片
 * - terminal: 终端代码块
 * - quote: 引用块
 * - assumptions: 假设网格
 * - timeline: 时间线
 * - stats: 统计数字
 * - valueCards: 价值卡片
 * - competitionBox: 竞争分析框
 * - strategyBox: 战略框
 * - ending: 结束页
 * 
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║   🎬 动画配置                                                                 ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * 优先级：element.animation > slide.defaultAnimation > 组件默认动画
 * 
 * 动画预设（preset）：
 * - fadeIn:     淡入
 * - slideUp:    从下方滑入（默认）
 * - slideDown:  从上方滑入
 * - slideLeft:  从右侧滑入
 * - slideRight: 从左侧滑入
 * - scaleIn:    缩放进入
 * - zoomIn:     放大进入
 * - flipIn:     翻转进入
 * 
 * 配置方式：
 * 
 * 1. Slide 级别（本页所有元素默认）:
 *    {
 *        defaultAnimation: { preset: 'slideUp', duration: 500 },
 *        elements: [...]
 *    }
 * 
 * 2. Element 级别（单个元素）:
 *    { step: 1, type: "quote", animation: { preset: "scaleIn", duration: 800, delay: 200 } }
 * 
 * 3. 简写形式:
 *    { step: 1, type: "quote", animation: "scaleIn" }
 * 
 * 可配置参数：
 * - preset:   动画预设名称
 * - duration: 动画时长（毫秒）
 * - delay:    动画延迟（毫秒）
 * - easing:   缓动函数（如 "ease-out", "cubic-bezier(0.4, 0, 0.2, 1)"）
 * - stagger:  列表项依次延迟间隔（毫秒，仅对 timeline/valueCards/stats 等列表组件有效）
 */

const SLIDES = [
    // ==================== 幻灯片 1: 封面 + 范式转移 ====================
    {
        badge: { icon: "✦", text: "AI STRATEGY 2026" },
        title: { text: "范式转移", gradient: true },
        subtitle: "从「石油时代」到「智能涌现」的战略重构",
        clickHint: "点击开启探索",
        elements: [
            {
                step: 1,
                type: "comparison",
                style: "width: 90%; margin-bottom: 2vmin;",
                left: {
                    icon: "⬡",
                    title: "19世纪：石油革命",
                    items: [
                        "马车 → 汽车 (动力重构)",
                        "人力 → 机械力 (效率跃迁)",
                        "局部能源 → 全球电网 (基础设施)"
                    ]
                },
                right: {
                    icon: "✦",
                    title: "21世纪：AI革命",
                    items: [
                        "人力思考 → AI协同 (认知重构)",
                        "局部智能 → 泛在智能 (决策跃迁)",
                        "固定流程 → 自适应系统 (基础设施)"
                    ]
                }
            },
            {
                step: 2,
                type: "terminal",
                style: "max-width: 600px; box-shadow: var(--shadow-lg); margin-bottom: 2vmin;",
                content: [
                    { type: "prompt", text: "AI_STRATEGY > " },
                    { type: "text", text: "Paradigm_Shift = " },
                    { type: "highlight", text: "REDEFINE_ASSUMPTIONS" },
                    { type: "text", text: " + " },
                    { type: "highlight", text: "REINVENT_WORKFLOW" },
                    { type: "cursor" }
                ]
            },
            {
                step: 3,
                type: "quote",
                style: "border-left: 4px solid var(--accent-coral);",
                text: "“不是在旧赛道上跑得更快，而是切换到完全不同的维度。”",
                textStyle: "font-size: clamp(1.2rem, 2.8vmin, 1.8rem); font-weight: 600;",
                author: { icon: "✦", text: "Paradigm Shift" }
            }
        ]
    },

    // ==================== 幻灯片 2: AI打破假设 ====================
    {
        badge: { icon: "✧", text: "BREAKING LIMITS" },
        title: { text: "AI：打破不可能边界" },
        clickHint: "点击解构传统假设",
        elements: [
            {
                step: 1,
                type: "assumptions",
                style: "gap: 2.5vmin; margin-bottom: 3vmin;",
                revealStep: 2,
                items: [
                    { old: "✕ 创意是人类最后的堡垒", new: "→ 多模态生成 (AIGC) 爆发" },
                    { old: "✕ 复杂决策必须依赖直觉", new: "→ 数据驱动的推理与规划" },
                    { old: "✕ 个性化服务 = 高人力成本", new: "→ 规模化的「千人千面」" },
                    { old: "✕ 知识获取存在天然壁垒", new: "→ 语义搜索与实时知识合成" }
                ]
            },
            {
                step: 3,
                type: "quote",
                style: "background: var(--bg-tertiary);",
                text: "「当假设被打破，边界即成为新的起跑线」",
                gradient: true,
                author: { icon: "✦", text: "The New Reality" }
            }
        ]
    },

    // ==================== 幻灯片 3: 2026产品战略 ====================
    {
        badge: { icon: "◈", text: "PRODUCT EVOLUTION" },
        title: { text: "2026：AI产品演进路径" },
        clickHint: "点击查看进化阶段",
        elements: [
            {
                step: 1,
                type: "timeline",
                style: "margin-bottom: 3vmin;",
                items: [
                    { activeStep: 1, badge: "Phase 1", icon: "○", title: "对话即产品", desc: "Prompt Engineering", case: "交互重构：NewIdea" },
                    { activeStep: 2, badge: "Phase 2", icon: "◐", title: "知识即产品", desc: "RAG & Knowledge Base", case: "专业深挖：DeepSeek+PubMed" },
                    { activeStep: 3, badge: "Phase 3", icon: "◑", title: "流程即产品", desc: "AI Agents Workflow", case: "效率闭环：Monica / Pollo" },
                    { activeStep: 4, badge: "Phase 4", badgeCurrent: true, icon: "●", iconFilled: true, title: "能力即产品", desc: "Autonomous Skills", case: "终极形态：Claude Code" }
                ]
            },
            {
                step: 5,
                type: "stats",
                items: [
                    { icon: "⚡", value: "AGILE", label: "以周为单位的进化" },
                    { icon: "∞", value: "FLYWHEEL", label: "数据驱动的自增长" },
                    { icon: "◈", value: "NATIVE", label: "原生AI思维重构" }
                ]
            },
            {
                step: 6,
                type: "quote",
                style: "margin-top: 2vmin;",
                text: "“通量解决概率问题，规模化自动一切。”",
                gradient: true,
                author: { text: "劳博 · 2026 战略共识" }
            }
        ]
    },

    // ==================== 幻灯片 4: 人类价值 + 战略 + 结尾 ====================
    {
        badge: { icon: "✦", text: "HUMAN VALUE" },
        title: { text: "回归：AI时代的人类锚点" },
        clickHint: "点击探寻核心价值",
        elements: [
            {
                step: 1,
                type: "valueCards",
                style: "margin-bottom: 3vmin;",
                items: [
                    { activeStep: 1, icon: "✦", title: "意义发现者", desc: "定义「为什么」· 编织叙事 · 建立深层链接" },
                    { activeStep: 2, icon: "◈", title: "责任承担者", desc: "伦理裁决 · 风险把控 · 最终决策背书" },
                    { activeStep: 3, icon: "◇", title: "体验承载者", desc: "情感共振 · 审美直觉 · 创造独特记忆" }
                ]
            },
            {
                step: 4,
                type: "competitionBox",
                style: "margin-top: 2vmin;",
                title: "当生产力不再是瓶颈，竞争的核心将转向：",
                items: ["品牌叙事 (Brand Story)", "情感连接 (Empathy)", "社群共识 (Community)"],
                conclusion: "意义 (Meaning) > 效率 (Efficiency)"
            },
            {
                step: 5,
                type: "strategyBox",
                style: "margin-top: 2vmin; border: 1px solid var(--border-strong);",
                title: "解螺旋 2026 核心战略",
                items: [
                    { type: "wrong", text: "不做「更好的马车」(旧模式优化)" },
                    { type: "wrong", text: "也不仅是「造汽车」(工具提供商)" },
                    { type: "right", text: "我们定义「如何驾驶」(赋能与教育)" }
                ],
                final: { arrow: "➔", text: "「教你用 AI 重新定义科研」" }
            },
            {
                step: 6,
                type: "ending",
                style: "margin-top: 3vmin;",
                icon: "✦",
                message: "从范式转移到价值回归",
                thanks: "THANKS FOR WATCHING"
            }
        ]
    }
];
