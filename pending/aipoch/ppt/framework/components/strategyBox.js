/**
 * PPT Framework - 战略框组件
 * 
 * 展示战略选择、对错对比
 */

const strategyBox = {
    meta: {
        name: 'strategyBox',
        description: '战略框',
        defaultAnimation: { preset: 'slideUp', duration: 500 }
    },

    render(data, slideData = {}) {
        const anim = Registry.resolveAnimation(data, slideData);
        const combinedStyle = [anim.style, data.style].filter(Boolean).join('; ');
        const hideStepAttr = data.hideStep ? ` data-hide-step="${data.hideStep}"` : '';
        
        return `
            <div class="strategy-box ${anim.className}" data-step="${data.step}"${hideStepAttr} style="${combinedStyle}">
                <h3><span class="claude-icon">✶</span> ${data.title}</h3>
                ${data.items.map(item => `
                    <div class="strategy-item ${item.type}">
                        <span class="strategy-icon">${item.type === 'wrong' ? '×' : '✓'}</span>
                        <span>${item.text}</span>
                    </div>
                `).join('')}
                <div class="strategy-final">
                    <div class="icon-arrow-right">${data.final.arrow}</div>
                    <p>${data.final.text}</p>
                </div>
            </div>`;
    }
};

/**
 * 注册组件
 */
function registerStrategyBox() {
    if (typeof Registry !== 'undefined') {
        Registry.registerComponent('strategyBox', strategyBox);
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { strategyBox, registerStrategyBox };
} else {
    window.StrategyBoxComponent = { strategyBox, registerStrategyBox };
}
