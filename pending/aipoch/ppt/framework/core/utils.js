/**
 * PPT Framework - 工具函数
 * 
 * 提供通用的辅助函数
 */

const Utils = {
    /**
     * 合并样式字符串
     * @param {...string} styles - 多个样式字符串
     * @returns {string} 合并后的样式
     */
    mergeStyles(...styles) {
        return styles.filter(Boolean).join('; ');
    },

    /**
     * 转义 HTML 特殊字符
     * @param {string} str - 原始字符串
     * @returns {string} 转义后的字符串
     */
    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    /**
     * 深度合并对象
     * @param {Object} target - 目标对象
     * @param {...Object} sources - 源对象
     * @returns {Object} 合并后的对象
     */
    deepMerge(target, ...sources) {
        if (!sources.length) return target;
        const source = sources.shift();
        
        if (this.isObject(target) && this.isObject(source)) {
            for (const key in source) {
                if (this.isObject(source[key])) {
                    if (!target[key]) Object.assign(target, { [key]: {} });
                    this.deepMerge(target[key], source[key]);
                } else {
                    Object.assign(target, { [key]: source[key] });
                }
            }
        }
        
        return this.deepMerge(target, ...sources);
    },

    /**
     * 检查是否为普通对象
     * @param {*} item - 要检查的值
     * @returns {boolean}
     */
    isObject(item) {
        return item && typeof item === 'object' && !Array.isArray(item);
    },

    /**
     * 防抖函数
     * @param {Function} func - 要防抖的函数
     * @param {number} wait - 等待时间（毫秒）
     * @returns {Function}
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * 节流函数
     * @param {Function} func - 要节流的函数
     * @param {number} limit - 时间限制（毫秒）
     * @returns {Function}
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * 生成唯一 ID
     * @param {string} prefix - ID 前缀
     * @returns {string}
     */
    generateId(prefix = 'ppt') {
        return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    },

    /**
     * 克隆对象（深拷贝）
     * @param {*} obj - 要克隆的对象
     * @returns {*}
     */
    clone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (Array.isArray(obj)) return obj.map(item => this.clone(item));
        
        const cloned = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                cloned[key] = this.clone(obj[key]);
            }
        }
        return cloned;
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Utils;
} else {
    window.Utils = Utils;
}
