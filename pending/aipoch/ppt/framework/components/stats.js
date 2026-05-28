/**
 * PPT Framework - 统计数字组件
 * 
 * 展示关键数据、指标、特点
 */

const stats = {
    meta: {
        name: 'stats',
        description: '统计数字',
        defaultAnimation: { preset: 'slideUp', duration: 400 }
    },

    render(data, slideData = {}) {
        const anim = Registry.resolveAnimation(data, slideData);
        const combinedStyle = [anim.style, data.style].filter(Boolean).join('; ');
        const hideStepAttr = data.hideStep ? ` data-hide-step="${data.hideStep}"` : '';
        const titleHtml = data.title ? `<div class="stats-title">${data.title}</div>` : '';
        
        return `
            <div class="stats-container ${anim.className}" data-step="${data.step}"${hideStepAttr} style="${combinedStyle}">
                ${titleHtml}
                <div class="stats-row">
                    ${data.items.map((item, idx) => {
                        const delay = anim.stagger * idx;
                        const itemStyle = delay ? `--anim-delay: ${delay}ms` : '';
                        return `
                        <div class="stat-item" style="${itemStyle}">
                            <div class="stat-icon-wrapper">
                                <div class="stat-icon claude-icon">${item.icon}</div>
                            </div>
                            <div class="stat-value">${item.value}</div>
                            <div class="stat-label">${item.label}</div>
                        </div>`;
                    }).join('')}
                </div>
            </div>`;
    }
};

/**
 * 注册组件
 */
function registerStats() {
    if (typeof Registry !== 'undefined') {
        Registry.registerComponent('stats', stats);
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { stats, registerStats };
} else {
    window.StatsComponent = { stats, registerStats };
}
