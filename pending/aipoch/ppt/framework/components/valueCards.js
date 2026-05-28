/**
 * PPT Framework - 价值卡片组件
 * 
 * 展示核心价值、关键角色，支持依次激活
 */

const valueCards = {
    meta: {
        name: 'valueCards',
        description: '价值卡片',
        defaultAnimation: { preset: 'slideUp', duration: 500, stagger: 150 }
    },

    render(data, slideData = {}) {
        const anim = Registry.resolveAnimation(data, slideData);
        const combinedStyle = [anim.style, data.style].filter(Boolean).join('; ');
        const hideStepAttr = data.hideStep ? ` data-hide-step="${data.hideStep}"` : '';
        
        return `
            <div class="value-cards ${anim.className}" data-step="${data.step}"${hideStepAttr} style="${combinedStyle}">
                ${data.items.map((item, idx) => {
                    const delay = anim.stagger * idx;
                    const itemStyle = delay ? `--anim-delay: ${delay}ms` : '';
                    const activeStepAttr = item.activeStep ? ` data-active-step="${item.activeStep}"` : '';
                    return `
                    <div class="value-card"${activeStepAttr} style="${itemStyle}">
                        <div class="value-card-icon claude-icon">${item.icon}</div>
                        <h4>${item.title}</h4>
                        <p>${item.desc}</p>
                    </div>`;
                }).join('')}
            </div>`;
    }
};

/**
 * 注册组件
 */
function registerValueCards() {
    if (typeof Registry !== 'undefined') {
        Registry.registerComponent('valueCards', valueCards);
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { valueCards, registerValueCards };
} else {
    window.ValueCardsComponent = { valueCards, registerValueCards };
}
