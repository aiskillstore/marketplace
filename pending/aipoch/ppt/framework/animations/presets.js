/**
 * PPT Framework - 动画预设定义
 * 
 * 定义所有可用的动画预设和组件默认动画
 */

// ========== 动画预设 ==========
const ANIMATION_PRESETS = {
    fadeIn:     { transform: 'none', initialOpacity: 0 },
    slideUp:    { transform: 'translateY(30px)', initialOpacity: 0 },
    slideDown:  { transform: 'translateY(-30px)', initialOpacity: 0 },
    slideLeft:  { transform: 'translateX(30px)', initialOpacity: 0 },
    slideRight: { transform: 'translateX(-30px)', initialOpacity: 0 },
    scaleIn:    { transform: 'scale(0.9)', initialOpacity: 0 },
    zoomIn:     { transform: 'scale(0.5)', initialOpacity: 0 },
    flipIn:     { transform: 'perspective(400px) rotateX(-10deg)', initialOpacity: 0 }
};

// ========== 组件默认动画 ==========
const COMPONENT_DEFAULTS = {
    comparison:     { preset: 'slideUp', duration: 600 },
    terminal:       { preset: 'scaleIn', duration: 500 },
    quote:          { preset: 'scaleIn', duration: 400 },
    assumptions:    { preset: 'fadeIn', duration: 500 },
    timeline:       { preset: 'fadeIn', duration: 500, stagger: 100 },
    stats:          { preset: 'slideUp', duration: 400 },
    valueCards:     { preset: 'slideUp', duration: 500, stagger: 150 },
    competitionBox: { preset: 'slideUp', duration: 500 },
    strategyBox:    { preset: 'slideUp', duration: 500 },
    ending:         { preset: 'scaleIn', duration: 600 }
};

/**
 * 注册所有动画预设到 Registry
 */
function registerAnimationPresets() {
    if (typeof Registry !== 'undefined') {
        // 注册动画预设
        Registry.registerAnimationPresets(ANIMATION_PRESETS);
        
        // 注册组件默认动画
        Object.entries(COMPONENT_DEFAULTS).forEach(([name, config]) => {
            Registry._componentDefaults[name] = config;
        });
        
        console.log('AnimationPresets: Registered', Object.keys(ANIMATION_PRESETS).length, 'presets');
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ANIMATION_PRESETS, COMPONENT_DEFAULTS, registerAnimationPresets };
} else {
    window.ANIMATION_PRESETS = ANIMATION_PRESETS;
    window.COMPONENT_DEFAULTS = COMPONENT_DEFAULTS;
    window.registerAnimationPresets = registerAnimationPresets;
}
