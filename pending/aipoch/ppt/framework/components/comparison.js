/**
 * PPT Framework - 对比卡片组件
 * 
 * 左右对比布局，适合展示新旧对比、前后变化
 */

const comparison = {
    meta: {
        name: 'comparison',
        description: '对比卡片',
        defaultAnimation: { preset: 'slideUp', duration: 600 }
    },

    render(data, slideData = {}) {
        const anim = Registry.resolveAnimation(data, slideData);
        const combinedStyle = [anim.style, data.style].filter(Boolean).join('; ');
        const hideStepAttr = data.hideStep ? ` data-hide-step="${data.hideStep}"` : '';
        
        return `
            <div class="comparison ${anim.className}" data-step="${data.step}"${hideStepAttr} style="${combinedStyle}">
                <div class="comparison-card">
                    <h4><span class="icon-circle">${data.left.icon}</span> ${data.left.title}</h4>
                    <ul class="comparison-list">
                        ${data.left.items.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
                <div class="comparison-card">
                    <h4><span class="icon-circle filled">${data.right.icon}</span> ${data.right.title}</h4>
                    <ul class="comparison-list">
                        ${data.right.items.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            </div>`;
    }
};

/**
 * 注册组件
 */
function registerComparison() {
    if (typeof Registry !== 'undefined') {
        Registry.registerComponent('comparison', comparison);
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { comparison, registerComparison };
} else {
    window.ComparisonComponent = { comparison, registerComparison };
}
