/**
 * PPT Framework - 假设网格组件
 * 
 * 展示被打破的假设，支持划线 + 揭示新内容的动画
 */

const assumptions = {
    meta: {
        name: 'assumptions',
        description: '假设网格',
        defaultAnimation: { preset: 'fadeIn', duration: 500 }
    },

    render(data, slideData = {}) {
        const anim = Registry.resolveAnimation(data, slideData);
        const hideStepAttr = data.hideStep ? ` data-hide-step="${data.hideStep}"` : '';
        
        return `
            <div class="assumption-grid" data-step="${data.step}"${hideStepAttr} style="${data.style || ''}">
                ${data.items.map((item, idx) => {
                    const delay = anim.stagger * idx;
                    const itemStyle = delay ? `--anim-delay: ${delay}ms` : '';
                    return `
                    <div class="assumption-item">
                        <div class="assumption-old ${anim.className} visible" data-step="${data.step}" data-struck-step="${data.revealStep}" style="${itemStyle}">${item.old}</div>
                        <div class="assumption-new ${anim.className}" data-step="${data.revealStep}" style="${itemStyle}">${item.new}</div>
                    </div>`;
                }).join('')}
            </div>`;
    }
};

/**
 * 注册组件
 */
function registerAssumptions() {
    if (typeof Registry !== 'undefined') {
        Registry.registerComponent('assumptions', assumptions);
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { assumptions, registerAssumptions };
} else {
    window.AssumptionsComponent = { assumptions, registerAssumptions };
}
