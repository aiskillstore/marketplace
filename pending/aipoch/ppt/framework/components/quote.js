/**
 * PPT Framework - 引用块组件
 * 
 * 突出展示金句、观点、结论
 */

const quote = {
    meta: {
        name: 'quote',
        description: '引用块',
        defaultAnimation: { preset: 'scaleIn', duration: 400 }
    },

    render(data, slideData = {}) {
        const anim = Registry.resolveAnimation(data, slideData);
        const combinedStyle = [anim.style, data.style].filter(Boolean).join('; ');
        const hideStepAttr = data.hideStep ? ` data-hide-step="${data.hideStep}"` : '';
        
        return `
            <div class="quote-block ${anim.className}" data-step="${data.step}"${hideStepAttr} style="${combinedStyle}">
                <p class="quote-text ${data.gradient ? 'gradient' : ''}" ${data.textStyle ? `style="${data.textStyle}"` : ''}>${data.text}</p>
                ${data.author ? `<p class="quote-author">${data.author.icon ? `<span class="claude-icon">${data.author.icon}</span> ` : ''}${data.author.text}</p>` : ''}
            </div>`;
    }
};

/**
 * 注册组件
 */
function registerQuote() {
    if (typeof Registry !== 'undefined') {
        Registry.registerComponent('quote', quote);
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { quote, registerQuote };
} else {
    window.QuoteComponent = { quote, registerQuote };
}
