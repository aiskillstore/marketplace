/**
 * PPT Framework - 组件注册中心
 * 
 * 提供组件、动画预设的统一注册和获取接口
 * 支持插件化扩展，新组件只需调用 register 方法即可自动集成
 */

const Registry = {
    // 已注册的组件
    _components: {},
    
    // 已注册的动画预设
    _animationPresets: {},
    
    // 组件默认动画配置
    _componentDefaults: {},

    /**
     * 注册组件
     * @param {string} name - 组件名称（如 'comparison', 'terminal'）
     * @param {Object} config - 组件配置
     * @param {Function} config.render - 渲染函数 (data, slideData) => HTMLString
     * @param {Object} config.meta - 组件元数据
     * @param {Object} config.meta.defaultAnimation - 默认动画配置
     */
    registerComponent(name, config) {
        if (!name || typeof name !== 'string') {
            console.error('Registry: Component name must be a non-empty string');
            return;
        }
        if (!config.render || typeof config.render !== 'function') {
            console.error(`Registry: Component "${name}" must have a render function`);
            return;
        }
        
        this._components[name] = config.render;
        
        // 存储默认动画配置
        if (config.meta && config.meta.defaultAnimation) {
            this._componentDefaults[name] = config.meta.defaultAnimation;
        }
        
        console.log(`Registry: Component "${name}" registered`);
    },

    /**
     * 获取组件渲染器
     * @param {string} name - 组件名称
     * @returns {Function|null} 渲染函数或 null
     */
    getComponent(name) {
        return this._components[name] || null;
    },

    /**
     * 获取所有已注册组件名称
     * @returns {string[]}
     */
    getComponentNames() {
        return Object.keys(this._components);
    },

    /**
     * 注册动画预设
     * @param {string} name - 预设名称（如 'fadeIn', 'slideUp'）
     * @param {Object} config - 预设配置
     * @param {string} config.transform - CSS transform 值
     * @param {number} config.initialOpacity - 初始透明度
     */
    registerAnimationPreset(name, config) {
        if (!name || typeof name !== 'string') {
            console.error('Registry: Animation preset name must be a non-empty string');
            return;
        }
        
        this._animationPresets[name] = config;
    },

    /**
     * 获取动画预设
     * @param {string} name - 预设名称
     * @returns {Object|null}
     */
    getAnimationPreset(name) {
        return this._animationPresets[name] || null;
    },

    /**
     * 获取所有动画预设
     * @returns {Object}
     */
    getAnimationPresets() {
        return { ...this._animationPresets };
    },

    /**
     * 获取组件默认动画配置
     * @param {string} componentName - 组件名称
     * @returns {Object}
     */
    getComponentDefault(componentName) {
        return this._componentDefaults[componentName] || { preset: 'slideUp', duration: 500 };
    },

    /**
     * 批量注册动画预设
     * @param {Object} presets - 预设对象 { name: config, ... }
     */
    registerAnimationPresets(presets) {
        Object.entries(presets).forEach(([name, config]) => {
            this.registerAnimationPreset(name, config);
        });
    },

    /**
     * 检查组件是否已注册
     * @param {string} name - 组件名称
     * @returns {boolean}
     */
    hasComponent(name) {
        return name in this._components;
    },

    /**
     * 检查动画预设是否已注册
     * @param {string} name - 预设名称
     * @returns {boolean}
     */
    hasAnimationPreset(name) {
        return name in this._animationPresets;
    },

    /**
     * 解析动画配置
     * 优先级：element.animation > slide.defaultAnimation > componentDefaults
     * @param {Object} elementData - 元素数据
     * @param {Object} slideData - 幻灯片数据
     * @returns {Object} { className, style, stagger }
     */
    resolveAnimation(elementData, slideData = {}) {
        const componentType = elementData.type;
        
        // 1. 获取组件默认配置
        const componentDefault = this.getComponentDefault(componentType);
        
        // 2. 合并配置（优先级：element > slide > component default）
        const slideDefault = slideData.defaultAnimation || {};
        const elementAnim = elementData.animation || {};
        
        // 支持简写形式：animation: "scaleIn" 等同于 animation: { preset: "scaleIn" }
        const normalizedElementAnim = typeof elementAnim === 'string' 
            ? { preset: elementAnim } 
            : elementAnim;
        
        const finalConfig = {
            ...componentDefault,
            ...slideDefault,
            ...normalizedElementAnim
        };
        
        // 3. 生成 CSS 类名
        const preset = finalConfig.preset || 'slideUp';
        const className = `anim anim-${preset}`;
        
        // 4. 生成 CSS 变量样式
        const styleVars = [];
        if (finalConfig.duration) {
            styleVars.push(`--anim-duration: ${finalConfig.duration}ms`);
        }
        if (finalConfig.delay) {
            styleVars.push(`--anim-delay: ${finalConfig.delay}ms`);
        }
        if (finalConfig.easing) {
            styleVars.push(`--anim-easing: ${finalConfig.easing}`);
        }
        
        return {
            className,
            style: styleVars.join('; '),
            stagger: finalConfig.stagger || 0
        };
    }
};

// 导出（支持 ES Module 和全局变量）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Registry;
} else {
    window.Registry = Registry;
}
