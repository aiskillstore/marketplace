/**
 * PPT Framework - 结束页组件
 * 
 * 演示结束页面
 */

const ending = {
    meta: {
        name: 'ending',
        description: '结束页',
        defaultAnimation: { preset: 'scaleIn', duration: 600 }
    },

    render(data, slideData = {}) {
        const anim = Registry.resolveAnimation(data, slideData);
        const combinedStyle = ['text-align: center', anim.style, data.style].filter(Boolean).join('; ');
        const hideStepAttr = data.hideStep ? ` data-hide-step="${data.hideStep}"` : '';
        
        return `
            <div class="${anim.className}" data-step="${data.step}"${hideStepAttr} style="${combinedStyle}">
                <div class="ending-icon claude-icon">${data.icon}</div>
                <p class="ending-message">${data.message}</p>
                <p class="ending-thanks">${data.thanks}</p>
            </div>`;
    }
};

/**
 * 注册组件
 */
function registerEnding() {
    if (typeof Registry !== 'undefined') {
        Registry.registerComponent('ending', ending);
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ending, registerEnding };
} else {
    window.EndingComponent = { ending, registerEnding };
}
